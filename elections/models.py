from django.db import models

from candidates.models import PresidentialCandidate, ParliamentaryCandidate
from regions.models import Constituency


class PresidentialConstituencyVote(models.Model):
    candidate = models.ForeignKey(PresidentialCandidate, on_delete=models.CASCADE, related_name='election_prez_candidate')

    constituency = models.ForeignKey(Constituency, on_delete=models.CASCADE, related_name='presidential_constituency')

    total_votes = models.IntegerField(default=0)
    total_votes_percent = models.IntegerField(default=0)
    parliamentary_seat = models.IntegerField(default=0)


class ParliamentaryElection(models.Model):
    candidate = models.ForeignKey(ParliamentaryCandidate, on_delete=models.CASCADE, related_name='election_parl_candidate')

    constituency = models.ForeignKey(Constituency, on_delete=models.CASCADE, related_name='parliamentary_constituency')

    total_votes = models.IntegerField(default=0)
    total_votes_percent = models.IntegerField(default=0)
    parliamentary_seat = models.IntegerField(default=0)





