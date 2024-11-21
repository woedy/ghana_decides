
from django.contrib.auth import get_user_model
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db.models import Q
from regions.api.serializers import AllConstituencyVotersParticipationSerializer, AllElectoralVotersParticipationSerializer, AllPollingStationVotersParticipationSerializer, AllRegionalVotersParticipationSerializer
from regions.models import ConstituencyVotersParticipation, ElectoralVotersParticipation, PollingStation, PollingStationVotersParticipation, Region, RegionalVotersParticipation
from rest_framework import status
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import authentication_classes, api_view, permission_classes
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response


@api_view(['POST'])
@permission_classes([IsAuthenticated])
@authentication_classes([TokenAuthentication])
def add_election_polling_station_registered_voters_view(request):
    payload = {}
    data = {}
    errors = {}

    polling_station_id = request.data.get('polling_station_id', '')
    registered_voters = int(request.data.get('registered_voters', 0))  # Ensure this is an integer

    if not polling_station_id:
        errors['polling_station_id'] = ['Polling Station ID is required.']

    if not registered_voters:
        errors['registered_voters'] = ['Registered voters required.']

    try:
        polling_station = PollingStation.objects.get(polling_station_id=polling_station_id)
    except PollingStation.DoesNotExist:
        errors['polling_station_id'] = ['Polling Station does not exist.']

    if errors:
        payload['message'] = "Errors"
        payload['errors'] = errors
        return Response(payload, status=status.HTTP_400_BAD_REQUEST)

    # Unpack the instance from get_or_create()
    polling_participant, _ = PollingStationVotersParticipation.objects.get_or_create(polling_station=polling_station)
    polling_participant.registered_voters += registered_voters
    polling_participant.save()

    electoral_area = polling_station.electoral_area
    electoral_area_participant, _ = ElectoralVotersParticipation.objects.get_or_create(electoral_area=electoral_area)
    electoral_area_participant.registered_voters += registered_voters
    electoral_area_participant.save()

    constituency = electoral_area.constituency
    constituency_participant, _ = ConstituencyVotersParticipation.objects.get_or_create(constituency=constituency)
    constituency_participant.registered_voters += registered_voters
    constituency_participant.save()

    region = constituency.region
    region_participant, _ = RegionalVotersParticipation.objects.get_or_create(region=region)
    region_participant.registered_voters += registered_voters
    region_participant.save()

    payload['message'] = "Successful"
    payload['data'] = data

    return Response(payload, status=status.HTTP_200_OK)



@api_view(['POST'])
@permission_classes([IsAuthenticated])
@authentication_classes([TokenAuthentication])
def add_election_polling_station_attended_voters_view(request):
    payload = {}
    data = {}
    errors = {}

    polling_station_id = request.data.get('polling_station_id', '')

    if not polling_station_id:
        errors['polling_station_id'] = ['Polling Station ID is required.']

    try:
        polling_station = PollingStation.objects.get(polling_station_id=polling_station_id)
    except PollingStation.DoesNotExist:
        errors['polling_station_id'] = ['Polling Station does not exist.']

    if errors:
        payload['message'] = "Errors"
        payload['errors'] = errors
        return Response(payload, status=status.HTTP_400_BAD_REQUEST)

    # Polling Station Participation
    polling_participant, _ = PollingStationVotersParticipation.objects.get_or_create(polling_station=polling_station)
    polling_participant.voters += 1
    polling_participant.non_voters = polling_participant.registered_voters - polling_participant.voters
    if polling_participant.registered_voters > 0:
        polling_participant.turn_out_percent = (polling_participant.voters / polling_participant.registered_voters) * 100
    polling_participant.save()

    # Electoral Area Participation
    electoral_area = polling_station.electoral_area
    electoral_area_participant, _ = ElectoralVotersParticipation.objects.get_or_create(electoral_area=electoral_area)
    electoral_area_participant.voters += 1
    electoral_area_participant.non_voters = electoral_area_participant.registered_voters - electoral_area_participant.voters
    if electoral_area_participant.registered_voters > 0:
        electoral_area_participant.turn_out_percent = (electoral_area_participant.voters / electoral_area_participant.registered_voters) * 100
    electoral_area_participant.save()

    # Constituency Participation
    constituency = electoral_area.constituency
    constituency_participant, _ = ConstituencyVotersParticipation.objects.get_or_create(constituency=constituency)
    constituency_participant.voters += 1
    constituency_participant.non_voters = constituency_participant.registered_voters - constituency_participant.voters
    if constituency_participant.registered_voters > 0:
        constituency_participant.turn_out_percent = (constituency_participant.voters / constituency_participant.registered_voters) * 100
    constituency_participant.save()

    # Regional Participation
    region = constituency.region
    region_participant, _ = RegionalVotersParticipation.objects.get_or_create(region=region)
    region_participant.voters += 1
    region_participant.non_voters = region_participant.registered_voters - region_participant.voters
    if region_participant.registered_voters > 0:
        region_participant.turn_out_percent = (region_participant.voters / region_participant.registered_voters) * 100
    region_participant.save()

    payload['message'] = "Successful"
    payload['data'] = data

    return Response(payload, status=status.HTTP_200_OK)



