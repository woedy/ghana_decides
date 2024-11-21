
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
from regions.api.serializers import AllRegionsSerializer, AllConstituenciesSerializer, ElectoralAreaSerializer, \
    PollingStationSerializer
from regions.models import Region, Constituency, ElectoralArea, PollingStation

User = get_user_model()


class PollingStationConsumer(AsyncJsonWebsocketConsumer):

    async def connect(self):
        self.user = None
        self.room_group_name = "polling-station-room"
        self.user_id = None

        await self.accept()

    async def receive_json(self, content):
        command = content.get("command", None)
        user_id = content.get("user_id", None)
        data = content.get("data", None)
        search = content.get("search", None)
        page = content.get("page", None)
        polling_station_id = content.get("polling_station_id", None)

        try:
            if command == "add_polling_station":
                await self.add_polling_station(user_id, data)

            if command == "get_all_polling_stations":
                await self.get_all_polling_stations(user_id, search, page)

            if command == "delete_polling_station":
                await self.delete_polling_station(user_id, polling_station_id)

            if command == "edit_polling_station":
                await self.edit_polling_station(user_id, polling_station_id, data)

        except ClientError as e:
            await self.handle_client_error(e)

    async def add_polling_station(self, user_id, data):
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        add_polling_station_data = await add_polling_station(user_id, data)

        if add_polling_station_data is not None:
            payload = json.loads(add_polling_station_data)

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

    async def get_all_polling_stations(self, user_id, search, page):
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        get_all_polling_stations_data = await get_all_polling_stations(user_id, search, page)

        if get_all_polling_stations_data is not None:
            payload = json.loads(get_all_polling_stations_data)

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

    async def delete_polling_station(self, user_id, polling_station_id):
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        delete_polling_station_data = await delete_polling_station(user_id, polling_station_id)

        if delete_polling_station_data is not None:
            payload = json.loads(delete_polling_station_data)

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

    async def edit_polling_station(self, user_id, polling_station_id, data):
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        edit_polling_station_data = await edit_polling_station(user_id, polling_station_id, data)

        if edit_polling_station_data is not None:
            payload = json.loads(edit_polling_station_data)

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
        print("PollingStationConsumer: disconnect")
        try:
            if self.room_id is not None:
                await self.leave_room(self.room_id)
        except Exception:
            pass

    async def handle_client_error(self, e):
        error_data = {}
        error_data['error'] = e.code
        if e.message:
            error_data['message'] = e.message
            await self.send_json(error_data)
        return



@database_sync_to_async
def add_polling_station(user_id, dataa):
    payload = {}
    errors = {}

    polling_station_name = dataa['polling_station_name']
    electoral_area_id = dataa['electoral_area_id']
    central_lat = dataa['central_lat']
    central_lng = dataa['central_lng']

    if not polling_station_name:
        errors['polling_station_name'] = ['Polling station name is required.']

    if not electoral_area_id:
        errors['electoral_area_id'] = ['Electoral area ID is required.']

    try:
        electoral_area = ElectoralArea.objects.get(electoral_area_id=electoral_area_id)
    except ElectoralArea.DoesNotExist:
        errors['electoral_area_id'] = ['Electoral area does not exist.']

    if errors:
        payload['message'] = "Errors"
        payload['errors'] = errors
        return json.dumps(payload)

    new_polling_station = PollingStation.objects.create(
        polling_station_name=polling_station_name,
        electoral_area=electoral_area,
        central_lat=central_lat,
        central_lng=central_lng,
    )

    new_activity = AllActivity.objects.create(
        user=1,
        subject="Polling Station Registration",
        body="New Polling Station added"
    )
    new_activity.save()

    all_polling_stations = PollingStation.objects.all()
    paginator = Paginator(all_polling_stations, 10)

    page = ""

    try:
        polling_stations = paginator.page(page)
    except PageNotAnInteger:
        polling_stations = paginator.page(1)
    except EmptyPage:
        polling_stations = paginator.page(paginator.num_pages)

    all_polling_stations_serializer = PollingStationSerializer(polling_stations, many=True)
    _all_polling_stations = all_polling_stations_serializer.data

    payload['message'] = "Successful"
    payload['data'] = _all_polling_stations
    payload['pagination'] = {
        'total_items': paginator.count,
        'items_per_page': 10,
        'total_pages': paginator.num_pages,
        'current_page': polling_stations.number,
        'has_next': polling_stations.has_next(),
        'has_previous': polling_stations.has_previous(),
    }

    return json.dumps(payload)

