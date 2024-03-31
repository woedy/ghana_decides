from django.contrib import admin

from elections.models import Election, ElectionPresidentialCandidate, \
    PresidentialCandidateRegionalScore, PresidentialCandidateConstituencyScore, PresidentialCandidateZonalScore, \
    PresidentialCandidatePollingStationScore, ParliamentaryCandidatePollingStationScore, \
    ParliamentaryCandidateZonalScore, ParliamentaryCandidateConstituencyScore, ParliamentaryCandidateRegionalScore, \
    ElectionParliamentaryCandidate

admin.site.register(Election)
admin.site.register(ElectionPresidentialCandidate)
admin.site.register(PresidentialCandidateRegionalScore)
admin.site.register(PresidentialCandidateConstituencyScore)
admin.site.register(PresidentialCandidateZonalScore)
admin.site.register(PresidentialCandidatePollingStationScore)



admin.site.register(ElectionParliamentaryCandidate)
admin.site.register(ParliamentaryCandidateRegionalScore)
admin.site.register(ParliamentaryCandidateConstituencyScore)
admin.site.register(ParliamentaryCandidateZonalScore)
admin.site.register(ParliamentaryCandidatePollingStationScore)

