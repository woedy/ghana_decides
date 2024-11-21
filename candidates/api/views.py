
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage

from django.contrib.auth import get_user_model
from django.db.models import Q
from rest_framework import status
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import authentication_classes, api_view, permission_classes
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from activities.models import AllActivity
from candidates.api.serializers import AllParliamentaryCandidateSerializer, ParliamentaryCandidateDetailSerializer, \
    AllPresidentialCandidateSerializer, PresidentialCandidateDetailSerializer
from candidates.models import ParliamentaryCandidate, PresidentialCandidate
from candidates.models import Party
from regions.models import Region, Constituency

User = get_user_model()


@api_view(['POST', ])
@permission_classes([])
@authentication_classes([])
def add_parliamentary_candidate(request):
    payload = {}
    data = {}
    errors = {}

    constituency_id = request.data.get('constituency_id', '')
    party_id = request.data.get('party_id', '')
    first_name = request.data.get('first_name', '')
    last_name = request.data.get('last_name', '')
    middle_name = request.data.get('middle_name', '')
    photo = request.data.get('photo', '')
    gender = request.data.get('gender', '')
    candidate_type = request.data.get('candidate_type', '')

    if not constituency_id:
        errors['constituency_id'] = ['Constituency id is required.']

    if not party_id:
        errors['party_id'] = ['Party id is required.']

    if not first_name:
        errors['first_name'] = ['First name id is required.']

    if not last_name:
        errors['last_name'] = ['Last Name is required.']

    if not photo:
        errors['photo'] = ['Photo is required.']

    if not gender:
        errors['gender'] = ['Gender is required.']

    if not candidate_type:
        errors['candidate_type'] = ['Candidate type is required.']


    try:
        party = Party.objects.get(party_id=party_id)
    except Party.DoesNotExist:
        errors['party_id'] = ['Party does not exist.']

    try:
        constituency = Constituency.objects.get(constituency_id=constituency_id)
    except Constituency.DoesNotExist:
        errors['constituency_id'] = ['Constituency does not exist.']

    if errors:
        payload['message'] = "Errors"
        payload['errors'] = errors
        return Response(payload, status=status.HTTP_400_BAD_REQUEST)

    new_parl_can = ParliamentaryCandidate.objects.create(
        constituency=constituency,
        party=party,
        first_name=first_name,
        last_name=last_name,
        middle_name=middle_name,
        photo=photo,
        gender=gender,
        candidate_type=candidate_type,
    )

    data['parl_can_id'] = new_parl_can.parl_can_id

    #
    new_activity = AllActivity.objects.create(
        user=User.objects.get(id=1),
        subject="Parliamentary Candidate Registration",
        body="New Parliamentary Candidate added"
    )
    new_activity.save()

    payload['message'] = "Successful"
    payload['data'] = data

    return Response(payload, status=status.HTTP_200_OK)


