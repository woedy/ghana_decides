from datetime import datetime

from celery import chain
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.mail import EmailMessage
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db.models import Q
from django.utils import timezone
from django.utils.dateparse import parse_time
from rest_framework import status
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import authentication_classes, api_view, permission_classes
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from activities.models import AllActivity
from regions.api.serializers import AllRegionsSerializer, RegionDetailSerializer, RegionalConstituenciesSerializer, \
    AllConstituenciesSerializer, ConstituencyDetailSerializer, ConstituencyZoneSerializer, ZoneSerializer, \
    PollingStationSerializer
from regions.models import Region, Constituency, Zone, PollingStation, PollingStationVotersParticipation

User = get_user_model()


@api_view(['POST', ])
@permission_classes([IsAuthenticated, ])
@authentication_classes([TokenAuthentication, ])
def add_region_view(request):
    payload = {}
    data = {}
    errors = {}

    region_name = request.data.get('region_name', '')
    map_image = request.data.get('map_image', '')
    initials = request.data.get('initials', '')
    capital = request.data.get('capital', '')

    if not region_name:
        errors['region_name'] = ['Region name is required.']

    if errors:
        payload['message'] = "Errors"
        payload['errors'] = errors
        return Response(payload, status=status.HTTP_400_BAD_REQUEST)

    new_region = Region.objects.create(
        region_name=region_name,
        map_image=map_image,
        initials=initials,
        capital=capital
    )

    data['region_id'] = new_region.region_id

    #
    new_activity = AllActivity.objects.create(
        user=User.objects.get(id=1),
        subject="Region Registration",
        body="New Region added"
    )
    new_activity.save()

    payload['message'] = "Successful"
    payload['data'] = data

    return Response(payload, status=status.HTTP_200_OK)


@api_view(['POST', ])
@permission_classes([IsAuthenticated, ])
@authentication_classes([TokenAuthentication, ])
def edit_region_view(request):
    payload = {}
    data = {}
    errors = {}

    region_id = request.data.get('region_id', '')
    region_name = request.data.get('region_name', '')
    map_image = request.data.get('map_image', '')
    initials = request.data.get('initials', '')
    capital = request.data.get('capital', '')

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
        return Response(payload, status=status.HTTP_400_BAD_REQUEST)


    region.region_name = region_name
    region.map_image = map_image
    region.initials = initials
    region.capital = capital
    region.save()


    data['region_id'] = region.region_id

    #
    new_activity = AllActivity.objects.create(
        user=User.objects.get(id=1),
        subject="Region Edited",
        body="Region Edited"
    )
    new_activity.save()

    payload['message'] = "Successful"
    payload['data'] = data

    return Response(payload, status=status.HTTP_200_OK)



@api_view(['GET', ])
@permission_classes([])
@authentication_classes([])
def get_all_regions(request):
    payload = {}
    data = {}
    errors = {}

    if errors:
        payload['message'] = "Errors"
        payload['errors'] = errors
        return Response(payload, status=status.HTTP_400_BAD_REQUEST)

    all_regions = Region.objects.all()

    # Search functionality
    search_query = request.GET.get('search')
    if search_query:
        all_regions = all_regions.filter(
            Q(region_name__icontains=search_query) |
            Q(initials__icontains=search_query)
        )

    paginator = Paginator(all_regions, 10)  # 10 items per page
    page = request.GET.get('page')

    try:
        regions = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        regions = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        regions = paginator.page(paginator.num_pages)

    all_regions_serializer = AllRegionsSerializer(regions, many=True)
    if all_regions_serializer:
        _all_regions = all_regions_serializer.data

    payload['message'] = "Successful"
    payload['data'] = _all_regions
    payload['pagination'] = {
        'total_items': paginator.count,
        'items_per_page': 10,
        'total_pages': paginator.num_pages,
        'current_page': regions.number,
        'has_next': regions.has_next(),
        'has_previous': regions.has_previous(),
    }

    return Response(payload, status=status.HTTP_200_OK)

