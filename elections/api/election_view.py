from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.contrib.auth import get_user_model
from rest_framework import status
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db.models import Sum, Q

from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from activities.models import AllActivity
from candidates.models import PresidentialCandidate, ParliamentaryCandidate
from elections.api.serializers import ElectionPresidentialCandidateSerializer, ElectionParliamentaryCandidateSerializer, \
    AllElectionSerializer, PresidentialCandidateConstituencyVoteSerializer, PresidentialCandidateElectoralAreaVoteSerializer, PresidentialCandidatePollingStationVoteSerializer, \
    ParliamentaryCandidatePollingStationVoteSerializer, PresidentialCandidateRegionalVoteSerializer
from elections.models import ElectionPresidentialCandidate, ElectionParliamentaryCandidate, Election, \
    PresidentialCandidatePollingStationVote, PresidentialCandidateElectoralAreaVote, \
    PresidentialCandidateConstituencyVote, PresidentialCandidateRegionalVote, ParliamentaryCandidatePollingStationVote, \
    ParliamentaryCandidateElectoralAreaVote, ParliamentaryCandidateConstituencyVote, ParliamentaryCandidateRegionalVote
from regions.models import PollingStation, Constituency, ElectoralArea

User = get_user_model()

@api_view(['POST', ])
@permission_classes([IsAuthenticated, ])
@authentication_classes([TokenAuthentication, ])
def add_election_presidential_candidate_view(request):
    payload = {}
    data = {}
    errors = {}

    prez_can_id = request.data.get('prez_can_id', '')
    ballot_number = request.data.get('ballot_number', '')

    if not prez_can_id:
        errors['prez_can_id'] = ['Presidential Candidate id is required.']

    try:
        prez_can = PresidentialCandidate.objects.get(prez_can_id=prez_can_id)
    except:
        errors['prez_can_id'] = ['Presidential candidate does not exist.']


    if errors:
        payload['message'] = "Errors"
        payload['errors'] = errors
        return Response(payload, status=status.HTTP_400_BAD_REQUEST)

    election = Election.objects.get(year=2024)

    new_election_prez_can = ElectionPresidentialCandidate.objects.create(
        candidate=prez_can,
        election=election
    )

    data['election_prez_id'] = new_election_prez_can.election_prez_id

    #
    new_activity = AllActivity.objects.create(
        user=User.objects.get(id=1),
        subject="Election Presidential Candidate Added",
        body="New Election Presidential Candidate added"
    )
    new_activity.save()

    payload['message'] = "Successful"
    payload['data'] = data

    return Response(payload, status=status.HTTP_200_OK)

@api_view(['POST', ])
@permission_classes([IsAuthenticated, ])
@authentication_classes([TokenAuthentication, ])
def add_election_presidential_candidate_list_view(request):
    payload = {}
    data = {}
    errors = {}

    candidates = request.data.get('candidates', [])
    for candidate in candidates:
        prez_can_id = candidate.get('prez_can_id', '')
        ballot_number = candidate.get('ballot_number', '')

        if not prez_can_id:
            errors['prez_can_id'] = ['Presidential Candidate id is required.']

        try:
            prez_can = PresidentialCandidate.objects.get(prez_can_id=prez_can_id)
        except PresidentialCandidate.DoesNotExist:
            errors['prez_can_id'] = ['Presidential candidate does not exist.']

        if errors:
            payload['message'] = "Errors"
            payload['errors'] = errors
            return Response(payload, status=status.HTTP_400_BAD_REQUEST)

        election = Election.objects.get(year=2024)

        new_election_prez_can = ElectionPresidentialCandidate.objects.create(
            candidate=prez_can,
            election=election,
            ballot_number=ballot_number
        )

        data['election_prez_id'] = new_election_prez_can.id

        new_activity = AllActivity.objects.create(
            user=User.objects.get(id=1),
            subject="Election Presidential Candidate Added",
            body="New Election Presidential Candidate added"
        )
        new_activity.save()

    payload['message'] = "Successful"
    payload['data'] = data

    return Response(payload, status=status.HTTP_200_OK)





@api_view(['GET'])
@permission_classes([IsAuthenticated])
@authentication_classes([TokenAuthentication])
def get_all_election_presidential_candidate_view(request):
    payload = {}
    data = {}
    errors = {}

    search_query = request.query_params.get('search', '')
    page_number = request.query_params.get('page', 1)
    region_id = request.query_params.get('region_id', '')
    constituency_id = request.query_params.get('constituency_id', '')
    electoral_area_id = request.query_params.get('electoral_area_id', '')
    polling_station_id = request.query_params.get('polling_station_id', '')
    election_year = request.query_params.get('election_year', '')
    page_size = 50

    # Start with all presidential candidates
    all_election_prez_can = ElectionPresidentialCandidate.objects.all().order_by("ballot_number")

    # Apply search filter if search query is provided
    if search_query:
        all_election_prez_can = all_election_prez_can.filter(
            Q(candidate__first_name__icontains=search_query) |
            Q(candidate__last_name__icontains=search_query) |
            Q(ballot_number__icontains=search_query)
        )

    # Filter by region_id using the PresidentialCandidateRegionalVote relationship
    if region_id:
        candidate_ids = PresidentialCandidateRegionalVote.objects.filter(
            region__region_id=region_id
        ).values_list('prez_candidate__id', flat=True)
        all_election_prez_can = all_election_prez_can.filter(id__in=candidate_ids)

    # Filter by constituency_id using the PresidentialCandidateConstituencyVote relationship
    if constituency_id:
        consti_candidate_ids = PresidentialCandidateConstituencyVote.objects.filter(
            constituency__constituency_id=constituency_id
        ).values_list('prez_candidate__id', flat=True)
        all_election_prez_can = all_election_prez_can.filter(id__in=consti_candidate_ids)


    # Filter by electoral_area_id using the PresidentialCandidateElectoralAreaVote relationship
    if electoral_area_id:
        electoral_candidate_ids = PresidentialCandidateElectoralAreaVote.objects.filter(
            electoral_area__electoral_area_id=electoral_area_id
        ).values_list('prez_candidate__id', flat=True)
        all_election_prez_can = all_election_prez_can.filter(id__in=electoral_candidate_ids)


    # Filter by polling_station_id
    if polling_station_id:
        polling_candidate_ids = PresidentialCandidatePollingStationVote.objects.filter(
            polling_station__polling_station_id=polling_station_id
        ).values_list('prez_candidate__id', flat=True)
        all_election_prez_can = all_election_prez_can.filter(id__in=polling_candidate_ids)


    # Apply election year filter if provided
    if election_year:
        all_election_prez_can = all_election_prez_can.filter(
            election__year=election_year
        )

    # Pagination
    paginator = Paginator(all_election_prez_can, page_size)

    try:
        paginated_candidates = paginator.page(page_number)
    except PageNotAnInteger:
        paginated_candidates = paginator.page(1)
    except EmptyPage:
        paginated_candidates = paginator.page(paginator.num_pages)

    # Serialize and prepare data
    all_election_prez_can_serializer = ElectionPresidentialCandidateSerializer(paginated_candidates, many=True)

    data['candidates'] = all_election_prez_can_serializer.data
    data['pagination'] = {
        'page_number': paginated_candidates.number,
        'count': all_election_prez_can.count(),
        'total_pages': paginator.num_pages,
        'next': paginated_candidates.next_page_number() if paginated_candidates.has_next() else None,
        'previous': paginated_candidates.previous_page_number() if paginated_candidates.has_previous() else None,
    }

    payload['message'] = "Successful"
    payload['data'] = data

    return Response(payload, status=status.HTTP_200_OK)




