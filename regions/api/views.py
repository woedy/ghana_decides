from datetime import datetime

from celery import chain
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.mail import EmailMessage
from django.utils import timezone
from django.utils.dateparse import parse_time
from rest_framework import status
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import authentication_classes, api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from activities.models import AllActivity
from regions.api.serializers import AllRegionsSerializer, RegionDetailSerializer, RegionalConstituenciesSerializer, \
    AllConstituenciesSerializer, ConstituencyDetailSerializer
from regions.models import Region, Constituency

User = get_user_model()


@api_view(['POST', ])
@permission_classes([])
@authentication_classes([])
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


@api_view(['GET', ])
@permission_classes([IsAuthenticated, ])
@authentication_classes([TokenAuthentication, ])
def get_all_regions(request):
    payload = {}
    data = {}
    errors = {}

    if errors:
        payload['message'] = "Errors"
        payload['errors'] = errors
        return Response(payload, status=status.HTTP_400_BAD_REQUEST)

    all_regions = Region.objects.all()

    all_regions_serializer = AllRegionsSerializer(all_regions, many=True)
    if all_regions_serializer:
        _all_regions = all_regions_serializer.data

    payload['message'] = "Successful"
    payload['data'] = _all_regions

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

    constituencies_serializer = RegionalConstituenciesSerializer(constituencies, many=True)
    if constituencies_serializer:
        _all_consti = constituencies_serializer.data

    payload['message'] = "Successful"
    payload['data'] = _all_consti

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

    if errors:
        payload['message'] = "Errors"
        payload['errors'] = errors
        return Response(payload, status=status.HTTP_400_BAD_REQUEST)

    all_constituencies = Constituency.objects.all()

    all_constituencies_serializer = AllConstituenciesSerializer(all_constituencies, many=True)
    if all_constituencies_serializer:
        _all_constituencies = all_constituencies_serializer.data

    payload['message'] = "Successful"
    payload['data'] = _all_constituencies

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
