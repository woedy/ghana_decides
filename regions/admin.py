from django.contrib import admin

from regions.models import Region, Constituency, PollingStation, ElectoralArea, RegionalVotersParticipation, \
    ConstituencyVotersParticipation, ElectoralVotersParticipation, PollingStationVotersParticipation, \
    ElectoralAreaLayerCoordinate, PollingStationLayerCoordinate, ConstituencyLayerCoordinate, RegionLayerCoordinate

admin.site.register(Region)
admin.site.register(Constituency)
admin.site.register(ElectoralArea)
admin.site.register(PollingStation)

admin.site.register(RegionalVotersParticipation)
admin.site.register(ConstituencyVotersParticipation)
admin.site.register(ElectoralVotersParticipation)
admin.site.register(PollingStationVotersParticipation)

admin.site.register(RegionLayerCoordinate)
admin.site.register(ConstituencyLayerCoordinate)
admin.site.register(ElectoralAreaLayerCoordinate)
admin.site.register(PollingStationLayerCoordinate)