@api_view(['GET'])
@permission_classes([IsAuthenticated])
@authentication_classes([TokenAuthentication])
def get_all_election_presidential_candidate_regional_view(request):
    payload = {}
    data = {}
    errors = {}

    search_query = request.query_params.get('search', '')
    page_number = request.query_params.get('page', 1)
    region_id = request.query_params.get('region_id', '')

    election_year = request.query_params.get('election_year', '')
    page_size = 50

    # Start with all presidential candidates
    all_election_prez_can = PresidentialCandidateRegionalVote.objects.all().order_by("prez_candidate__ballot_number")

    # Apply search filter if search query is provided
    if search_query:
        all_election_prez_can = all_election_prez_can.filter(
            Q(prez_candidate__candidate__first_name__icontains=search_query) |
            Q(prez_candidate__candidate__last_name__icontains=search_query) |
            Q(prez_candidate__ballot_number__icontains=search_query)
        )



    if region_id:
        all_election_prez_can = all_election_prez_can.filter(region__region_id=region_id)



    # Apply election year filter if provided
    if election_year:
        all_election_prez_can = all_election_prez_can.filter(
            election__year=election_year
        )

    # Pagination
    paginator = Paginator(all_election_prez_can, page_size)

    try:
        paginated_candidates = paginator.page(page_number)
    except PageNotAnInteger:
        paginated_candidates = paginator.page(1)
    except EmptyPage:
        paginated_candidates = paginator.page(paginator.num_pages)

    # Serialize and prepare data
    all_election_prez_can_serializer = PresidentialCandidateRegionalVoteSerializer(paginated_candidates, many=True)

    data['candidates'] = all_election_prez_can_serializer.data
    data['pagination'] = {
        'page_number': paginated_candidates.number,
        'count': all_election_prez_can.count(),
        'total_pages': paginator.num_pages,
        'next': paginated_candidates.next_page_number() if paginated_candidates.has_next() else None,
        'previous': paginated_candidates.previous_page_number() if paginated_candidates.has_previous() else None,
    }

    payload['message'] = "Successful"
    payload['data'] = data

    return Response(payload, status=status.HTTP_200_OK)










@api_view(['GET'])
@permission_classes([IsAuthenticated])
@authentication_classes([TokenAuthentication])
def get_all_election_presidential_candidate_constituency_view(request):
    payload = {}
    data = {}
    errors = {}

    search_query = request.query_params.get('search', '')
    page_number = request.query_params.get('page', 1)
    constituency_id = request.query_params.get('constituency_id', '')

    election_year = request.query_params.get('election_year', '')
    page_size = 50

    # Start with all presidential candidates
    all_election_prez_can = PresidentialCandidateConstituencyVote.objects.all().order_by("prez_candidate__ballot_number")

    # Apply search filter if search query is provided
    if search_query:
        all_election_prez_can = all_election_prez_can.filter(
            Q(prez_candidate__candidate__first_name__icontains=search_query) |
            Q(prez_candidate__candidate__last_name__icontains=search_query) |
            Q(prez_candidate__ballot_number__icontains=search_query)
        )



    if constituency_id:
        all_election_prez_can = all_election_prez_can.filter(constituency__constituency_id=constituency_id)



    # Apply election year filter if provided
    if election_year:
        all_election_prez_can = all_election_prez_can.filter(
            election__year=election_year
        )

    # Pagination
    paginator = Paginator(all_election_prez_can, page_size)

    try:
        paginated_candidates = paginator.page(page_number)
    except PageNotAnInteger:
        paginated_candidates = paginator.page(1)
    except EmptyPage:
        paginated_candidates = paginator.page(paginator.num_pages)

    # Serialize and prepare data
    all_election_prez_can_serializer = PresidentialCandidateConstituencyVoteSerializer(paginated_candidates, many=True)

    data['candidates'] = all_election_prez_can_serializer.data
    data['pagination'] = {
        'page_number': paginated_candidates.number,
        'count': all_election_prez_can.count(),
        'total_pages': paginator.num_pages,
        'next': paginated_candidates.next_page_number() if paginated_candidates.has_next() else None,
        'previous': paginated_candidates.previous_page_number() if paginated_candidates.has_previous() else None,
    }

    payload['message'] = "Successful"
    payload['data'] = data

    return Response(payload, status=status.HTTP_200_OK)










@api_view(['GET'])
@permission_classes([IsAuthenticated])
@authentication_classes([TokenAuthentication])
def get_all_election_presidential_candidate_electoral_area_view(request):
    payload = {}
    data = {}
    errors = {}

    search_query = request.query_params.get('search', '')
    page_number = request.query_params.get('page', 1)
    electoral_area_id = request.query_params.get('electoral_area_id', '')

    election_year = request.query_params.get('election_year', '')
    page_size = 50

    # Start with all presidential candidates
    all_election_prez_can = PresidentialCandidateElectoralAreaVote.objects.all().order_by("prez_candidate__ballot_number")

    # Apply search filter if search query is provided
    if search_query:
        all_election_prez_can = all_election_prez_can.filter(
            Q(prez_candidate__candidate__first_name__icontains=search_query) |
            Q(prez_candidate__candidate__last_name__icontains=search_query) |
            Q(prez_candidate__ballot_number__icontains=search_query)
        )



    if electoral_area_id:
        all_election_prez_can = all_election_prez_can.filter(electoral_area__electoral_area_id=electoral_area_id)



    # Apply election year filter if provided
    if election_year:
        all_election_prez_can = all_election_prez_can.filter(
            election__year=election_year
        )

    # Pagination
    paginator = Paginator(all_election_prez_can, page_size)

    try:
        paginated_candidates = paginator.page(page_number)
    except PageNotAnInteger:
        paginated_candidates = paginator.page(1)
    except EmptyPage:
        paginated_candidates = paginator.page(paginator.num_pages)

    # Serialize and prepare data
    all_election_prez_can_serializer = PresidentialCandidateElectoralAreaVoteSerializer(paginated_candidates, many=True)

    data['candidates'] = all_election_prez_can_serializer.data
    data['pagination'] = {
        'page_number': paginated_candidates.number,
        'count': all_election_prez_can.count(),
        'total_pages': paginator.num_pages,
        'next': paginated_candidates.next_page_number() if paginated_candidates.has_next() else None,
        'previous': paginated_candidates.previous_page_number() if paginated_candidates.has_previous() else None,
    }

    payload['message'] = "Successful"
    payload['data'] = data

    return Response(payload, status=status.HTTP_200_OK)










@api_view(['GET'])
@permission_classes([IsAuthenticated])
@authentication_classes([TokenAuthentication])
def get_all_election_presidential_candidate_polling_station_view(request):
    payload = {}
    data = {}
    errors = {}

    search_query = request.query_params.get('search', '')
    page_number = request.query_params.get('page', 1)
    polling_station_id = request.query_params.get('polling_station_id', '')

    election_year = request.query_params.get('election_year', '')
    page_size = 50

    # Start with all presidential candidates
    all_election_prez_can = PresidentialCandidatePollingStationVote.objects.all().order_by("prez_candidate__ballot_number")

    # Apply search filter if search query is provided
    if search_query:
        all_election_prez_can = all_election_prez_can.filter(
            Q(prez_candidate__candidate__first_name__icontains=search_query) |
            Q(prez_candidate__candidate__last_name__icontains=search_query) |
            Q(prez_candidate__ballot_number__icontains=search_query)
        )



    if polling_station_id:
        all_election_prez_can = all_election_prez_can.filter(polling_station__polling_station_id=polling_station_id)



    # Apply election year filter if provided
    if election_year:
        all_election_prez_can = all_election_prez_can.filter(
            election__year=election_year
        )

    # Pagination
    paginator = Paginator(all_election_prez_can, page_size)

    try:
        paginated_candidates = paginator.page(page_number)
    except PageNotAnInteger:
        paginated_candidates = paginator.page(1)
    except EmptyPage:
        paginated_candidates = paginator.page(paginator.num_pages)

    # Serialize and prepare data
    all_election_prez_can_serializer = PresidentialCandidatePollingStationVoteSerializer(paginated_candidates, many=True)

    data['candidates'] = all_election_prez_can_serializer.data
    data['pagination'] = {
        'page_number': paginated_candidates.number,
        'count': all_election_prez_can.count(),
        'total_pages': paginator.num_pages,
        'next': paginated_candidates.next_page_number() if paginated_candidates.has_next() else None,
        'previous': paginated_candidates.previous_page_number() if paginated_candidates.has_previous() else None,
    }

    payload['message'] = "Successful"
    payload['data'] = data

    return Response(payload, status=status.HTTP_200_OK)










