import json

from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model

from channels.generic.websocket import AsyncJsonWebsocketConsumer
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db.models import Q

from elections.api.serializers import AllElectionSerializer, ElectionPresidentialCandidateSerializer, \
    ElectionParliamentaryCandidateSerializer
from elections.models import Election, ElectionPresidentialCandidate, PresidentialCandidatePollingStationVote, \
    PresidentialCandidateElectoralAreaVote, PresidentialCandidateConstituencyVote, PresidentialCandidateRegionalVote, \
    ElectionParliamentaryCandidate, ParliamentaryCandidatePollingStationVote, ParliamentaryCandidateElectoralAreaVote, \
    ParliamentaryCandidateConstituencyVote, ParliamentaryCandidateRegionalVote
from ghana_decides_proj.exceptions import ClientError
from regions.models import PollingStation

User = get_user_model()


class Election2024Consumers(AsyncJsonWebsocketConsumer):

    async def connect(self):
        self.user = None
        self.room_group_name = "elections-2024-room"
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
            if command == "add_presidential_vote":
                await self.add_presidential_vote(user_id, polling_station_id, ballot)

            if command == "add_parliamentary_vote":
                await self.add_parliamentary_vote(user_id, polling_station_id, ballot)



        except ClientError as e:
            await self.handle_client_error(e)

    async def add_presidential_vote(self, user_id, polling_station_id, ballot):
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        add_presidential_vote_data = await add_presidential_vote(user_id, polling_station_id, ballot)

        if add_presidential_vote_data is not None:
            payload = json.loads(add_presidential_vote_data)

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

            # Trigger the event on 2024 Election Dashboard
            await self.channel_layer.group_send(
                'elections-2024-room-dashboard',
                {
                    "type": "update_2024_election_dashboard",
                }
            )



        else:
            raise ClientError(204, "Something went wrong retrieving the data.")




    async def add_parliamentary_vote(self, user_id, polling_station_id, ballot):
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        add_parliamentary_vote_data = await add_parliamentary_vote(user_id, polling_station_id, ballot)

        if add_parliamentary_vote_data is not None:
            payload = json.loads(add_parliamentary_vote_data)

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

            # Trigger the event on 2024 Election Dashboard
            await self.channel_layer.group_send(
                'elections-2024-room-dashboard',
                {
                    "type": "update_2024_election_dashboard",
                }
            )



        else:
            raise ClientError(204, "Something went wrong retrieving the data.")


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
def add_presidential_vote(user_id, polling_station_id, ballot):
    payload = {}
    data = {}
    errors = {}

    if not polling_station_id:
        errors['polling_station_id'] = ['Polling Station id is required.']

    if not ballot:
        errors['ballot'] = ['Ballot is required.']

    try:
        polling_station = PollingStation.objects.get(polling_station_id=polling_station_id)
    except:
        errors['polling_station_id'] = ['Polling Station does not exist.']

    if errors:
        payload['message'] = "Errors"
        payload['errors'] = errors
        return json.dumps(payload)

    # Get Election Year (2024)
    election = Election.objects.get(year="2024")

    # Get polling station, electoral area, constituency, Region

    electoral_area = polling_station.electoral_area
    constituency = electoral_area.constituency
    region = constituency.region

    total_votes = sum(candidate['votes'] for candidate in ballot)

    for candidate in ballot:

        # Add vote to candidate votes
        election_prez_candidate = ElectionPresidentialCandidate.objects.get(
            election_prez_id=candidate['election_prez_id'])

        election_prez_candidate.total_votes = int(election_prez_candidate.total_votes) + int(candidate['votes'])
        election_prez_candidate.save()

        polling_station_vote = PresidentialCandidatePollingStationVote.objects.filter(
            election=election,
            prez_candidate=election_prez_candidate,
            polling_station=polling_station)

        if polling_station_vote.exists():
            print(polling_station)
            errors['polling_station_id'] = ['Election result for this Polling Station already exists.']

        if errors:
            payload['message'] = "Errors"
            payload['errors'] = errors
            return json.dumps(payload)

        polling_station_vote = PresidentialCandidatePollingStationVote.objects.create(
            election=election,
            prez_candidate=election_prez_candidate,
            polling_station=polling_station)

        polling_station_vote.total_votes = int(polling_station_vote.total_votes) + int(candidate['votes'])
        percentage_share = calculate_percentage(candidate['votes'], total_votes)
        polling_station_vote.total_votes_percent = percentage_share
        polling_station_vote.save()

        #     # Add vote to Electoral Area
        electoral_area_vote = PresidentialCandidateElectoralAreaVote.objects.filter(
            election=election,
            prez_candidate=election_prez_candidate,
            electoral_area=electoral_area
        ).first()

        if electoral_area_vote is not None:
            electoral_area_vote.total_votes = int(electoral_area_vote.total_votes) + int(candidate['votes'])
            electoral_area_vote.save()
        else:
            electoral_area_vote = PresidentialCandidateElectoralAreaVote.objects.create(
                election=election,
                prez_candidate=election_prez_candidate,
                electoral_area=electoral_area
            )
            electoral_area_vote.total_votes = int(candidate['votes'])
            electoral_area_vote.save()

        # Add vote to Constituency

        constituency_vote = PresidentialCandidateConstituencyVote.objects.filter(
            election=election,
            prez_candidate=election_prez_candidate,
            constituency=constituency
        ).first()

        if constituency_vote is not None:
            constituency_vote.total_votes = int(constituency_vote.total_votes) + int(candidate['votes'])
            constituency_vote.save()
        else:
            constituency_vote = PresidentialCandidateConstituencyVote.objects.create(
                election=election,
                prez_candidate=election_prez_candidate,
                constituency=constituency
            )
            constituency_vote.total_votes = int(candidate['votes'])
            constituency_vote.save()

        # Add vote to Region

        region_vote = PresidentialCandidateRegionalVote.objects.filter(
            election=election,
            prez_candidate=election_prez_candidate,
            region=region
        ).first()

        if region_vote is not None:
            region_vote.total_votes = int(region_vote.total_votes) + int(candidate['votes'])
            region_vote.save()
        else:
            region_vote = PresidentialCandidateRegionalVote.objects.create(
                election=election,
                prez_candidate=election_prez_candidate,
                region=region
            )
            region_vote.total_votes = int(candidate['votes'])
            region_vote.save()

    # Calculate General Percentage share
    presidential_candidates = ElectionPresidentialCandidate.objects.all()
    g_total_votes = sum(candidate.total_votes for candidate in presidential_candidates)
    for candidate in presidential_candidates:
        percentage_share = calculate_percentage(candidate.total_votes, g_total_votes)
        candidate.total_votes_percent = percentage_share
        candidate.save()

    # Calculate Electoral Area Percentage Share
    electoral_area_candidates = PresidentialCandidateElectoralAreaVote.objects.filter(
        election=election,
        electoral_area=electoral_area
    )
    ea_total_votes = sum(candidate.total_votes for candidate in electoral_area_candidates)
    for candidate in electoral_area_candidates:
        percentage_share = calculate_percentage(candidate.total_votes, ea_total_votes)
        candidate.total_votes_percent = percentage_share
        candidate.save()

    # Calculate Constituency Percentage Share
    constituency_candidates = PresidentialCandidateConstituencyVote.objects.filter(
        election=election,
        constituency=constituency
    )
    c_total_votes = sum(candidate.total_votes for candidate in constituency_candidates)
    for candidate in constituency_candidates:
        percentage_share = calculate_percentage(candidate.total_votes, c_total_votes)
        candidate.total_votes_percent = percentage_share
        candidate.save()

    # Calculate Region Percentage Share
    region_candidates = PresidentialCandidateRegionalVote.objects.filter(
        election=election,
        region=region
    )
    r_total_votes = sum(candidate.total_votes for candidate in region_candidates)
    for candidate in region_candidates:
        percentage_share = calculate_percentage(candidate.total_votes, r_total_votes)
        candidate.total_votes_percent = percentage_share
        candidate.save()

    # new_activity = AllActivity.objects.create(
    #     user=User.objects.get(id=1),
    #     subject="Election Parliamentary Candidate Added",
    #     body="New Election Parliamentary Candidate added"
    # )
    # new_activity.save()

    payload['message'] = "Successful"
    payload['data'] = data

    return json.dumps(payload)


