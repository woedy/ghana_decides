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
def add_parliamentary_candidate(request):
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