@api_view(['GET'])
@permission_classes([IsAuthenticated])
@authentication_classes([TokenAuthentication])
def get_all_election_parliamentary_swing_constituency_view(request):
    payload = {}
    data = {}
    errors = {}

    search_query = request.query_params.get('search', '')
    page_number = request.query_params.get('page', 1)

    election_year = request.query_params.get('election_year', '')
    page_size = 50


  
    payload['message'] = "Successful"
    payload['data'] = data

    return Response(payload, status=status.HTTP_200_OK)














@api_view(['GET'])
@permission_classes([IsAuthenticated])
@authentication_classes([TokenAuthentication])
def get_all_election_presidential_swing_constituency_view(request):
    payload = {}
    data = {}
    errors = {}

    search_query = request.query_params.get('search', '')
    page_number = request.query_params.get('page', 1)

    election_year = request.query_params.get('election_year', '')
    page_size = 50


  
    payload['message'] = "Successful"
    payload['data'] = data

    return Response(payload, status=status.HTTP_200_OK)




@api_view(['GET'])
@permission_classes([IsAuthenticated])
@authentication_classes([TokenAuthentication])
def get_all_election_presidential_marginal_constituency_view(request):
    payload = {}
    data = {}
    errors = {}

    search_query = request.query_params.get('search', '')
    page_number = request.query_params.get('page', 1)

    election_year = request.query_params.get('election_year', '')
    page_size = 50


  
    payload['message'] = "Successful"
    payload['data'] = data

    return Response(payload, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
@authentication_classes([TokenAuthentication])
def get_all_election_skirt_and_blouse_constituency_view(request):
    payload = {}
    data = {}
    errors = {}

    search_query = request.query_params.get('search', '')
    page_number = request.query_params.get('page', 1)

    election_year = request.query_params.get('election_year', '')
    page_size = 50


  
    payload['message'] = "Successful"
    payload['data'] = data

    return Response(payload, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
@authentication_classes([TokenAuthentication])
def get_all_election_parliamentary_marginal_constituency_view(request):
    payload = {}
    data = {}
    errors = {}

    search_query = request.query_params.get('search', '')
    page_number = request.query_params.get('page', 1)

    election_year = request.query_params.get('election_year', '')
    page_size = 50


  
    payload['message'] = "Successful"
    payload['data'] = data

    return Response(payload, status=status.HTTP_200_OK)













@api_view(['POST', ])
@permission_classes([IsAuthenticated, ])
@authentication_classes([TokenAuthentication, ])
def add_election_parliamentary_candidate_view(request):
    payload = {}
    data = {}
    errors = {}

    constituency_id = request.data.get('constituency_id', '')
    parl_can_id = request.data.get('parl_can_id', '')
    ballot_number = request.data.get('ballot_number', '')

    if not constituency_id:
        errors['constituency_id'] = ['Candidate Constituency id is required.']

    if not parl_can_id:
        errors['parl_can_id'] = ['Parliamentary Candidate id is required.']

    if not ballot_number:
        errors['ballot_number'] = ['Ballot Number is required.']

    try:
        parl_can = ParliamentaryCandidate.objects.get(parl_can_id=parl_can_id)
    except:
        errors['parl_can_id'] = ['Parliamentary candidate does not exist.']

    try:
        constituency = Constituency.objects.get(constituency_id=constituency_id)
    except:
        errors['constituency_id'] = ['Constituency does not exist.']


    if errors:
        payload['message'] = "Errors"
        payload['errors'] = errors
        return Response(payload, status=status.HTTP_400_BAD_REQUEST)

    election = Election.objects.get(year=2024)

    new_election_parl_can = ElectionParliamentaryCandidate.objects.create(
        election=election,
        constituency=constituency,
        candidate=parl_can,
        ballot_number=ballot_number

    )

    data['election_parl_id'] = new_election_parl_can.election_parl_id

    #
    new_activity = AllActivity.objects.create(
        user=User.objects.get(id=1),
        subject="Election Parliamentary Candidate Added",
        body="New Election Parliamentary Candidate added"
    )
    new_activity.save()

    payload['message'] = "Successful"
    payload['data'] = data

    return Response(payload, status=status.HTTP_200_OK)


@api_view(['POST', ])
@permission_classes([IsAuthenticated, ])
@authentication_classes([TokenAuthentication, ])
def add_election_parliamentary_candidate_list_view(request):
    payload = {}
    data = {}
    errors = {}

    candidates = request.data.get('candidates', [])
    for candidate in candidates:
        constituency_id = candidate.get('constituency_id', '')
        parl_can_id = candidate.get('parl_can_id', '')
        ballot_number = candidate.get('ballot_number', '')

        if not constituency_id:
            errors['constituency_id'] = ['Candidate Constituency id is required.']

        if not parl_can_id:
            errors['parl_can_id'] = ['Parliamentary Candidate id is required.']

        if not ballot_number:
            errors['ballot_number'] = ['Ballot Number is required.']

        try:
            parl_can = ParliamentaryCandidate.objects.get(parl_can_id=parl_can_id)
        except ParliamentaryCandidate.DoesNotExist:
            errors['parl_can_id'] = ['Parliamentary candidate does not exist.']

        try:
            constituency = Constituency.objects.get(constituency_id=constituency_id)
        except Constituency.DoesNotExist:
            errors['constituency_id'] = ['Constituency does not exist.']

        if errors:
            payload['message'] = "Errors"
            payload['errors'] = errors
            return Response(payload, status=status.HTTP_400_BAD_REQUEST)

        election = Election.objects.get(year=2024)

        new_election_parl_can = ElectionParliamentaryCandidate.objects.create(
            election=election,
            constituency=constituency,
            candidate=parl_can,
            ballot_number=ballot_number
        )

        data['election_parl_id'] = new_election_parl_can.id

        new_activity = AllActivity.objects.create(
            user=User.objects.get(id=1),
            subject="Election Parliamentary Candidate Added",
            body="New Election Parliamentary Candidate added"
        )
        new_activity.save()

    payload['message'] = "Successful"
    payload['data'] = data

    return Response(payload, status=status.HTTP_200_OK)



@api_view(['GET'])
@permission_classes([IsAuthenticated])
@authentication_classes([TokenAuthentication])
def get_all_election_parliamentary_candidate_view(request):
    payload = {}
    data = {}
    errors = {}

    page_number = request.query_params.get('page', 1)
    page_size = 50
    region_id = request.query_params.get('region_id', None)
    constituency_id = request.query_params.get('constituency_id', None)
    electoral_area_id = request.query_params.get('electoral_area_id', None)
    polling_station_id = request.query_params.get('polling_station_id', None)
    search = request.query_params.get('search', None)
    election_year = request.query_params.get('election_year', '')

    # Start with all candidates
    all_election_parl_can = ElectionParliamentaryCandidate.objects.all().order_by("candidate__first_name")


    if region_id:
        all_election_parl_can = all_election_parl_can.filter(
        constituency__region__region_id=region_id
    )
    # Filter by constituency_id if provided
    if constituency_id:
        all_election_parl_can = all_election_parl_can.filter(constituency__constituency_id=constituency_id)
        
    
    if electoral_area_id:
        all_election_parl_can = all_election_parl_can.filter(
        constituency__constituency_electoral_area__electoral_area_id=electoral_area_id
    )
    
    if polling_station_id:
        all_election_parl_can = all_election_parl_can.filter(
        constituency__constituency_electoral_area__electoral_area_polling_stations__polling_station_id=polling_station_id
    )
        
    # Implement search if search query is provided
    if search:
        all_election_parl_can = all_election_parl_can.filter(
            Q(candidate__first_name__icontains=search) |  
            Q(candidate__last_name__icontains=search) |
            Q(ballot_number__icontains=search)   
        )


    if election_year:
        all_election_parl_can = all_election_parl_can.filter(
            Q(election__year=election_year)
        )

    # Error handling for the filtering/searching process
    if errors:
        payload['message'] = "Errors"
        payload['errors'] = errors
        return Response(payload, status=status.HTTP_400_BAD_REQUEST)

    paginator = Paginator(all_election_parl_can, page_size)

    try:
        paginated_candidates = paginator.page(page_number)
    except PageNotAnInteger:
        paginated_candidates = paginator.page(1)
    except EmptyPage:
        paginated_candidates = paginator.page(paginator.num_pages)

    all_election_parl_can_serializer = ElectionParliamentaryCandidateSerializer(paginated_candidates, many=True)
    _all_election_parl_can = all_election_parl_can_serializer.data

    data['candidates'] = _all_election_parl_can
    data['pagination'] = {
        'page_number': paginated_candidates.number,
        'count': all_election_parl_can.count(),
        'total_pages': paginator.num_pages,
        'next': paginated_candidates.next_page_number() if paginated_candidates.has_next() else None,
        'previous': paginated_candidates.previous_page_number() if paginated_candidates.has_previous() else None,
    }

    payload['message'] = "Successful"
    payload['data'] = data

    return Response(payload, status=status.HTTP_200_OK)


@api_view(['POST', ])
@permission_classes([IsAuthenticated, ])
@authentication_classes([TokenAuthentication, ])
def add_election_presidential_vote_view(request):
    payload = {}
    data = {}
    errors = {}

    polling_station_id = request.data.get('polling_station_id', '')
    ballot = request.data.get('ballot', [])

    print(polling_station_id)
    print(ballot)

    if not polling_station_id:
        errors['polling_station_id'] = ['Polling Station id is required.']

    if not ballot:
        errors['ballot'] = ['Ballot is required.']

    try:
        polling_station = PollingStation.objects.get(polling_station_id=polling_station_id)
    except:
        errors['polling_station_id'] = ['Polling Station does not exist.']


    if errors:
        payload['message'] = "Errors"
        payload['errors'] = errors
        return Response(payload, status=status.HTTP_400_BAD_REQUEST)

    # Get Election Year (2024)
    election = Election.objects.get(year="2024")


    # Get polling station, electoral area, constituency, Region

    electoral_area = polling_station.electoral_area
    constituency = electoral_area.constituency
    region = constituency.region



    total_votes = sum(int(candidate['votes']) for candidate in ballot)

    for candidate in ballot:

        # Add vote to candidate votes
        election_prez_candidate = ElectionPresidentialCandidate.objects.get(
            election_prez_id=candidate['election_prez_id'])

        election_prez_candidate.total_votes = int(election_prez_candidate.total_votes) + int(candidate['votes'])
        election_prez_candidate.save()

        polling_station_vote = PresidentialCandidatePollingStationVote.objects.filter(
                election=election,
                prez_candidate=election_prez_candidate,
                polling_station=polling_station)

        if polling_station_vote.exists():
            print(polling_station)
            errors['polling_station_id'] = ['Election result for this Polling Station already exist.']

        if errors:
            payload['message'] = "Errors"
            payload['errors'] = errors
            return Response(payload, status=status.HTTP_400_BAD_REQUEST)

        polling_station_vote = PresidentialCandidatePollingStationVote.objects.create(
            election=election,
            prez_candidate=election_prez_candidate,
            polling_station=polling_station)

        polling_station_vote.total_votes = int(polling_station_vote.total_votes) + int(candidate['votes'])
        percentage_share = calculate_percentage(candidate['votes'], total_votes)
        polling_station_vote.total_votes_percent = percentage_share
        polling_station_vote.save()

        #     # Add vote to Electoral Area
        electoral_area_vote = PresidentialCandidateElectoralAreaVote.objects.filter(
            election=election,
                prez_candidate=election_prez_candidate,
                electoral_area=electoral_area
                ).first()

        if electoral_area_vote is not None:
            electoral_area_vote.total_votes = int(electoral_area_vote.total_votes) + int(candidate['votes'])
            electoral_area_vote.save()
        else:
            electoral_area_vote = PresidentialCandidateElectoralAreaVote.objects.create(
                election=election,
                prez_candidate=election_prez_candidate,
                electoral_area=electoral_area
                )
            electoral_area_vote.total_votes = int(candidate['votes'])
            electoral_area_vote.save()

        # Add vote to Constituency


        constituency_vote = PresidentialCandidateConstituencyVote.objects.filter(
            election=election,
                prez_candidate=election_prez_candidate,
                constituency=constituency
                ).first()

        if constituency_vote is not None:
            constituency_vote.total_votes = int(constituency_vote.total_votes) + int(candidate['votes'])
            constituency_vote.save()
        else:
            constituency_vote = PresidentialCandidateConstituencyVote.objects.create(
                election=election,
                prez_candidate=election_prez_candidate,
                constituency=constituency
                )
            constituency_vote.total_votes = int(candidate['votes'])
            constituency_vote.save()



        # Add vote to Region

        region_vote = PresidentialCandidateRegionalVote.objects.filter(
            election=election,
                prez_candidate=election_prez_candidate,
                region=region
                ).first()

        if region_vote is not None:
            region_vote.total_votes = int(region_vote.total_votes) + int(candidate['votes'])
            region_vote.save()
        else:
            region_vote = PresidentialCandidateRegionalVote.objects.create(
                election=election,
                prez_candidate=election_prez_candidate,
                region=region
                )
            region_vote.total_votes = int(candidate['votes'])
            region_vote.save()





    # Calculate General Percentage share
    presidential_candidates = ElectionPresidentialCandidate.objects.all()
    g_total_votes = sum(candidate.total_votes for candidate in presidential_candidates)
    for candidate in presidential_candidates:
        percentage_share = calculate_percentage(candidate.total_votes, g_total_votes)
        candidate.total_votes_percent = percentage_share
        candidate.save()


    # Calculate Electoral Area Percentage Share
    electoral_area_candidates = PresidentialCandidateElectoralAreaVote.objects.filter(
        election=election,
        electoral_area=electoral_area
    )
    ea_total_votes = sum(candidate.total_votes for candidate in electoral_area_candidates)
    for candidate in electoral_area_candidates:
        percentage_share = calculate_percentage(candidate.total_votes, ea_total_votes)
        candidate.total_votes_percent = percentage_share
        candidate.save()


    # Calculate Constituency Percentage Share
    constituency_candidates = PresidentialCandidateConstituencyVote.objects.filter(
        election=election,
        constituency=constituency
    )
    c_total_votes = sum(candidate.total_votes for candidate in constituency_candidates)
    for candidate in constituency_candidates:
        percentage_share = calculate_percentage(candidate.total_votes, c_total_votes)
        candidate.total_votes_percent = percentage_share
        candidate.save()



    # Calculate Region Percentage Share
    region_candidates = PresidentialCandidateRegionalVote.objects.filter(
        election=election,
        region=region
    )
    r_total_votes = sum(candidate.total_votes for candidate in region_candidates)
    for candidate in region_candidates:
        percentage_share = calculate_percentage(candidate.total_votes, r_total_votes)
        candidate.total_votes_percent = percentage_share
        candidate.save()


    # Declear Polling station submitted
    polling_station.presidential_submitted = True
    polling_station.save()

    # Check if all polling station is submitted in electoral Area and check Electoral Area Submitted
    electoral_area_polling_station_submit_qs = PollingStation.objects.filter(electoral_area=electoral_area).filter(presidential_submitted=False)
    if not electoral_area_polling_station_submit_qs.exists():
        electoral_area.presidential_submitted = True
        electoral_area.save()


    # Check if all Electoral Area is submitted in Constituency and check Constituency Submitted
    constituency_electoral_area_submit_qs = ElectoralArea.objects.filter(constituency=constituency).filter(presidential_submitted=False)
    if not constituency_electoral_area_submit_qs.exists():
        constituency.presidential_submitted = True
        constituency.save()


    # Check if all Constituencies is submitted in Region and check Region Submitted
    region_constituency_submit_qs = Constituency.objects.filter(region=region).filter(presidential_submitted=False)
    if not region_constituency_submit_qs.exists():
        region.presidential_submitted = True
        region.save()

    # new_activity = AllActivity.objects.create(
    #     user=User.objects.get(id=1),
    #     subject="Election Parliamentary Candidate Added",
    #     body="New Election Parliamentary Candidate added"
    # )
    # new_activity.save()

    # Send a WebSocket message to trigger the consumer
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        'elections-2024-room-dashboard',
        {
            "type": "update_2024_election_dashboard",
        }
    )

    async_to_sync(channel_layer.group_send)(
        'live-map-room',
        {
            "type": "update_map_dashboard",
        }
    )

    payload['message'] = "Successful"
    payload['data'] = data

    return Response(payload, status=status.HTTP_200_OK)


def calculate_percentage(candidate_votes, total_votes):
    return (int(candidate_votes) / int(total_votes)) * 100





@api_view(['GET', ])
@permission_classes([IsAuthenticated, ])
@authentication_classes([TokenAuthentication, ])
def get_election_2024_dashboard_view(request):
    payload = {}
    data = {}

    presidential_result_chart = []
    incoming_votes = []

    election_2024 = Election.objects.all().filter(year="2024").first()

    all_election_2024_presidential_candidates = ElectionPresidentialCandidate.objects.all().filter(election=election_2024).order_by("-total_votes")

    first_presidential_candidate = all_election_2024_presidential_candidates[0]
    first_presidential_candidate_serializer = ElectionPresidentialCandidateSerializer(first_presidential_candidate, many=False)
    if first_presidential_candidate_serializer:
        first_presidential_candidate = first_presidential_candidate_serializer.data


    second_presidential_candidate = all_election_2024_presidential_candidates[1]
    second_presidential_candidate_serializer = ElectionPresidentialCandidateSerializer(
        second_presidential_candidate, many=False)
    if second_presidential_candidate_serializer:
        second_presidential_candidate = second_presidential_candidate_serializer.data


    for candidate in all_election_2024_presidential_candidates:
        candidate_data = {
            "first_name": candidate.candidate.first_name,
            "last_name": candidate.candidate.last_name,
            "photo": candidate.candidate.photo.url,
            "party_full_name":candidate.candidate.party.party_full_name,
            "party_initial": candidate.candidate.party.party_initial,
            "party_logo": candidate.candidate.party.party_logo.url,
            "total_votes": candidate.total_votes,
            "total_votes_percent": candidate.total_votes_percent,
            "parliamentary_seat": candidate.parliamentary_seat,
        }

        presidential_result_chart.append(candidate_data)

    all_prez_incoming_vote_candidates = PresidentialCandidatePollingStationVote.objects.all().order_by("-created_at")
    all_prez_incoming_vote_candidates_serializer = PresidentialCandidatePollingStationVoteSerializer(all_prez_incoming_vote_candidates,
                                                                                      many=True)
    if all_prez_incoming_vote_candidates_serializer:
        all_prez_incoming_vote_candidates = all_prez_incoming_vote_candidates_serializer.data
        incoming_votes.extend(all_prez_incoming_vote_candidates)

    all_parl_incoming_vote_candidates = ParliamentaryCandidatePollingStationVote.objects.all().order_by("-created_at")
    all_parl_incoming_vote_candidates_serializer = ParliamentaryCandidatePollingStationVoteSerializer(
        all_parl_incoming_vote_candidates,
        many=True)
    if all_parl_incoming_vote_candidates_serializer:
        all_parl_incoming_vote_candidates = all_parl_incoming_vote_candidates_serializer.data
        incoming_votes.extend(all_parl_incoming_vote_candidates)

    data["first_presidential_candidate"] = first_presidential_candidate
    data["second_presidential_candidate"] = second_presidential_candidate
    data["presidential_result_chart"] = presidential_result_chart
    data["incoming_votes"] = incoming_votes
    payload['message'] = "Successful"
    payload['data'] = data

    return Response(payload, status=status.HTTP_200_OK)







@api_view(['POST', ])
@permission_classes([IsAuthenticated, ])
@authentication_classes([TokenAuthentication, ])
def add_election_parliamentary_vote_view222(request):
    payload = {}
    data = {}
    errors = {}

    old_leading_candidate_party = None

    polling_station_id = request.data.get('polling_station_id', '')
    ballot = request.data.get('ballot', [])

    if not polling_station_id:
        errors['polling_station_id'] = ['Polling Station id is required.']

    if not ballot:
        errors['ballot'] = ['Ballot is required.']

    try:
        polling_station = PollingStation.objects.get(polling_station_id=polling_station_id)
    except:
        errors['polling_station_id'] = ['Polling Station does not exist.']


    if errors:
        payload['message'] = "Errors"
        payload['errors'] = errors
        return Response(payload, status=status.HTTP_400_BAD_REQUEST)

    # Get Election Year (2024)
    election = Election.objects.get(year="2024")


    # Get polling station, electoral area, constituency, Region

    electoral_area = polling_station.electoral_area
    constituency = electoral_area.constituency
    region = constituency.region

    _old_leading_candidate = ParliamentaryCandidateConstituencyVote.objects.filter(
        election=election,
        constituency=constituency
    ).order_by('-total_votes').first()

    if _old_leading_candidate.total_votes != 0:
        old_leading_candidate = _old_leading_candidate
    else:
        old_leading_candidate = None



    total_votes = sum(int(candidate['votes']) for candidate in ballot)


    for candidate in ballot:

        # Add vote to candidate votes
        election_parl_candidate = ElectionParliamentaryCandidate.objects.get(
            election_parl_id=candidate['election_parl_id'])

        election_parl_candidate.total_votes = int(election_parl_candidate.total_votes) + int(candidate['votes'])
        election_parl_candidate.save()

        polling_station_vote = ParliamentaryCandidatePollingStationVote.objects.filter(
                election=election,
                parl_candidate=election_parl_candidate,
                polling_station=polling_station)

        if polling_station_vote.exists():
            print(polling_station)
            errors['polling_station_id'] = ['Election result for this Polling Station already exists.']

        if errors:
            payload['message'] = "Errors"
            payload['errors'] = errors
            return Response(payload, status=status.HTTP_400_BAD_REQUEST)

        polling_station_vote = ParliamentaryCandidatePollingStationVote.objects.create(
            election=election,
            parl_candidate=election_parl_candidate,
            polling_station=polling_station)

        polling_station_vote.total_votes = int(polling_station_vote.total_votes) + int(candidate['votes'])
        percentage_share = calculate_percentage(candidate['votes'], total_votes)
        polling_station_vote.total_votes_percent = percentage_share
        polling_station_vote.save()

        #     # Add vote to Electoral Area
        electoral_area_vote = ParliamentaryCandidateElectoralAreaVote.objects.filter(
            election=election,
                parl_candidate=election_parl_candidate,
                electoral_area=electoral_area
                ).first()

        if electoral_area_vote is not None:
            electoral_area_vote.total_votes = int(electoral_area_vote.total_votes) + int(candidate['votes'])
            electoral_area_vote.save()
        else:
            electoral_area_vote = ParliamentaryCandidateElectoralAreaVote.objects.create(
                election=election,
                parl_candidate=election_parl_candidate,
                electoral_area=electoral_area
                )
            electoral_area_vote.total_votes = int(candidate['votes'])
            electoral_area_vote.save()

        # Add vote to Constituency


        constituency_vote = ParliamentaryCandidateConstituencyVote.objects.filter(
            election=election,
                parl_candidate=election_parl_candidate,
                constituency=constituency
                ).first()

        if constituency_vote is not None:
            constituency_vote.total_votes = int(constituency_vote.total_votes) + int(candidate['votes'])
            constituency_vote.save()
        else:
            constituency_vote = ParliamentaryCandidateConstituencyVote.objects.create(
                election=election,
                parl_candidate=election_parl_candidate,
                constituency=constituency
                )
            constituency_vote.total_votes = int(candidate['votes'])
            constituency_vote.save()



        # Add vote to Region

        region_vote = ParliamentaryCandidateRegionalVote.objects.filter(
            election=election,
                parl_candidate=election_parl_candidate,
                region=region
                ).first()

        if region_vote is not None:
            region_vote.total_votes = int(region_vote.total_votes) + int(candidate['votes'])
            region_vote.save()
        else:
            region_vote = ParliamentaryCandidateRegionalVote.objects.create(
                election=election,
                parl_candidate=election_parl_candidate,
                region=region
                )
            region_vote.total_votes = int(candidate['votes'])
            region_vote.save()



    # Calculate Electoral Area Percentage Share
    electoral_area_candidates = ParliamentaryCandidateElectoralAreaVote.objects.filter(
        election=election,
        electoral_area=electoral_area
    )
    ea_total_votes = sum(candidate.total_votes for candidate in electoral_area_candidates)
    for candidate in electoral_area_candidates:
        percentage_share = calculate_percentage(candidate.total_votes, ea_total_votes)
        candidate.total_votes_percent = percentage_share
        candidate.save()


    # Calculate Constituency Percentage Share
    constituency_candidates = ParliamentaryCandidateConstituencyVote.objects.filter(
        election=election,
        constituency=constituency
    )
    c_total_votes = sum(candidate.total_votes for candidate in constituency_candidates)
    for candidate in constituency_candidates:
        percentage_share = calculate_percentage(candidate.total_votes, c_total_votes)
        candidate.total_votes_percent = percentage_share
        candidate.save()

    leading_candidate = ParliamentaryCandidateConstituencyVote.objects.filter(
        election=election,
        constituency=constituency
    ).order_by('-total_votes').first()

    leading_candidate_party = leading_candidate.parl_candidate.candidate.party

    all_prez_candidates = ElectionPresidentialCandidate.objects.all()

    if old_leading_candidate == None:
        for candidate in all_prez_candidates:
            if candidate.candidate.party.party_id == leading_candidate_party.party_id:
                candidate.parliamentary_seat = int(candidate.parliamentary_seat) + 1
                candidate.save()

    elif old_leading_candidate != None:
        if old_leading_candidate:
            pass


    for candidate in all_prez_candidates:
        if old_leading_candidate == None:
            if candidate.candidate.party.party_id == leading_candidate_party.party_id:
                candidate.parliamentary_seat = int(candidate.parliamentary_seat) + 1
                candidate.save()
        elif old_leading_candidate != None:
            if old_leading_candidate == leading_candidate:
                pass
           # elif old_leading_candidate != leading_candidate:





    # Calculate Region Percentage Share
    # region_candidates = ParliamentaryCandidateRegionalVote.objects.filter(
    #     election=election,
    #     region=region
    # )
    # r_total_votes = sum(candidate.total_votes for candidate in region_candidates)
    # for candidate in region_candidates:
    #     percentage_share = calculate_percentage(candidate.total_votes, r_total_votes)
    #     candidate.total_votes_percent = percentage_share
    #     candidate.save()



    # new_activity = AllActivity.objects.create(
    #     user=User.objects.get(id=1),
    #     subject="Election Parliamentary Candidate Added",
    #     body="New Election Parliamentary Candidate added"
    # )
    # new_activity.save()


    # Send a WebSocket message to trigger the consumer
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        'elections-2024-room-dashboard',
        {
            "type": "update_2024_election_dashboard",
        }
    )


    payload['message'] = "Successful"
    payload['data'] = data

    return Response(payload, status=status.HTTP_200_OK)




