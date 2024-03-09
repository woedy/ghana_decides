import os
import random

from django.db import models
from django.db.models.signals import pre_save

from ghana_decides_proj.utils import unique_party_id_generator


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
    year_formed = models.CharField(max_length=255, blank=True, null=True)
    party_logo = models.ImageField(upload_to=upload_party_logo_path, null=True, blank=True)



def pre_save_party_id_receiver(sender, instance, *args, **kwargs):
    if not instance.party_id:
        instance.party_id = unique_party_id_generator(instance)

pre_save.connect(pre_save_party_id_receiver, sender=Party)


class PartyFlagBearer(models.Model):
    pass

class PartyStandingCandidate(models.Model):
    pass

