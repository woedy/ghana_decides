from rest_framework import serializers

from regions.models import ConstituencyVotersParticipation, ElectoralVotersParticipation, PollingStationVotersParticipation, Region, Constituency, ElectoralArea, PollingStation, RegionalVotersParticipation


class PollingStationSerializer(serializers.ModelSerializer):

    class Meta:
        model = PollingStation
        fields = [
            'polling_station_id',
            'polling_station_name',
        ]

class ElectoralAreaSerializer(serializers.ModelSerializer):

    class Meta:
        model = ElectoralArea
        fields = [
            'electoral_area_id',
            'electoral_area_name',
        ]


class ConstituencyElectoralAreaSerializer(serializers.ModelSerializer):

    class Meta:
        model = ElectoralArea
        fields = [
            'electoral_area_id',
            'electoral_area_name',
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


class AllElectoralAreaSerializer(serializers.ModelSerializer):

    class Meta:
        model = ElectoralArea
        fields = [
            'electoral_area_id',
            'electoral_area_name'
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
                       'initials',
            'capital',
            'election_year'
     
        

        ]



class AllPollingStationVotersParticipationSerializer(serializers.ModelSerializer):
    polling_station_name = serializers.SerializerMethodField()

    class Meta:
        model = PollingStationVotersParticipation
        fields = "__all__"

    def get_polling_station_name(self, obj):
        polling_station_name = obj.polling_station.polling_station_name
        return polling_station_name



class AllElectoralVotersParticipationSerializer(serializers.ModelSerializer):
    electoral_area_name = serializers.SerializerMethodField()

    class Meta:
        model = ElectoralVotersParticipation
        fields = "__all__"

    def get_electoral_area_name(self, obj):
        electoral_area_name = obj.electoral_area.electoral_area_name
        return electoral_area_name






class AllConstituencyVotersParticipationSerializer(serializers.ModelSerializer):
    constituency_name = serializers.SerializerMethodField()

    class Meta:
        model = ConstituencyVotersParticipation
        fields = "__all__"

    def get_constituency_name(self, obj):
        constituency_name = obj.constituency.constituency_name
        return constituency_name




class AllRegionalVotersParticipationSerializer(serializers.ModelSerializer):
    region_name = serializers.SerializerMethodField()

    class Meta:
        model = RegionalVotersParticipation
        fields = "__all__"

    def get_region_name(self, obj):
        region_name = obj.region.region_name
        return region_name


