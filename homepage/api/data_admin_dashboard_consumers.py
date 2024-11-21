import json
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model

from channels.generic.websocket import AsyncJsonWebsocketConsumer
from django.db.models import Q
from rest_framework import status
from rest_framework.response import Response

from candidates.models import Party, PresidentialCandidate, ParliamentaryCandidate
from ghana_decides_proj.exceptions import ClientError
from regions.api.serializers import AllRegionsSerializer, AllConstituenciesSerializer
from regions.models import Region, Constituency, ElectoralArea, PollingStation

User = get_user_model()

class DataAdminDashboardConsumers(AsyncJsonWebsocketConsumer):

    async def connect(self):
        self.room_group_name = "data-stream"

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

    async def receive_json(self, content):
        print("DataAdminDashboardConsumers: receive_json")
        command = content.get("command", None)


        try:
            if command == "get_data_admin":
                await self.get_data_admin_dashboard_data()
                print("GETTING HOME DATA")

        except ClientError as e:
            await self.handle_client_error(e)

    async def get_data_admin_dashboard_data(self):

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        dashboard_data = await get_data_admin_dashboard_data()

        if dashboard_data != None:
            payload = json.loads(dashboard_data)

            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type": "chat.message",
                    "payload": payload,
                }
            )
        else:
            raise ClientError(204, "Something went wrong retrieving the data.")


    async def update_dashboard(self, event):
        await self.get_data_admin_dashboard_data()

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
        try:
            await self.channel_layer.group_discard(
                self.room_group_name,
                self.channel_name
            )
        except Exception:
            pass

    async def handle_client_error(self, e):
        """
        Called when a ClientError is raised.
        Sends error data to UI.
        """
        errorData = {}
        errorData['error'] = e.code
        if e.message:
            errorData['message'] = e.message
            await self.send_json(errorData)
        return



@database_sync_to_async
def get_data_admin_dashboard_data():
    payload = {}
    data = {}
    errors = {}


    if errors:
        payload['message'] = "Errors"
        payload['errors'] = errors
        return json.dumps(payload)


    regions = Region.objects.all()
    constituencies = Constituency.objects.all()
    electoral_areas = ElectoralArea.objects.all()
    polling_stations = PollingStation.objects.all()
    parties = Party.objects.all()
    presidential_candidates = PresidentialCandidate.objects.all()
    parliamentary_candidates = ParliamentaryCandidate.objects.all()


    payload['message'] = "Successful"
    payload['regions_count'] = regions.count()
    payload['constituencies_count'] = constituencies.count()
    payload['electoral_areas_count'] = electoral_areas.count()
    payload['polling_stations_count'] = polling_stations.count()
    payload['parties_count'] = parties.count()
    payload['presidential_candidates_count'] = presidential_candidates.count()
    payload['parliamentary_candidates_count'] = parliamentary_candidates.count()
    return json.dumps(payload)
