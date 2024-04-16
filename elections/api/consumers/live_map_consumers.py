import json

from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model

from channels.generic.websocket import AsyncJsonWebsocketConsumer
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db.models import Q

from elections.api.serializers import AllElectionSerializer, ElectionPresidentialCandidateSerializer, \
    ElectionParliamentaryCandidateSerializer, PresidentialCandidatePollingStationVoteSerializer, \
    ParliamentaryCandidatePollingStationVoteSerializer, PresidentialCandidateRegionalVoteSerializer
from elections.models import Election, ElectionPresidentialCandidate, PresidentialCandidatePollingStationVote, \
    PresidentialCandidateElectoralAreaVote, PresidentialCandidateConstituencyVote, PresidentialCandidateRegionalVote, \
    ElectionParliamentaryCandidate, ParliamentaryCandidatePollingStationVote
from ghana_decides_proj.exceptions import ClientError
from regions.models import PollingStation, Region

User = get_user_model()


class LiveMapConsumers(AsyncJsonWebsocketConsumer):

    async def connect(self):
        self.user = None
        self.room_group_name = "live-map-room"
        self.user_id = None

        await self.accept()

    async def receive_json(self, content):
        command = content.get("command", None)
        user_id = content.get("user_id", None)
        data = content.get("data", None)

        try:
            if command == "get_live_map_data":
                await self.get_live_map_data()

            if command == "get_map_filter_data":
                await self.get_map_filter_data(data)

        except ClientError as e:
            await self.handle_client_error(e)
    async def get_live_map_data(self):
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        get_live_map_data_data = await get_live_map_data()

        if get_live_map_data_data is not None:
            payload = json.loads(get_live_map_data_data)

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


    async def get_map_filter_data(self, data):
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        get_map_filter_data_data = await get_map_filter_data(data)

        if get_map_filter_data_data is not None:
            payload = json.loads(get_map_filter_data_data)

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
def get_live_map_data():
    payload = {}
    data = {}


    election_year = 2024
    election_level = "Presidential"
    result_state = "General"
    display_name = "All Regions"

    display_names_list = []


    region_name = None
    constituency_name = None
    electoral_area_name = None
    polling_station_name = None

    if result_state == "General":
        election_2024 = Election.objects.all().filter(year=election_year).first()

        general_prez_can_votes = ElectionPresidentialCandidate.objects.filter(election=election_2024).order_by("-total_votes")
        general_prez_can_votes_serializer = ElectionPresidentialCandidateSerializer(general_prez_can_votes, many=True)
        candidates = general_prez_can_votes_serializer.data

        regions = Region.objects.all()
        for region in regions:
            print(region.region_name)
            display_names_list.append(region.region_name)

    if result_state == "General":
        data['display_name'] = "All Regions"
    if result_state == "Region":
        data['display_name'] = region_name
    elif result_state == "Constituency":
        data['display_name'] = constituency_name
    elif result_state == "Electoral Area":
        data['display_name'] = electoral_area_name
    elif result_state == "Polling Station":
        data['display_name'] = polling_station_name


    data['election_year'] = election_year
    data['election_level'] = election_level
    data['result_state'] = result_state
    data['candidates'] = candidates
    data['display_names_list'] = display_names_list


    payload['message'] = "Successful"
    payload['data'] = data

    return json.dumps(payload)



@database_sync_to_async
def get_map_filter_data(dataa):
    payload = {}
    data = {}

    print("###Entry")
    print(dataa)


    election_year = dataa['election_year']
    election_level = dataa['election_level']
    result_state = dataa['result_state']
    display_name = dataa['display_name']

    display_names_list = None


    region_name = None
    constituency_name = None
    electoral_area_name = None
    polling_station_name = None

    if result_state == "General":
        election_2024 = Election.objects.all().filter(year=election_year).first()

        general_prez_can_votes = ElectionPresidentialCandidate.objects.filter(election=election_2024).order_by("-total_votes")
        general_prez_can_votes_serializer = ElectionPresidentialCandidateSerializer(general_prez_can_votes,
                                                                                         many=True)
        candidates = general_prez_can_votes_serializer.data
    elif result_state == "Region":
        print(dataa)
        election_2024 = Election.objects.all().filter(year=election_year).first()
        #region = Region.objects.all().get(region_name=region_name)


        regional_prez_can_votes = PresidentialCandidateRegionalVote.objects.filter(election=election_2024).order_by("-total_votes")
        region_name = regional_prez_can_votes.first().region.region_name
        regional_prez_can_votes_serializer = PresidentialCandidateRegionalVoteSerializer(regional_prez_can_votes, many=True)
        candidates = regional_prez_can_votes_serializer.data

    if result_state == "General":
        data['display_name'] = "All Regions"
    if result_state == "Region":
        data['display_name'] = region_name
    elif result_state == "Constituency":
        data['display_name'] = constituency_name
    elif result_state == "Electoral Area":
        data['display_name'] = electoral_area_name
    elif result_state == "Polling Station":
        data['display_name'] = polling_station_name


    data['election_year'] = election_year
    data['election_level'] = election_level
    data['result_state'] = result_state
    data['candidates'] = candidates
    data['display_names_list'] = display_names_list


    payload['message'] = "Successful"
    payload['data'] = data

    return json.dumps(payload)



