
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
from candidates.api.serializers import PartyDetailSerializer, AllPartiesSerializer, AllPresidentialCandidateSerializer, \
    AllParliamentaryCandidateSerializer
from candidates.models import Party, PresidentialCandidate, ParliamentaryCandidate, PartyFlagBearer, \
    PartyStandingCandidate

User = get_user_model()


@api_view(['POST', ])
@permission_classes([IsAuthenticated, ])
@authentication_classes([TokenAuthentication, ])
def add_party_view(request):
    payload = {}
    data = {}
    errors = {}

    party_full_name = request.data.get('party_full_name', '')
    party_logo = request.data.get('party_logo', '')
    party_initial = request.data.get('party_initial', '')
    year_formed = request.data.get('year_formed', '')
    election_year = request.data.get('election_year', '')

    if not party_full_name:
        errors['party_full_name'] = ['Party Full Name is required.']

    if not party_logo:
        errors['party_logo'] = ['Party logo is required.']

    if not party_initial:
        errors['party_initial'] = ['Party initials is required.']

    if not party_initial:
        errors['party_initial'] = ['Party initials is required.']

    if not election_year:
        errors['election_year'] = ['Election year is required.']

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


@api_view(['POST', ])
@permission_classes([IsAuthenticated, ])
@authentication_classes([TokenAuthentication, ])
def add_party_list_view(request):
    payload = {}
    data = []
    errors = {}

    parties = request.data.get('parties', [])

    if not parties:
        errors['parties'] = ['No parties provided.']

    for party_data in parties:
        party_full_name = party_data.get('name', '')
        party_logo = party_data.get('party_logo', '')
        party_initial = party_data.get('initials', '')
        year_formed = party_data.get('year_formed', '')
        bio = party_data.get('bio', '')
        founder = party_data.get('founder', '')

        if not party_full_name:
            errors.setdefault('parties', []).append('Party Full Name is required.')
        if not party_initial:
            errors.setdefault('parties', []).append('Party initials is required.')



        if not errors:
            new_party = Party.objects.create(
                party_full_name=party_full_name,
                party_logo=party_logo,
                party_initial=party_initial,
                year_formed=year_formed,
                bio=bio,
                founder=founder
            )
            data.append({'party_id': new_party.party_id})

    if errors:
        payload['message'] = "Errors"
        payload['errors'] = errors
        return Response(payload, status=status.HTTP_400_BAD_REQUEST)

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

    search_query = request.query_params.get('search', '')
    page_number = request.query_params.get('page', 1)
    page_size = 50

    parties = Party.objects.all().order_by('party_full_name')

    if search_query:
        parties = parties.filter(
            Q(party_full_name__icontains=search_query) |
            Q(party_abbreviation__icontains=search_query)
        )

    paginator = Paginator(parties, page_size)

    try:
        paginated_parties = paginator.page(page_number)
    except PageNotAnInteger:
        paginated_parties = paginator.page(1)
    except EmptyPage:
        paginated_parties = paginator.page(paginator.num_pages)

    party_serializer = AllPartiesSerializer(paginated_parties, many=True)

    data['parties'] = party_serializer.data
    data['pagination'] = {
        'page_number': paginated_parties.number,
        'count': parties.count(),
        'total_pages': paginator.num_pages,
        'next': paginated_parties.next_page_number() if paginated_parties.has_next() else None,
        'previous': paginated_parties.previous_page_number() if paginated_parties.has_previous() else None,
    }

    payload['message'] = "Successful"
    payload['data'] = data

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

@api_view(['POST', ])
@permission_classes([IsAuthenticated, ])
@authentication_classes([TokenAuthentication, ])
def edit_party_view(request):
    payload = {}
    data = {}
    errors = {}

    party_id = request.data.get('party_id', '')
    party_full_name = request.data.get('party_full_name', '')
    party_initial = request.data.get('party_initial', '')
    year_formed = request.data.get('year_formed', '')
    party_logo = request.data.get('party_logo', '')

    if not party_id:
        errors['party_id'] = ['Party ID is required.']

    if not party_full_name:
        errors['party_full_name'] = ['Party full name is required.']

    if not party_initial:
        errors['party_initial'] = ['Party initial is required.']

    if not year_formed:
        errors['year_formed'] = ['Year formed is required.']

    if not party_logo:
        errors['party_logo'] = ['Party logo is required.']

    try:
        party = Party.objects.get(party_id=party_id)
    except Party.DoesNotExist:
        errors['party_id'] = ['Party does not exist.']

    if errors:
        payload['message'] = "Errors"
        payload['errors'] = errors
        return Response(payload, status=status.HTTP_400_BAD_REQUEST)

    party.party_full_name = party_full_name
    party.party_initial = party_initial
    party.year_formed = year_formed
    if party_logo:
        party.party_logo = party_logo

    party.save()

    data['party_id'] = party.party_id

    #
    new_activity = AllActivity.objects.create(
        user=request.user,
        subject="Party Edited",
        body="Party Edited"
    )
    new_activity.save()

    payload['message'] = "Successful"
    payload['data'] = data

    return Response(payload, status=status.HTTP_200_OK)

