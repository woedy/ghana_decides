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

class RegionsConsumers(AsyncJsonWebsocketConsumer):

    async def connect(self):
        self.user = None
        self.room_group_name = "region-room"
        self.user_id = None

        await self.accept()

    async def receive_json(self, content):
        print("RegionsConsumers: receive_json")
        command = content.get("command", None)
        user_id = content.get("user_id", None)
        data = content.get("data", None)
        search = content.get("search", None)
        page = content.get("page", None)
        region_id = content.get("region_id", None)

        try:
            if command == "add_region":
                await self.add_region(user_id, data)

            if command == "get_all_regions":
                await self.get_all_regions(user_id, search, page)

            if command == "delete_region":
                await self.delete_region(user_id, region_id)

            if command == "edit_region":
                await self.edit_region(user_id, region_id, data)

        except ClientError as e:
            await self.handle_client_error(e)

    async def add_region(self, user_id, data):

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        add_region_data = await add_region(user_id, data)

        if add_region_data != None:

            payload = json.loads(add_region_data)

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

    async def get_all_regions(self, user_id, search, page):

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        get_all_regions_data = await get_all_regions(user_id, search, page)

        if get_all_regions_data != None:

            payload = json.loads(get_all_regions_data)

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



    async def delete_region(self, user_id, region_id):

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        delete_region_data = await delete_region(user_id, region_id)

        if delete_region_data != None:

            payload = json.loads(delete_region_data)

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


    async def edit_region(self, user_id, region_id, data):

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        edit_region_data = await edit_region(user_id, region_id, data)

        if edit_region_data != None:

            payload = json.loads(edit_region_data)

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
        print("RegionsConsumers: disconnect")
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
def add_region(user_id, dataa):

    payload = {}
    data = {}
    errors = {}

    region_name = dataa['region_name']
    map_image_base64 = dataa['map_image']
    initials = dataa['initials']
    capital = dataa['capital']

    if not region_name:
        errors['region_name'] = ['Region name is required.']

    if errors:
        payload['message'] = "Errors"
        payload['errors'] = errors
        return json.dumps(payload)

    # Decode base64 image data
    image_data = base64.b64decode(map_image_base64)
    image_file = BytesIO(image_data)

    image_data = base64.b64decode(map_image_base64)

    # Save the image to a Django ImageField
    new_region = Region.objects.create(
        region_name=region_name,
        initials=initials,
        capital=capital
    )

    new_region.map_image.save(f"{region_name}.jpg", ContentFile(image_data), save=True)

    #
    new_activity = AllActivity.objects.create(
        user=User.objects.get(id=1),
        subject="Region Registration",
        body="New Region added"
    )
    new_activity.save()

    all_regions = Region.objects.all()


    all_regions_serializer = AllRegionsSerializer(all_regions, many=True)
    if all_regions_serializer:
        _all_regions = all_regions_serializer.data

    payload['message'] = "Successful"
    payload['data'] = _all_regions

    return json.dumps(payload)

@database_sync_to_async
def get_all_regions(user_id, search, page):
    payload = {}
    data = {}
    errors = {}

    if errors:
        payload['message'] = "Errors"
        payload['errors'] = errors
        return json.dumps(payload)

    all_regions = Region.objects.all()

    # Search functionality
    search_query = search
    if search_query:
        all_regions = all_regions.filter(
            Q(region_name__icontains=search_query) |
            Q(initials__icontains=search_query)
        )


    all_regions_serializer = AllRegionsSerializer(all_regions, many=True)
    if all_regions_serializer:
        _all_regions = all_regions_serializer.data

    payload['message'] = "Successful"
    payload['data'] = _all_regions


    return json.dumps(payload)


@database_sync_to_async
def delete_region(user_id, region_id):
    payload = {}
    data = {}
    errors = {}



    if not region_id:
        errors['region_id'] = ["Region id required"]

    try:
        region = Region.objects.get(region_id=region_id)
    except Region.DoesNotExist:
        errors['region_id'] = ['Region does not exist.']

    if errors:
        payload['message'] = "Errors"
        payload['errors'] = errors
        return json.dumps(payload)

    region.delete()

    all_regions = Region.objects.all()

    all_regions_serializer = AllRegionsSerializer(all_regions, many=True)
    if all_regions_serializer:
        _all_regions = all_regions_serializer.data

    payload['message'] = "Successful"
    payload['data'] = _all_regions
    return json.dumps(payload)


@database_sync_to_async
def edit_region(user_id, region_id, dataa):
    payload = {}
    data = {}
    errors = {}




    region_id = dataa['region_id']
    region_name = dataa['region_name']
    map_image_base64 = dataa['map_image']
    initials = dataa['initials']
    capital = dataa['capital']
    print(region_id)


    if not region_id:
        errors['region_id'] = ['Region ID is required.']

    if not region_name:
        errors['region_name'] = ['Region name is required.']

    try:
        region = Region.objects.get(region_id=region_id)
    except Region.DoesNotExist:
        errors['region_id'] = ['Region does not exist.']

    if errors:
        payload['message'] = "Errors"
        payload['errors'] = errors
        return json.dumps(payload)

        # Decode base64 image data
    image_data = base64.b64decode(map_image_base64)
    image_file = BytesIO(image_data)
    image_data = base64.b64decode(map_image_base64)


    region.region_name = region_name
    region.initials = initials
    region.capital = capital
    region.save()

    region.map_image.save(f"{region_name}.jpg", ContentFile(image_data), save=True)

    #
    new_activity = AllActivity.objects.create(
        user=User.objects.get(id=1),
        subject="Region Edited",
        body="Region Edited"
    )
    new_activity.save()


    all_regions = Region.objects.all()


    all_regions_serializer = AllRegionsSerializer(all_regions, many=True)
    if all_regions_serializer:
        _all_regions = all_regions_serializer.data

    payload['message'] = "Successful"
    payload['data'] = _all_regions

    return json.dumps(payload)