@api_view(['POST'])
@permission_classes([IsAuthenticated])
@authentication_classes([TokenAuthentication])
def add_election_polling_station_attended_voters_view22222(request):
    payload = {}
    data = {}
    errors = {}

    polling_station_id = request.data.get('polling_station_id', '')


    if not polling_station_id:
        errors['polling_station_id'] = ['Polling Station ID is required.']

    try:
        polling_station = PollingStation.objects.get(polling_station_id=polling_station_id)
    except:
        errors['polling_station_id'] = ['Polling Station does not exist.']

    if errors:
        payload['message'] = "Errors"
        payload['errors'] = errors
        return Response(payload, status=status.HTTP_400_BAD_REQUEST)
    

    polling_participant = PollingStationVotersParticipation.objects.get_or_create(polling_station=polling_station)
    polling_participant.voters += 1
    polling_participant.save()


    # Get polling station, electoral area, constituency, Region
    electoral_area = polling_station.electoral_area
    electoral_area_participant = ElectoralVotersParticipation.objects.get_or_create(electoral_area=electoral_area)
    electoral_area_participant.voters += 1 
    electoral_area_participant.save()


    constituency = electoral_area.constituency
    constituency_participant = ConstituencyVotersParticipation.objects.get_or_create(constituency=constituency)
    constituency_participant.voters += 1
    constituency_participant.save()



    region = constituency.region
    region_participant = RegionalVotersParticipation.objects.get_or_create(region=region)
    region_participant.voters += 1
    region_participant.save()


    payload['message'] = "Successful"
    payload['data'] = data

    return Response(payload, status=status.HTTP_200_OK)




@api_view(['GET', ])
@permission_classes([IsAuthenticated, ])
@authentication_classes([TokenAuthentication])
def get_all_polling_stations_participants(request):
    payload = {}
    data = {}
    errors = {}

    search_query = request.query_params.get('search', '')
    page_number = request.query_params.get('page', 1)
    polling_station_id = request.query_params.get('polling_station_id', '')
    election_year = request.query_params.get('election_year', '')
    page_size = 50

    participations = PollingStationVotersParticipation.objects.all()

    if search_query:
        participations = participations.filter(
            Q(polling_station__polling_station_name__icontains=search_query)
        )

    if polling_station_id:
        participations = participations.filter(
            polling_station__polling_station_id=polling_station_id
        )


    if election_year:
        participations = participations.filter(
            polling_station__election_year=election_year
        )

    paginator = Paginator(participations, page_size)

    try:
        paginated_participations = paginator.page(page_number)
    except PageNotAnInteger:
        paginated_participations = paginator.page(1)
    except EmptyPage:
        paginated_participations = paginator.page(paginator.num_pages)

    all_participations_serializer = AllPollingStationVotersParticipationSerializer(paginated_participations, many=True)

    data['polling_station_participation'] = all_participations_serializer.data
    data['pagination'] = {
        'page_number': paginated_participations.number,
        'count': participations.count(),
        'total_pages': paginator.num_pages,
        'next': paginated_participations.next_page_number() if paginated_participations.has_next() else None,
        'previous': paginated_participations.previous_page_number() if paginated_participations.has_previous() else None,
    }

    payload['message'] = "Successful"
    payload['data'] = data

    return Response(payload, status=status.HTTP_200_OK)