@api_view(['GET', ])
@permission_classes([IsAuthenticated, ])
@authentication_classes([TokenAuthentication, ])
def get_region_detail(request):
    payload = {}
    data = {}
    errors = {}

    region_id = request.query_params.get('region_id', None)

    if not region_id:
        errors['region_id'] = ["Region id required"]

    try:
        region = Region.objects.get(region_id=region_id)
    except Region.DoesNotExist:
        errors['region_id'] = ['Region does not exist.']

    if errors:
        payload['message'] = "Errors"
        payload['errors'] = errors
        return Response(payload, status=status.HTTP_400_BAD_REQUEST)

    region_serializer = RegionDetailSerializer(region, many=False)
    if region_serializer:
        region = region_serializer.data

    payload['message'] = "Successful"
    payload['data'] = region

    return Response(payload, status=status.HTTP_200_OK)


@api_view(['POST', ])
@permission_classes([IsAuthenticated, ])
@authentication_classes([TokenAuthentication, ])
def delete_region_view(request):
    payload = {}
    data = {}
    errors = {}


    region_id = request.data.get('region_id', '')



    if not region_id:
        errors['region_id'] = ["Region id required"]

    try:
        region = Region.objects.get(region_id=region_id)
    except Region.DoesNotExist:
        errors['region_id'] = ['Region does not exist.']

    if errors:
        payload['message'] = "Errors"
        payload['errors'] = errors
        return Response(payload, status=status.HTTP_400_BAD_REQUEST)

    region.delete()

    payload['message'] = "Successful"
    payload['data'] = data

    return Response(payload, status=status.HTTP_200_OK)

@api_view(['GET', ])
@permission_classes([IsAuthenticated, ])
@authentication_classes([TokenAuthentication, ])
def get_region_constituencies(request):
    payload = {}
    data = {}
    errors = {}

    region_id = request.query_params.get('region_id', None)

    if not region_id:
        errors['region_id'] = ["Region id required"]

    try:
        region = Region.objects.get(region_id=region_id)
    except Region.DoesNotExist:
        errors['region_id'] = ['Region does not exist.']

    if errors:
        payload['message'] = "Errors"
        payload['errors'] = errors
        return Response(payload, status=status.HTTP_400_BAD_REQUEST)

    constituencies = Constituency.objects.all().filter(region=region)

    # Search functionality
    search_query = request.query_params.get('search')
    if search_query:
        constituencies = constituencies.filter(constituency_name__icontains=search_query)

    paginator = Paginator(constituencies, 10)  # 10 items per page
    page = request.query_params.get('page')

    try:
        constituencies_page = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        constituencies_page = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        constituencies_page = paginator.page(paginator.num_pages)

    constituencies_serializer = RegionalConstituenciesSerializer(constituencies_page, many=True)
    if constituencies_serializer:
        _all_consti = constituencies_serializer.data

    payload['message'] = "Successful"
    payload['data'] = _all_consti
    payload['pagination'] = {
        'total_items': paginator.count,
        'items_per_page': 10,
        'total_pages': paginator.num_pages,
        'current_page': constituencies_page.number,
        'has_next': constituencies_page.has_next(),
        'has_previous': constituencies_page.has_previous(),
    }

    return Response(payload, status=status.HTTP_200_OK)


@api_view(['POST', ])
@permission_classes([])
@authentication_classes([])
def add_constituency_view(request):
    payload = {}
    data = {}
    errors = {}

    constituency_name = request.data.get('constituency_name', '')
    region_id = request.data.get('region_id', '')

    if not constituency_name:
        errors['constituency_name'] = ['Constituency name is required.']

    if not region_id:
        errors['region_id'] = ['Region ID is required.']

    try:
        region = Region.objects.get(region_id=region_id)
    except Region.DoesNotExist:
        errors['region_id'] = ['Region does not exist.']

    if errors:
        payload['message'] = "Errors"
        payload['errors'] = errors
        return Response(payload, status=status.HTTP_400_BAD_REQUEST)



    new_constituency = Constituency.objects.create(
        constituency_name=constituency_name,
        region=region,
    )

    data['constituency_id'] = new_constituency.constituency_id

    #
    new_activity = AllActivity.objects.create(
        user=User.objects.get(id=1),
        subject="Constituency Registration",
        body="New Constituency added"
    )
    new_activity.save()

    payload['message'] = "Successful"
    payload['data'] = data

    return Response(payload, status=status.HTTP_200_OK)


