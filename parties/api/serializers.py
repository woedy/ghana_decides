from rest_framework import serializers

from parties.models import Party
from regions.models import Region, Constituency


class PartyDetailSerializer(serializers.ModelSerializer):

    class Meta:
        model = Party
        fields = [
            'party_id',
            'party_full_name',
            'party_initial',
            'year_formed',
            'party_logo',
        ]

class AllPartiesSerializer(serializers.ModelSerializer):

    class Meta:
        model = Party
        fields = [
            'party_id',
            'party_full_name',
            'party_initial',
            'party_logo',
        ]