@api_view(['POST'])
@permission_classes([IsAuthenticated])
@authentication_classes([TokenAuthentication])
def add_election_parliamentary_vote_view(request):
    payload = {}
    data = {}
    errors = {}

    polling_station_id = request.data.get('polling_station_id', '')
    ballot = request.data.get('ballot', [])

    if not polling_station_id:
        errors['polling_station_id'] = ['Polling Station id is required.']

    if not ballot:
        errors['ballot'] = ['Ballot is required.']

    try:
        polling_station = PollingStation.objects.get(polling_station_id=polling_station_id)
    except PollingStation.DoesNotExist:
        errors['polling_station_id'] = ['Polling Station does not exist.']

    if errors:
        payload['message'] = "Errors"
        payload['errors'] = errors
        return Response(payload, status=status.HTTP_400_BAD_REQUEST)

    # Get Election Year (2024)
    election = Election.objects.get(year="2024")

    # Get polling station, electoral area, constituency, Region
    electoral_area = polling_station.electoral_area
    constituency = electoral_area.constituency
    region = constituency.region

    total_votes = sum(int(candidate['votes']) for candidate in ballot)

    for candidate in ballot:
        # Add vote to candidate votes
        election_parl_candidate = ElectionParliamentaryCandidate.objects.get(
            election_parl_id=candidate['election_parl_id']
        )

        election_parl_candidate.total_votes += int(candidate['votes'])
        election_parl_candidate.save()

        polling_station_vote = ParliamentaryCandidatePollingStationVote.objects.filter(
            election=election,
            parl_candidate=election_parl_candidate,
            polling_station=polling_station
        )

        if polling_station_vote.exists():
            errors['polling_station_id'] = ['Election result for this Polling Station already exists.']

        if errors:
            payload['message'] = "Errors"
            payload['errors'] = errors
            return Response(payload, status=status.HTTP_400_BAD_REQUEST)

        polling_station_vote = ParliamentaryCandidatePollingStationVote.objects.create(
            election=election,
            parl_candidate=election_parl_candidate,
            polling_station=polling_station
        )

        polling_station_vote.total_votes += int(candidate['votes'])
        percentage_share = calculate_percentage(candidate['votes'], total_votes)
        polling_station_vote.total_votes_percent = percentage_share
        polling_station_vote.save()

        # Add vote to Electoral Area
        electoral_area_vote = ParliamentaryCandidateElectoralAreaVote.objects.filter(
            election=election,
            parl_candidate=election_parl_candidate,
            electoral_area=electoral_area
        ).first()

        if electoral_area_vote is not None:
            electoral_area_vote.total_votes += int(candidate['votes'])
            electoral_area_vote.save()
        else:
            electoral_area_vote = ParliamentaryCandidateElectoralAreaVote.objects.create(
                election=election,
                parl_candidate=election_parl_candidate,
                electoral_area=electoral_area,
                total_votes=int(candidate['votes'])  # Initialize with current votes
            )
        
        # Add vote to Constituency
        constituency_vote = ParliamentaryCandidateConstituencyVote.objects.filter(
            election=election,
            parl_candidate=election_parl_candidate,
            constituency=constituency
        ).first()

        if constituency_vote is not None:
            constituency_vote.total_votes += int(candidate['votes'])
            constituency_vote.save()
        else:
            constituency_vote = ParliamentaryCandidateConstituencyVote.objects.create(
                election=election,
                parl_candidate=election_parl_candidate,
                constituency=constituency,
                total_votes=int(candidate['votes']),  # Initialize with current votes
                won=False  # Default to not won
            )

        # Add vote to Region
        region_vote = ParliamentaryCandidateRegionalVote.objects.filter(
            election=election,
            parl_candidate=election_parl_candidate,
            region=region
        ).first()

        if region_vote is not None:
            region_vote.total_votes += int(candidate['votes'])
            region_vote.save()
        else:
            region_vote = ParliamentaryCandidateRegionalVote.objects.create(
                election=election,
                parl_candidate=election_parl_candidate,
                region=region,
                total_votes=int(candidate['votes'])  # Initialize with current votes
            )

    # Calculate Electoral Area Percentage Share
    electoral_area_candidates = ParliamentaryCandidateElectoralAreaVote.objects.filter(
        election=election,
        electoral_area=electoral_area
    )
    ea_total_votes = sum(candidate.total_votes for candidate in electoral_area_candidates)
    for candidate in electoral_area_candidates:
        percentage_share = calculate_percentage(candidate.total_votes, ea_total_votes)
        candidate.total_votes_percent = percentage_share
        candidate.save()

    # Calculate Constituency Percentage Share
    constituency_candidates = ParliamentaryCandidateConstituencyVote.objects.filter(
        election=election,
        constituency=constituency
    )
    c_total_votes = sum(candidate.total_votes for candidate in constituency_candidates)
    for candidate in constituency_candidates:
        percentage_share = calculate_percentage(candidate.total_votes, c_total_votes)
        candidate.total_votes_percent = percentage_share
        candidate.save()

    # Declare Polling station submitted
    polling_station.parliamentary_submitted = True
    polling_station.save()

    # Check if all polling stations are submitted in electoral Area and check Electoral Area Submitted
    electoral_area_polling_station_submit_qs = PollingStation.objects.filter(
        electoral_area=electoral_area,
        election_year=election.year,
        parliamentary_submitted=False
    )
    if not electoral_area_polling_station_submit_qs.exists():
        electoral_area.parliamentary_submitted = True
        electoral_area.save()

    # Check if all Electoral Areas are submitted in Constituency and check Constituency Submitted
    constituency_electoral_area_submit_qs = ElectoralArea.objects.filter(
        constituency=constituency,
        election_year=election.year,
        parliamentary_submitted=False
    )
    if not constituency_electoral_area_submit_qs.exists():
        constituency.parliamentary_submitted = True
        constituency.save()

        # Set Parliamentary seat holder in constituency
        leading_candidate = ParliamentaryCandidateConstituencyVote.objects.filter(
            election=election,
            constituency=constituency
        ).order_by('-total_votes').first()

        if leading_candidate:
            leading_candidate_party = leading_candidate.parl_candidate.candidate.party
            all_prez_candidates = ElectionPresidentialCandidate.objects.all()

            for candidate in all_prez_candidates:
                if candidate.candidate.party.party_id == leading_candidate_party.party_id:
                    candidate.parliamentary_seat += 1
                    candidate.save()

                    # Add Regional Seat
                    region_vote = PresidentialCandidateRegionalVote.objects.filter(
                        election=election,
                        prez_candidate=candidate,
                        region=region
                    ).first()

                    if region_vote is not None:
                        region_vote.parliamentary_seat += 1
                        region_vote.save()
                    else:
                        # Create new record if it does not exist
                        PresidentialCandidateRegionalVote.objects.create(
                            election=election,
                            prez_candidate=candidate,
                            region=region,
                            parliamentary_seat=1  # Initialize with 1 since it's the first vote
                        )

                    # Set Presidential Candidate to win in Constituency
                    constituency_vote = PresidentialCandidateConstituencyVote.objects.filter(
                        election=election,
                        prez_candidate=candidate,
                        constituency=constituency
                    ).first()

                    if constituency_vote:
                        constituency_vote.won = True
                        constituency_vote.save()

            leading_candidate.parl_candidate.won = True
            leading_candidate.parl_candidate.save()
            leading_candidate.save()

    # Check if all Constituencies are submitted in Region and check Region Submitted
    region_constituency_submit_qs = Constituency.objects.filter(
        region=region,
        election_year=election.year,
        parliamentary_submitted=False
    )
    if not region_constituency_submit_qs.exists():
        region.parliamentary_submitted = True
        region.save()

    # Send a WebSocket message to trigger the consumer
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        'elections-2024-room-dashboard',
        {
            "type": "update_2024_election_dashboard",
        }
    )

    payload['message'] = "Successful"
    payload['data'] = data

    return Response(payload, status=status.HTTP_200_OK)




