import json

from channels.db import database_sync_to_async

from channels.generic.websocket import AsyncJsonWebsocketConsumer
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db.models import Q



class PresenterDashboardConsumers(AsyncJsonWebsocketConsumer):

    async def connect(self):
        self.user = None
        self.room_group_name = "elections-2024-room-dashboard"
        self.user_id = None

        await self.accept()

    async def receive_json(self, content):
        command = content.get("command", None)
        user_id = content.get("user_id", None)
        data = content.get("data", None)
        search = content.get("search", None)
        page = content.get("page", None)
        polling_station_id = content.get("polling_station_id", None)
        ballot = content.get("ballot", None)

        try:
            if command == "get_presenter_dashboard_data":
                await self.get_presenter_dashboard()

        except ClientError as e:
            await self.handle_client_error(e)
    async def get_presenter_dashboard(self):
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        get_presenter_dashboard_data = await get_presenter_dashboard()

        if get_presenter_dashboard_data is not None:
            payload = json.loads(get_presenter_dashboard_data)

            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type": "chat.message",
                    "payload": payload,
                }
            )

            # Trigger the event on DataAdminDashboardConsumers
            await self.channel_layer.group_send(
                'data-stream',
                {
                    "type": "update_dashboard",
                }
            )
        else:
            raise ClientError(204, "Something went wrong retrieving the data.")

    async def update_2024_election_dashboard(self, event):
        await self.get_presenter_dashboard()


    async def chat_message(self, event):
        await self.send_json(
            {
                "payload": event["payload"],
            },
        )

    async def disconnect(self, close_code):
        """
        Called when the WebSocket closes for any reason.
        """
        # leave the room
        try:
            if self.room_id is not None:
                await self.leave_room(self.room_id)
        except Exception:
            pass

    async def handle_client_error(self, e):
        """
        Called when a ClientError is raised.
        Sends error data to UI.
        """
        error_data = {}
        error_data['error'] = e.code
        if e.message:
            error_data['message'] = e.message
            await self.send_json(error_data)
        return



