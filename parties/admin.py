from django.contrib import admin

from candidates.models import Party, PartyFlagBearer, PartyStandingCandidate, PartyPresidentailPrimary, \
    PartyParliamentaryPrimary

admin.site.register(Party)
admin.site.register(PartyFlagBearer)
admin.site.register(PartyStandingCandidate)
admin.site.register(PartyPresidentailPrimary)
admin.site.register(PartyParliamentaryPrimary)
