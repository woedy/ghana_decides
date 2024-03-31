from django.contrib import admin

from regions.models import Region, Constituency, PollingStation, Zone, RegionalVotersParticipation, \
    ConstituencyVotersParticipation, ZonalVotersParticipation, PollingStationVotersParticipation

admin.site.register(Region)
admin.site.register(Constituency)
admin.site.register(Zone)
admin.site.register(PollingStation)

admin.site.register(RegionalVotersParticipation)
admin.site.register(ConstituencyVotersParticipation)
admin.site.register(ZonalVotersParticipation)
admin.site.register(PollingStationVotersParticipation)