@api_view(['GET', ])
@permission_classes([IsAuthenticated, ])
@authentication_classes([TokenAuthentication, ])
def get_all_constituencies(request):
    payload = {}
    data = {}
    errors = {}

    search_query = request.GET.get('search')

    if errors:
        payload['message'] = "Errors"
        payload['errors'] = errors
        return Response(payload, status=status.HTTP_400_BAD_REQUEST)

    all_constituencies = Constituency.objects.all()

    # Search functionality
    if search_query:
        all_constituencies = all_constituencies.filter(
            Q(constituency_name__icontains=search_query)
        )

    paginator = PageNumberPagination()
    paginator.page_size = 10  # Number of items per page
    result_page = paginator.paginate_queryset(all_constituencies, request)

    all_constituencies_serializer = AllConstituenciesSerializer(result_page, many=True)
    if all_constituencies_serializer:
        _all_constituencies = all_constituencies_serializer.data

    payload['message'] = "Successful"
    payload['data'] = _all_constituencies
    payload['pagination'] = {
        'total_items': paginator.page.paginator.count,
        'items_per_page': paginator.page_size,
        'total_pages': paginator.page.paginator.num_pages,
        'current_page': paginator.page.number,
        'has_next': paginator.page.has_next(),
        'has_previous': paginator.page.has_previous(),
    }

    return Response(payload, status=status.HTTP_200_OK)


@api_view(['GET', ])
@permission_classes([IsAuthenticated, ])
@authentication_classes([TokenAuthentication, ])
def get_constituency_detail(request):
    payload = {}
    data = {}
    errors = {}

    constituency_id = request.query_params.get('constituency_id', None)

    if not constituency_id:
        errors['constituency_id'] = ["Constituency id required"]

    try:
        constituency = Constituency.objects.get(constituency_id=constituency_id)
    except Constituency.DoesNotExist:
        errors['constituency_id'] = ['Constituency does not exist.']

    if errors:
        payload['message'] = "Errors"
        payload['errors'] = errors
        return Response(payload, status=status.HTTP_400_BAD_REQUEST)

    constituency_serializer = ConstituencyDetailSerializer(constituency, many=False)
    if constituency_serializer:
        _constituency = constituency_serializer.data

    payload['message'] = "Successful"
    payload['data'] = _constituency

    return Response(payload, status=status.HTTP_200_OK)



@api_view(['GET', ])
@permission_classes([IsAuthenticated, ])
@authentication_classes([TokenAuthentication, ])
def get_constituency_zone(request):
    payload = {}
    data = {}
    errors = {}

    constituency_id = request.query_params.get('constituency_id', None)

    if not constituency_id:
        errors['constituency_id'] = ["Constituency id required"]

    try:
        constituency = Constituency.objects.get(constituency_id=constituency_id)
    except Constituency.DoesNotExist:
        errors['constituency_id'] = ['Constituency does not exist.']

    if errors:
        payload['message'] = "Errors"
        payload['errors'] = errors
        return Response(payload, status=status.HTTP_400_BAD_REQUEST)

    zones = Zone.objects.all().filter(constituency=constituency)

    # Search functionality
    search_query = request.query_params.get('search')
    if search_query:
        zones = zones.filter(zone_name__icontains=search_query)

    paginator = Paginator(zones, 10)  # 10 items per page
    page = request.query_params.get('page')

    try:
        zones_page = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        zones_page = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        zones_page = paginator.page(paginator.num_pages)

    zone_serializer = ConstituencyZoneSerializer(zones_page, many=True)
    if zone_serializer:
        _all_zones = zone_serializer.data

    payload['message'] = "Successful"
    payload['data'] = _all_zones
    payload['pagination'] = {
        'total_items': paginator.count,
        'items_per_page': 10,
        'total_pages': paginator.num_pages,
        'current_page': zones_page.number,
        'has_next': zones_page.has_next(),
        'has_previous': zones_page.has_previous(),
    }

    return Response(payload, status=status.HTTP_200_OK)




