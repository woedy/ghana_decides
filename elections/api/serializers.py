from rest_framework import serializers

from candidates.api.serializers import AllPresidentialCandidateSerializer
from elections.models import Election, ElectionPresidentialCandidate, \
    PresidentialCandidateRegionalScore, PresidentialCandidateConstituencyScore
from regions.api.serializers import AllRegionsSerializer, AllConstituenciesSerializer


class ElectionHistoryPresidentialCandidateSerializer(serializers.ModelSerializer):
    candidate = AllPresidentialCandidateSerializer(many=False)
    class Meta:
        model = ElectionPresidentialCandidate
        fields = [
            'candidate',
            'total_votes_percent',
            'parliamentary_seat',
        ]



class PresidentialCandidateRegionalScoreSerializer(serializers.ModelSerializer):
    region = AllRegionsSerializer(many=False)
    hist_candidate = ElectionHistoryPresidentialCandidateSerializer(many=False)
    class Meta:
        model = PresidentialCandidateRegionalScore
        fields = [
            'prez_candidate',
            'region',
            'total_votes',
            'total_votes_percent',
            'parliamentary_seat',
        ]

class PresidentialCandidateConstituencyScoreSerializer(serializers.ModelSerializer):
    constituency = AllConstituenciesSerializer(many=False)
    prez_candidate = ElectionHistoryPresidentialCandidateSerializer(many=False)
    class Meta:
        model = PresidentialCandidateConstituencyScore
        fields = [
            'prez_candidate',
            'constituency',
            'total_votes',
            'total_votes_percent',
            'won',
        ]


class ElectionDetailSerializer(serializers.ModelSerializer):
    winner = ElectionHistoryPresidentialCandidateSerializer(many=False)
    first_runner_up = ElectionHistoryPresidentialCandidateSerializer(many=False)
    second_runner_up = ElectionHistoryPresidentialCandidateSerializer(many=False)
    presidential_candidates_regional = PresidentialCandidateRegionalScoreSerializer(many=True)
    presidential_candidates_constituency = PresidentialCandidateConstituencyScoreSerializer(many=True)
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