@api_view(['POST', ])
@permission_classes([])
@authentication_classes([])
def add_parliamentary_candidate_list(request):
    payload = {}
    data = {}
    errors = {}

    candidates = request.data.get('candidates', [])
    for candidate in candidates:
        constituency_id = candidate.get('constituency_id', '')
        party_id = candidate.get('party_id', '')
        first_name = candidate.get('first_name', '')
        last_name = candidate.get('last_name', '')
        middle_name = candidate.get('middle_name', '')
        photo = candidate.get('photo', '')
        gender = candidate.get('gender', '')
        candidate_type = candidate.get('candidate_type', '')

        if not constituency_id:
            errors['constituency_id'] = ['Constituency id is required.']

        if not party_id:
            errors['party_id'] = ['Party id is required.']

        if not first_name:
            errors['first_name'] = ['First name is required.']

        if not last_name:
            errors['last_name'] = ['Last Name is required.']

        if not photo:
            errors['photo'] = ['Photo is required.']

        if not gender:
            errors['gender'] = ['Gender is required.']

        if not candidate_type:
            errors['candidate_type'] = ['Candidate type is required.']

        try:
            party = Party.objects.get(party_id=party_id)
        except Party.DoesNotExist:
            errors['party_id'] = ['Party does not exist.']

        try:
            constituency = Constituency.objects.get(constituency_id=constituency_id)
        except Constituency.DoesNotExist:
            errors['constituency_id'] = ['Constituency does not exist.']

        if errors:
            payload['message'] = "Errors"
            payload['errors'] = errors
            return Response(payload, status=status.HTTP_400_BAD_REQUEST)

        new_parl_can = ParliamentaryCandidate.objects.create(
            constituency=constituency,
            party=party,
            first_name=first_name,
            last_name=last_name,
            middle_name=middle_name,
            photo=photo,
            gender=gender,
            candidate_type=candidate_type,
        )

        data['parl_can_id'] = new_parl_can.id

        new_activity = AllActivity.objects.create(
            user=User.objects.get(id=1),
            subject="Parliamentary Candidate Registration",
            body="New Parliamentary Candidate added"
        )
        new_activity.save()

    payload['message'] = "Successful"
    payload['data'] = data

    return Response(payload, status=status.HTTP_200_OK)

@api_view(['POST', ])
@permission_classes([IsAuthenticated, ])
@authentication_classes([TokenAuthentication, ])
def edit_parliamentary_candidate_view(request):
    payload = {}
    data = {}
    errors = {}

    parl_can_id = request.data.get('parl_can_id', '')
    first_name = request.data.get('first_name', '')
    last_name = request.data.get('last_name', '')
    middle_name = request.data.get('middle_name', '')
    photo = request.data.get('photo', '')
    gender = request.data.get('gender', '')
    candidate_type = request.data.get('candidate_type', '')
    party_id = request.data.get('party_id', '')
    constituency_id = request.data.get('constituency_id', '')

    if not parl_can_id:
        errors['parl_can_id'] = ['Candidate ID is required.']

    try:
        candidate = ParliamentaryCandidate.objects.get(parl_can_id=parl_can_id)
    except ParliamentaryCandidate.DoesNotExist:
        errors['candidate_id'] = ['Parliamentary candidate does not exist.']

    if not errors:
        # Update candidate fields if the corresponding data is provided
        if first_name:
            candidate.first_name = first_name
        if last_name:
            candidate.last_name = last_name
        if middle_name:
            candidate.middle_name = middle_name
        if photo:
            candidate.photo = photo
        if gender:
            candidate.gender = gender
        if candidate_type:
            candidate.candidate_type = candidate_type

        # Update party and constituency if IDs are provided
        if party_id:
            try:
                party = Party.objects.get(party_id=party_id)
                candidate.party = party
            except Party.DoesNotExist:
                errors['party_id'] = ['Party does not exist.']
        if constituency_id:
            try:
                constituency = Constituency.objects.get(constituency_id=constituency_id)
                candidate.constituency = constituency
            except Constituency.DoesNotExist:
                errors['constituency_id'] = ['Constituency does not exist.']

        if not errors:
            candidate.save()
            data['parl_can_id'] = candidate.parl_can_id
            payload['message'] = "Successfully"
            payload['data'] = data
        else:
            payload['message'] = "Errors"
            payload['errors'] = errors
            return Response(payload, status=status.HTTP_400_BAD_REQUEST)

    return Response(payload, status=status.HTTP_200_OK)


