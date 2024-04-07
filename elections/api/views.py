from django.contrib.auth import get_user_model

from rest_framework import status
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import authentication_classes, api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from activities.models import AllActivity
from elections.api.serializers import AllElectionSerializer, ElectionDetailSerializer
from elections.models import Election
from candidates.models import Party

User = get_user_model()


@api_view(['POST', ])
@permission_classes([IsAuthenticated, ])
@authentication_classes([TokenAuthentication, ])
def add_election_view(request):
    payload = {}
    data = {}
    errors = {}

    year = request.data.get('year', '')

    if year == "2024":
        errors['year'] = ['Election 2024 is yet to take place.']

    if not year:
        errors['year'] = ['Year is required.']

    qs = Election.objects.filter(year=year)
    if qs.exists():
        errors['year'] = ['Election year already exists.']
    else:
        pass

    if errors:
        payload['message'] = "Errors"
        payload['errors'] = errors
        return Response(payload, status=status.HTTP_400_BAD_REQUEST)

    new_election = Election.objects.create(
        year=year
    )

    data['election_id'] = new_election.election_id

    #
    new_activity = AllActivity.objects.create(
        user=User.objects.get(id=1),
        subject="Election Added",
        body="New Election added"
    )
    new_activity.save()

    payload['message'] = "Successful"
    payload['data'] = data

    return Response(payload, status=status.HTTP_200_OK)


@api_view(['GET', ])
@permission_classes([IsAuthenticated, ])
@authentication_classes([TokenAuthentication, ])
def get_all_election_history_view(request):
    payload = {}
    data = {}
    errors = {}

    if errors:
        payload['message'] = "Errors"
        payload['errors'] = errors
        return Response(payload, status=status.HTTP_400_BAD_REQUEST)

    all_elections = Election.objects.all().exclude(year="2024")

    all_elections_serializer = AllElectionSerializer(all_elections, many=True)
    if all_elections_serializer:
        _all_elections = all_elections_serializer.data

    payload['message'] = "Successful"
    payload['data'] = _all_elections

    return Response(payload, status=status.HTTP_200_OK)


@api_view(['GET', ])
@permission_classes([IsAuthenticated, ])
@authentication_classes([TokenAuthentication, ])
def get_election_details(request):
    payload = {}
    data = {}
    errors = {}

    election_id = request.query_params.get('election_id', None)

    if not election_id:
        errors['election_id'] = ["Election id required"]

    try:
        election = Election.objects.get(election_id=election_id)
    except Election.DoesNotExist:
        errors['election_id'] = ['Election does not exist.']

    if errors:
        payload['message'] = "Errors"
        payload['errors'] = errors
        return Response(payload, status=status.HTTP_400_BAD_REQUEST)

    election_serializer = ElectionDetailSerializer(election, many=False)
    if election_serializer:
        election = election_serializer.data

    payload['message'] = "Successful"
    payload['data'] = election

    return Response(payload, status=status.HTTP_200_OK)


@api_view(['POST', ])
@permission_classes([IsAuthenticated, ])
@authentication_classes([TokenAuthentication, ])
def add_election_2024_view(request):
    payload = {}
    data = {}
    errors = {}

    year = request.data.get('year', '')

    if not year:
        errors['year'] = ['Year is required.']

    if year != "2024":
        errors['year'] = ['Election year must be 2024.']

    if year == "2024":
        qs = Election.objects.filter(year=year)

        if qs.exists():
            errors['year'] = ['Election 2024 already exists.']
        else:
            pass

    if errors:
        payload['message'] = "Errors"
        payload['errors'] = errors
        return Response(payload, status=status.HTTP_400_BAD_REQUEST)

    new_election = Election.objects.create(
        year=year
    )

    data['election_id'] = new_election.election_id

    #
    new_activity = AllActivity.objects.create(
        user=User.objects.get(id=1),
        subject="Election Added",
        body="New Election added"
    )
    new_activity.save()

    payload['message'] = "Successful"
    payload['data'] = data

    return Response(payload, status=status.HTTP_200_OK)