@api_view(['POST', ])
@permission_classes([IsAuthenticated, ])
@authentication_classes([TokenAuthentication, ])
def edit_constituency_view(request):
    payload = {}
    data = {}
    errors = {}

    constituency_id = request.data.get('constituency_id', '')
    constituency_name = request.data.get('constituency_name', '')
    central_lat = request.data.get('central_lat', '')
    central_lng = request.data.get('central_lng', '')

    if not constituency_id:
        errors['constituency_id'] = ['Constituency ID is required.']

    if not constituency_name:
        errors['constituency_name'] = ['Constituency name is required.']

    try:
        constituency = Constituency.objects.get(constituency_id=constituency_id)
    except Constituency.DoesNotExist:
        errors['constituency_id'] = ['Constituency does not exist.']

    if errors:
        payload['message'] = "Errors"
        payload['errors'] = errors
        return Response(payload, status=status.HTTP_400_BAD_REQUEST)

    constituency.constituency_name = constituency_name
    constituency.central_lat = central_lat
    constituency.central_lng = central_lng
    constituency.save()

    data['constituency_id'] = constituency.constituency_id

    #
    new_activity = AllActivity.objects.create(
        user=User.objects.get(id=1),
        subject="Constituency Edited",
        body="Constituency Edited"
    )
    new_activity.save()

    payload['message'] = "Successful"
    payload['data'] = data

    return Response(payload, status=status.HTTP_200_OK)



@api_view(['POST', ])
@permission_classes([IsAuthenticated, ])
@authentication_classes([TokenAuthentication, ])
def delete_constituency_view(request):
    payload = {}
    data = {}
    errors = {}

    constituency_id = request.data.get('constituency_id', '')

    if not constituency_id:
        errors['constituency_id'] = ['Constituency ID is required.']

    try:
        constituency = Constituency.objects.get(constituency_id=constituency_id)
    except Constituency.DoesNotExist:
        errors['constituency_id'] = ['Constituency does not exist.']

    if errors:
        payload['message'] = "Errors"
        payload['errors'] = errors
        return Response(payload, status=status.HTTP_400_BAD_REQUEST)

    constituency.delete()

    #
    new_activity = AllActivity.objects.create(
        user=User.objects.get(id=1),
        subject="Constituency Deleted",
        body="Constituency Deleted"
    )
    new_activity.save()

    payload['message'] = "Successful"
    payload['data'] = {}

    return Response(payload, status=status.HTTP_200_OK)




@api_view(['POST', ])
@permission_classes([])
@authentication_classes([])
def add_zone_view(request):
    payload = {}
    data = {}
    errors = {}

    constituency_id = request.data.get('constituency_id', '')
    zone_name = request.data.get('zone_name', '')

    if not constituency_id:
        errors['constituency_id'] = ['Constituency ID is required.']

    if not zone_name:
        errors['zone_name'] = ['Zone name is required.']

    try:
        constituency = Constituency.objects.get(constituency_id=constituency_id)
    except Constituency.DoesNotExist:
        errors['constituency_id'] = ['Constituency does not exist.']

    if errors:
        payload['message'] = "Errors"
        payload['errors'] = errors
        return Response(payload, status=status.HTTP_400_BAD_REQUEST)

    new_zone = Zone.objects.create(
        constituency=constituency,
        zone_name=zone_name,
    )

    data['zone_id'] = new_zone.zone_id

    #
    new_activity = AllActivity.objects.create(
        user=User.objects.get(id=1),
        subject="Zone Registration",
        body="New Zone added"
    )
    new_activity.save()

    payload['message'] = "Successful"
    payload['data'] = data

    return Response(payload, status=status.HTTP_200_OK)




@api_view(['GET', ])
@permission_classes([])
@authentication_classes([])
def get_all_zones_view(request):
    payload = {}
    data = {}
    errors = {}

    # Retrieve all zones
    zones = Zone.objects.all()

    # Search functionality
    search_query = request.query_params.get('search')
    if search_query:
        zones = zones.filter(zone_name__icontains=search_query)

    # Pagination
    paginator = Paginator(zones, 10)  # 10 items per page
    page = request.query_params.get('page', 1)

    try:
        zones_page = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        zones_page = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        zones_page = paginator.page(paginator.num_pages)

    zone_serializer = ZoneSerializer(zones_page, many=True)

    payload['message'] = "Successful"
    payload['data'] = zone_serializer.data
    payload['pagination'] = {
        'total_items': paginator.count,
        'items_per_page': 10,
        'total_pages': paginator.num_pages,
        'current_page': zones_page.number,
        'has_next': zones_page.has_next(),
        'has_previous': zones_page.has_previous(),
    }

    return Response(payload, status=status.HTTP_200_OK)


