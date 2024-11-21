from django.db.models import Q
from rest_framework import status
from rest_framework.decorators import permission_classes, api_view, authentication_classes
from rest_framework.response import Response

from regions.api.serializers import AllRegionsSerializer, AllConstituenciesSerializer
from regions.models import Region, Constituency


@api_view(['GET', ])
@permission_classes([])
@authentication_classes([])
def general_search_view(request):
    payload = {}
    data = {}
    errors = {}

    search_query = request.GET.get('search')

    if not search_query:
        errors['search'] = "Search query is required"
        #return Response(payload, status=status.HTTP_400_BAD_REQUEST)

    if errors:
        payload['message'] = "Errors"
        payload['errors'] = errors
        return Response(payload, status=status.HTTP_400_BAD_REQUEST)



    regions = Region.objects.filter(
        Q(region_name__icontains=search_query) |
        Q(initials__icontains=search_query)
    )

    constituencies = Constituency.objects.filter(
        Q(constituency_name__icontains=search_query)
    )

    regions_serializer = AllRegionsSerializer(regions, many=True)
    constituencies_serializer = AllConstituenciesSerializer(constituencies, many=True)

    payload['message'] = "Successful"
    payload['regions'] = regions_serializer.data
    payload['constituencies'] = constituencies_serializer.data

    return Response(payload, status=status.HTTP_200_OK)
