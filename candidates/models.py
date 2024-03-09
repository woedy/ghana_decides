import os
import random

from django.db import models

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

    first_name = models.CharField(max_length=255, blank=True, null=True)
    last_name = models.CharField(max_length=255, blank=True, null=True)
    middle_name = models.CharField(max_length=255, blank=True, null=True)
    photo = models.ImageField(upload_to=upload_prez_can_photo_path, null=True, blank=True)
    gender = models.CharField(max_length=100, choices=GENDER_CHOICES, blank=True, null=True)
    candidate_type = models.CharField(max_length=100, choices=CANDIDATE_TYPE, blank=True, null=True)






class ParliamentaryCandidate(models.Model):
    constituency = models.ForeignKey(Constituency, on_delete=models.CASCADE, related_name='consti_parlia_candidate')

    first_name = models.CharField(max_length=255, blank=True, null=True)
    last_name = models.CharField(max_length=255, blank=True, null=True)
    middle_name = models.CharField(max_length=255, blank=True, null=True)
    photo = models.ImageField(upload_to=upload_parl_can_photo_path, null=True, blank=True)
    gender = models.CharField(max_length=100, choices=GENDER_CHOICES, blank=True, null=True)

    candidate_type = models.CharField(max_length=100, choices=CANDIDATE_TYPE, blank=True, null=True)