@api_view(['GET', ])
@permission_classes([])
@authentication_classes([])
def get_zone_detail_view(request):
    payload = {}
    data = {}
    errors = {}

    zone_id = request.query_params.get('zone_id', None)

    if not zone_id:
        errors['zone_id'] = ["Zone id required"]

    try:
        zone = Zone.objects.get(zone_id=zone_id)
    except Zone.DoesNotExist:
        errors['zone_id'] = ['Zone does not exist.']

    if errors:
        payload['message'] = "Errors"
        payload['errors'] = errors
        return Response(payload, status=status.HTTP_400_BAD_REQUEST)

    zone_serializer = ZoneSerializer(zone, many=False)
    if zone_serializer:
        zone_data = zone_serializer.data

    payload['message'] = "Successful"
    payload['data'] = zone_data

    return Response(payload, status=status.HTTP_200_OK)



@api_view(['POST', ])
@permission_classes([IsAuthenticated, ])
@authentication_classes([TokenAuthentication, ])
def edit_zone_view(request):
    payload = {}
    data = {}
    errors = {}

    zone_id = request.data.get('zone_id', '')
    zone_name = request.data.get('zone_name', '')
    central_lat = request.data.get('central_lat', '')
    central_lng = request.data.get('central_lng', '')

    if not zone_id:
        errors['zone_id'] = ['Zone ID is required.']

    if not zone_name:
        errors['zone_name'] = ['Zone name is required.']

    try:
        zone = Zone.objects.get(zone_id=zone_id)
    except Zone.DoesNotExist:
        errors['zone_id'] = ['Zone does not exist.']

    if errors:
        payload['message'] = "Errors"
        payload['errors'] = errors
        return Response(payload, status=status.HTTP_400_BAD_REQUEST)

    zone.zone_name = zone_name
    zone.central_lat = central_lat
    zone.central_lng = central_lng
    zone.save()

    # Create activity
    new_activity = AllActivity.objects.create(
        user=request.user,
        subject="Zone Edited",
        body=f"Zone '{zone_name}' edited"
    )
    new_activity.save()

    payload['message'] = "Successful"
    payload['data'] = {}

    return Response(payload, status=status.HTTP_200_OK)


@api_view(['POST', ])
@permission_classes([IsAuthenticated, ])
@authentication_classes([TokenAuthentication, ])
def delete_zone_view(request):
    payload = {}
    data = {}
    errors = {}

    zone_id = request.data.get('zone_id', '')

    if not zone_id:
        errors['zone_id'] = ['Zone ID is required.']

    try:
        zone = Zone.objects.get(zone_id=zone_id)
    except Zone.DoesNotExist:
        errors['zone_id'] = ['Zone does not exist.']

    if errors:
        payload['message'] = "Errors"
        payload['errors'] = errors
        return Response(payload, status=status.HTTP_400_BAD_REQUEST)

    # Create activity
    new_activity = AllActivity.objects.create(
        user=request.user,
        subject="Zone Deleted",
        body=f"Zone '{zone.zone_name}' deleted"
    )
    new_activity.save()

    zone.delete()

    payload['message'] = "Successful"
    payload['data'] = {}

    return Response(payload, status=status.HTTP_200_OK)



@api_view(['GET', ])
@permission_classes([IsAuthenticated, ])
@authentication_classes([TokenAuthentication, ])
def get_zone_polling_stations(request):
    payload = {}
    data = {}
    errors = {}

    zone_id = request.query_params.get('zone_id', None)

    if not zone_id:
        errors['zone_id'] = ["Zone id required"]

    try:
        zone = Zone.objects.get(zone_id=zone_id)
    except Zone.DoesNotExist:
        errors['zone_id'] = ['Zone does not exist.']

    if errors:
        payload['message'] = "Errors"
        payload['errors'] = errors
        return Response(payload, status=status.HTTP_400_BAD_REQUEST)

    polling_stations = PollingStation.objects.filter(zone=zone)

    # Search functionality
    search_query = request.query_params.get('search')
    if search_query:
        polling_stations = polling_stations.filter(polling_station_name__icontains=search_query)

    paginator = Paginator(polling_stations, 10)  # 10 items per page
    page = request.query_params.get('page')

    try:
        polling_stations_page = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        polling_stations_page = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        polling_stations_page = paginator.page(paginator.num_pages)

    polling_station_serializer = PollingStationSerializer(polling_stations_page, many=True)
    if polling_station_serializer:
        _all_polling_stations = polling_station_serializer.data

    payload['message'] = "Successful"
    payload['data'] = _all_polling_stations
    payload['pagination'] = {
        'total_items': paginator.count,
        'items_per_page': 10,
        'total_pages': paginator.num_pages,
        'current_page': polling_stations_page.number,
        'has_next': polling_stations_page.has_next(),
        'has_previous': polling_stations_page.has_previous(),
    }

    return Response(payload, status=status.HTTP_200_OK)




