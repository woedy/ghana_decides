from django.contrib import admin

from elections.models import ParliamentaryElection, PresidentialConstituencyVote

admin.site.register(PresidentialConstituencyVote)
admin.site.register(ParliamentaryElection)
