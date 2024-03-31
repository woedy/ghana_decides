from django.db import models
from django.conf import settings


User = settings.AUTH_USER_MODEL

class Room(models.Model):
    callers = models.ManyToManyField(User, null=True, blank=True, related_name='room_callers')



class CallerCandidate(models.Model):
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name="caller_candidates")
    candidate = models.TextField(null=True, blank=True)
    sdp_m_line_index = models.IntegerField(null=True, blank=True)
    sdp_mid = models.CharField(max_length=1000, null=True, blank=True)


class CalleeCandidate(models.Model):
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name="callee_candidates")
    candidate = models.TextField(null=True, blank=True)
    sdp_m_line_index = models.IntegerField(null=True, blank=True)
    sdp_mid = models.CharField(max_length=1000, null=True, blank=True)



class Offer(models.Model):
    room = models.OneToOneField(Room, on_delete=models.CASCADE, related_name="offer")
    sdp = models.TextField(null=True, blank=True)
    type = models.CharField(max_length=1000, null=True, blank=True)



class Answer(models.Model):
    room = models.OneToOneField(Room, on_delete=models.CASCADE, related_name="answer")
    sdp = models.TextField(null=True, blank=True)
    type = models.CharField(max_length=1000, null=True, blank=True)