@api_view(['POST', ])
@permission_classes([IsAuthenticated, ])
@authentication_classes([TokenAuthentication, ])
def add_polling_station_view(request):
    payload = {}
    data = {}
    errors = {}

    zone_id = request.data.get('zone_id', '')
    polling_station_name = request.data.get('polling_station_name', '')
    central_lat = request.data.get('central_lat', 0.0)
    central_lng = request.data.get('central_lng', 0.0)

    if not zone_id:
        errors['zone_id'] = ['Zone ID is required.']

    if not polling_station_name:
        errors['polling_station_name'] = ['Polling station name is required.']

    try:
        zone = Zone.objects.get(zone_id=zone_id)
    except Zone.DoesNotExist:
        errors['zone_id'] = ['Zone does not exist.']

    if errors:
        payload['message'] = "Errors"
        payload['errors'] = errors
        return Response(payload, status=status.HTTP_400_BAD_REQUEST)

    new_polling_station = PollingStation.objects.create(
        zone=zone,
        polling_station_name=polling_station_name,
        central_lat=central_lat,
        central_lng=central_lng
    )

    data['polling_station_id'] = new_polling_station.polling_station_id

    # Create activity
    new_activity = AllActivity.objects.create(
        user=request.user,
        subject="Polling Station Added",
        body=f"Polling station '{polling_station_name}' added to zone {zone_id}"
    )
    new_activity.save()

    payload['message'] = "Successful"
    payload['data'] = data

    return Response(payload, status=status.HTTP_200_OK)



@api_view(['GET', ])
@permission_classes([])
@authentication_classes([])
def get_all_polling_stations(request):
    payload = {}
    data = {}
    errors = {}

    polling_stations = PollingStation.objects.all()

    # Search functionality
    search_query = request.query_params.get('search')
    if search_query:
        polling_stations = polling_stations.filter(polling_station_name__icontains=search_query)

    paginator = Paginator(polling_stations, 10)  # 10 items per page
    page = request.query_params.get('page')

    try:
        polling_stations_page = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        polling_stations_page = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        polling_stations_page = paginator.page(paginator.num_pages)

    polling_station_serializer = PollingStationSerializer(polling_stations_page, many=True)
    if polling_station_serializer:
        _all_polling_stations = polling_station_serializer.data

    payload['message'] = "Successful"
    payload['data'] = _all_polling_stations
    payload['pagination'] = {
        'total_items': paginator.count,
        'items_per_page': 10,
        'total_pages': paginator.num_pages,
        'current_page': polling_stations_page.number,
        'has_next': polling_stations_page.has_next(),
        'has_previous': polling_stations_page.has_previous(),
    }

    return Response(payload, status=status.HTTP_200_OK)


@api_view(['GET', ])
@permission_classes([])
@authentication_classes([])
def get_polling_station_detail(request):
    payload = {}
    data = {}
    errors = {}

    polling_station_id = request.query_params.get('polling_station_id', None)

    if not polling_station_id:
        errors['polling_station_id'] = ["Polling station id required"]

    try:
        polling_station = PollingStation.objects.get(polling_station_id=polling_station_id)
    except PollingStation.DoesNotExist:
        errors['polling_station_id'] = ['Polling station does not exist.']

    if errors:
        payload['message'] = "Errors"
        payload['errors'] = errors
        return Response(payload, status=status.HTTP_400_BAD_REQUEST)

    polling_station_serializer = PollingStationSerializer(polling_station, many=False)
    if polling_station_serializer:
        polling_station_data = polling_station_serializer.data

    payload['message'] = "Successful"
    payload['data'] = polling_station_data

    return Response(payload, status=status.HTTP_200_OK)




