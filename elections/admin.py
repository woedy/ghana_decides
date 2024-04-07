from django.contrib import admin

from elections.models import Election, ElectionPresidentialCandidate, \
    PresidentialCandidateRegionalVote, PresidentialCandidateConstituencyVote, PresidentialCandidateElectoralAreaVote, \
    PresidentialCandidatePollingStationVote, ParliamentaryCandidatePollingStationVote, \
    ParliamentaryCandidateElectoralAreaVote, ParliamentaryCandidateConstituencyVote, ParliamentaryCandidateRegionalVote, \
    ElectionParliamentaryCandidate

admin.site.register(Election)
admin.site.register(ElectionPresidentialCandidate)
admin.site.register(PresidentialCandidateRegionalVote)
admin.site.register(PresidentialCandidateConstituencyVote)
admin.site.register(PresidentialCandidateElectoralAreaVote)
admin.site.register(PresidentialCandidatePollingStationVote)



admin.site.register(ElectionParliamentaryCandidate)
admin.site.register(ParliamentaryCandidateRegionalVote)
admin.site.register(ParliamentaryCandidateConstituencyVote)
admin.site.register(ParliamentaryCandidateElectoralAreaVote)
admin.site.register(ParliamentaryCandidatePollingStationVote)

