from rest_framework import serializers

from candidates.api.serializers import AllPresidentialCandidateSerializer, AllParliamentaryCandidateSerializer
from elections.models import Election, ElectionPresidentialCandidate, PresidentialCandidateElectoralAreaVote, \
    PresidentialCandidateRegionalVote, PresidentialCandidateConstituencyVote, ElectionParliamentaryCandidate, \
    PresidentialCandidatePollingStationVote, ParliamentaryCandidatePollingStationVote
from regions.api.serializers import AllElectoralAreaSerializer, AllRegionsSerializer, AllConstituenciesSerializer
from regions.models import PollingStation


class ElectionParliamentaryCandidateSerializer(serializers.ModelSerializer):
    candidate = AllPresidentialCandidateSerializer(many=False)
    class Meta:
        model = ElectionParliamentaryCandidate
        fields = [
            'election_parl_id',
            'candidate',
            'total_votes',
            'total_votes_percent',
            'created_at',
        ]




class ElectionPresidentialCandidateSerializer(serializers.ModelSerializer):
    candidate = AllPresidentialCandidateSerializer(many=False)
    class Meta:
        model = ElectionPresidentialCandidate
        fields = [
            'election_prez_id',
            'candidate',
              'ballot_number',
            'total_votes',
            'total_votes_percent',
            'parliamentary_seat',
            'created_at',
        ]



class PresidentialCandidateRegionalVoteSerializer(serializers.ModelSerializer):
    region = AllRegionsSerializer(many=False)
    prez_candidate = ElectionPresidentialCandidateSerializer(many=False)
    class Meta:
        model = PresidentialCandidateRegionalVote
        fields = [
            'prez_candidate',
            'region',
            'total_votes',
            'total_votes_percent',
            'parliamentary_seat',
        ]

class PresidentialCandidateConstituencyVoteSerializer(serializers.ModelSerializer):
    constituency = AllConstituenciesSerializer(many=False)
    prez_candidate = ElectionPresidentialCandidateSerializer(many=False)
    class Meta:
        model = PresidentialCandidateConstituencyVote
        fields = [
            'prez_candidate',
            'constituency',
            'total_votes',
            'total_votes_percent',
            'won',
        ]



class PresidentialCandidateElectoralAreaVoteSerializer(serializers.ModelSerializer):
    electoral_area = AllElectoralAreaSerializer(many=False)
    prez_candidate = ElectionPresidentialCandidateSerializer(many=False)
    class Meta:
        model = PresidentialCandidateElectoralAreaVote
        fields = [
            'prez_candidate',
            'electoral_area',
            'total_votes',
            'total_votes_percent',
            'won',
        ]


class ElectionDetailSerializer(serializers.ModelSerializer):
    winner = ElectionPresidentialCandidateSerializer(many=False)
    first_runner_up = ElectionPresidentialCandidateSerializer(many=False)
    second_runner_up = ElectionPresidentialCandidateSerializer(many=False)
    presidential_candidates_regional = PresidentialCandidateRegionalVoteSerializer(many=True)
    presidential_candidates_constituency = PresidentialCandidateConstituencyVoteSerializer(many=True)
    class Meta:
        model = Election
        fields = [
            'election_id',
            'year',
            'winner',
            'first_runner_up',
            'second_runner_up',
            'presidential_candidates_regional',
            'presidential_candidates_constituency'

        ]


class AllElectionSerializer(serializers.ModelSerializer):

    class Meta:
        model = Election
        fields = [
            'election_id',
            'year',
            'winner',


        ]






class PollingStationVoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = PollingStation
        fields = [
            'polling_station_id',
            'polling_station_name',
        ]



class ParliamentaryCandidatePollingStationVoteSerializer(serializers.ModelSerializer):
    polling_station = PollingStationVoteSerializer(many=False)
    candidate = ElectionParliamentaryCandidateSerializer(source='parl_candidate')  # Rename prez_candidate to candidate

    class Meta:
        model = ParliamentaryCandidatePollingStationVote
        fields = [
            'election',
            'candidate',
            'polling_station',
            'total_votes',
            'total_votes_percent',
            'created_at',
        ]



class PresidentialCandidatePollingStationVoteSerializer(serializers.ModelSerializer):
    polling_station = PollingStationVoteSerializer(many=False)
    candidate = ElectionPresidentialCandidateSerializer(source='prez_candidate')  # Rename prez_candidate to candidate

    class Meta:
        model = PresidentialCandidatePollingStationVote
        fields = [
            'election',
            'candidate',  # Use the renamed field here
            'polling_station',
            'total_votes',
            'total_votes_percent',
            'created_at',
        ]

class ElectionParliamentaryCandidateSerializer(serializers.ModelSerializer):
    candidate = AllParliamentaryCandidateSerializer(many=False)
    class Meta:
        model = ElectionParliamentaryCandidate
        fields = [
            'election_parl_id',
            'candidate',
            'ballot_number',
            'total_votes',
            'total_votes_percent',
            'created_at',
        ]