@api_view(['GET', ])
@permission_classes([IsAuthenticated, ])
@authentication_classes([TokenAuthentication])
def get_all_parliamentary_candidate(request):
    payload = {}
    data = {}
    errors = {}

    search_query = request.query_params.get('search', '')
    page_number = request.query_params.get('page', 1)
    page_size = 50
    all_parl_can = ParliamentaryCandidate.objects.all()

    # Apply search filter if search query is provided
    if search_query:
        all_parl_can = all_parl_can.filter(
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query) |
            Q(middle_name__icontains=search_query)
        )

    paginator = Paginator(all_parl_can, page_size)

    try:
        paginated_candidates = paginator.page(page_number)
    except PageNotAnInteger:
        paginated_candidates = paginator.page(1)
    except EmptyPage:
        paginated_candidates = paginator.page(paginator.num_pages)

    all_parl_can_serializer = AllParliamentaryCandidateSerializer(paginated_candidates, many=True)

    data['candidates'] = all_parl_can_serializer.data
    data['pagination'] = {
        'page_number': paginated_candidates.number,
        'count': all_parl_can.count(),
        'total_pages': paginator.num_pages,
        'next': paginated_candidates.next_page_number() if paginated_candidates.has_next() else None,
        'previous': paginated_candidates.previous_page_number() if paginated_candidates.has_previous() else None,
    }

    payload['message'] = "Successful"
    payload['data'] = data

    return Response(payload, status=status.HTTP_200_OK)

@api_view(['GET', ])
@permission_classes([IsAuthenticated, ])
@authentication_classes([TokenAuthentication, ])
def get_parliamentary_candidate_details(request):
    payload = {}
    data = {}
    errors = {}

    parl_can_id = request.query_params.get('parl_can_id', None)

    if not parl_can_id:
        errors['parl_can_id'] = ["Parliamentary Candidate id required"]

    try:
        parl_can = ParliamentaryCandidate.objects.get(parl_can_id=parl_can_id)
    except ParliamentaryCandidate.DoesNotExist:
        errors['parl_can_id'] = ['Parliamentary Candidate does not exist.']

    if errors:
        payload['message'] = "Errors"
        payload['errors'] = errors
        return Response(payload, status=status.HTTP_400_BAD_REQUEST)

    parl_can_serializer = ParliamentaryCandidateDetailSerializer(parl_can, many=False)
    if parl_can_serializer:
        parl_can = parl_can_serializer.data

    payload['message'] = "Successful"
    payload['data'] = parl_can

    return Response(payload, status=status.HTTP_200_OK)


@api_view(['POST', ])
@permission_classes([IsAuthenticated, ])
@authentication_classes([TokenAuthentication, ])
def delete_parliamentary_candidate_view(request):
    payload = {}
    data = {}
    errors = {}

    parl_can_id = request.data.get('parl_can_id', '')

    if not parl_can_id:
        errors['parl_can_id'] = ['Parliamentary Candidate ID is required.']

    try:
        candidate = ParliamentaryCandidate.objects.get(parl_can_id=parl_can_id)
    except ParliamentaryCandidate.DoesNotExist:
        errors['parl_can_id'] = ['Parliamentary candidate does not exist.']

    if errors:
        payload['message'] = "Errors"
        payload['errors'] = errors
        return Response(payload, status=status.HTTP_400_BAD_REQUEST)

    candidate.delete()

    #
    new_activity = AllActivity.objects.create(
        user=User.objects.get(id=1),
        subject="Parliamentary Candidate Deleted",
        body="Parliamentary Candidate Deleted"
    )
    new_activity.save()

    payload['message'] = "Successful"
    payload['data'] = {}

    return Response(payload, status=status.HTTP_200_OK)



#######################
##### PRESIDENTIAL
###################