@api_view(['POST', ])
@permission_classes([IsAuthenticated, ])
@authentication_classes([TokenAuthentication, ])
def delete_party_view(request):
    payload = {}
    data = {}
    errors = {}

    party_id = request.data.get('party_id', None)

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

    party.delete()

    payload['message'] = "Successfully"
    payload['data'] = {}

    return Response(payload, status=status.HTTP_200_OK)



@api_view(['GET', ])
@permission_classes([IsAuthenticated, ])
@authentication_classes([TokenAuthentication, ])
def get_all_party_candidates(request):
    payload = {}
    data = {}
    errors = {}

    party_id = request.query_params.get('party_id', '')

    if not party_id:
        errors['party_id'] = ['Party ID is required.']

    try:
        party = Party.objects.get(party_id=party_id)
    except Party.DoesNotExist:
        errors['party_id'] = ['Party does not exist.']

    if errors:
        payload['message'] = "Errors"
        payload['errors'] = errors
        return Response(payload, status=status.HTTP_400_BAD_REQUEST)

    presidential_candidates = PresidentialCandidate.objects.filter(party=party)
    parliamentary_candidates = ParliamentaryCandidate.objects.filter(party=party)

    # Search functionality
    search_query = request.query_params.get('search', '')
    if search_query:
        presidential_candidates = presidential_candidates.filter(name__icontains=search_query)
        parliamentary_candidates = parliamentary_candidates.filter(name__icontains=search_query)

    # Pagination
    paginator = PageNumberPagination()
    paginator.page_size = 10  # Set the number of items per page
    presidential_candidates_page = paginator.paginate_queryset(presidential_candidates, request)
    parliamentary_candidates_page = paginator.paginate_queryset(parliamentary_candidates, request)

    presidential_serializer = AllPresidentialCandidateSerializer(presidential_candidates_page, many=True)
    parliamentary_serializer = AllParliamentaryCandidateSerializer(parliamentary_candidates_page, many=True)

    data['presidential_candidates'] = presidential_serializer.data
    data['parliamentary_candidates'] = parliamentary_serializer.data

    # Add pagination information to response
    data['presidential_candidates_count'] = paginator.page.paginator.count
    data['presidential_candidates_next'] = paginator.get_next_link()
    data['presidential_candidates_previous'] = paginator.get_previous_link()
    data['parliamentary_candidates_count'] = paginator.page.paginator.count
    data['parliamentary_candidates_next'] = paginator.get_next_link()
    data['parliamentary_candidates_previous'] = paginator.get_previous_link()

    payload['message'] = "Successful"
    payload['data'] = data

    return Response(payload, status=status.HTTP_200_OK)


