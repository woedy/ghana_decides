import json

from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model

from channels.generic.websocket import AsyncJsonWebsocketConsumer
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db.models import Q
from rest_framework import status
from rest_framework.response import Response

from activities.models import AllActivity
from candidates.api.serializers import AllPartiesSerializer
from candidates.models import Party
from ghana_decides_proj.exceptions import ClientError


User = get_user_model()

class PartyConsumers(AsyncJsonWebsocketConsumer):

    async def connect(self):
        self.user = None
        self.room_group_name = "party-room"
        self.user_id = None

        await self.accept()

    async def receive_json(self, content):
        command = content.get("command", None)
        user_id = content.get("user_id", None)
        data = content.get("data", None)
        search = content.get("search", None)
        page = content.get("page", None)
        party_id = content.get("party_id", None)

        try:
            if command == "add_party":
                await self.add_party(user_id, data)

            if command == "get_all_parties":
                await self.get_all_parties(user_id, search, page)

            if command == "delete_party":
                await self.delete_party(user_id, party_id)

            if command == "edit_party":
                await self.edit_party(user_id, party_id, data)

        except ClientError as e:
            await self.handle_client_error(e)

    async def add_party(self, user_id, data):
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        add_party_data = await add_party(user_id, data)

        if add_party_data is not None:
            payload = json.loads(add_party_data)

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

    async def get_all_parties(self, user_id, search, page):
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        get_all_parties_data = await get_all_parties(user_id, search, page)

        if get_all_parties_data is not None:
            payload = json.loads(get_all_parties_data)

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

    async def delete_party(self, user_id, party_id):
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        delete_party_data = await delete_party(user_id, party_id)

        if delete_party_data is not None:
            payload = json.loads(delete_party_data)

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

    async def edit_party(self, user_id, party_id, data):
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        edit_party_data = await edit_party(user_id, party_id, data)

        if edit_party_data is not None:
            payload = json.loads(edit_party_data)

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
def add_party(user_id, dataa):
    payload = {}
    errors = {}

    party_full_name = dataa['party_full_name']
    party_initial = dataa['party_initial']
    year_formed = dataa['year_formed']
    party_logo = dataa['party_logo']
    bio = dataa['bio']

    if not party_full_name:
        errors['party_full_name'] = ['Party name is required.']

    if errors:
        payload['message'] = "Errors"
        payload['errors'] = errors
        return Response(payload, status=status.HTTP_400_BAD_REQUEST)

    new_party = Party.objects.create(
        party_full_name=party_full_name,
        party_initial=party_initial,
        year_formed=year_formed,
        party_logo=party_logo,
        bio=bio,
    )

    new_activity = AllActivity.objects.create(
        user=1,
        subject="Party Registration",
        body="New Party added"
    )
    new_activity.save()

    all_parties = Party.objects.all()
    paginator = Paginator(all_parties, 10)

    page = ""

    try:
        parties = paginator.page(page)
    except PageNotAnInteger:
        parties = paginator.page(1)
    except EmptyPage:
        parties = paginator.page(paginator.num_pages)

    all_parties_serializer = AllPartiesSerializer(parties, many=True)
    _all_parties = all_parties_serializer.data

    payload['message'] = "Successful"
    payload['data'] = _all_parties
    payload['pagination'] = {
        'total_items': paginator.count,
        'items_per_page': 10,
        'total_pages': paginator.num_pages,
        'current_page': parties.number,
        'has_next': parties.has_next(),
        'has_previous': parties.has_previous(),
    }

    return json.dumps(payload)

@database_sync_to_async
def get_all_parties(user_id, search, page):
    payload = {}
    errors = {}

    all_parties = Party.objects.all()

    search_query = search
    if search_query:
        all_parties = all_parties.filter(
            Q(party_full_name__icontains=search_query)
        )

    paginator = Paginator(all_parties, 10)

    try:
        parties = paginator.page(page)
    except PageNotAnInteger:
        parties = paginator.page(1)
    except EmptyPage:
        parties = paginator.page(paginator.num_pages)

    all_parties_serializer = AllPartiesSerializer(parties, many=True)
    _all_parties = all_parties_serializer.data

    payload['message'] = "Successful"
    payload['data'] = _all_parties
    payload['pagination'] = {
        'total_items': paginator.count,
        'items_per_page': 10,
        'total_pages': paginator.num_pages,
        'current_page': parties.number,
        'has_next': parties.has_next(),
        'has_previous': parties.has_previous(),
    }

    return json.dumps(payload)

@database_sync_to_async
def delete_party(user_id, party_id):
    payload = {}
    errors = {}

    if not party_id:
        errors['party_id'] = ["Party id required"]

    try:
        party = Party.objects.get(party_id=party_id)
    except Party.DoesNotExist:
        errors['party_id'] = ['Party does not exist.']

    if errors:
        payload['message'] = "Errors"
        payload['errors'] = errors
        return json.dumps(payload)

    party.delete()

    all_parties = Party.objects.all()
    paginator = Paginator(all_parties, 10)

    page = ""

    try:
        parties = paginator.page(page)
    except PageNotAnInteger:
        parties = paginator.page(1)
    except EmptyPage:
        parties = paginator.page(paginator.num_pages)

    all_parties_serializer = AllPartiesSerializer(parties, many=True)
    _all_parties = all_parties_serializer.data

    payload['message'] = "Successful"
    payload['data'] = _all_parties
    payload['pagination'] = {
        'total_items': paginator.count,
        'items_per_page': 10,
        'total_pages': paginator.num_pages,
        'current_page': parties.number,
        'has_next': parties.has_next(),
        'has_previous': parties.has_previous(),
    }

    return json.dumps(payload)

@database_sync_to_async
def edit_party(user_id, party_id, dataa):
    payload = {}
    errors = {}

    party_id = dataa['party_id']
    party_full_name = dataa['party_full_name']
    party_initial = dataa['party_initial']
    year_formed = dataa['year_formed']
    party_logo = dataa['party_logo']
    bio = dataa['bio']


    if not party_id:
        errors['party_id'] = ['Party ID is required.']

    if not party_full_name:
        errors['party_full_name'] = ['Party name is required.']

    try:
        party = Party.objects.get(id=party_id)
    except Party.DoesNotExist:
        errors['party_id'] = ['Party does not exist.']

    if errors:
        payload['message'] = "Errors"
        payload['errors'] = errors
        return json.dumps(payload)

    party.party_full_name = party_full_name
    party.party_initial = party_initial
    party.year_formed = year_formed
    party.party_logo = party_logo
    party.bio = bio

    party.save()

    new_activity = AllActivity.objects.create(
        user=User.objects.get(id=user_id),
        subject="Party Edited",
        body="Party Edited"
    )
    new_activity.save()

    all_parties = Party.objects.all()
    paginator = Paginator(all_parties, 10)

    page = ""

    try:
        parties = paginator.page(page)
    except PageNotAnInteger:
        parties = paginator.page(1)
    except EmptyPage:
        parties = paginator.page(paginator.num_pages)

    all_parties_serializer = AllPartiesSerializer(parties, many=True)
    _all_parties = all_parties_serializer.data

    payload['message'] = "Successful"
    payload['data'] = _all_parties
    payload['pagination'] = {
        'total_items': paginator.count,
        'items_per_page': 10,
        'total_pages': paginator.num_pages,
        'current_page': parties.number,
        'has_next': parties.has_next(),
        'has_previous': parties.has_previous(),
    }

    return json.dumps(payload)