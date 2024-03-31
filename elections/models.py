from django.db import models
from django.db.models.signals import pre_save

from candidates.models import PresidentialCandidate, ParliamentaryCandidate
from ghana_decides_proj.utils import unique_election_id_generator
from regions.models import Constituency, Region, Zone


class ElectionPresidentialCandidate(models.Model):
    candidate = models.ForeignKey(PresidentialCandidate, on_delete=models.CASCADE, related_name='presidential_candidates')

    total_votes = models.IntegerField(default=0)
    total_votes_percent = models.DecimalField(default=0.0, max_digits=5, decimal_places=1, null=True, blank=True)
    parliamentary_seat = models.IntegerField(default=0)



class ElectionParliamentaryCandidate(models.Model):
    candidate = models.ForeignKey(ParliamentaryCandidate, on_delete=models.CASCADE, related_name='parliamentary_candidates')

    total_votes = models.IntegerField(default=0)
    total_votes_percent = models.DecimalField(default=0.0, max_digits=5, decimal_places=1, null=True, blank=True)







YEAR_CHOICES = (
    ('1992', '1992'),
    ('1996', '1996'),
    ('2000', '2000'),
    ('2000R', '2000R'),
    ('2004', '2004'),
    ('2008', '2008'),
    ('2008R', '2008R'),
    ('2012', '2012'),
    ('2016', '2016'),
    ('2020', '2020'),
    ('2024', '2024'),

)


class Election(models.Model):
    election_id = models.CharField(max_length=255, blank=True, null=True)
    year = models.CharField(max_length=255, choices=YEAR_CHOICES, blank=True, null=True)
    winner = models.ForeignKey(ElectionPresidentialCandidate, on_delete=models.SET_NULL, null=True, blank=True, related_name='election_presidential_winner')
    first_runner_up = models.ForeignKey(ElectionPresidentialCandidate, on_delete=models.SET_NULL, null=True, blank=True, related_name='election_presidential_first_runner_up')
    second_runner_up = models.ForeignKey(ElectionPresidentialCandidate, on_delete=models.SET_NULL, null=True, blank=True, related_name='election_presidential_second_runner_up')

    def __str__(self):
        return f"{self.year}"


def pre_save_election_id_receiver(sender, instance, *args, **kwargs):
    if not instance.election_id:
        instance.election_id = unique_election_id_generator(instance)

pre_save.connect(pre_save_election_id_receiver, sender=Election)



################### PRESIDENTIAL ##################

class PresidentialCandidateRegionalScore(models.Model):
    election = models.ForeignKey(Election, on_delete=models.SET_NULL, null=True, related_name='presidential_candidates_regional')
    prez_candidate = models.ForeignKey(ElectionPresidentialCandidate, on_delete=models.CASCADE, related_name='presidential_candidate')
    region = models.ForeignKey(Region, on_delete=models.SET_NULL, null=True, related_name='presidential_candidate_region')

    total_votes = models.IntegerField(default=0)
    position = models.IntegerField(default=0)
    won = models.BooleanField(default=False)
    total_votes_percent = models.DecimalField(default=0.0, max_digits=5, decimal_places=1, null=True, blank=True)
    parliamentary_seat = models.IntegerField(default=0)


class PresidentialCandidateConstituencyScore(models.Model):
    election = models.ForeignKey(Election, on_delete=models.SET_NULL, null=True, related_name='presidential_candidates_constituency')
    prez_candidate = models.ForeignKey(ElectionPresidentialCandidate, on_delete=models.CASCADE, related_name='presidential_candidate_consti_score')
    constituency = models.ForeignKey(Constituency, on_delete=models.SET_NULL, null=True, related_name='presidential_candidate_constituency')

    total_votes = models.IntegerField(default=0)
    total_votes_percent = models.DecimalField(default=0.0, max_digits=5, decimal_places=1, null=True, blank=True)
    won = models.BooleanField(default=False)
    position = models.IntegerField(default=0)