def calculate_percentage(candidate_votes, total_votes):
    return (candidate_votes / total_votes) * 100

@database_sync_to_async
def add_parliamentary_vote(user_id, polling_station_id, ballot):
    payload = {}
    data = {}
    errors = {}

    if not polling_station_id:
        errors['polling_station_id'] = ['Polling Station id is required.']

    if not ballot:
        errors['ballot'] = ['Ballot is required.']

    try:
        polling_station = PollingStation.objects.get(polling_station_id=polling_station_id)
    except:
        errors['polling_station_id'] = ['Polling Station does not exist.']


    if errors:
        payload['message'] = "Errors"
        payload['errors'] = errors
        return json.dumps(payload)

    # Get Election Year (2024)
    election = Election.objects.get(year="2024")


    # Get polling station, electoral area, constituency, Region

    electoral_area = polling_station.electoral_area
    constituency = electoral_area.constituency
    region = constituency.region



    total_votes = sum(candidate['votes'] for candidate in ballot)

    for candidate in ballot:

        # Add vote to candidate votes
        election_parl_candidate = ElectionParliamentaryCandidate.objects.get(
            election_parl_id=candidate['election_parl_id'])

        election_parl_candidate.total_votes = int(election_parl_candidate.total_votes) + int(candidate['votes'])
        election_parl_candidate.save()

        polling_station_vote = ParliamentaryCandidatePollingStationVote.objects.filter(
                election=election,
                parl_candidate=election_parl_candidate,
                polling_station=polling_station)

        if polling_station_vote.exists():
            print(polling_station)
            errors['polling_station_id'] = ['Election result for this Polling Station already exists.']

        if errors:
            payload['message'] = "Errors"
            payload['errors'] = errors
            return json.dumps(payload)

        polling_station_vote = ParliamentaryCandidatePollingStationVote.objects.create(
            election=election,
            parl_candidate=election_parl_candidate,
            polling_station=polling_station)

        polling_station_vote.total_votes = int(polling_station_vote.total_votes) + int(candidate['votes'])
        percentage_share = calculate_percentage(candidate['votes'], total_votes)
        polling_station_vote.total_votes_percent = percentage_share
        polling_station_vote.save()

        #     # Add vote to Electoral Area
        electoral_area_vote = ParliamentaryCandidateElectoralAreaVote.objects.filter(
            election=election,
                parl_candidate=election_parl_candidate,
                electoral_area=electoral_area
                ).first()

        if electoral_area_vote is not None:
            electoral_area_vote.total_votes = int(electoral_area_vote.total_votes) + int(candidate['votes'])
            electoral_area_vote.save()
        else:
            electoral_area_vote = ParliamentaryCandidateElectoralAreaVote.objects.create(
                election=election,
                parl_candidate=election_parl_candidate,
                electoral_area=electoral_area
                )
            electoral_area_vote.total_votes = int(candidate['votes'])
            electoral_area_vote.save()

        # Add vote to Constituency


        constituency_vote = ParliamentaryCandidateConstituencyVote.objects.filter(
            election=election,
                parl_candidate=election_parl_candidate,
                constituency=constituency
                ).first()

        if constituency_vote is not None:
            constituency_vote.total_votes = int(constituency_vote.total_votes) + int(candidate['votes'])
            constituency_vote.save()
        else:
            constituency_vote = ParliamentaryCandidateConstituencyVote.objects.create(
                election=election,
                parl_candidate=election_parl_candidate,
                constituency=constituency
                )
            constituency_vote.total_votes = int(candidate['votes'])
            constituency_vote.save()



        # Add vote to Region

        region_vote = ParliamentaryCandidateRegionalVote.objects.filter(
            election=election,
                parl_candidate=election_parl_candidate,
                region=region
                ).first()

        if region_vote is not None:
            region_vote.total_votes = int(region_vote.total_votes) + int(candidate['votes'])
            region_vote.save()
        else:
            region_vote = ParliamentaryCandidateRegionalVote.objects.create(
                election=election,
                parl_candidate=election_parl_candidate,
                region=region
                )
            region_vote.total_votes = int(candidate['votes'])
            region_vote.save()



    # Calculate Electoral Area Percentage Share
    electoral_area_candidates = ParliamentaryCandidateElectoralAreaVote.objects.filter(
        election=election,
        electoral_area=electoral_area
    )
    ea_total_votes = sum(candidate.total_votes for candidate in electoral_area_candidates)
    for candidate in electoral_area_candidates:
        percentage_share = calculate_percentage(candidate.total_votes, ea_total_votes)
        candidate.total_votes_percent = percentage_share
        candidate.save()


    # Calculate Constituency Percentage Share
    constituency_candidates = ParliamentaryCandidateConstituencyVote.objects.filter(
        election=election,
        constituency=constituency
    )
    c_total_votes = sum(candidate.total_votes for candidate in constituency_candidates)
    for candidate in constituency_candidates:
        percentage_share = calculate_percentage(candidate.total_votes, c_total_votes)
        candidate.total_votes_percent = percentage_share
        candidate.save()

    leading_candidate = ParliamentaryCandidateConstituencyVote.objects.filter(
        election=election,
        constituency=constituency
    ).order_by('-total_votes').first()

    leading_candidate_party = leading_candidate.parl_candidate.candidate.party

    all_prez_candidates = ElectionPresidentialCandidate.objects.all()

    for candidate in all_prez_candidates:
        if candidate.candidate.party.party_id == leading_candidate_party.party_id:
            candidate.parliamentary_seat = int(candidate.parliamentary_seat) + 1
            candidate.save()





    # Calculate Region Percentage Share
    # region_candidates = ParliamentaryCandidateRegionalVote.objects.filter(
    #     election=election,
    #     region=region
    # )
    # r_total_votes = sum(candidate.total_votes for candidate in region_candidates)
    # for candidate in region_candidates:
    #     percentage_share = calculate_percentage(candidate.total_votes, r_total_votes)
    #     candidate.total_votes_percent = percentage_share
    #     candidate.save()



    # new_activity = AllActivity.objects.create(
    #     user=User.objects.get(id=1),
    #     subject="Election Parliamentary Candidate Added",
    #     body="New Election Parliamentary Candidate added"
    # )
    # new_activity.save()

    payload['message'] = "Successful"
    payload['data'] = data

    return json.dumps(payload)
