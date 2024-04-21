from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from activities.models import AllActivity
from candidates.models import PresidentialCandidate, ParliamentaryCandidate
from elections.api.serializers import ElectionPresidentialCandidateSerializer, ElectionParliamentaryCandidateSerializer, \
    AllElectionSerializer, PresidentialCandidatePollingStationVoteSerializer, \
    ParliamentaryCandidatePollingStationVoteSerializer
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



@api_view(['GET', ])
@permission_classes([IsAuthenticated, ])
@authentication_classes([TokenAuthentication, ])
def get_all_election_presidential_candidate_view(request):
    payload = {}
    data = {}
    errors = {}

    if errors:
        payload['message'] = "Errors"
        payload['errors'] = errors
        return Response(payload, status=status.HTTP_400_BAD_REQUEST)

    all_election_prez_can = ElectionPresidentialCandidate.objects.all().order_by("ballot_number")

    all_election_prez_can_serializer = ElectionPresidentialCandidateSerializer(all_election_prez_can, many=True)
    if all_election_prez_can_serializer:
        _all_election_prez_can = all_election_prez_can_serializer.data

    payload['message'] = "Successful"
    payload['data'] = _all_election_prez_can

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



@api_view(['GET', ])
@permission_classes([IsAuthenticated, ])
@authentication_classes([TokenAuthentication, ])
def get_all_election_parliamentary_candidate_view(request):
    payload = {}
    data = {}
    errors = {}

    constituency_id = request.GET.get('constituency_id', None)

    if not constituency_id:
        errors['constituency_id'] = ['Constituency ID  is required.']


    try:
        constituency = Constituency.objects.get(constituency_id=constituency_id)
    except:
        errors['constituency_id'] = ['Constituency does not exist.']


    if errors:
        payload['message'] = "Errors"
        payload['errors'] = errors
        return Response(payload, status=status.HTTP_400_BAD_REQUEST)

    all_election_parl_can = ElectionParliamentaryCandidate.objects.all().filter(constituency=constituency).order_by("ballot_number")

    all_election_parl_can_serializer = ElectionParliamentaryCandidateSerializer(all_election_parl_can, many=True)
    if all_election_parl_can_serializer:
        _all_election_parl_can = all_election_parl_can_serializer.data

    payload['message'] = "Successful"
    payload['data'] = _all_election_parl_can

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
            errors['polling_station_id'] = ['Election result for this Polling Station already exists.']

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

    for candidate in all_prez_candidates:
        if candidate.candidate.party.party_id == leading_candidate_party.party_id:
            candidate.parliamentary_seat = int(candidate.parliamentary_seat) + 1
            candidate.save()





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
