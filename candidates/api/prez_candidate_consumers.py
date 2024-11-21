import base64
import json
from io import BytesIO

from PIL import Image
from channels.db import database_sync_to_async


from channels.generic.websocket import AsyncJsonWebsocketConsumer
from django.core.files.base import ContentFile
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db.models import Q
from rest_framework import status
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

from activities.models import AllActivity
from candidates.api.serializers import AllPartiesSerializer, AllPresidentialCandidateSerializer
from candidates.models import Party, PresidentialCandidate
from ghana_decides_proj.exceptions import ClientError



class PresidentialCandidateConsumers(AsyncJsonWebsocketConsumer):

    async def connect(self):
        self.user = None
        self.room_group_name = "presidential-candidate-room"
        self.user_id = None

        await self.accept()

    async def receive_json(self, content):
        command = content.get("command", None)
        user_id = content.get("user_id", None)
        data = content.get("data", None)
        search = content.get("search", None)
        page = content.get("page", None)
        prez_can_id = content.get("prez_can_id", None)

        try:
            if command == "add_presidential_candidate":
                await self.add_presidential_candidate(user_id, data)

            if command == "get_all_presidential_candidates":
                await self.get_all_presidential_candidates(user_id, search, page)

            if command == "delete_presidential_candidate":
                await self.delete_presidential_candidate(user_id, prez_can_id)

            if command == "edit_presidential_candidate":
                await self.edit_presidential_candidate(user_id, prez_can_id, data)

        except ClientError as e:
            await self.handle_client_error(e)

    async def add_presidential_candidate(self, user_id, data):
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        add_candidate_data = await add_presidential_candidate(user_id, data)

        if add_candidate_data is not None:
            payload = json.loads(add_candidate_data)

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

    async def get_all_presidential_candidates(self, user_id, search, page):
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        get_all_candidates_data = await get_all_presidential_candidates(user_id, search, page)

        if get_all_candidates_data is not None:
            payload = json.loads(get_all_candidates_data)

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

    async def delete_presidential_candidate(self, user_id, prez_can_id):
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        delete_candidate_data = await delete_presidential_candidate(user_id, prez_can_id)

        if delete_candidate_data is not None:
            payload = json.loads(delete_candidate_data)

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

    async def edit_presidential_candidate(self, user_id, candidate_id, data):
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        edit_candidate_data = await edit_presidential_candidate(user_id, candidate_id, data)

        if edit_candidate_data is not None:
            payload = json.loads(edit_candidate_data)

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
def add_presidential_candidate(user_id, dataa):
    payload = {}
    data = {}
    errors = {}

    party_id = dataa['party_id']
    first_name = dataa['first_name']
    last_name = dataa['last_name']
    middle_name = dataa['middle_name']
    photo = dataa['photo']
    gender = dataa['gender']
    candidate_type = dataa['candidate_type']


    if not party_id:
        errors['party_id'] = ['Party id is required.']

    if not first_name:
        errors['first_name'] = ['First name id is required.']

    if not last_name:
        errors['last_name'] = ['Last Name is required.']

    if not photo:
        errors['photo'] = ['Photo is required.']

    if not gender:
        errors['gender'] = ['Gender is required.']

    if not candidate_type:
        errors['candidate_type'] = ['Candidate type is required.']


    try:
        party = Party.objects.get(party_id=party_id)
    except Party.DoesNotExist:
        errors['party_id'] = ['Party does not exist.']

    if errors:
        payload['message'] = "Errors"
        payload['errors'] = errors
        return json.dumps(payload)

    new_prez_can = PresidentialCandidate.objects.create(
        party=party,
        first_name=first_name,
        last_name=last_name,
        middle_name=middle_name,
        photo=photo,
        gender=gender,
        candidate_type=candidate_type,
    )

    data['prez_can_id'] = new_prez_can.prez_can_id

    #
    new_activity = AllActivity.objects.create(
        user=1,
        subject="Presidential Candidate Registration",
        body="New Presidential Candidate added"
    )
    new_activity.save()

    payload['message'] = "Successful"
    payload['data'] = data

    return json.dumps(payload)


@database_sync_to_async
def get_all_presidential_candidates(user_id, search_query, page):
    payload = {}
    data = {}
    errors = {}



    all_prez_can = PresidentialCandidate.objects.all()

    # Apply search filter if search query is provided
    if search_query:
        all_prez_can = all_prez_can.filter(
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query) |
            Q(middle_name__icontains=search_query)
        )

    all_candidates = PresidentialCandidate.objects.all()
    paginator = Paginator(all_candidates, 10)

    page = ""

    try:
        candidates = paginator.page(page)
    except PageNotAnInteger:
        candidates = paginator.page(1)
    except EmptyPage:
        candidates = paginator.page(paginator.num_pages)

    candidates_serializer = AllPresidentialCandidateSerializer(candidates, many=True)
    _candidates = candidates_serializer.data

    payload['message'] = "Successful"
    payload['data'] = _candidates
    payload['pagination'] = {
        'total_items': paginator.count,
        'items_per_page': 10,
        'total_pages': paginator.num_pages,
        'current_page': candidates.number,
        'has_next': candidates.has_next(),
        'has_previous': candidates.has_previous(),
    }
    return json.dumps(payload)


@database_sync_to_async
def edit_presidential_candidate(user_id, candidate_id, data):
    # Implement the logic to edit a presidential candidate
    pass



@database_sync_to_async
def delete_presidential_candidate(user_id, prez_can_id):
    payload = {}
    errors = {}

    if not prez_can_id:
        errors['prez_can_id'] = ["Presidential Candidate ID is required."]
    else:
        try:
            candidate = PresidentialCandidate.objects.get(prez_can_id=prez_can_id)
            candidate.delete()
        except PresidentialCandidate.DoesNotExist:
            errors['prez_can_id'] = ["Presidential  Candidate does not exist."]

    if errors:
        payload['message'] = "Errors"
        payload['errors'] = errors
        return json.dumps(payload)

    all_candidates = PresidentialCandidate.objects.all()
    paginator = Paginator(all_candidates, 10)

    page = ""

    try:
        candidates = paginator.page(page)
    except PageNotAnInteger:
        candidates = paginator.page(1)
    except EmptyPage:
        candidates = paginator.page(paginator.num_pages)

    candidates_serializer = AllPresidentialCandidateSerializer(candidates, many=True)
    _candidates = candidates_serializer.data

    payload['message'] = "Successful"
    payload['data'] = _candidates
    payload['pagination'] = {
        'total_items': paginator.count,
        'items_per_page': 10,
        'total_pages': paginator.num_pages,
        'current_page': candidates.number,
        'has_next': candidates.has_next(),
        'has_previous': candidates.has_previous(),
    }

    return json.dumps(payload)