@database_sync_to_async
def get_all_polling_stations(user_id, search, page):
    payload = {}
    errors = {}

    all_polling_stations = PollingStation.objects.all()

    search_query = search
    if search_query:
        all_polling_stations = all_polling_stations.filter(
            Q(polling_station_name__icontains=search_query)
        )

    paginator = Paginator(all_polling_stations, 10)

    try:
        polling_stations = paginator.page(page)
    except PageNotAnInteger:
        polling_stations = paginator.page(1)
    except EmptyPage:
        polling_stations = paginator.page(paginator.num_pages)

    all_polling_stations_serializer = PollingStationSerializer(polling_stations, many=True)
    _all_polling_stations = all_polling_stations_serializer.data

    payload['message'] = "Successful"
    payload['data'] = _all_polling_stations
    payload['pagination'] = {
        'total_items': paginator.count,
        'items_per_page': 10,
        'total_pages': paginator.num_pages,
        'current_page': polling_stations.number,
        'has_next': polling_stations.has_next(),
        'has_previous': polling_stations.has_previous(),
    }

    return json.dumps(payload)

@database_sync_to_async
def delete_polling_station(user_id, polling_station_id):
    payload = {}
    errors = {}

    if not polling_station_id:
        errors['polling_station_id'] = ["Polling station id required"]

    try:
        polling_station = PollingStation.objects.get(polling_station_id=polling_station_id)
    except PollingStation.DoesNotExist:
        errors['polling_station_id'] = ['Polling station does not exist.']

    if errors:
        payload['message'] = "Errors"
        payload['errors'] = errors
        return json.dumps(payload)

    polling_station.delete()

    all_polling_stations = PollingStation.objects.all()
    paginator = Paginator(all_polling_stations, 10)

    page = ""

    try:
        polling_stations = paginator.page(page)
    except PageNotAnInteger:
        polling_stations = paginator.page(1)
    except EmptyPage:
        polling_stations = paginator.page(paginator.num_pages)

    all_polling_stations_serializer = PollingStationSerializer(polling_stations, many=True)
    _all_polling_stations = all_polling_stations_serializer.data

    payload['message'] = "Successful"
    payload['data'] = _all_polling_stations
    payload['pagination'] = {
        'total_items': paginator.count,
        'items_per_page': 10,
        'total_pages': paginator.num_pages,
        'current_page': polling_stations.number,
        'has_next': polling_stations.has_next(),
        'has_previous': polling_stations.has_previous(),
    }

    return json.dumps(payload)

@database_sync_to_async
def edit_polling_station(user_id, polling_station_id, data):
    payload = {}
    errors = {}

    polling_station_name = data.get('polling_station_name', None)
    electoral_area_id = data.get('electoral_area_id', None)
    central_lat = data.get('central_lat', None)
    central_lng = data.get('central_lng', None)

    if not polling_station_id:
        errors['polling_station_id'] = ['Polling station ID is required.']

    if not polling_station_name:
        errors['polling_station_name'] = ['Polling station name is required.']

    try:
        polling_station = PollingStation.objects.get(id=polling_station_id)
    except PollingStation.DoesNotExist:
        errors['polling_station_id'] = ['Polling station does not exist.']

    if errors:
        payload['message'] = "Errors"
        payload['errors'] = errors
        return json.dumps(payload)

    polling_station.polling_station_name = polling_station_name
    polling_station.electoral_area_id = electoral_area_id
    polling_station.central_lat = central_lat
    polling_station.central_lng = central_lng
    polling_station.save()

    new_activity = AllActivity.objects.create(
        user=User.objects.get(id=user_id),
        subject="Polling Station Edited",
        body="Polling Station Edited"
    )
    new_activity.save()

    all_polling_stations = PollingStation.objects.all()
    paginator = Paginator(all_polling_stations, 10)

    page = ""

    try:
        polling_stations = paginator.page(page)
    except PageNotAnInteger:
        polling_stations = paginator.page(1)
    except EmptyPage:
        polling_stations = paginator.page(paginator.num_pages)

    all_polling_stations_serializer = PollingStationSerializer(polling_stations, many=True)
    _all_polling_stations = all_polling_stations_serializer.data

    payload['message'] = "Successful"
    payload['data'] = _all_polling_stations
    payload['pagination'] = {
        'total_items': paginator.count,
        'items_per_page': 10,
        'total_pages': paginator.num_pages,
        'current_page': polling_stations.number,
        'has_next': polling_stations.has_next(),
        'has_previous': polling_stations.has_previous(),
    }

    return json.dumps(payload)
