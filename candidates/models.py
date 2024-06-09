import os
import random

from django.db import models
from django.db.models.signals import pre_save

from ghana_decides_proj.utils import unique_parl_can_id_generator, unique_prez_can_id_generator, \
    unique_party_id_generator
from regions.models import Constituency


def get_file_ext(filepath):
    base_name = os.path.basename(filepath)
    name, ext = os.path.splitext(base_name)
    return name, ext


def upload_prez_can_photo_path(instance, filename):
    new_filename = random.randint(1, 3910209312)
    name, ext = get_file_ext(filename)
    final_filename = '{new_filename}{ext}'.format(new_filename=new_filename, ext=ext)
    return "prez_can/{new_filename}/{final_filename}".format(
        new_filename=new_filename,
        final_filename=final_filename
    )



def upload_parl_can_photo_path(instance, filename):
    new_filename = random.randint(1, 3910209312)
    name, ext = get_file_ext(filename)
    final_filename = '{new_filename}{ext}'.format(new_filename=new_filename, ext=ext)
    return "parl_can/{new_filename}/{final_filename}".format(
        new_filename=new_filename,
        final_filename=final_filename
    )






GENDER_CHOICES = (
    ('Male', 'Male'),
    ('Female', 'Female'),

)


CANDIDATE_TYPE = (
    ('Independent', 'Independent'),
    ('Main Stream', 'Main Stream'),

)

class PresidentialCandidate(models.Model):
    prez_can_id = models.CharField(max_length=255, blank=True, null=True)
    party = models.ForeignKey('Party', on_delete=models.CASCADE, related_name='prezi_candidate_party')

    first_name = models.CharField(max_length=255, blank=True, null=True)
    last_name = models.CharField(max_length=255, blank=True, null=True)
    middle_name = models.CharField(max_length=255, blank=True, null=True)
    photo = models.ImageField(upload_to=upload_prez_can_photo_path, null=True, blank=True)
    gender = models.CharField(max_length=100, choices=GENDER_CHOICES, blank=True, null=True)
    candidate_type = models.CharField(max_length=100, choices=CANDIDATE_TYPE, blank=True, null=True)

    def __str__(self):
        return f"{self.first_name}"

def pre_save_prez_can_id_receiver(sender, instance, *args, **kwargs):
    if not instance.prez_can_id:
        instance.prez_can_id = unique_prez_can_id_generator(instance)

pre_save.connect(pre_save_prez_can_id_receiver, sender=PresidentialCandidate)








class ParliamentaryCandidate(models.Model):
    parl_can_id = models.CharField(max_length=255, blank=True, null=True)
    constituency = models.ForeignKey(Constituency, on_delete=models.CASCADE, related_name='consti_parlia_candidate')
    party = models.ForeignKey('Party', on_delete=models.CASCADE, related_name='parlia_candidate_party')

    first_name = models.CharField(max_length=255, blank=True, null=True)
    last_name = models.CharField(max_length=255, blank=True, null=True)
    middle_name = models.CharField(max_length=255, blank=True, null=True)
    photo = models.ImageField(upload_to=upload_parl_can_photo_path, null=True, blank=True)
    gender = models.CharField(max_length=100, choices=GENDER_CHOICES, blank=True, null=True)

    candidate_type = models.CharField(max_length=100, choices=CANDIDATE_TYPE, blank=True, null=True)

    def __str__(self):
        return f"{self.first_name}"

def pre_save_parl_can_id_receiver(sender, instance, *args, **kwargs):
    if not instance.parl_can_id:
        instance.parl_can_id = unique_parl_can_id_generator(instance)

pre_save.connect(pre_save_parl_can_id_receiver, sender=ParliamentaryCandidate)





def get_file_ext(filepath):
    base_name = os.path.basename(filepath)
    name, ext = os.path.splitext(base_name)
    return name, ext


def upload_party_logo_path(instance, filename):
    new_filename = random.randint(1, 3910209312)
    name, ext = get_file_ext(filename)
    final_filename = '{new_filename}{ext}'.format(new_filename=new_filename, ext=ext)
    return "party_logo/{new_filename}/{final_filename}".format(
        new_filename=new_filename,
        final_filename=final_filename
    )

class Party(models.Model):
    party_id = models.CharField(max_length=255, blank=True, null=True, unique=True)

    party_full_name = models.CharField(max_length=255, blank=True, null=True)
    party_initial = models.CharField(max_length=255, blank=True, null=True)
    party_color = models.CharField(max_length=255, blank=True, null=True)
    year_formed = models.CharField(max_length=255, blank=True, null=True)
    founder = models.CharField(max_length=255, blank=True, null=True)
    party_logo = models.ImageField(upload_to=upload_party_logo_path, null=True, blank=True)
    bio = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.party_full_name}"

def pre_save_party_id_receiver(sender, instance, *args, **kwargs):
    if not instance.party_id:
        instance.party_id = unique_party_id_generator(instance)

pre_save.connect(pre_save_party_id_receiver, sender=Party)


class PartyFlagBearer(models.Model):
    flag_bearer = models.ForeignKey(PresidentialCandidate, on_delete=models.SET_NULL, null=True, related_name='party_flag_bearers')
    party = models.ForeignKey(Party, on_delete=models.CASCADE, related_name='party_flag_bearers')
    year = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return f"{self.flag_bearer.last_name}, {self.year} Flag Bearer ({self.party.party_initial})"


class PartyStandingCandidate(models.Model):
    standing_candidate = models.ForeignKey(PresidentialCandidate, on_delete=models.SET_NULL, null=True, related_name='party_standing_candidates')
    party = models.ForeignKey(Party, on_delete=models.CASCADE, related_name='party_standing_candidates')
    year = models.CharField(max_length=255, blank=True, null=True)
    won = models.BooleanField(default=False)  # Optional field to track if the candidate won the election

    def __str__(self):
        return f"{self.standing_candidate.last_name}, {self.year} Candidate ({self.party.party_initial})"



class PartyPresidentailPrimary(models.Model):
    candidate = models.ForeignKey(PresidentialCandidate, on_delete=models.SET_NULL, null=True, related_name='party_presidential_primaries')
    party = models.ForeignKey(Party, on_delete=models.CASCADE, related_name='party_presidential_primaries')
    year = models.CharField(max_length=255, blank=True, null=True)
    position = models.IntegerField(default=0)

    won = models.BooleanField(default=False)


class PartyParliamentaryPrimary(models.Model):
    candidate = models.ForeignKey(PresidentialCandidate, on_delete=models.SET_NULL, null=True, related_name='party_parliamentary_primaries')
    party = models.ForeignKey(Party, on_delete=models.CASCADE, related_name='party_parliamentary_primaries')
    year = models.CharField(max_length=255, blank=True, null=True)
    position = models.IntegerField(default=0)

    won = models.BooleanField(default=False)