@api_view(['POST', ])
@permission_classes([IsAuthenticated, ])
@authentication_classes([TokenAuthentication, ])
def add_election_parliamentary_vote_view2222(request):
    payload = {}
    data = {}
    errors = {}

    polling_station_id = request.data.get('polling_station_id', '')
    ballot = request.data.get('ballot', [])

    if not polling_station_id:
        errors['polling_station_id'] = ['Polling Station id is required.']

    if not ballot:
        errors['ballot'] = ['Ballot is required.']

    try:
        polling_station = PollingStation.objects.get(polling_station_id=polling_station_id)
    except:
        errors['polling_station_id'] = ['Polling Station does not exist.']


    if errors:
        payload['message'] = "Errors"
        payload['errors'] = errors
        return Response(payload, status=status.HTTP_400_BAD_REQUEST)

    # Get Election Year (2024)
    election = Election.objects.get(year="2024")


    # Get polling station, electoral area, constituency, Region

    electoral_area = polling_station.electoral_area
    constituency = electoral_area.constituency
    region = constituency.region

    total_votes = sum(int(candidate['votes']) for candidate in ballot)

    for candidate in ballot:

        # Add vote to candidate votes
        election_parl_candidate = ElectionParliamentaryCandidate.objects.get(
            election_parl_id=candidate['election_parl_id'])

        election_parl_candidate.total_votes = int(election_parl_candidate.total_votes) + int(candidate['votes'])
        election_parl_candidate.save()

        polling_station_vote = ParliamentaryCandidatePollingStationVote.objects.filter(
                election=election,
                parl_candidate=election_parl_candidate,
                polling_station=polling_station)

        if polling_station_vote.exists():
            print(polling_station)
            errors['polling_station_id'] = ['Election result for this Polling Station already exist.']

        if errors:
            payload['message'] = "Errors"
            payload['errors'] = errors
            return Response(payload, status=status.HTTP_400_BAD_REQUEST)

        polling_station_vote = ParliamentaryCandidatePollingStationVote.objects.create(
            election=election,
            parl_candidate=election_parl_candidate,
            polling_station=polling_station)

        polling_station_vote.total_votes = int(polling_station_vote.total_votes) + int(candidate['votes'])
        percentage_share = calculate_percentage(candidate['votes'], total_votes)
        polling_station_vote.total_votes_percent = percentage_share
        polling_station_vote.save()

        #     # Add vote to Electoral Area
        electoral_area_vote = ParliamentaryCandidateElectoralAreaVote.objects.filter(
            election=election,
                parl_candidate=election_parl_candidate,
                electoral_area=electoral_area
                ).first()

        if electoral_area_vote is not None:
            electoral_area_vote.total_votes = int(electoral_area_vote.total_votes) + int(candidate['votes'])
            electoral_area_vote.save()
        else:
            electoral_area_vote = ParliamentaryCandidateElectoralAreaVote.objects.create(
                election=election,
                parl_candidate=election_parl_candidate,
                electoral_area=electoral_area
                )
            electoral_area_vote.total_votes = int(candidate['votes'])
            electoral_area_vote.save()

        # Add vote to Constituency


        constituency_vote = ParliamentaryCandidateConstituencyVote.objects.filter(
            election=election,
                parl_candidate=election_parl_candidate,
                constituency=constituency
                ).first()

        if constituency_vote is not None:
            constituency_vote.total_votes = int(constituency_vote.total_votes) + int(candidate['votes'])
            constituency_vote.save()
        else:
            constituency_vote = ParliamentaryCandidateConstituencyVote.objects.create(
                election=election,
                parl_candidate=election_parl_candidate,
                constituency=constituency
                )
            constituency_vote.total_votes = int(candidate['votes'])
            constituency_vote.save()



        # Add vote to Region

        region_vote = ParliamentaryCandidateRegionalVote.objects.filter(
            election=election,
                parl_candidate=election_parl_candidate,
                region=region
                ).first()

        if region_vote is not None:
            region_vote.total_votes = int(region_vote.total_votes) + int(candidate['votes'])
            region_vote.save()
        else:
            region_vote = ParliamentaryCandidateRegionalVote.objects.create(
                election=election,
                parl_candidate=election_parl_candidate,
                region=region
                )
            region_vote.total_votes = int(candidate['votes'])
            region_vote.save()



    # Calculate Electoral Area Percentage Share
    electoral_area_candidates = ParliamentaryCandidateElectoralAreaVote.objects.filter(
        election=election,
        electoral_area=electoral_area
    )
    ea_total_votes = sum(candidate.total_votes for candidate in electoral_area_candidates)
    for candidate in electoral_area_candidates:
        percentage_share = calculate_percentage(candidate.total_votes, ea_total_votes)
        candidate.total_votes_percent = percentage_share
        candidate.save()




    # Calculate Constituency Percentage Share
    constituency_candidates = ParliamentaryCandidateConstituencyVote.objects.filter(
        election=election,
        constituency=constituency
    )
    c_total_votes = sum(candidate.total_votes for candidate in constituency_candidates)
    for candidate in constituency_candidates:
        percentage_share = calculate_percentage(candidate.total_votes, c_total_votes)
        candidate.total_votes_percent = percentage_share
        candidate.save()

        #########################################################

    # Declear Polling station submitted
    polling_station.parliamentary_submitted = True
    polling_station.save()

    # Check if all polling station is submitted in electoral Area and check Electoral Area Submitted
    electoral_area_polling_station_submit_qs = PollingStation.objects.filter(electoral_area=electoral_area).filter(election_year=election.year).filter(
        parliamentary_submitted=False)
    if not electoral_area_polling_station_submit_qs.exists():

        electoral_area.parliamentary_submitted = True
        electoral_area.save()

    # Check if all Electoral Area is submitted in Constituency and check Constituency Submitted
    constituency_electoral_area_submit_qs = ElectoralArea.objects.filter(constituency=constituency).filter(election_year=election.year).filter(
        parliamentary_submitted=False)
    if not constituency_electoral_area_submit_qs.exists():
        constituency.parliamentary_submitted = True
        constituency.save()

        ##### Set Parliamentary seat holder in constituency
        leading_candidate = ParliamentaryCandidateConstituencyVote.objects.filter(
            election=election,
            constituency=constituency
        ).order_by('-total_votes').first()

        leading_candidate_party = leading_candidate.parl_candidate.candidate.party

        all_prez_candidates = ElectionPresidentialCandidate.objects.all()

        for candidate in all_prez_candidates:
            if candidate.candidate.party.party_id == leading_candidate_party.party_id:
                candidate.parliamentary_seat = int(candidate.parliamentary_seat) + 1
                candidate.save()

                #Add Regional Seat ################
                #Add Regional Seat ################
                #Add Regional Seat ################
                # region_vote = PresidentialCandidateRegionalVote.objects.filter(
                #     election=election,
                #     prez_candidate=candidate,
                #     region=region
                # ).first()