@database_sync_to_async
def get_presenter_dashboard():

    from django.contrib.auth import get_user_model


    from elections.api.serializers import AllElectionSerializer, ElectionPresidentialCandidateSerializer, \
    ElectionParliamentaryCandidateSerializer, PresidentialCandidatePollingStationVoteSerializer, \
    ParliamentaryCandidatePollingStationVoteSerializer
    
    from elections.models import Election, ElectionPresidentialCandidate, PresidentialCandidatePollingStationVote, \
    PresidentialCandidateElectoralAreaVote, PresidentialCandidateConstituencyVote, PresidentialCandidateRegionalVote, \
    ElectionParliamentaryCandidate, ParliamentaryCandidatePollingStationVote
    from ghana_decides_proj.exceptions import ClientError
    
    from regions.models import PollingStation, Constituency

    User = get_user_model()

    payload = {}
    data = {}

    presidential_result_chart = []
    incoming_presidential_votes = []  # Initialize list for incoming presidential votes
    incoming_parliamentary_votes = []  # Initialize list for incoming parliamentary votes

    first_presidential_candidate = {}
    second_presidential_candidate = {}

    election_2024 = Election.objects.all().filter(year="2024").first()

    all_election_2024_presidential_candidates = ElectionPresidentialCandidate.objects.all().filter(election=election_2024).order_by("-total_votes")

    if all_election_2024_presidential_candidates:
        _first_presidential_candidate = all_election_2024_presidential_candidates[0]
        first_presidential_candidate_serializer = ElectionPresidentialCandidateSerializer(_first_presidential_candidate, many=False)
        if first_presidential_candidate_serializer:
            __first_presidential_candidate = first_presidential_candidate_serializer.data

        first_presidential_candidate['first_presidential_candidate'] = __first_presidential_candidate

        first_prez_parl_can = (ElectionParliamentaryCandidate.objects
                               .filter(election=election_2024)
                               .filter(won=True)
                               .filter(candidate__party=_first_presidential_candidate.candidate.party)
                               .order_by('-created_at')
                               ).first()

        __first_prez_parl_can_candidate = None
        if first_prez_parl_can is not None:
            first_prez_parl_can_serializer = ElectionParliamentaryCandidateSerializer(first_prez_parl_can, many=False)
            __first_prez_parl_can_candidate = first_prez_parl_can_serializer.data

        first_presidential_candidate['parliamentary_candidate'] = __first_prez_parl_can_candidate

        if len(all_election_2024_presidential_candidates) > 1:
            _second_presidential_candidate = all_election_2024_presidential_candidates[1]
            second_presidential_candidate_serializer = ElectionPresidentialCandidateSerializer(_second_presidential_candidate, many=False)
            if second_presidential_candidate_serializer:
                __second_presidential_candidate = second_presidential_candidate_serializer.data

            second_presidential_candidate['second_presidential_candidate'] = __second_presidential_candidate

            second_prez_parl_can = (ElectionParliamentaryCandidate.objects
                                    .filter(election=election_2024)
                                    .filter(won=True)
                                    .filter(candidate__party=_second_presidential_candidate.candidate.party)
                                    .order_by('-created_at')
                                    ).first()

            __second_prez_parl_can_candidate = None
            if second_prez_parl_can is not None:
                second_prez_parl_can_serializer = ElectionParliamentaryCandidateSerializer(second_prez_parl_can, many=False)
                if second_prez_parl_can_serializer.data:  # Check if data is not empty
                    __second_prez_parl_can_candidate = second_prez_parl_can_serializer.data

            second_presidential_candidate['parliamentary_candidate'] = __second_prez_parl_can_candidate

        else:
            second_presidential_candidate = {}
    else:
        first_presidential_candidate = {}
        second_presidential_candidate = {}

    for candidate in all_election_2024_presidential_candidates:
        candidate_data = {
            "first_name": candidate.candidate.first_name,
            "last_name": candidate.candidate.last_name,
            "photo": candidate.candidate.photo.url,
            "party_full_name": candidate.candidate.party.party_full_name,
            "party_initial": candidate.candidate.party.party_initial,
            "party_logo": candidate.candidate.party.party_logo.url,
            "total_votes": float(candidate.total_votes),
            "total_votes_percent": float(candidate.total_votes_percent),
            "parliamentary_seat": candidate.parliamentary_seat,
        }

        presidential_result_chart.append(candidate_data)

    all_votes = []

    all_prez_incoming_vote_candidates = PresidentialCandidatePollingStationVote.objects.all().order_by("-created_at")
    all_prez_incoming_vote_candidates_serializer = PresidentialCandidatePollingStationVoteSerializer(all_prez_incoming_vote_candidates, many=True)
    if all_prez_incoming_vote_candidates_serializer:
        all_prez_incoming_vote_candidates = all_prez_incoming_vote_candidates_serializer.data
        incoming_presidential_votes.extend(all_prez_incoming_vote_candidates)

    all_parl_incoming_vote_candidates = ParliamentaryCandidatePollingStationVote.objects.all().order_by("-created_at")
    all_parl_incoming_vote_candidates_serializer = ParliamentaryCandidatePollingStationVoteSerializer(all_parl_incoming_vote_candidates, many=True)
    if all_parl_incoming_vote_candidates_serializer:
        all_parl_incoming_vote_candidates = all_parl_incoming_vote_candidates_serializer.data
        incoming_parliamentary_votes.extend(all_parl_incoming_vote_candidates)

    print(len(all_votes))

    incoming_presidential_votes = sorted(incoming_presidential_votes, key=lambda x: x['created_at'], reverse=True)[:10]  # Take only the first 3 items
    incoming_parliamentary_votes = sorted(incoming_parliamentary_votes, key=lambda x: x['created_at'], reverse=True)[:10]  # Take only the first 3 items

    print(len(incoming_presidential_votes))
    print(len(incoming_parliamentary_votes))

    data["first_presidential_candidate"] = first_presidential_candidate
    data["second_presidential_candidate"] = second_presidential_candidate
    data["presidential_result_chart"] = presidential_result_chart
    data["incoming_presidential_votes"] = incoming_presidential_votes
    data["incoming_parliamentary_votes"] = incoming_parliamentary_votes
    payload['message'] = "Successful"
    payload['data'] = data

    
    return json.dumps(payload)