@api_view(['POST', ])
@permission_classes([IsAuthenticated, ])
@authentication_classes([TokenAuthentication, ])
def edit_polling_station_view(request):
    payload = {}
    data = {}
    errors = {}

    polling_station_id = request.data.get('polling_station_id', '')
    polling_station_name = request.data.get('polling_station_name', '')
    central_lat = request.data.get('central_lat', '')
    central_lng = request.data.get('central_lng', '')

    if not polling_station_id:
        errors['polling_station_id'] = ['Polling station ID is required.']

    try:
        polling_station = PollingStation.objects.get(polling_station_id=polling_station_id)
    except PollingStation.DoesNotExist:
        errors['polling_station_id'] = ['Polling station does not exist.']

    if errors:
        payload['message'] = "Errors"
        payload['errors'] = errors
        return Response(payload, status=status.HTTP_400_BAD_REQUEST)

    polling_station.polling_station_name = polling_station_name
    polling_station.central_lat = central_lat
    polling_station.central_lng = central_lng
    polling_station.save()

    data['polling_station_id'] = polling_station_id

    # Create activity
    new_activity = AllActivity.objects.create(
        user=request.user,
        subject="Polling Station Edited",
        body=f"Polling station '{polling_station_name}' edited"
    )
    new_activity.save()

    payload['message'] = "Successful"
    payload['data'] = data

    return Response(payload, status=status.HTTP_200_OK)



@api_view(['POST', ])
@permission_classes([IsAuthenticated, ])
@authentication_classes([TokenAuthentication, ])
def delete_polling_station_view(request):
    payload = {}
    data = {}
    errors = {}

    polling_station_id = request.data.get('polling_station_id', '')

    if not polling_station_id:
        errors['polling_station_id'] = ['Polling station ID is required.']

    try:
        polling_station = PollingStation.objects.get(polling_station_id=polling_station_id)
    except PollingStation.DoesNotExist:
        errors['polling_station_id'] = ['Polling station does not exist.']

    if errors:
        payload['message'] = "Errors"
        payload['errors'] = errors
        return Response(payload, status=status.HTTP_400_BAD_REQUEST)

    polling_station_name = polling_station.polling_station_name

    # Delete the polling station
    polling_station.delete()

    # Create activity
    new_activity = AllActivity.objects.create(
        user=request.user,
        subject="Polling Station Deleted",
        body=f"Polling station '{polling_station_name}' deleted"
    )
    new_activity.save()

    payload['message'] = "Successful"
    payload['data'] = {}

    return Response(payload, status=status.HTTP_200_OK)




@api_view(['POST', ])
@permission_classes([IsAuthenticated, ])
@authentication_classes([TokenAuthentication, ])
def add_polling_station_participation(request):
    payload = {}
    data = {}
    errors = {}

    polling_station_id = request.data.get('polling_station_id', '')
    year = request.data.get('year', '')
    registered_voters = request.data.get('registered_voters', 0)
    voters = request.data.get('voters', 0)

    if not polling_station_id:
        errors['polling_station_id'] = ['Polling station ID is required.']

    if not year:
        errors['year'] = ['Year is required.']

    try:
        polling_station = PollingStation.objects.get(polling_station_id=polling_station_id)
    except PollingStation.DoesNotExist:
        errors['polling_station_id'] = ['Polling station does not exist.']

    # Check if the year already exists for the polling station
    if PollingStationVotersParticipation.objects.filter(polling_station=polling_station, year=year).exists():
        errors['year'] = ['Year already exists for the polling station.']

    if errors:
        payload['message'] = "Errors"
        payload['errors'] = errors
        return Response(payload, status=status.HTTP_400_BAD_REQUEST)

    # Calculate turnout and turnout percentage
    non_voters = registered_voters - voters
    turnout_percent = calculate_voter_turnout(voters, registered_voters)

    new_participation = PollingStationVotersParticipation.objects.create(
        polling_station=polling_station,
        year=year,
        registered_voters=registered_voters,
        voters=voters,
        non_voters=non_voters,
        turn_out_percent=turnout_percent,
    )

    data['participation_id'] = new_participation.id

    payload['message'] = "Polling station participation added successfully"
    payload['data'] = data

    return Response(payload, status=status.HTTP_200_OK)



def calculate_voter_turnout(num_voters, total_registered_voters):
    if total_registered_voters == 0:
        return 0.0
    return (num_voters / total_registered_voters) * 100.0