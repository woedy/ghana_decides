from rest_framework import serializers

from regions.models import Region, Constituency, Zone, PollingStation


class PollingStationSerializer(serializers.ModelSerializer):

    class Meta:
        model = PollingStation
        fields = [
            'polling_station_id',
            'polling_station_name',
        ]

class ZoneSerializer(serializers.ModelSerializer):

    class Meta:
        model = Zone
        fields = [
            'zone_id',
            'zone_name',
        ]


class ConstituencyZoneSerializer(serializers.ModelSerializer):

    class Meta:
        model = Zone
        fields = [
            'zone_id',
            'zone_name',
        ]


class ConstituencyRegionSerializer(serializers.ModelSerializer):

    class Meta:
        model = Region
        fields = [
            'region_id',
            'region_name',
        ]
class ConstituencyDetailSerializer(serializers.ModelSerializer):
    region = ConstituencyRegionSerializer(many=False)
    class Meta:
        model = Constituency
        fields = [
            'constituency_id',
            'constituency_name',
            'region'
        ]

class AllConstituenciesSerializer(serializers.ModelSerializer):

    class Meta:
        model = Constituency
        fields = [
            'constituency_id',
            'constituency_name'
        ]


class RegionalConstituenciesSerializer(serializers.ModelSerializer):

    class Meta:
        model = Constituency
        fields = [
            'constituency_id',
            'constituency_name'
        ]

class RegionDetailSerializer(serializers.ModelSerializer):
    region_constituencies = RegionalConstituenciesSerializer(many=True)

    class Meta:
        model = Region
        fields = [
            'region_id',
            'region_name',
            'map_image',
            'initials',
            'region_constituencies'

        ]

class AllRegionsSerializer(serializers.ModelSerializer):

    class Meta:
        model = Region
        fields = [
            'region_id',
            'region_name',
        ]
