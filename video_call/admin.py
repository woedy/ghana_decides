from django.contrib import admin

# Register your models here.
from video_call.models import Room, Answer, Offer, CalleeCandidate, CallerCandidate

admin.site.register(Room)
admin.site.register(CallerCandidate)
admin.site.register(CalleeCandidate)
admin.site.register(Offer)
admin.site.register(Answer)
