
from django.contrib.auth import get_user_model

from rest_framework import status
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import authentication_classes, api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from activities.models import AllActivity
from parties.api.serializers import AllPartiesSerializer, PartyDetailSerializer
from parties.models import Party


User = get_user_model()


@api_view(['POST', ])
@permission_classes([])
@authentication_classes([])
def add_party_view(request):
    payload = {}
    data = {}
    errors = {}

    party_full_name = request.data.get('party_full_name', '')
    party_logo = request.data.get('party_logo', '')
    party_initial = request.data.get('party_initial', '')
    year_formed = request.data.get('year_formed', '')

    if not party_full_name:
        errors['party_full_name'] = ['Party Full Name is required.']

    if not party_logo:
        errors['party_logo'] = ['Party logo is required.']

    if not party_initial:
        errors['party_initial'] = ['Party initials is required.']

    if not party_initial:
        errors['party_initial'] = ['Party initials is required.']

    if errors:
        payload['message'] = "Errors"
        payload['errors'] = errors
        return Response(payload, status=status.HTTP_400_BAD_REQUEST)

    new_party = Party.objects.create(
        party_full_name=party_full_name,
        party_logo=party_logo,
        party_initial=party_initial,
        year_formed=year_formed
    )

    data['party_id'] = new_party.party_id

    #
    new_activity = AllActivity.objects.create(
        user=User.objects.get(id=1),
        subject="Party Registration",
        body="New Party added"
    )
    new_activity.save()

    payload['message'] = "Successful"
    payload['data'] = data

    return Response(payload, status=status.HTTP_200_OK)



@api_view(['GET', ])
@permission_classes([IsAuthenticated, ])
@authentication_classes([TokenAuthentication, ])
def get_all_parties_view(request):
    payload = {}
    data = {}
    errors = {}

    if errors:
        payload['message'] = "Errors"
        payload['errors'] = errors
        return Response(payload, status=status.HTTP_400_BAD_REQUEST)

    all_parties = Party.objects.all()

    all_party_serializer = AllPartiesSerializer(all_parties, many=True)
    if all_party_serializer:
        _all_parties = all_party_serializer.data

    payload['message'] = "Successful"
    payload['data'] = _all_parties

    return Response(payload, status=status.HTTP_200_OK)



@api_view(['GET', ])
@permission_classes([IsAuthenticated, ])
@authentication_classes([TokenAuthentication, ])
def get_party_detail(request):
    payload = {}
    data = {}
    errors = {}

    party_id = request.query_params.get('party_id', None)

    if not party_id:
        errors['party_id'] = ["Party id required"]

    try:
        party = Party.objects.get(party_id=party_id)
    except Party.DoesNotExist:
        errors['party_id'] = ['Party does not exist.']

    if errors:
        payload['message'] = "Errors"
        payload['errors'] = errors
        return Response(payload, status=status.HTTP_400_BAD_REQUEST)

    party_serializer = PartyDetailSerializer(party, many=False)
    if party_serializer:
        party = party_serializer.data

    payload['message'] = "Successful"
    payload['data'] = party

    return Response(payload, status=status.HTTP_200_OK)
