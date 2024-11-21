
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
from regions.api.serializers import AllRegionsSerializer, AllConstituenciesSerializer, ElectoralAreaSerializer
from regions.models import Region, Constituency, ElectoralArea

User = get_user_model()

User = get_user_model()

class ElectoralAreaConsumers(AsyncJsonWebsocketConsumer):

    async def connect(self):
        self.user = None
        self.room_group_name = "electoral-area-room"
        self.user_id = None

        await self.accept()

    async def receive_json(self, content):
        print("ElectoralAreaConsumers: receive_json")
        command = content.get("command", None)
        user_id = content.get("user_id", None)
        data = content.get("data", None)
        search = content.get("search", None)
        page = content.get("page", None)
        electoral_area_id = content.get("electoral_area_id", None)

        try:
            if command == "add_electoral_area":
                await self.add_electoral_area(user_id, data)

            if command == "get_all_electoral_areas":
                await self.get_all_electoral_areas(user_id, search, page)

            if command == "delete_electoral_area":
                await self.delete_electoral_area(user_id, electoral_area_id)

            if command == "edit_electoral_area":
                await self.edit_electoral_area(user_id, electoral_area_id, data)

        except ClientError as e:
            await self.handle_client_error(e)

    async def add_electoral_area(self, user_id, data):
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        add_electoral_area_data = await add_electoral_area(user_id, data)

        if add_electoral_area_data is not None:
            payload = json.loads(add_electoral_area_data)

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

    async def get_all_electoral_areas(self, user_id, search, page):
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        get_all_electoral_areas_data = await get_all_electoral_areas(user_id, search, page)

        if get_all_electoral_areas_data is not None:
            payload = json.loads(get_all_electoral_areas_data)

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

    async def delete_electoral_area(self, user_id, electoral_area_id):
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        delete_electoral_area_data = await delete_electoral_area(user_id, electoral_area_id)

        if delete_electoral_area_data is not None:
            payload = json.loads(delete_electoral_area_data)

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

    async def edit_electoral_area(self, user_id, electoral_area_id, data):
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        edit_electoral_area_data = await edit_electoral_area(user_id, electoral_area_id, data)

        if edit_electoral_area_data is not None:
            payload = json.loads(edit_electoral_area_data)

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
        print("ElectoralAreaConsumers: disconnect")
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
def add_electoral_area(user_id, data):
    payload = {}
    data = {}
    errors = {}

    electoral_area_name = data['electoral_area_name']
    constituency_id = data['constituency_id']
    central_lat = data['central_lat']
    central_lng = data['central_lng']

    if not electoral_area_name:
        errors['electoral_area_name'] = ['Electoral area name is required.']

    if not constituency_id:
        errors['constituency_id'] = ['Constituency ID is required.']

    try:
        constituency = Constituency.objects.get(id=constituency_id)
    except Constituency.DoesNotExist:
        errors['constituency_id'] = ['Constituency does not exist.']

    if errors:
        payload['message'] = "Errors"
        payload['errors'] = errors
        return Response(payload, status=status.HTTP_400_BAD_REQUEST)

    new_electoral_area = ElectoralArea.objects.create(
        electoral_area_name=electoral_area_name,
        constituency=constituency,
    )

    new_activity = AllActivity.objects.create(
        user=User.objects.get(id=1),
        subject="Electoral Area Registration",
        body="New Electoral Area added"
    )
    new_activity.save()

    all_electoral_areas = ElectoralArea.objects.all()
    paginator = Paginator(all_electoral_areas, 10)  # 10 items per page

    page = ""

    try:
        electoral_areas = paginator.page(page)
    except PageNotAnInteger:
        electoral_areas = paginator.page(1)
    except EmptyPage:
        electoral_areas = paginator.page(paginator.num_pages)

    all_electoral_areas_serializer = ElectoralAreaSerializer(electoral_areas, many=True)
    _all_electoral_areas = all_electoral_areas_serializer.data

    payload['message'] = "Successful"
    payload['data'] = _all_electoral_areas
    payload['pagination'] = {
        'total_items': paginator.count,
        'items_per_page': 10,
        'total_pages': paginator.num_pages,
        'current_page': electoral_areas.number,
        'has_next': electoral_areas.has_next(),
        'has_previous': electoral_areas.has_previous(),
    }

    return json.dumps(payload)