@database_sync_to_async
def get_presenter_dashboard2222():

    from django.contrib.auth import get_user_model

    from elections.api.serializers import AllElectionSerializer, ElectionPresidentialCandidateSerializer, \
    ElectionParliamentaryCandidateSerializer, PresidentialCandidatePollingStationVoteSerializer, \
    ParliamentaryCandidatePollingStationVoteSerializer
    
    from elections.models import Election, ElectionPresidentialCandidate, PresidentialCandidatePollingStationVote, \
    PresidentialCandidateElectoralAreaVote, PresidentialCandidateConstituencyVote, PresidentialCandidateRegionalVote, \
    ElectionParliamentaryCandidate, ParliamentaryCandidatePollingStationVote
    from ghana_decides_proj.exceptions import ClientError
    
    from regions.models import PollingStation, Constituency

    User = get_user_model()

    payload = {}
    data = {}


    presidential_result_chart = []
    incoming_votes = []

    first_presidential_candidate = {}
    second_presidential_candidate = {}

    election_2024 = Election.objects.all().filter(year="2024").first()

    all_election_2024_presidential_candidates = ElectionPresidentialCandidate.objects.all().filter(election=election_2024).order_by("-total_votes")

    if all_election_2024_presidential_candidates:
        _first_presidential_candidate = all_election_2024_presidential_candidates[0]
        first_presidential_candidate_serializer = ElectionPresidentialCandidateSerializer(_first_presidential_candidate, many=False)
        if first_presidential_candidate_serializer:
            __first_presidential_candidate = first_presidential_candidate_serializer.data

        first_presidential_candidate['first_presidential_candidate'] = __first_presidential_candidate

        first_prez_parl_can = (ElectionParliamentaryCandidate.objects
                               .filter(election=election_2024)
                               .filter(won=True)
                               .filter(candidate__party=_first_presidential_candidate.candidate.party)
                               .order_by('-created_at')
                               ).first()

        __first_prez_parl_can_candidate = None
        if first_prez_parl_can is not None:
            first_prez_parl_can_serializer = ElectionParliamentaryCandidateSerializer(first_prez_parl_can, many=False)
            __first_prez_parl_can_candidate = first_prez_parl_can_serializer.data

        first_presidential_candidate['parliamentary_candidate'] = __first_prez_parl_can_candidate


        if len(all_election_2024_presidential_candidates) > 1:
            _second_presidential_candidate = all_election_2024_presidential_candidates[1]
            second_presidential_candidate_serializer = ElectionPresidentialCandidateSerializer(_second_presidential_candidate, many=False)
            if second_presidential_candidate_serializer:
                __second_presidential_candidate = second_presidential_candidate_serializer.data

            second_presidential_candidate['second_presidential_candidate'] = __second_presidential_candidate

            second_prez_parl_can = (ElectionParliamentaryCandidate.objects
                                    .filter(election=election_2024)
                                    .filter(won=True)
                                    .filter(candidate__party=_second_presidential_candidate.candidate.party)
                                    .order_by('-created_at')
                                    ).first()

            __second_prez_parl_can_candidate = None
            if second_prez_parl_can is not None:
                second_prez_parl_can_serializer = ElectionParliamentaryCandidateSerializer(second_prez_parl_can,
                                                                                           many=False)
                if second_prez_parl_can_serializer.data:  # Check if data is not empty
                    __second_prez_parl_can_candidate = second_prez_parl_can_serializer.data

            second_presidential_candidate['parliamentary_candidate'] = __second_prez_parl_can_candidate




        else:
            second_presidential_candidate = {}
    else:
        first_presidential_candidate = {}
        second_presidential_candidate = {}

    for candidate in all_election_2024_presidential_candidates:
        candidate_data = {
            "first_name": candidate.candidate.first_name,
            "last_name": candidate.candidate.last_name,
            "photo": candidate.candidate.photo.url,
            "party_full_name":candidate.candidate.party.party_full_name,
            "party_initial": candidate.candidate.party.party_initial,
            "party_logo": candidate.candidate.party.party_logo.url,
            "total_votes": float(candidate.total_votes),
            "total_votes_percent": float(candidate.total_votes_percent),
            "parliamentary_seat": candidate.parliamentary_seat,
        }

        presidential_result_chart.append(candidate_data)

    all_votes = []

    all_prez_incoming_vote_candidates = PresidentialCandidatePollingStationVote.objects.all().order_by("-created_at")
    all_prez_incoming_vote_candidates_serializer = PresidentialCandidatePollingStationVoteSerializer(all_prez_incoming_vote_candidates,
                                                                                      many=True)
    if all_prez_incoming_vote_candidates_serializer:
        all_prez_incoming_vote_candidates = all_prez_incoming_vote_candidates_serializer.data
        all_votes.extend(all_prez_incoming_vote_candidates)

    all_parl_incoming_vote_candidates = ParliamentaryCandidatePollingStationVote.objects.all().order_by("-created_at")

    print(all_parl_incoming_vote_candidates)
    all_parl_incoming_vote_candidates_serializer = ParliamentaryCandidatePollingStationVoteSerializer(
        all_parl_incoming_vote_candidates,
        many=True)
        
    if all_parl_incoming_vote_candidates_serializer:
        all_parl_incoming_vote_candidates = all_parl_incoming_vote_candidates_serializer.data
        all_votes.extend(all_parl_incoming_vote_candidates)

    print(len(all_votes))

    incoming_votes = sorted(all_votes, key=lambda x: x['created_at'])

    print(len(incoming_votes))

    data["first_presidential_candidate"] = first_presidential_candidate
    data["second_presidential_candidate"] = second_presidential_candidate
    data["presidential_result_chart"] = presidential_result_chart
    data["incoming_votes"] = incoming_votes
    payload['message'] = "Successful"
    payload['data'] = data

    return json.dumps(payload)