@api_view(['GET', ])
@permission_classes([IsAuthenticated, ])
@authentication_classes([TokenAuthentication, ])
def get_all_party_presidential_candidates(request):
    payload = {}
    data = {}
    errors = {}

    party_id = request.query_params.get('party_id', '')
    search_query = request.query_params.get('search', '')  # Search query parameter

    if not party_id:
        errors['party_id'] = ['Party ID is required.']

    try:
        party = Party.objects.get(party_id=party_id)
    except Party.DoesNotExist:
        errors['party_id'] = ['Party does not exist.']

    if errors:
        payload['message'] = "Errors"
        payload['errors'] = errors
        return Response(payload, status=status.HTTP_400_BAD_REQUEST)

    presidential_candidates = PresidentialCandidate.objects.filter(party=party)

    # Apply search filter
    if search_query:
        presidential_candidates = presidential_candidates.filter(name__icontains=search_query)

    paginator = PageNumberPagination()
    paginator.page_size = 10

    presidential_candidates_page = paginator.paginate_queryset(presidential_candidates, request)

    presidential_serializer = AllPresidentialCandidateSerializer(presidential_candidates_page, many=True)

    data['presidential_candidates'] = presidential_serializer.data

    payload['message'] = "Successful"
    payload['data'] = data
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
def get_all_party_parliamentary_candidates(request):
    payload = {}
    data = {}
    errors = {}

    party_id = request.query_params.get('party_id', '')
    search_query = request.query_params.get('search', '')  # Search query parameter
    page_number = request.query_params.get('page', 1)  # Page number parameter
    page_size = request.query_params.get('page_size', 10)  # Page size parameter

    if not party_id:
        errors['party_id'] = ['Party ID is required.']

    try:
        party = Party.objects.get(party_id=party_id)
    except Party.DoesNotExist:
        errors['party_id'] = ['Party does not exist.']

    if errors:
        payload['message'] = "Errors"
        payload['errors'] = errors
        return Response(payload, status=status.HTTP_400_BAD_REQUEST)

    parliamentary_candidates = ParliamentaryCandidate.objects.filter(party=party)

    # Apply search filter
    if search_query:
        parliamentary_candidates = parliamentary_candidates.filter(name__icontains=search_query)

    paginator = PageNumberPagination()
    paginator.page_size = page_size

    parliamentary_candidates_page = paginator.paginate_queryset(parliamentary_candidates, request)

    parliamentary_serializer = AllParliamentaryCandidateSerializer(parliamentary_candidates_page, many=True)

    data['parliamentary_candidates'] = parliamentary_serializer.data

    payload['message'] = "Successful"
    payload['data'] = data
    payload['pagination'] = {
        'total_items': paginator.page.paginator.count,
        'items_per_page': paginator.page_size,
        'total_pages': paginator.page.paginator.num_pages,
        'current_page': paginator.page.number,
        'has_next': paginator.page.has_next(),
        'has_previous': paginator.page.has_previous(),
    }

    return Response(payload, status=status.HTTP_200_OK)




@api_view(['POST', ])
@permission_classes([])
@authentication_classes([])
def add_flag_bearer(request):
    payload = {}
    data = {}
    errors = {}

    party_id = request.data.get('party_id', '')
    prez_can_id = request.data.get('prez_can_id', '')
    year = request.data.get('year', '')

    if not party_id:
        errors['party_id'] = ['Party ID is required.']

    if not prez_can_id:
        errors['prez_can_id'] = ['Presidential Candidate ID is required.']

    try:
        party = Party.objects.get(party_id=party_id)
    except Party.DoesNotExist:
        errors['party_id'] = ['Party does not exist.']

    try:
        presidential_candidate = PresidentialCandidate.objects.get(prez_can_id=prez_can_id)
    except PresidentialCandidate.DoesNotExist:
        errors['presidential_candidate_id'] = ['Presidential Candidate does not exist.']

    if errors:
        payload['message'] = "Errors"
        payload['errors'] = errors
        return Response(payload, status=status.HTTP_400_BAD_REQUEST)

    new_flag_bearer = PartyFlagBearer.objects.create(
        party=party,
        flag_bearer=presidential_candidate,
        year=year,
    )

    data['flag_bearer_id'] = new_flag_bearer.id

    payload['message'] = "Flag bearer added successfully"
    payload['data'] = data

    return Response(payload, status=status.HTTP_200_OK)



@api_view(['POST', ])
@permission_classes([])
@authentication_classes([])
def add_standing_candidate(request):
    payload = {}
    data = {}
    errors = {}

    party_id = request.data.get('party_id', '')
    prez_can_id = request.data.get('prez_can_id', '')
    year = request.data.get('year', '')
    won = request.data.get('won', '')

    if not party_id:
        errors['party_id'] = ['Party ID is required.']

    if not prez_can_id:
        errors['prez_can_id'] = ['Presidential Candidate ID is required.']

    try:
        party = Party.objects.get(party_id=party_id)
    except Party.DoesNotExist:
        errors['party_id'] = ['Party does not exist.']

    try:
        presidential_candidate = PresidentialCandidate.objects.get(prez_can_id=prez_can_id)
    except PresidentialCandidate.DoesNotExist:
        errors['presidential_candidate_id'] = ['Presidential Candidate does not exist.']

    if errors:
        payload['message'] = "Errors"
        payload['errors'] = errors
        return Response(payload, status=status.HTTP_400_BAD_REQUEST)

    new_standing_candidate = PartyStandingCandidate.objects.create(
        party=party,
        standing_candidate=presidential_candidate,
        year=year,
        won=won,
    )

    data['standing_candidate_id'] = new_standing_candidate.id

    payload['message'] = "Successfully"
    payload['data'] = data

    return Response(payload, status=status.HTTP_200_OK)
