from django.contrib import admin

from regions.models import Region, Constituency, PollingStation, ElectoralArea, RegionalVotersParticipation, \
    ConstituencyVotersParticipation, ElectoralVotersParticipation, PollingStationVotersParticipation

admin.site.register(Region)
admin.site.register(Constituency)
admin.site.register(ElectoralArea)
admin.site.register(PollingStation)

admin.site.register(RegionalVotersParticipation)
admin.site.register(ConstituencyVotersParticipation)
admin.site.register(ElectoralVotersParticipation)
admin.site.register(PollingStationVotersParticipation)
