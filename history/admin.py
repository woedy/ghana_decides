from django.contrib import admin

from history.models import History, HistoryPresidentialContestant, HistoryParliamentaryContestant

admin.site.register(History)
admin.site.register(HistoryPresidentialContestant)
admin.site.register(HistoryParliamentaryContestant)