class PresidentialCandidateZonalScore(models.Model):
    election = models.ForeignKey(Election, on_delete=models.SET_NULL, null=True, related_name='presidential_candidates_zone')
    prez_candidate = models.ForeignKey(ElectionPresidentialCandidate, on_delete=models.CASCADE, related_name='presidential_candidate_zone_score')
    zone = models.ForeignKey(Zone, on_delete=models.SET_NULL, null=True, related_name='presidential_candidate_zone')

    total_votes = models.IntegerField(default=0)
    total_votes_percent = models.DecimalField(default=0.0, max_digits=5, decimal_places=1, null=True, blank=True)
    won = models.BooleanField(default=False)
    position = models.IntegerField(default=0)



class PresidentialCandidatePollingStationScore(models.Model):
    election = models.ForeignKey(Election, on_delete=models.SET_NULL, null=True, related_name='presidential_candidates_polling_station')
    prez_candidate = models.ForeignKey(ElectionPresidentialCandidate, on_delete=models.CASCADE, related_name='presidential_candidate_polling_station_score')
    zone = models.ForeignKey(Zone, on_delete=models.SET_NULL, null=True, related_name='presidential_candidate_polling_station')

    total_votes = models.IntegerField(default=0)
    total_votes_percent = models.DecimalField(default=0.0, max_digits=5, decimal_places=1, null=True, blank=True)
    won = models.BooleanField(default=False)
    position = models.IntegerField(default=0)





################### PARLIAMENTARY ##################

class ParliamentaryCandidateRegionalScore(models.Model):
    election = models.ForeignKey(Election, on_delete=models.SET_NULL, null=True, related_name='parliamentary_candidates_regional')
    parlia_candidate = models.ForeignKey(ElectionParliamentaryCandidate, on_delete=models.CASCADE, related_name='parliamentary_candidate')
    region = models.ForeignKey(Region, on_delete=models.SET_NULL, null=True, related_name='parliamentary_candidate_region')
    won = models.BooleanField(default=False)

    total_votes = models.IntegerField(default=0)
    position = models.IntegerField(default=0)
    total_votes_percent = models.DecimalField(default=0.0, max_digits=5, decimal_places=1, null=True, blank=True)



class ParliamentaryCandidateConstituencyScore(models.Model):
    election = models.ForeignKey(Election, on_delete=models.SET_NULL, null=True, related_name='parliamentary_candidates_constituency')
    parlia_candidate = models.ForeignKey(ElectionParliamentaryCandidate, on_delete=models.CASCADE, related_name='parliamentary_candidate_consti_score')
    constituency = models.ForeignKey(Constituency, on_delete=models.SET_NULL, null=True, related_name='parliamentary_candidate_constituency')

    total_votes = models.IntegerField(default=0)
    total_votes_percent = models.DecimalField(default=0.0, max_digits=5, decimal_places=1, null=True, blank=True)
    won = models.BooleanField(default=False)
    position = models.IntegerField(default=0)


class ParliamentaryCandidateZonalScore(models.Model):
    election = models.ForeignKey(Election, on_delete=models.SET_NULL, null=True, related_name='parliamentary_candidates_zone')
    parlia_candidate = models.ForeignKey(ElectionParliamentaryCandidate, on_delete=models.CASCADE, related_name='parliamentary_candidate_zone_score')
    zone = models.ForeignKey(Zone, on_delete=models.SET_NULL, null=True, related_name='parliamentary_candidate_zone')

    total_votes = models.IntegerField(default=0)
    total_votes_percent = models.DecimalField(default=0.0, max_digits=5, decimal_places=1, null=True, blank=True)
    won = models.BooleanField(default=False)
    position = models.IntegerField(default=0)


class ParliamentaryCandidatePollingStationScore(models.Model):
    election = models.ForeignKey(Election, on_delete=models.SET_NULL, null=True, related_name='parliamentary_candidates_polling_station')
    parlia_candidate = models.ForeignKey(ElectionParliamentaryCandidate, on_delete=models.CASCADE, related_name='parliamentary_candidate_polling_station_score')
    zone = models.ForeignKey(Zone, on_delete=models.SET_NULL, null=True, related_name='parliamentary_candidate_polling_station')

    total_votes = models.IntegerField(default=0)
    total_votes_percent = models.DecimalField(default=0.0, max_digits=5, decimal_places=1, null=True, blank=True)
    won = models.BooleanField(default=False)
    position = models.IntegerField(default=0)
