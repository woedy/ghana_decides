from django.db import models

from candidates.models import PresidentialCandidate, ParliamentaryCandidate
from regions.models import Constituency


class History(models.Model):
    constituency = models.ForeignKey(Constituency, on_delete=models.CASCADE, related_name='constituencies_history')

    prez_elect = models.ForeignKey(PresidentialCandidate, on_delete=models.CASCADE, related_name='presidential_candidate_elect')
    mp_elect = models.ForeignKey(ParliamentaryCandidate, on_delete=models.CASCADE, related_name='parliamentary_candidate_elect')

    year = models.CharField(max_length=255, blank=True, null=True)

    registered_voters = models.IntegerField(default=0)
    total_votes = models.IntegerField(default=0)


class HistoryPresidentialContestant(models.Model):
    constituency = models.ForeignKey(Constituency, on_delete=models.CASCADE, related_name='constituencies_prez_history')
    contestant = models.ForeignKey(PresidentialCandidate, on_delete=models.CASCADE, related_name='history_prez_contestant')

    total_votes = models.IntegerField(default=0)
    total_votes_percent = models.IntegerField(default=0)



class HistoryParliamentaryContestant(models.Model):
    constituency = models.ForeignKey(Constituency, on_delete=models.CASCADE, related_name='constituencies_parl_history')
    contestant = models.ForeignKey(ParliamentaryCandidate, on_delete=models.CASCADE, related_name='history_parl_contestant')

    total_votes = models.IntegerField(default=0)
    total_votes_percent = models.IntegerField(default=0)