@api_view(['GET', ])
@permission_classes([IsAuthenticated, ])
@authentication_classes([TokenAuthentication])
def get_all_electoral_area_participants(request):
    payload = {}
    data = {}
    errors = {}

    search_query = request.query_params.get('search', '')
    page_number = request.query_params.get('page', 1)
    electoral_area_id = request.query_params.get('electoral_area_id', '')
    election_year = request.query_params.get('election_year', '')
    page_size = 50

    participations = ElectoralVotersParticipation.objects.all()

    if search_query:
        participations = participations.filter(
            Q(electoral_area__electoral_area_name__icontains=search_query)
        )

    if electoral_area_id:
        participations = participations.filter(
            electoral_area__electoral_area_id=electoral_area_id
        )

    if election_year:
        participations = participations.filter(
            electoral_area__election_year=election_year
        )


    paginator = Paginator(participations, page_size)

    try:
        paginated_participations = paginator.page(page_number)
    except PageNotAnInteger:
        paginated_participations = paginator.page(1)
    except EmptyPage:
        paginated_participations = paginator.page(paginator.num_pages)

    all_participations_serializer = AllElectoralVotersParticipationSerializer(paginated_participations, many=True)

    data['electoral_area_participation'] = all_participations_serializer.data
    data['pagination'] = {
        'page_number': paginated_participations.number,
        'count': participations.count(),
        'total_pages': paginator.num_pages,
        'next': paginated_participations.next_page_number() if paginated_participations.has_next() else None,
        'previous': paginated_participations.previous_page_number() if paginated_participations.has_previous() else None,
    }

    payload['message'] = "Successful"
    payload['data'] = data

    return Response(payload, status=status.HTTP_200_OK)




@api_view(['GET', ])
@permission_classes([IsAuthenticated, ])
@authentication_classes([TokenAuthentication])
def get_all_constituency_participants(request):
    payload = {}
    data = {}
    errors = {}

    search_query = request.query_params.get('search', '')
    page_number = request.query_params.get('page', 1)
    constituency_id = request.query_params.get('constituency_id', '')
    election_year = request.query_params.get('election_year', '')
    page_size = 50

    participations = ConstituencyVotersParticipation.objects.all()

    if search_query:
        participations = participations.filter(
            Q(constituency__constituency_name__icontains=search_query)
        )

    if constituency_id:
        participations = participations.filter(
            constituency__constituency_id=constituency_id
        )

    if election_year:
        participations = participations.filter(
            constituency__election_year=election_year
        )


    paginator = Paginator(participations, page_size)

    try:
        paginated_participations = paginator.page(page_number)
    except PageNotAnInteger:
        paginated_participations = paginator.page(1)
    except EmptyPage:
        paginated_participations = paginator.page(paginator.num_pages)

    all_participations_serializer = AllConstituencyVotersParticipationSerializer(paginated_participations, many=True)

    data['constituency_participation'] = all_participations_serializer.data
    data['pagination'] = {
        'page_number': paginated_participations.number,
        'count': participations.count(),
        'total_pages': paginator.num_pages,
        'next': paginated_participations.next_page_number() if paginated_participations.has_next() else None,
        'previous': paginated_participations.previous_page_number() if paginated_participations.has_previous() else None,
    }

    payload['message'] = "Successful"
    payload['data'] = data

    return Response(payload, status=status.HTTP_200_OK)




@api_view(['GET', ])
@permission_classes([IsAuthenticated, ])
@authentication_classes([TokenAuthentication])
def get_all_region_participants(request):
    payload = {}
    data = {}
    errors = {}

    search_query = request.query_params.get('search', '')
    page_number = request.query_params.get('page', 1)
    region_id = request.query_params.get('region_id', '')
    election_year = request.query_params.get('election_year', '')
    page_size = 50

    participations = RegionalVotersParticipation.objects.all()

    if search_query:
        participations = participations.filter(
            Q(region__region_name__icontains=search_query)
        )

    if region_id:
        participations = participations.filter(
            region__region_id=region_id
        )

    if election_year:
        participations = participations.filter(
            region__election_year=election_year
        )


    paginator = Paginator(participations, page_size)

    try:
        paginated_participations = paginator.page(page_number)
    except PageNotAnInteger:
        paginated_participations = paginator.page(1)
    except EmptyPage:
        paginated_participations = paginator.page(paginator.num_pages)

    all_participations_serializer = AllRegionalVotersParticipationSerializer(paginated_participations, many=True)

    data['region_participation'] = all_participations_serializer.data
    data['pagination'] = {
        'page_number': paginated_participations.number,
        'count': participations.count(),
        'total_pages': paginator.num_pages,
        'next': paginated_participations.next_page_number() if paginated_participations.has_next() else None,
        'previous': paginated_participations.previous_page_number() if paginated_participations.has_previous() else None,
    }

    payload['message'] = "Successful"
    payload['data'] = data

    return Response(payload, status=status.HTTP_200_OK)