@api_view(['POST', ])
@permission_classes([])
@authentication_classes([])
def add_presidential_candidate(request):
    payload = {}
    data = {}
    errors = {}

    party_id = request.data.get('party_id', '')
    first_name = request.data.get('first_name', '')
    last_name = request.data.get('last_name', '')
    middle_name = request.data.get('middle_name', '')
    photo = request.data.get('photo', '')
    gender = request.data.get('gender', '')
    candidate_type = request.data.get('candidate_type', '')


    if not party_id:
        errors['party_id'] = ['Party id is required.']

    if not first_name:
        errors['first_name'] = ['First name id is required.']

    if not last_name:
        errors['last_name'] = ['Last Name is required.']

    if not photo:
        errors['photo'] = ['Photo is required.']

    if not gender:
        errors['gender'] = ['Gender is required.']

    if not candidate_type:
        errors['candidate_type'] = ['Candidate type is required.']


    try:
        party = Party.objects.get(party_id=party_id)
    except Party.DoesNotExist:
        errors['party_id'] = ['Party does not exist.']

    if errors:
        payload['message'] = "Errors"
        payload['errors'] = errors
        return Response(payload, status=status.HTTP_400_BAD_REQUEST)

    new_prez_can = PresidentialCandidate.objects.create(
        party=party,
        first_name=first_name,
        last_name=last_name,
        middle_name=middle_name,
        photo=photo,
        gender=gender,
        candidate_type=candidate_type,
    )

    data['prez_can_id'] = new_prez_can.prez_can_id

    #
    new_activity = AllActivity.objects.create(
        user=User.objects.get(id=1),
        subject="Presidential Candidate Registration",
        body="New Presidential Candidate added"
    )
    new_activity.save()

    payload['message'] = "Successful"
    payload['data'] = data

    return Response(payload, status=status.HTTP_200_OK)



@api_view(['POST', ])
@permission_classes([])
@authentication_classes([])
def add_presidential_candidates_list(request):
    payload = {}
    data = {}
    errors = {}

    candidates = request.data.get('candidates', [])
    for candidate in candidates:
        first_name = candidate.get('first_name', '')
        middle_name = candidate.get('middle_name', '')
        last_name = candidate.get('last_name', '')
        party = candidate.get('party', '')
        gender = candidate.get('gender', '')

        # Assuming you have a Party model with a name field
        try:
            party = Party.objects.get(party_initial=party)
        except Party.DoesNotExist:
            errors['party'] = ['Party does not exist.']

        if not first_name:
            errors['first_name'] = ['First name is required.']

        if not last_name:
            errors['last_name'] = ['Last Name is required.']

        if not gender:
            errors['gender'] = ['Gender is required.']

        if errors:
            payload['message'] = "Errors"
            payload['errors'] = errors
            return Response(payload, status=status.HTTP_400_BAD_REQUEST)

        new_prez_can = PresidentialCandidate.objects.create(
            party=party,
            first_name=first_name,
            last_name=last_name,
            middle_name=middle_name,
            gender=gender,
        )

        data['prez_can_id'] = new_prez_can.id

        new_activity = AllActivity.objects.create(
            user=User.objects.get(id=1),
            subject="Presidential Candidate Registration",
            body="New Presidential Candidate added"
        )
        new_activity.save()

    payload['message'] = "Successful"
    payload['data'] = data

    return Response(payload, status=status.HTTP_200_OK)


@api_view(['POST', ])
@permission_classes([IsAuthenticated, ])
@authentication_classes([TokenAuthentication, ])
def edit_presidential_candidate_view(request):
    payload = {}
    data = {}
    errors = {}

    prez_can_id = request.data.get('prez_can_id', '')
    first_name = request.data.get('first_name', '')
    last_name = request.data.get('last_name', '')
    middle_name = request.data.get('middle_name', '')
    photo = request.data.get('photo', '')
    gender = request.data.get('gender', '')
    candidate_type = request.data.get('candidate_type', '')

    if not prez_can_id:
        errors['prez_can_id'] = ['Candidate ID is required.']

    try:
        candidate = PresidentialCandidate.objects.get(prez_can_id=prez_can_id)
    except PresidentialCandidate.DoesNotExist:
        errors['candidate_id'] = ['Presidential candidate does not exist.']

    if errors:
        payload['message'] = "Errors"
        payload['errors'] = errors
        return Response(payload, status=status.HTTP_400_BAD_REQUEST)

    # Update candidate fields if the corresponding data is provided
    if first_name:
        candidate.first_name = first_name
    if last_name:
        candidate.last_name = last_name
    if middle_name:
        candidate.middle_name = middle_name
    if photo:
        candidate.photo = photo
    if gender:
        candidate.gender = gender
    if candidate_type:
        candidate.candidate_type = candidate_type

    candidate.save()

    data['prez_can_id'] = candidate.prez_can_id

    payload['message'] = "Successfully"
    payload['data'] = data

    return Response(payload, status=status.HTTP_200_OK)


