import json

from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model

from channels.generic.websocket import AsyncJsonWebsocketConsumer
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db.models import Q

from elections.api.serializers import AllElectionSerializer, ElectionPresidentialCandidateSerializer, \
    ElectionParliamentaryCandidateSerializer, PresidentialCandidatePollingStationVoteSerializer, \
    ParliamentaryCandidatePollingStationVoteSerializer
from elections.models import Election, ElectionPresidentialCandidate, PresidentialCandidatePollingStationVote, \
    PresidentialCandidateElectoralAreaVote, PresidentialCandidateConstituencyVote, PresidentialCandidateRegionalVote, \
    ElectionParliamentaryCandidate, ParliamentaryCandidatePollingStationVote
from ghana_decides_proj.exceptions import ClientError
from regions.models import PollingStation

User = get_user_model()


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
    payload = {}
    data = {}


    presidential_result_chart = []
    incoming_votes = []

    election_2024 = Election.objects.all().filter(year="2024").first()

    all_election_2024_presidential_candidates = ElectionPresidentialCandidate.objects.all().filter(election=election_2024).order_by("-total_votes")

    if all_election_2024_presidential_candidates:
        first_presidential_candidate = all_election_2024_presidential_candidates[0]
        first_presidential_candidate_serializer = ElectionPresidentialCandidateSerializer(first_presidential_candidate, many=False)
        if first_presidential_candidate_serializer:
            first_presidential_candidate = first_presidential_candidate_serializer.data

        if len(all_election_2024_presidential_candidates) > 1:
            second_presidential_candidate = all_election_2024_presidential_candidates[1]
            second_presidential_candidate_serializer = ElectionPresidentialCandidateSerializer(second_presidential_candidate, many=False)
            if second_presidential_candidate_serializer:
                second_presidential_candidate = second_presidential_candidate_serializer.data
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

    all_prez_incoming_vote_candidates = PresidentialCandidatePollingStationVote.objects.all().order_by("-created_at")
    all_prez_incoming_vote_candidates_serializer = PresidentialCandidatePollingStationVoteSerializer(all_prez_incoming_vote_candidates,
                                                                                      many=True)
    if all_prez_incoming_vote_candidates_serializer:
        all_prez_incoming_vote_candidates = all_prez_incoming_vote_candidates_serializer.data
        incoming_votes.extend(all_prez_incoming_vote_candidates)

    all_parl_incoming_vote_candidates = ParliamentaryCandidatePollingStationVote.objects.all().order_by("-created_at")
    all_parl_incoming_vote_candidates_serializer = ParliamentaryCandidatePollingStationVoteSerializer(
        all_parl_incoming_vote_candidates,
        many=True)
    if all_parl_incoming_vote_candidates_serializer:
        all_parl_incoming_vote_candidates = all_parl_incoming_vote_candidates_serializer.data
        incoming_votes.extend(all_parl_incoming_vote_candidates)

    data["first_presidential_candidate"] = first_presidential_candidate
    data["second_presidential_candidate"] = second_presidential_candidate
    data["presidential_result_chart"] = presidential_result_chart
    data["incoming_votes"] = incoming_votes
    payload['message'] = "Successful"
    payload['data'] = data

    return json.dumps(payload)
