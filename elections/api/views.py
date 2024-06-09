from django.contrib.auth import get_user_model

from rest_framework import status
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import authentication_classes, api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from activities.models import AllActivity
from elections.api.serializers import AllElectionSerializer, ElectionDetailSerializer, \
    PresidentialCandidateRegionalVoteSerializer, ElectionPresidentialCandidateSerializer
from elections.models import Election, PresidentialCandidateRegionalVote
from candidates.models import Party
from regions.models import RegionLayerCoordinate

User = get_user_model()


@api_view(['POST', ])
@permission_classes([IsAuthenticated, ])
@authentication_classes([TokenAuthentication, ])
def  add_election_view(request):
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


#########################################################

@api_view(['GET', ])
@permission_classes([IsAuthenticated, ])
@authentication_classes([TokenAuthentication, ])
def get_regional_presidential_votes(request):
    payload = {}
    errors = {}

    if errors:
        payload['message'] = "Errors"
        payload['errors'] = errors
        return Response(payload, status=status.HTTP_400_BAD_REQUEST)

    election_2024 = Election.objects.filter(year='2024').first()

    if not election_2024:
        payload['message'] = "Election not found"
        return Response(payload, status=status.HTTP_404_NOT_FOUND)

    regional_prez_can_votes = PresidentialCandidateRegionalVote.objects.filter(election=election_2024)

    regionsss = {}

    for entry in regional_prez_can_votes:
        region_name = entry.region.region_name
        prez_candidate = entry.prez_candidate

        # Serialize the prez_candidate object
        prez_candidate_serialized = ElectionPresidentialCandidateSerializer(prez_candidate).data

        candidate_info = {
            "election_prez_id": prez_candidate_serialized['election_prez_id'],
            "candidate": prez_candidate_serialized['candidate'],
            "total_votes": prez_candidate_serialized['total_votes'],
            "total_votes_percent": prez_candidate_serialized['total_votes_percent'],
            "region_total_votes": entry.total_votes,
            "region_total_votes_percent": entry.total_votes_percent,
            "region_parliamentary_seat": entry.parliamentary_seat
        }

        if region_name not in regionsss:
            regionsss[region_name] = []

        regionsss[region_name].append(candidate_info)

    payload['message'] = "Successful"
    payload['data'] = regionsss

    return Response(payload, status=status.HTTP_200_OK)

@api_view(['GET', ])
@permission_classes([IsAuthenticated, ])
@authentication_classes([TokenAuthentication, ])
def get_regional_presidential_votes(request):
    payload = {}
    data = {}
    errors = {}

    if errors:
        payload['message'] = "Errors"
        payload['errors'] = errors
        return Response(payload, status=status.HTTP_400_BAD_REQUEST)

    election_2024 = Election.objects.all().filter(year='2024').first()

    regional_prez_can_votes = PresidentialCandidateRegionalVote.objects.filter(election=election_2024)

    regions_map_data = {}

    for entry in regional_prez_can_votes:
        region_name = entry.region.region_name
        region_id = entry.region.region_id
        prez_candidate = entry.prez_candidate
        prez_candidate_serialized = ElectionPresidentialCandidateSerializer(prez_candidate, many=False).data

        # Retrieve region coordinates
        region_coordinates = RegionLayerCoordinate.objects.filter(region=entry.region)
        coordinates = [{"lng": coord.lng, "lat": coord.lat} for coord in region_coordinates]

        candidate_info = {
            "region_id": region_id,
            "election_prez_id": prez_candidate_serialized['election_prez_id'],
            "party_id": prez_candidate_serialized['candidate']['party']['party_id'],
            "party_name": prez_candidate_serialized['candidate']['party']['party_full_name'],
            "party_color": prez_candidate_serialized['candidate']['party']['party_color'],
            "total_votes": entry.total_votes,
            "coordinates": coordinates
        }

        if region_name not in regions_map_data:
            regions_map_data[region_name] = candidate_info
        else:
            if candidate_info["total_votes"] > regions_map_data[region_name]["total_votes"]:
                regions_map_data[region_name] = candidate_info

    # Map to the desired structure
    region_data_list = []

    for region_name, info in regions_map_data.items():
        coordinates = info["coordinates"]
        formatted_coordinates = [[coord["lng"], coord["lat"]] for coord in coordinates]

        region_data = {
            "type": "Feature",
            "properties": {
                "region_id": info.get("region_id", ""),  # Assuming region_id can be added in the original data structure
                "region_name": region_name,
                "leading_color": info["party_color"]
            },
            "geometry": {
                "coordinates": [formatted_coordinates],
                "type": "Polygon"
            }
        }

        region_data_list.append(region_data)

    payload['message'] = "Successful"
    payload['data'] = region_data_list

    return Response(payload, status=status.HTTP_200_OK)