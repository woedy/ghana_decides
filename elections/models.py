from django.db import models
from django.db.models.signals import pre_save

from candidates.models import PresidentialCandidate, ParliamentaryCandidate
from ghana_decides_proj.utils import unique_election_id_generator, unique_election_prez_id_generator, \
    unique_election_parl_id_generator
from regions.models import Constituency, Region, ElectoralArea, PollingStation


class ElectionPresidentialCandidate(models.Model):
    election_prez_id = models.CharField(max_length=255, unique=True, blank=True, null=True)
    election = models.ForeignKey("Election", on_delete=models.CASCADE, related_name='prez_candidate_election_year')

    candidate = models.ForeignKey(PresidentialCandidate, on_delete=models.CASCADE, related_name='presidential_candidates')

    ballot_number = models.IntegerField(null=True, blank=True)

    total_votes = models.IntegerField(default=0)
    total_votes_percent = models.DecimalField(default=0.0, max_digits=5, decimal_places=1, null=True, blank=True)
    parliamentary_seat = models.IntegerField(default=0)


    active = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


def pre_save_election_prez_id_receiver(sender, instance, *args, **kwargs):
    if not instance.election_prez_id:
        instance.election_prez_id = unique_election_prez_id_generator(instance)

pre_save.connect(pre_save_election_prez_id_receiver, sender=ElectionPresidentialCandidate)




class ElectionParliamentaryCandidate(models.Model):
    election_parl_id = models.CharField(max_length=255, unique=True, blank=True, null=True)

    candidate = models.ForeignKey(ParliamentaryCandidate, on_delete=models.CASCADE, related_name='parliamentary_candidates')
    election = models.ForeignKey("Election", on_delete=models.CASCADE, related_name='parl_candidate_election_year')

    constituency = models.ForeignKey(Constituency, blank=True, null=True, on_delete=models.SET_NULL, related_name='election_parliamentary_can_constituency')

    ballot_number = models.IntegerField(null=True, blank=True)

    won = models.BooleanField(default=False)

    total_votes = models.IntegerField(default=0)
    total_votes_percent = models.DecimalField(default=0.0, max_digits=5, decimal_places=1, null=True, blank=True)


    active = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

def pre_save_election_parl_id_receiver(sender, instance, *args, **kwargs):
    if not instance.election_parl_id:
        instance.election_parl_id = unique_election_parl_id_generator(instance)

pre_save.connect(pre_save_election_parl_id_receiver, sender=ElectionParliamentaryCandidate)






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

class PresidentialCandidateRegionalVote(models.Model):
    election = models.ForeignKey(Election, on_delete=models.SET_NULL, null=True, related_name='presidential_candidates_regional')
    prez_candidate = models.ForeignKey(ElectionPresidentialCandidate, on_delete=models.CASCADE, related_name='presidential_candidate')
    region = models.ForeignKey(Region, on_delete=models.SET_NULL, null=True, related_name='presidential_candidate_region')

    total_votes = models.IntegerField(default=0)
    position = models.IntegerField(default=0)
    won = models.BooleanField(default=False)
    total_votes_percent = models.DecimalField(default=0.0, max_digits=5, decimal_places=1, null=True, blank=True)
    parliamentary_seat = models.IntegerField(default=0)

    active = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class PresidentialCandidateConstituencyVote(models.Model):
    election = models.ForeignKey(Election, on_delete=models.SET_NULL, null=True, related_name='presidential_candidates_constituency')
    prez_candidate = models.ForeignKey(ElectionPresidentialCandidate, on_delete=models.CASCADE, related_name='presidential_candidate_consti_vote')
    constituency = models.ForeignKey(Constituency, on_delete=models.SET_NULL, null=True, related_name='presidential_candidate_constituency')

    total_votes = models.IntegerField(default=0)
    total_votes_percent = models.DecimalField(default=0.0, max_digits=5, decimal_places=1, null=True, blank=True)
    won = models.BooleanField(default=False)
    position = models.IntegerField(default=0)

    active = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class PresidentialCandidateElectoralAreaVote(models.Model):
    election = models.ForeignKey(Election, on_delete=models.SET_NULL, null=True, related_name='presidential_candidates_electoral_area')
    prez_candidate = models.ForeignKey(ElectionPresidentialCandidate, on_delete=models.CASCADE, related_name='presidential_candidate_electoral_area_vote')
    electoral_area = models.ForeignKey(ElectoralArea, on_delete=models.SET_NULL, null=True, related_name='presidential_candidate_electoral_area')

    total_votes = models.IntegerField(default=0)
    total_votes_percent = models.DecimalField(default=0.0, max_digits=5, decimal_places=1, null=True, blank=True)
    won = models.BooleanField(default=False)
    position = models.IntegerField(default=0)

    active = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class PresidentialCandidatePollingStationVote(models.Model):
    election = models.ForeignKey(Election, on_delete=models.SET_NULL, null=True, related_name='presidential_candidates_polling_station')
    prez_candidate = models.ForeignKey(ElectionPresidentialCandidate, on_delete=models.CASCADE, related_name='presidential_candidate_polling_station_vote')
    polling_station = models.ForeignKey(PollingStation, on_delete=models.SET_NULL, null=True, related_name='presidential_candidate_polling_station')

    total_votes = models.IntegerField(default=0)
    total_votes_percent = models.DecimalField(default=0.0, max_digits=5, decimal_places=1, null=True, blank=True)
    won = models.BooleanField(default=False)
    position = models.IntegerField(default=0)

    active = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