# 
                # region_vote.parliamentary_seat = region_vote.parliamentary_seat + 1
                # region_vote.save()

                # Add Regional Seat
                region_vote = PresidentialCandidateRegionalVote.objects.filter(
                    election=election,
                    prez_candidate=candidate,
                    region=region
                ).first()

                if region_vote is not None:
                    region_vote.parliamentary_seat += 1
                    region_vote.save()
                else:
                    # Create new record if it does not exist
                    region_vote = PresidentialCandidateRegionalVote.objects.create(
                        election=election,
                        prez_candidate=candidate,
                        region=region,
                        parliamentary_seat=1  # Initialize with 1 since it's the first vote
                    )

                #### Set Presidential Candidate to win in Constituency
                constituency_vote = PresidentialCandidateConstituencyVote.objects.filter(
                    election=election,
                    prez_candidate=candidate,
                    constituency=constituency
                ).first()

                constituency_vote.won = True
                constituency_vote.save()

        leading_candidate.parl_candidate.won = True
        leading_candidate.parl_candidate.save()
        leading_candidate.save()






    # Check if all Constituencies is submitted in Region and check Region Submitted
    region_constituency_submit_qs = Constituency.objects.filter(region=region).filter(election_year=election.year).filter(parliamentary_submitted=False)
    if not region_constituency_submit_qs.exists():
        region.parliamentary_submitted = True
        region.save()









    # Calculate Region Percentage Share
    # region_candidates = ParliamentaryCandidateRegionalVote.objects.filter(
    #     election=election,
    #     region=region
    # )
    # r_total_votes = sum(candidate.total_votes for candidate in region_candidates)
    # for candidate in region_candidates:
    #     percentage_share = calculate_percentage(candidate.total_votes, r_total_votes)
    #     candidate.total_votes_percent = percentage_share
    #     candidate.save()



    # new_activity = AllActivity.objects.create(
    #     user=User.objects.get(id=1),
    #     subject="Election Parliamentary Candidate Added",
    #     body="New Election Parliamentary Candidate added"
    # )
    # new_activity.save()


    # Send a WebSocket message to trigger the consumer
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        'elections-2024-room-dashboard',
        {
            "type": "update_2024_election_dashboard",
        }
    )


    payload['message'] = "Successful"
    payload['data'] = data

    return Response(payload, status=status.HTTP_200_OK)
