
from django.contrib.auth import get_user_model
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db.models import Q
from rest_framework import status
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import authentication_classes, api_view, permission_classes
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from activities.models import AllActivity
from regions.api.serializers import AllRegionsSerializer, RegionDetailSerializer, RegionalConstituenciesSerializer, \
    AllConstituenciesSerializer, ConstituencyDetailSerializer, ConstituencyElectoralAreaSerializer, ElectoralAreaSerializer, \
    PollingStationSerializer
from regions.models import Region, Constituency, ElectoralArea, PollingStation, PollingStationVotersParticipation, \
    RegionLayerCoordinate

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
    election_year = request.data.get('election_year', '')

    if not region_name:
        errors['region_name'] = ['Region name is required.']
    if not election_year:
        errors['election_year'] = ['Election year is required.']

    if errors:
        payload['message'] = "Errors"
        payload['errors'] = errors
        return Response(payload, status=status.HTTP_400_BAD_REQUEST)

    new_region = Region.objects.create(
        region_name=region_name,
        map_image=map_image,
        initials=initials,
        capital=capital,
        election_year=election_year
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
def clear_all_coordinates(request):

    payload = {}

    data = {}
    errors = {}

    region_coords = RegionLayerCoordinate.objects.all()
    for coord in region_coords:
        coord.delete()

    payload['message'] = "Successful"
    payload['data'] = data

    return Response(payload, status=status.HTTP_200_OK)



@api_view(['POST', ])
@permission_classes([IsAuthenticated, ])
@authentication_classes([TokenAuthentication, ])
def add_regions_coordinates(request):

    payload = {}

    data = {}
    errors = {}

    regions_geojson = request.data.get('regions_geojson', '')


    if not regions_geojson:
        errors['regions_geojson'] = ['Regions Geojson data is required.']

    if errors:
        payload['message'] = "Errors"
        payload['errors'] = errors
        return Response(payload, status=status.HTTP_400_BAD_REQUEST)


    features = regions_geojson['features']

    for feature in features:
        region_id = feature['properties']['region_id']
        coords_list = feature['geometry']['coordinates']


        for coords in coords_list:
            for coord in coords:
                region = Region.objects.get(region_id=region_id)
                region_coord = RegionLayerCoordinate.objects.create(
                   region=region,
                    lat=coord[1],
                    lng=coord[0]
                )

    payload['message'] = "Successful"
    payload['data'] = data

    return Response(payload, status=status.HTTP_200_OK)



@api_view(['GET', ])
@permission_classes([IsAuthenticated, ])
@authentication_classes([TokenAuthentication, ])
def list_all_region_coordinates(request):
    payload = {}
    data = {}
    errors = {}

    geojson_data = {
        "type": "FeatureCollection",
        "features": []
    }


    if errors:
        payload['message'] = "Errors"
        payload['errors'] = errors
        return Response(payload, status=status.HTTP_400_BAD_REQUEST)


    regions = Region.objects.all()
    response_data = []

    for region in regions:
        coordinates = RegionLayerCoordinate.objects.filter(region=region)

        formatted_coordinates = [[coord.lng, coord.lat] for coord in coordinates]


        region_data = {
            "type": "Feature",
            "properties": {
                "region_id": region.region_id,
                "region_name": region.region_name,
                "leading_color": "#0000FF"
            },
            "geometry": {
                "coordinates": [
                    formatted_coordinates
                ],
                "type": "Polygon"
            }
        }



        geojson_data["features"].append(region_data)



    payload['message'] = "Successful"
    payload['data'] = geojson_data

    return Response(payload, status=status.HTTP_200_OK)








@api_view(['POST', ])
@permission_classes([IsAuthenticated, ])
@authentication_classes([TokenAuthentication, ])
def add_all_region_constituencies(request):
    payload = {}
    data = {}
    errors = {}

    regions_data = request.data.get('regions', [])

    if not regions_data:
        errors['regions'] = ['Regions data is required.']

    if errors:
        payload['message'] = "Errors"
        payload['errors'] = errors
        return Response(payload, status=status.HTTP_400_BAD_REQUEST)

    for region_data in regions_data:
        region_name = region_data.get('region_name', '')
        capital = region_data.get('capital', '')
        election_year = region_data.get('election_year', '')
        constituencies = region_data.get('constituencies', [])

        if not region_name:
            errors['region_name'] = ['Region name is required.']
            continue

        region = Region.objects.create(region_name=region_name, capital=capital, election_year=election_year)

        for constituency_name in constituencies:
            if not constituency_name:
                continue
            Constituency.objects.create(region=region, constituency_name=constituency_name, election_year=election_year)

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
@permission_classes([IsAuthenticated, ])
@authentication_classes([TokenAuthentication])
def get_all_regions(request):
    payload = {}
    data = {}
    errors = {}

    search_query = request.query_params.get('search', '')
    page_number = request.query_params.get('page', 1)
    election_year = request.query_params.get('election_year', 1)
    page_size = 10

    all_regions = Region.objects.all().order_by('region_name')

    if search_query:
        all_regions = all_regions.filter(
            Q(region_name__icontains=search_query) |
            Q(initials__icontains=search_query)
        )

    if election_year:
        all_regions = all_regions.filter(
            election_year=election_year
          
        )

    paginator = Paginator(all_regions, page_size)

    try:
        paginated_regions = paginator.page(page_number)
    except PageNotAnInteger:
        paginated_regions = paginator.page(1)
    except EmptyPage:
        paginated_regions = paginator.page(paginator.num_pages)

    all_regions_serializer = AllRegionsSerializer(paginated_regions, many=True)

    data['regions'] = all_regions_serializer.data
    data['pagination'] = {
        'page_number': paginated_regions.number,
        'count': all_regions.count(),

        'total_pages': paginator.num_pages,
        'next': paginated_regions.next_page_number() if paginated_regions.has_next() else None,
        'previous': paginated_regions.previous_page_number() if paginated_regions.has_previous() else None,
    }

    payload['message'] = "Successful"
    payload['data'] = data

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
    election_year = request.data.get('region_id', '')

    if not constituency_name:
        errors['constituency_name'] = ['Constituency name is required.']

    if not region_id:
        errors['region_id'] = ['Region ID is required.']

    if not election_year:
        errors['election_year'] = ['Election year required.']

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
        election_year=election_year
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
@authentication_classes([TokenAuthentication])
def get_all_constituencies(request):
    payload = {}
    data = {}
    errors = {}

    search_query = request.query_params.get('search', '')
    page_number = request.query_params.get('page', 1)
    region_id = request.query_params.get('region_id', '')
    election_year = request.query_params.get('election_year', '')
    page_size = 50

    all_constituencies = Constituency.objects.all().order_by('constituency_name')

    if search_query:
        all_constituencies = all_constituencies.filter(
            Q(constituency_name__icontains=search_query) |
            Q(constituency_id__icontains=search_query)
        )

    if region_id:
        all_constituencies = all_constituencies.filter(
            region__region_id=region_id
        )

    if election_year:
        all_constituencies = all_constituencies.filter(
            constituency__election_year=election_year
        )

    paginator = Paginator(all_constituencies, page_size)

    try:
        paginated_constituencies = paginator.page(page_number)
    except PageNotAnInteger:
        paginated_constituencies = paginator.page(1)
    except EmptyPage:
        paginated_constituencies = paginator.page(paginator.num_pages)

    all_constituencies_serializer = AllConstituenciesSerializer(paginated_constituencies, many=True)

    data['constituencies'] = all_constituencies_serializer.data
    data['pagination'] = {
        'page_number': paginated_constituencies.number,
        'count': all_constituencies.count(),
        'total_pages': paginator.num_pages,
        'next': paginated_constituencies.next_page_number() if paginated_constituencies.has_next() else None,
        'previous': paginated_constituencies.previous_page_number() if paginated_constituencies.has_previous() else None,
    }

    payload['message'] = "Successful"
    payload['data'] = data

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
def get_constituency_electoral_area(request):
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

    electoral_areas = ElectoralArea.objects.all().filter(constituency=constituency)

    # Search functionality
    search_query = request.query_params.get('search')
    if search_query:
        electoral_areas = electoral_areas.filter(electoral_area_name__icontains=search_query)

    electoral_area_serializer = ConstituencyElectoralAreaSerializer(electoral_areas, many=True)
    if electoral_area_serializer:
        _all_electoral_areas = electoral_area_serializer.data

    payload['message'] = "Successful"
    payload['data'] = _all_electoral_areas

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
def add_electoral_area_view(request):
    payload = {}
    data = {}
    errors = {}

    constituency_id = request.data.get('constituency_id', '')
    electoral_area_name = request.data.get('electoral_area_name', '')
    election_year = request.data.get('election_year', '')

    if not constituency_id:
        errors['constituency_id'] = ['Constituency ID is required.']

    if not electoral_area_name:
        errors['electoral_area_name'] = ['Electoral Area name is required.']


    if not election_year:
        errors['election_year'] = ['Election year is required.']

    try:
        constituency = Constituency.objects.get(constituency_id=constituency_id)
    except Constituency.DoesNotExist:
        errors['constituency_id'] = ['Constituency does not exist.']

    if constituency.election_year is not election_year:
        errors['election_year'] = [f'Add contituency from election year {election_year}']


    if errors:
        payload['message'] = "Errors"
        payload['errors'] = errors
        return Response(payload, status=status.HTTP_400_BAD_REQUEST)

    new_electoral_area = ElectoralArea.objects.create(
        constituency=constituency,
        electoral_area_name=electoral_area_name,
    )

    data['electoral_area_id'] = new_electoral_area.electoral_area_id

    #
    new_activity = AllActivity.objects.create(
        user=User.objects.get(id=1),
        subject="Electoral Area Registration",
        body="New Electoral Area added"
    )
    new_activity.save()

    payload['message'] = "Successful"
    payload['data'] = data

    return Response(payload, status=status.HTTP_200_OK)


@api_view(['POST', ])
@permission_classes([IsAuthenticated, ])
@authentication_classes([TokenAuthentication, ])
def add_electoral_areas_list_view(request):
    payload = {}
    data = {}
    errors = {}

    electoral_areas = request.data.get('electoral_areas', [])
    election_year = request.data.get('election_year', '')

    if not electoral_areas:
        errors['electoral_areas'] = ['Electoral areas data is required.']

    if not election_year:
        errors['election_year'] = ['Election year is required.']

    if errors:
        payload['message'] = "Errors"
        payload['errors'] = errors
        return Response(payload, status=status.HTTP_400_BAD_REQUEST)

    for electoral_area in electoral_areas:
        electoral_area_name = electoral_area.get('electoral_area_name', '')
        constituency_id = electoral_area.get('constituency_id', '')

        if not electoral_area_name:
            errors['electoral_area'] = ['Electoral Area name is required.']
            continue

        consti = Constituency.objects.get(constituency_id=constituency_id)

        if consti.election_year is not election_year:
            errors['election_year'] = [f'Add contituency from election year {election_year}']
        else:
            electoral_area = ElectoralArea.objects.create(
            electoral_area_name=electoral_area_name,
            constituency=consti,
            election_year=election_year)
        
    if errors:
        payload['message'] = "Errors"
        payload['errors'] = errors
        return Response(payload, status=status.HTTP_400_BAD_REQUEST)


    payload['message'] = "Successful"
    payload['data'] = data

    return Response(payload, status=status.HTTP_200_OK)





@api_view(['GET', ])
@permission_classes([IsAuthenticated, ])
@authentication_classes([TokenAuthentication])
def get_all_electoral_area_view(request):
    payload = {}
    data = {}
    errors = {}

    search_query = request.query_params.get('search', '')
    page_number = request.query_params.get('page', 1)
    constituency_id = request.query_params.get('constituency_id', '')
    page_size = 50

    electoral_areas = ElectoralArea.objects.all().order_by('electoral_area_name')

    if search_query:
        electoral_areas = electoral_areas.filter(
            Q(electoral_area_name__icontains=search_query) |
            Q(electoral_area_id__icontains=search_query)
        )

    if constituency_id:
        electoral_areas = electoral_areas.filter(
            constituency__constituency_id=constituency_id
        )

    paginator = Paginator(electoral_areas, page_size)

    try:
        paginated_areas = paginator.page(page_number)
    except PageNotAnInteger:
        paginated_areas = paginator.page(1)
    except EmptyPage:
        paginated_areas = paginator.page(paginator.num_pages)

    electoral_areas_serializer = ElectoralAreaSerializer(paginated_areas, many=True)

    data['electoral_areas'] = electoral_areas_serializer.data
    data['pagination'] = {
        'page_number': paginated_areas.number,
                'count': electoral_areas.count(),

        'total_pages': paginator.num_pages,
        'next': paginated_areas.next_page_number() if paginated_areas.has_next() else None,
        'previous': paginated_areas.previous_page_number() if paginated_areas.has_previous() else None,
    }

    payload['message'] = "Successful"
    payload['data'] = data

    return Response(payload, status=status.HTTP_200_OK)
@api_view(['GET', ])
@permission_classes([])
@authentication_classes([])
def get_electoral_area_detail_view(request):
    payload = {}
    data = {}
    errors = {}

    electoral_area_id = request.query_params.get('electoral_area_id', None)

    if not electoral_area_id:
        errors['electoral_area_id'] = ["Electoral Area id required"]

    try:
        electoral_area = ElectoralArea.objects.get(electoral_area_id=electoral_area_id)
    except ElectoralArea.DoesNotExist:
        errors['electoral_area_id'] = ['Electoral Area does not exist.']

    if errors:
        payload['message'] = "Errors"
        payload['errors'] = errors
        return Response(payload, status=status.HTTP_400_BAD_REQUEST)

    electoral_area_serializer = ElectoralAreaSerializer(electoral_area, many=False)
    if electoral_area_serializer:
        electoral_area_data = electoral_area_serializer.data

    payload['message'] = "Successful"
    payload['data'] = electoral_area_data

    return Response(payload, status=status.HTTP_200_OK)



@api_view(['POST', ])
@permission_classes([IsAuthenticated, ])
@authentication_classes([TokenAuthentication, ])
def edit_electoral_area_view(request):
    payload = {}
    data = {}
    errors = {}

    electoral_area_id = request.data.get('electoral_area_id', '')
    electoral_area_name = request.data.get('electoral_area_name', '')
    central_lat = request.data.get('central_lat', '')
    central_lng = request.data.get('central_lng', '')

    if not electoral_area_id:
        errors['electoral_area_id'] = ['Electoral Area is required.']

    if not electoral_area_name:
        errors['electoral_area_name'] = ['Electoral Area is required.']

    try:
        electoral_area = ElectoralArea.objects.get(electoral_area_id=electoral_area_id)
    except ElectoralArea.DoesNotExist:
        errors['electoral_area_id'] = ['Electoral Area does not exist.']

    if errors:
        payload['message'] = "Errors"
        payload['errors'] = errors
        return Response(payload, status=status.HTTP_400_BAD_REQUEST)

    electoral_area.electoral_area_name = electoral_area_name
    electoral_area.central_lat = central_lat
    electoral_area.central_lng = central_lng
    electoral_area.save()

    # Create activity
    new_activity = AllActivity.objects.create(
        user=request.user,
        subject="Electoral Area Edited",
        body=f"Electoral '{electoral_area_name}' edited"
    )
    new_activity.save()

    payload['message'] = "Successful"
    payload['data'] = {}

    return Response(payload, status=status.HTTP_200_OK)


@api_view(['POST', ])
@permission_classes([IsAuthenticated, ])
@authentication_classes([TokenAuthentication, ])
def delete_electoral_view(request):
    payload = {}
    data = {}
    errors = {}

    electoral_area_id = request.data.get('electoral_area_id', '')

    if not electoral_area_id:
        errors['electoral_area_id'] = ['Electoral Area ID is required.']

    try:
        electoral_area = ElectoralArea.objects.get(electoral_area_id=electoral_area_id)
    except ElectoralArea.DoesNotExist:
        errors['electoral_area_id'] = ['Elctoral Area does not exist.']

    if errors:
        payload['message'] = "Errors"
        payload['errors'] = errors
        return Response(payload, status=status.HTTP_400_BAD_REQUEST)

    # Create activity
    new_activity = AllActivity.objects.create(
        user=request.user,
        subject="Electoral Area Deleted",
        body=f"Electoral Area '{electoral_area.electoral_area_name}' deleted"
    )
    new_activity.save()

    electoral_area.delete()

    payload['message'] = "Successful"
    payload['data'] = {}

    return Response(payload, status=status.HTTP_200_OK)



@api_view(['GET', ])
@permission_classes([IsAuthenticated, ])
@authentication_classes([TokenAuthentication, ])
def get_electoral_area_polling_stations(request):
    payload = {}
    data = {}
    errors = {}

    electoral_area_id = request.query_params.get('electoral_area_id', None)

    if not electoral_area_id:
        errors['electoral_area_id'] = ["Electoral Area id required"]

    try:
        electoral_area = ElectoralArea.objects.get(electoral_area_id=electoral_area_id)
    except ElectoralArea.DoesNotExist:
        errors['electoral_area_id'] = ['Electoral Area does not exist.']

    if errors:
        payload['message'] = "Errors"
        payload['errors'] = errors
        return Response(payload, status=status.HTTP_400_BAD_REQUEST)

    polling_stations = PollingStation.objects.filter(electoral_area=electoral_area)

    # Search functionality
    search_query = request.query_params.get('search')
    if search_query:
        polling_stations = polling_stations.filter(polling_station_name__icontains=search_query)


    polling_station_serializer = PollingStationSerializer(polling_stations, many=True)
    if polling_station_serializer:
        _all_polling_stations = polling_station_serializer.data

    payload['message'] = "Successful"
    payload['data'] = _all_polling_stations

    return Response(payload, status=status.HTTP_200_OK)




@api_view(['POST', ])
@permission_classes([IsAuthenticated, ])
@authentication_classes([TokenAuthentication, ])
def add_polling_station_view(request):
    payload = {}
    data = {}
    errors = {}

    electoral_area_id = request.data.get('electoral_area_id', '')
    polling_station_name = request.data.get('polling_station_name', '')
    central_lat = request.data.get('central_lat', 0.0)
    central_lng = request.data.get('central_lng', 0.0)

    if not electoral_area_id:
        errors['electoral_area_id'] = ['Electoral Area ID is required.']

    if not polling_station_name:
        errors['polling_station_name'] = ['Polling station name is required.']

    try:
        electoral_area = ElectoralArea.objects.get(electoral_area_id=electoral_area_id)
    except ElectoralArea.DoesNotExist:
        errors['electoral_area_id'] = ['Electoral Area does not exist.']

    if errors:
        payload['message'] = "Errors"
        payload['errors'] = errors
        return Response(payload, status=status.HTTP_400_BAD_REQUEST)

    new_polling_station = PollingStation.objects.create(
        electoral_area=electoral_area,
        polling_station_name=polling_station_name,
        central_lat=central_lat,
        central_lng=central_lng
    )

    data['polling_station_id'] = new_polling_station.polling_station_id

    # Create activity
    new_activity = AllActivity.objects.create(
        user=request.user,
        subject="Polling Station Added",
        body=f"Polling station '{polling_station_name}' added to electoral_area {electoral_area_id}"
    )
    new_activity.save()

    payload['message'] = "Successful"
    payload['data'] = data

    return Response(payload, status=status.HTTP_200_OK)



@api_view(['POST', ])
@permission_classes([IsAuthenticated, ])
@authentication_classes([TokenAuthentication, ])
def add_polling_stations_list_view(request):
    payload = {}
    data = {}
    errors = {}

    polling_stations = request.data.get('polling_stations', [])
    election_year = request.data.get('election_year', '')

    if not polling_stations:
        errors['polling_stations'] = ['Polling Stations data is required.']

    if not election_year:
        errors['election_year'] = ['Election  year is required.']

    if errors:
        payload['message'] = "Errors"
        payload['errors'] = errors
        return Response(payload, status=status.HTTP_400_BAD_REQUEST)

    for polling_station in polling_stations:
        polling_station_name = polling_station.get('polling_station_name', '')
        electoral_area_id = polling_station.get('electoral_area_id', '')

        if not polling_station_name:
            errors['polling_station'] = ['Polling Station name is required.']
            continue

        electoral_area = ElectoralArea.objects.get(electoral_area_id=electoral_area_id)
        print(electoral_area.election_year)
        if electoral_area.election_year is not election_year:
            errors['election_year'] = [f'Add electoral area from election year {election_year}']
        else:
            polling_station = PollingStation.objects.create(
            electoral_area=electoral_area,
            polling_station_name=polling_station_name, 
            election_year=election_year
            )

    if errors:
        payload['message'] = "Errors"
        payload['errors'] = errors
        return Response(payload, status=status.HTTP_400_BAD_REQUEST)



    payload['message'] = "Successful"
    payload['data'] = data

    return Response(payload, status=status.HTTP_200_OK)




@api_view(['GET', ])
@permission_classes([IsAuthenticated, ])
@authentication_classes([TokenAuthentication])
def get_all_polling_stations(request):
    payload = {}
    data = {}
    errors = {}

    search_query = request.query_params.get('search', '')
    page_number = request.query_params.get('page', 1)
    electoral_area_id = request.query_params.get('electoral_area_id', '')
    page_size = 50

    polling_stations = PollingStation.objects.all().order_by('polling_station_name')

    if search_query:
        polling_stations = polling_stations.filter(
            Q(polling_station_name__icontains=search_query) |
            Q(polling_station_id__icontains=search_query) |
            Q(polling_station_code__icontains=search_query)
        )

    if electoral_area_id:
        polling_stations = polling_stations.filter(
            electoral_area__electoral_area_id=electoral_area_id
        )

    paginator = Paginator(polling_stations, page_size)

    try:
        paginated_stations = paginator.page(page_number)
    except PageNotAnInteger:
        paginated_stations = paginator.page(1)
    except EmptyPage:
        paginated_stations = paginator.page(paginator.num_pages)

    polling_station_serializer = PollingStationSerializer(paginated_stations, many=True)

    data['polling_stations'] = polling_station_serializer.data
    data['pagination'] = {
        'page_number': paginated_stations.number,
                        'count': polling_stations.count(),

        
        'total_pages': paginator.num_pages,
        'next': paginated_stations.next_page_number() if paginated_stations.has_next() else None,
        'previous': paginated_stations.previous_page_number() if paginated_stations.has_previous() else None,
    }

    payload['message'] = "Successful"
    payload['data'] = data

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