################### PARLIAMENTARY ##################

class ParliamentaryCandidateRegionalVote(models.Model):
    election = models.ForeignKey(Election, on_delete=models.SET_NULL, null=True, related_name='parliamentary_candidates_regional')
    parl_candidate = models.ForeignKey(ElectionParliamentaryCandidate, on_delete=models.CASCADE, related_name='parliamentary_candidate')
    region = models.ForeignKey(Region, on_delete=models.SET_NULL, null=True, related_name='parliamentary_candidate_region')
    won = models.BooleanField(default=False)

    total_votes = models.IntegerField(default=0)
    position = models.IntegerField(default=0)
    total_votes_percent = models.DecimalField(default=0.0, max_digits=5, decimal_places=1, null=True, blank=True)

    active = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class ParliamentaryCandidateConstituencyVote(models.Model):
    election = models.ForeignKey(Election, on_delete=models.SET_NULL, null=True, related_name='parliamentary_candidates_constituency')
    parl_candidate = models.ForeignKey(ElectionParliamentaryCandidate, on_delete=models.CASCADE, related_name='parliamentary_candidate_consti_vote')
    constituency = models.ForeignKey(Constituency, on_delete=models.SET_NULL, null=True, related_name='parliamentary_candidate_constituency')

    total_votes = models.IntegerField(default=0)
    total_votes_percent = models.DecimalField(default=0.0, max_digits=5, decimal_places=1, null=True, blank=True)
    won = models.BooleanField(default=False)
    position = models.IntegerField(default=0)

    active = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class ParliamentaryCandidateElectoralAreaVote(models.Model):
    election = models.ForeignKey(Election, on_delete=models.SET_NULL, null=True, related_name='parliamentary_candidates_electoral_area')
    parl_candidate = models.ForeignKey(ElectionParliamentaryCandidate, on_delete=models.CASCADE, related_name='parliamentary_candidate_electoral_area_vote')
    electoral_area = models.ForeignKey(ElectoralArea, on_delete=models.SET_NULL, null=True, related_name='parliamentary_candidate_electoral_area')

    total_votes = models.IntegerField(default=0)
    total_votes_percent = models.DecimalField(default=0.0, max_digits=5, decimal_places=1, null=True, blank=True)
    won = models.BooleanField(default=False)
    position = models.IntegerField(default=0)

    active = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class ParliamentaryCandidatePollingStationVote(models.Model):
    election = models.ForeignKey(Election, on_delete=models.SET_NULL, null=True, related_name='parliamentary_candidates_polling_station')
    parl_candidate = models.ForeignKey(ElectionParliamentaryCandidate, on_delete=models.CASCADE, related_name='parliamentary_candidate_polling_station_vote')
    polling_station = models.ForeignKey(PollingStation, on_delete=models.SET_NULL, null=True, related_name='parliamentary_candidate_polling_station')

    total_votes = models.IntegerField(default=0)
    total_votes_percent = models.DecimalField(default=0.0, max_digits=5, decimal_places=1, null=True, blank=True)
    won = models.BooleanField(default=False)
    position = models.IntegerField(default=0)

    active = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
