from django.contrib import admin

from candidates.models import ParliamentaryCandidate, PresidentialCandidate

# Register your models here.
admin.site.register(PresidentialCandidate)
admin.site.register(ParliamentaryCandidate)
