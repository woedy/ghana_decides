import json

from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model

from channels.generic.websocket import AsyncJsonWebsocketConsumer
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db.models import Q

from elections.api.serializers import AllElectionSerializer
from elections.models import Election
from ghana_decides_proj.exceptions import ClientError

User = get_user_model()

class ElectionConsumers(AsyncJsonWebsocketConsumer):

    async def connect(self):
        self.user = None
        self.room_group_name = "elections-room"
        self.user_id = None

        await self.accept()

    async def receive_json(self, content):
        command = content.get("command", None)
        user_id = content.get("user_id", None)
        data = content.get("data", None)
        search = content.get("search", None)
        page = content.get("page", None)
        election_id = content.get("election_id", None)

        try:
            if command == "add_election":
                await self.add_election(user_id, data)

            if command == "get_all_elections":
                await self.get_all_elections(user_id, search, page)

            if command == "delete_election":
                await self.delete_election(user_id, election_id)

            if command == "edit_election":
                await self.edit_election(user_id, election_id, data)

        except ClientError as e:
            await self.handle_client_error(e)

    async def add_election(self, user_id, data):
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        add_election_data = await add_election(user_id, data)

        if add_election_data is not None:
            payload = json.loads(add_election_data)

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

    async def get_all_elections(self, user_id, search, page):
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        get_all_elections_data = await get_all_elections(user_id, search, page)

        if get_all_elections_data is not None:
            payload = json.loads(get_all_elections_data)

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

    async def delete_election(self, user_id, election_id):
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        delete_election_data = await delete_election(user_id, election_id)

        if delete_election_data is not None:
            payload = json.loads(delete_election_data)

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

    async def edit_election(self, user_id, election_id, data):
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        edit_election_data = await edit_election(user_id, election_id, data)

        if edit_election_data is not None:
            payload = json.loads(edit_election_data)

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
def add_election(user_id, dataa):
    pass


@database_sync_to_async
def get_all_elections(user_id, search, page):
    payload = {}
    errors = {}

    all_elections = Election.objects.all()

    search_query = search
    if search_query:
        all_elections = all_elections.filter(
            Q(year__icontains=search_query)
        )

    paginator = Paginator(all_elections, 10)

    try:
        elections = paginator.page(page)
    except PageNotAnInteger:
        elections = paginator.page(1)
    except EmptyPage:
        elections = paginator.page(paginator.num_pages)

    all_elections_serializer = AllElectionSerializer(elections, many=True)
    _all_elections = all_elections_serializer.data

    payload['message'] = "Successful"
    payload['data'] = _all_elections
    payload['pagination'] = {
        'total_items': paginator.count,
        'items_per_page': 10,
        'total_pages': paginator.num_pages,
        'current_page': elections.number,
        'has_next': elections.has_next(),
        'has_previous': elections.has_previous(),
    }

    return json.dumps(payload)

@database_sync_to_async
def delete_election(user_id, election_id):
    payload = {}
    data = {}
    errors = {}



    if not election_id:
        errors['election_id'] = ["Election id required"]

    try:
        election = Election.objects.get(election_id=election_id)
    except Election.DoesNotExist:
        errors['election_id'] = ['Election does not exist.']

    if errors:
        payload['message'] = "Errors"
        payload['errors'] = errors
        return json.dumps(payload)

    election.delete()

    all_elections = Election.objects.all()

    paginator = Paginator(all_elections, 10)  # 10 items per page
    page = ""

    try:
        elections = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        elections = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        elections = paginator.page(paginator.num_pages)

    all_elections_serializer = AllElectionSerializer(elections, many=True)
    if all_elections_serializer:
        _all_elections = all_elections_serializer.data

    payload['message'] = "Successful"
    payload['data'] = _all_elections
    payload['pagination'] = {
        'total_items': paginator.count,
        'items_per_page': 10,
        'total_pages': paginator.num_pages,
        'current_page': elections.number,
        'has_next': elections.has_next(),
        'has_previous': elections.has_previous(),
    }

    return json.dumps(payload)


@database_sync_to_async
def edit_election(user_id, election_id, dataa):
    pass