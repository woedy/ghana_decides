import base64
import json
from io import BytesIO

from PIL import Image
from channels.db import database_sync_to_async
from channels.layers import get_channel_layer
from django.contrib.auth import get_user_model

from channels.generic.websocket import AsyncJsonWebsocketConsumer
from django.core.files.base import ContentFile
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db.models import Q
from rest_framework import status
from rest_framework.response import Response

from activities.models import AllActivity
from ghana_decides_proj.exceptions import ClientError
from regions.api.serializers import AllRegionsSerializer, AllConstituenciesSerializer
from regions.models import Region, Constituency

User = get_user_model()

class ConstituencyConsumers(AsyncJsonWebsocketConsumer):

    async def connect(self):
        self.user = None
        self.room_group_name = "constituency-room"
        self.user_id = None

        await self.accept()

    async def receive_json(self, content):
        print("ConstituencyConsumers: receive_json")
        command = content.get("command", None)
        user_id = content.get("user_id", None)
        data = content.get("data", None)
        search = content.get("search", None)
        page = content.get("page", None)
        constituency_id = content.get("constituency_id", None)

        try:
            if command == "add_Constituency":
                await self.add_constituency(user_id, data)

            if command == "get_all_constituencies":
                await self.get_all_constituencies(user_id, search, page)

            if command == "delete_constituency":
                await self.delete_constituency(user_id, constituency_id)

            if command == "edit_constituency":
                await self.edit_constituency(user_id, constituency_id, data)

        except ClientError as e:
            await self.handle_client_error(e)

    async def add_constituency(self, user_id, data):
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        add_constituency_data = await add_constituency(user_id, data)

        if add_constituency_data is not None:
            payload = json.loads(add_constituency_data)

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

    async def get_all_constituencies(self, user_id, search, page):
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        get_all_constituencies_data = await get_all_constituencies(user_id, search, page)

        if get_all_constituencies_data is not None:
            payload = json.loads(get_all_constituencies_data)

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

    async def delete_constituency(self, user_id, constituency_id):
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        delete_constituency_data = await delete_constituency(user_id, constituency_id)

        if delete_constituency_data is not None:
            payload = json.loads(delete_constituency_data)

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

    async def edit_constituency(self, user_id, constituency_id, data):
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        edit_constituency_data = await edit_constituency(user_id, constituency_id, data)

        if edit_constituency_data is not None:
            payload = json.loads(edit_constituency_data)

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
        print("ConstituencyConsumers: disconnect")
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
def add_constituency(user_id, dataa):
    payload = {}
    data = {}
    errors = {}

    constituency_name = dataa['constituency_name']
    region_id = dataa['region_id']
    central_lat = dataa['central_lat']
    central_lng = dataa['central_lng']


    if not constituency_name:
        errors['constituency_name'] = ['Constituency name is required.']

    if not region_id:
        errors['region_id'] = ['Region ID is required.']

    try:
        region = Region.objects.get(region_id=region_id)
    except Region.DoesNotExist:
        errors['region_id'] = ['Region does not exist.']

    if errors:
        payload['message'] = "Errors"
        payload['errors'] = errors
        return Response(payload, status=status.HTTP_400_BAD_REQUEST)

    new_constituency = Constituency.objects.create(
        constituency_name=constituency_name,
        region=region,
    )


    new_activity = AllActivity.objects.create(
        user=User.objects.get(id=1),
        subject="Constituency Registration",
        body="New Constituency added"
    )
    new_activity.save()

    # Retrieve all constituencies and paginate the results
    all_constituencies = Constituency.objects.all().order_by("constituency_name")

    # Serialize the data
    all_constituencies_serializer = AllConstituenciesSerializer(all_constituencies, many=True)
    _all_constituencies = all_constituencies_serializer.data

    # Prepare the payload
    payload['message'] = "Successful"
    payload['data'] = _all_constituencies


    return json.dumps(payload)

@database_sync_to_async
def get_all_constituencies(user_id, search, page):
    payload = {}
    data = {}
    errors = {}

    # Retrieve all constituencies and paginate the results
    all_constituencies = Constituency.objects.all()

    # Search functionality
    search_query = search
    if search_query:
        all_constituencies = all_constituencies.filter(
            Q(constituency_name__icontains=search_query) |
            Q(initials__icontains=search_query)
        )

    # Serialize the data
    all_constituencies_serializer = AllConstituenciesSerializer(all_constituencies, many=True)
    _all_constituencies = all_constituencies_serializer.data

    # Prepare the payload
    payload['message'] = "Successful"
    payload['data'] = _all_constituencies

    return json.dumps(payload)

@database_sync_to_async
def delete_constituency(user_id, constituency_id):
    payload = {}
    data = {}
    errors = {}

    if not constituency_id:
        errors['constituency_id'] = ["Constituency id required"]

    try:
        constituency = Constituency.objects.get(constituency_id=constituency_id)
    except Constituency.DoesNotExist:
        errors['constituency_id'] = ['Constituency does not exist.']

    if errors:
        payload['message'] = "Errors"
        payload['errors'] = errors
        return json.dumps(payload)

    constituency.delete()

    # Retrieve all constituencies and paginate the results
    all_constituencies = Constituency.objects.all()

    # Serialize the data
    all_constituencies_serializer = AllConstituenciesSerializer(all_constituencies, many=True)
    _all_constituencies = all_constituencies_serializer.data

    # Prepare the payload
    payload['message'] = "Successful"
    payload['data'] = _all_constituencies


    return json.dumps(payload)

@database_sync_to_async
def edit_constituency(user_id, constituency_id, data):
    payload = {}
    data = {}
    errors = {}

    constituency_id = data['constituency_id']
    constituency_name = data['constituency_name']
    map_image_base64 = data['map_image']
    initials = data['initials']
    capital = data['capital']

    if not constituency_id:
        errors['constituency_id'] = ['Constituency ID is required.']

    if not constituency_name:
        errors['constituency_name'] = ['Constituency name is required.']

    try:
        constituency = Constituency.objects.get(id=constituency_id)
    except Constituency.DoesNotExist:
        errors['constituency_id'] = ['Constituency does not exist.']

    if errors:
        payload['message'] = "Errors"
        payload['errors'] = errors
        return json.dumps(payload)

    # Decode base64 image data
    image_data = base64.b64decode(map_image_base64)
    image_file = BytesIO(image_data)

    # Update the constituency fields
    constituency.constituency_name = constituency_name
    constituency.initials = initials
    constituency.capital = capital
    constituency.save()

    # Save the image to a Django ImageField
    constituency.map_image.save(f"{constituency_name}.jpg", ContentFile(image_data), save=True)

    # Create a new activity
    new_activity = AllActivity.objects.create(
        user=User.objects.get(id=user_id),
        subject="Constituency Edited",
        body="Constituency Edited"
    )
    new_activity.save()

    # Retrieve all constituencies and paginate the results
    all_constituencies = Constituency.objects.all()

    # Serialize the data
    all_constituencies_serializer = AllConstituenciesSerializer(all_constituencies, many=True)
    _all_constituencies = all_constituencies_serializer.data

    # Prepare the payload
    payload['message'] = "Successful"
    payload['data'] = _all_constituencies


    return json.dumps(payload)
