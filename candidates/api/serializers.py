from rest_framework import serializers

from candidates.models import ParliamentaryCandidate, PresidentialCandidate
from candidates.models import Party
from regions.api.serializers import AllConstituenciesSerializer


class CandidatePartySerializer(serializers.ModelSerializer):

    class Meta:
        model = Party
        fields = [
            'party_id',
            'party_full_name',
            'party_initial',
            'party_logo',
            'party_color',
        ]


class ParliamentaryCandidateDetailSerializer(serializers.ModelSerializer):
    party = CandidatePartySerializer(many=False)
    constituency = AllConstituenciesSerializer(many=False)

    class Meta:
        model = ParliamentaryCandidate
        fields = [
            'parl_can_id',
            'constituency',
            'party',
            'first_name',
            'last_name',
            'middle_name',
            'photo',
            'gender',
            'candidate_type',
        ]

class AllParliamentaryCandidateSerializer(serializers.ModelSerializer):
    party = CandidatePartySerializer(many=False)
    constituency = AllConstituenciesSerializer(many=False)

    class Meta:
        model = ParliamentaryCandidate
        fields = [
            'parl_can_id',
            'constituency',
            'first_name',
            'last_name',
            'middle_name',
            'photo',
            'party'

        ]



class PresidentialCandidateDetailSerializer(serializers.ModelSerializer):
    party = CandidatePartySerializer(many=False)

    class Meta:
        model = PresidentialCandidate
        fields = [
            'prez_can_id',
            'first_name',
            'last_name',
            'middle_name',
            'photo',
            'gender',
            'candidate_type',
            'party',
        ]


class AllPresidentialCandidateSerializer(serializers.ModelSerializer):
    party = CandidatePartySerializer(many=False)

    class Meta:
        model = PresidentialCandidate
        fields = [
            'prez_can_id',
            'first_name',
            'last_name',
            'middle_name',
            'photo',
            'party'

        ]




class PartyDetailSerializer(serializers.ModelSerializer):

    class Meta:
        model = Party
        fields = [
            'party_id',
            'party_full_name',
            'party_initial',
            'year_formed',
            'party_logo',
            'party_color',

        ]

class AllPartiesSerializer(serializers.ModelSerializer):

    class Meta:
        model = Party
        fields = [
            'party_id',
            'party_full_name',
            'party_initial',
            'party_logo',
            'party_color',

        ]