@database_sync_to_async
def get_all_electoral_areas(user_id, search, page):
    payload = {}
    data = {}
    errors = {}

    all_electoral_areas = ElectoralArea.objects.all()

    search_query = search
    if search_query:
        all_electoral_areas = all_electoral_areas.filter(
            Q(electoral_area_name__icontains=search_query)
        )

    paginator = Paginator(all_electoral_areas, 10)

    try:
        electoral_areas = paginator.page(page)
    except PageNotAnInteger:
        electoral_areas = paginator.page(1)
    except EmptyPage:
        electoral_areas = paginator.page(paginator.num_pages)

    all_electoral_areas_serializer = ElectoralAreaSerializer(electoral_areas, many=True)
    _all_electoral_areas = all_electoral_areas_serializer.data

    payload['message'] = "Successful"
    payload['data'] = _all_electoral_areas
    payload['pagination'] = {
        'total_items': paginator.count,
        'items_per_page': 10,
        'total_pages': paginator.num_pages,
        'current_page': electoral_areas.number,
        'has_next': electoral_areas.has_next(),
        'has_previous': electoral_areas.has_previous(),
    }

    return json.dumps(payload)

@database_sync_to_async
def delete_electoral_area(user_id, electoral_area_id):
    payload = {}
    data = {}
    errors = {}

    if not electoral_area_id:
        errors['electoral_area_id'] = ["Electoral area id required"]

    try:
        electoral_area = ElectoralArea.objects.get(electoral_area_id=electoral_area_id)
    except ElectoralArea.DoesNotExist:
        errors['electoral_area_id'] = ['Electoral area does not exist.']

    if errors:
        payload['message'] = "Errors"
        payload['errors'] = errors
        return json.dumps(payload)

    electoral_area.delete()

    all_electoral_areas = ElectoralArea.objects.all()
    paginator = Paginator(all_electoral_areas, 10)

    page = ""

    try:
        electoral_areas = paginator.page(page)
    except PageNotAnInteger:
        electoral_areas = paginator.page(1)
    except EmptyPage:
        electoral_areas = paginator.page(paginator.num_pages)

    all_electoral_areas_serializer = ElectoralAreaSerializer(electoral_areas, many=True)
    _all_electoral_areas = all_electoral_areas_serializer.data

    payload['message'] = "Successful"
    payload['data'] = _all_electoral_areas
    payload['pagination'] = {
        'total_items': paginator.count,
        'items_per_page': 10,
        'total_pages': paginator.num_pages,
        'current_page': electoral_areas.number,
        'has_next': electoral_areas.has_next(),
        'has_previous': electoral_areas.has_previous(),
    }

    return json.dumps(payload)

@database_sync_to_async
def edit_electoral_area(user_id, electoral_area_id, data):
    payload = {}
    data = {}
    errors = {}

    electoral_area_id = data['electoral_area_id']
    electoral_area_name = data['electoral_area_name']

    if not electoral_area_id:
        errors['electoral_area_id'] = ['Electoral area ID is required.']

    if not electoral_area_name:
        errors['electoral_area_name'] = ['Electoral area name is required.']

    try:
        electoral_area = ElectoralArea.objects.get(id=electoral_area_id)
    except ElectoralArea.DoesNotExist:
        errors['electoral_area_id'] = ['Electoral area does not exist.']

    if errors:
        payload['message'] = "Errors"
        payload['errors'] = errors
        return json.dumps(payload)

    electoral_area.electoral_area_name = electoral_area_name
    electoral_area.save()

    new_activity = AllActivity.objects.create(
        user=User.objects.get(id=user_id),
        subject="Electoral Area Edited",
        body="Electoral Area Edited"
    )
    new_activity.save()

    all_electoral_areas = ElectoralArea.objects.all()
    paginator = Paginator(all_electoral_areas, 10)

    page = ""

    try:
        electoral_areas = paginator.page(page)
    except PageNotAnInteger:
        electoral_areas = paginator.page(1)
    except EmptyPage:
        electoral_areas = paginator.page(paginator.num_pages)

    all_electoral_areas_serializer = ElectoralAreaSerializer(electoral_areas, many=True)
    _all_electoral_areas = all_electoral_areas_serializer.data

    payload['message'] = "Successful"
    payload['data'] = _all_electoral_areas
    payload['pagination'] = {
        'total_items': paginator.count,
        'items_per_page': 10,
        'total_pages': paginator.num_pages,
        'current_page': electoral_areas.number,
        'has_next': electoral_areas.has_next(),
        'has_previous': electoral_areas.has_previous(),
    }

    return json.dumps(payload)