@api_view(['GET', ])
@permission_classes([IsAuthenticated, ])
@authentication_classes([TokenAuthentication])
def get_all_presidential_candidate(request):
    payload = {}
    data = {}
    errors = {}

    search_query = request.query_params.get('search', '')
    page_number = request.query_params.get('page', 1)
    page_size = 50

    all_prez_can = PresidentialCandidate.objects.all()

    # Apply search filter if search query is provided
    if search_query:
        all_prez_can = all_prez_can.filter(
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query) |
            Q(middle_name__icontains=search_query)
        )

    paginator = Paginator(all_prez_can, page_size)

    try:
        paginated_candidates = paginator.page(page_number)
    except PageNotAnInteger:
        paginated_candidates = paginator.page(1)
    except EmptyPage:
        paginated_candidates = paginator.page(paginator.num_pages)

    all_prez_can_serializer = AllPresidentialCandidateSerializer(paginated_candidates, many=True)

    data['candidates'] = all_prez_can_serializer.data
    data['pagination'] = {
        'page_number': paginated_candidates.number,
        'count': all_prez_can.count(),
        'total_pages': paginator.num_pages,
        'next': paginated_candidates.next_page_number() if paginated_candidates.has_next() else None,
        'previous': paginated_candidates.previous_page_number() if paginated_candidates.has_previous() else None,
    }

    payload['message'] = "Successful"
    payload['data'] = data

    return Response(payload, status=status.HTTP_200_OK)


@api_view(['GET', ])
@permission_classes([IsAuthenticated, ])
@authentication_classes([TokenAuthentication, ])
def get_presidential_candidate_details(request):
    payload = {}
    data = {}
    errors = {}

    prez_can_id = request.query_params.get('prez_can_id', None)

    if not prez_can_id:
        errors['prez_can_id'] = ["Presidential Candidate id required"]

    try:
        prez_can = PresidentialCandidate.objects.get(prez_can_id=prez_can_id)
    except PresidentialCandidate.DoesNotExist:
        errors['prez_can_id'] = ['Presidential Candidate does not exist.']

    if errors:
        payload['message'] = "Errors"
        payload['errors'] = errors
        return Response(payload, status=status.HTTP_400_BAD_REQUEST)

    prez_can_serializer = PresidentialCandidateDetailSerializer(prez_can, many=False)
    if prez_can_serializer:
        prez_can = prez_can_serializer.data

    payload['message'] = "Successful"
    payload['data'] = prez_can

    return Response(payload, status=status.HTTP_200_OK)



@api_view(['POST', ])
@permission_classes([IsAuthenticated, ])
@authentication_classes([TokenAuthentication, ])
def delete_presidential_candidate_view(request):
    payload = {}
    data = {}
    errors = {}

    prez_can_id = request.data.get('prez_can_id', '')


    print(prez_can_id)

    if not prez_can_id:
        errors['prez_can_id'] = ['Presidential Candidate ID is required.']

    try:
        candidate = PresidentialCandidate.objects.get(prez_can_id=prez_can_id)
    except PresidentialCandidate.DoesNotExist:
        errors['prez_can_id'] = ['Presidential candidate does not exist.']

    if errors:
        payload['message'] = "Errors"
        payload['errors'] = errors
        return Response(payload, status=status.HTTP_400_BAD_REQUEST)

    candidate.delete()

    #
    new_activity = AllActivity.objects.create(
        user=User.objects.get(id=1),
        subject="Presidential Candidate Deleted",
        body="Presidential Candidate Deleted"
    )
    new_activity.save()

    payload['message'] = "Successful"
    payload['data'] = {}

    return Response(payload, status=status.HTTP_200_OK)

