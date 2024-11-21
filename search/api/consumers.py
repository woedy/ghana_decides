import json
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model

from channels.generic.websocket import AsyncJsonWebsocketConsumer
from django.db.models import Q
from rest_framework import status
from rest_framework.response import Response

from ghana_decides_proj.exceptions import ClientError
from regions.api.serializers import AllRegionsSerializer, AllConstituenciesSerializer
from regions.models import Region, Constituency

User = get_user_model()

class SearchSystemConsumers(AsyncJsonWebsocketConsumer):

    async def connect(self):
        self.user = None
        self.room_group_name = "search-system"
        self.user_id = None

        await self.accept()

    async def receive_json(self, content):
        print("SearchSystemConsumers: receive_json")
        command = content.get("command", None)
        user_id = content.get("user_id", None)
        search = content.get("search", None)
        page_number = content.get("page_number", None)

        try:
            if command == "search":
                await self.search_system(user_id, search, page_number)

        except ClientError as e:
            await self.handle_client_error(e)

    async def search_system(self, user_id, search, page_number):

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        search_data = await search_all_system(user_id, search, page_number)

        if search_data != None:
            payload = json.loads(search_data)

            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type": "chat.message",
                    "payload": payload,
                }
            )
        else:
            raise ClientError(204, "Something went wrong retrieving the search data.")

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
        print("Admin Chat Consumers: disconnect")
        try:
            if self.room_id != None:
                await self.leave_room(self.room_id)
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
def search_all_system(user_id, search, page_number):
    payload = {}
    data = {}
    errors = {}


    if not search:
        errors['search'] = "Search query is required"

    if errors:
        payload['message'] = "Errors"
        payload['errors'] = errors
        return json.dumps(payload)


    regions = Region.objects.filter(
        Q(region_name__icontains=search) |
        Q(initials__icontains=search)
    )

    constituencies = Constituency.objects.filter(
        Q(constituency_name__icontains=search)
    )

    regions_serializer = AllRegionsSerializer(regions, many=True)
    constituencies_serializer = AllConstituenciesSerializer(constituencies, many=True)

    payload['message'] = "Successful"
    payload['regions'] = regions_serializer.data
    payload['constituencies'] = constituencies_serializer.data

    return json.dumps(payload)
