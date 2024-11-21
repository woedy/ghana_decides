
from django.contrib.auth import get_user_model
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage

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
from elections.models import PresidentialCandidatePollingStationVote, PresidentialCandidateElectoralAreaVote, \
    PresidentialCandidateConstituencyVote, PresidentialCandidateRegionalVote, ElectionPresidentialCandidate, \
    ParliamentaryCandidatePollingStationVote, ParliamentaryCandidateElectoralAreaVote, \
    ParliamentaryCandidateConstituencyVote, ParliamentaryCandidateRegionalVote, ElectionParliamentaryCandidate
from regions.models import Region, Constituency, ElectoralArea, PollingStation

User = get_user_model()


@api_view(['POST', ])
@permission_classes([IsAuthenticated, ])
@authentication_classes([TokenAuthentication, ])
def reset_votes(request):
    payload = {}
    data = {}
    errors = {}

    prez_polling_station_votes = PresidentialCandidatePollingStationVote.objects.all()
    for vote in prez_polling_station_votes:
        vote.delete()

    parl_polling_station_votes = ParliamentaryCandidatePollingStationVote.objects.all()
    for vote in parl_polling_station_votes:
        vote.delete()


    electoral_area_vote = PresidentialCandidateElectoralAreaVote.objects.all()
    for vote in electoral_area_vote:
        vote.delete()


    parl_electoral_area_vote = ParliamentaryCandidateElectoralAreaVote.objects.all()
    for vote in parl_electoral_area_vote:
        vote.delete()


    constituency_vote = PresidentialCandidateConstituencyVote.objects.all()
    for vote in constituency_vote:
        vote.delete()

    parl_constituency_vote = ParliamentaryCandidateConstituencyVote.objects.all()
    for vote in parl_constituency_vote:
        vote.delete()

    regional_vote = PresidentialCandidateRegionalVote.objects.all()
    for vote in regional_vote:
        vote.delete()

    parl_regional_vote = ParliamentaryCandidateRegionalVote.objects.all()
    for vote in parl_regional_vote:
        vote.delete()



    presidential_votes = ElectionPresidentialCandidate.objects.all()
    for candidate in presidential_votes:
        candidate.total_votes = 0
        candidate.total_votes_percent = 0.0
        candidate.parliamentary_seat = 0
        candidate.save()

    parliamentary_votes = ElectionParliamentaryCandidate.objects.all()
    for candidate in parliamentary_votes:
        candidate.total_votes = 0
        candidate.total_votes_percent = 0.0
        candidate.won = False
        candidate.save()

    payload['message'] = "Successful"
    payload['data'] = data

    return Response(payload, status=status.HTTP_200_OK)


@api_view(['POST', ])
@permission_classes([IsAuthenticated, ])
@authentication_classes([TokenAuthentication, ])
def reset_region_2024(request):
    payload = {}
    data = {}
    errors = {}

    polling_station = PollingStation.objects.all()
    for polling in polling_station:
        polling.election_year = "2024"
        polling.parliamentary_submitted = False
        polling.presidential_submitted = False
        polling.save()


    electoral = ElectoralArea.objects.all()
    for elect in electoral:
        elect.election_year = "2024"

        elect.parliamentary_submitted = False
        elect.presidential_submitted = False
        elect.save()


    constituency = Constituency.objects.all()
    for cons in constituency:
        cons.election_year = "2024"
        cons.parliamentary_submitted = False
        cons.presidential_submitted = False
        cons.save()

    regions = Region.objects.all()
    for region in regions:
        region.election_year = "2024"
        region.parliamentary_submitted = False
        region.presidential_submitted = False
        region.save()



    payload['message'] = "Successful"
    payload['data'] = data

    return Response(payload, status=status.HTTP_200_OK)




@api_view(['POST', ])
@permission_classes([ ])
@authentication_classes([ ])
def reset_demo(request):
    payload = {}
    data = {}
    errors = {}

    prez_polling_station_votes = PresidentialCandidatePollingStationVote.objects.all()
    for vote in prez_polling_station_votes:
        vote.delete()

    parl_polling_station_votes = ParliamentaryCandidatePollingStationVote.objects.all()
    for vote in parl_polling_station_votes:
        vote.delete()


    electoral_area_vote = PresidentialCandidateElectoralAreaVote.objects.all()
    for vote in electoral_area_vote:
        vote.delete()


    parl_electoral_area_vote = ParliamentaryCandidateElectoralAreaVote.objects.all()
    for vote in parl_electoral_area_vote:
        vote.delete()


    constituency_vote = PresidentialCandidateConstituencyVote.objects.all()
    for vote in constituency_vote:
        vote.delete()

    parl_constituency_vote = ParliamentaryCandidateConstituencyVote.objects.all()
    for vote in parl_constituency_vote:
        vote.delete()

    regional_vote = PresidentialCandidateRegionalVote.objects.all()
    for vote in regional_vote:
        vote.delete()

    parl_regional_vote = ParliamentaryCandidateRegionalVote.objects.all()
    for vote in parl_regional_vote:
        vote.delete()



    presidential_votes = ElectionPresidentialCandidate.objects.all()
    for candidate in presidential_votes:
        candidate.total_votes = 0
        candidate.total_votes_percent = 0.0
        candidate.parliamentary_seat = 0
        candidate.save()

    parliamentary_votes = ElectionParliamentaryCandidate.objects.all()
    for candidate in parliamentary_votes:
        candidate.total_votes = 0
        candidate.total_votes_percent = 0.0
        candidate.won = False
        candidate.save()


    ############################


    polling_station = PollingStation.objects.all()
    for polling in polling_station:
        polling.election_year = "2024"
        polling.parliamentary_submitted = False
        polling.presidential_submitted = False
        polling.save()


    electoral = ElectoralArea.objects.all()
    for elect in electoral:
        elect.election_year = "2024"

        elect.parliamentary_submitted = False
        elect.presidential_submitted = False
        elect.save()


    constituency = Constituency.objects.all()
    for cons in constituency:
        cons.election_year = "2024"
        cons.parliamentary_submitted = False
        cons.presidential_submitted = False
        cons.save()

    regions = Region.objects.all()
    for region in regions:
        region.election_year = "2024"
        region.parliamentary_submitted = False
        region.presidential_submitted = False
        region.save()


    payload['message'] = "Successful"
    payload['data'] = data

    return Response(payload, status=status.HTTP_200_OK)
