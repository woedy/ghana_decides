import os
import random

from django.db import models
from django.db.models.signals import pre_save

from ghana_decides_proj.utils import unique_region_id_generator, unique_constituency_id_generator


def get_file_ext(filepath):
    base_name = os.path.basename(filepath)
    name, ext = os.path.splitext(base_name)
    return name, ext


def upload_region_image_path(instance, filename):
    new_filename = random.randint(1, 3910209312)
    name, ext = get_file_ext(filename)
    final_filename = '{new_filename}{ext}'.format(new_filename=new_filename, ext=ext)
    return "region/{new_filename}/{final_filename}".format(
        new_filename=new_filename,
        final_filename=final_filename
    )


REGION_NAME_CHOICES = (
    ('Ashanti', 'Ashanti'),
    ('Brong Ahafo', 'Brong Ahafo'),
    ('Central', 'Central'),
    ('Eastern', 'Eastern'),
    ('Greater Accra', 'Greater Accra'),
    ('Northern', 'Northern'),
    ('Upper East', 'Upper East'),
    ('Upper West', 'Upper West'),
    ('Volta', 'Volta'),
    ('Western', 'Western'),
    ('Savannah', 'Savannah'),
    ('Bono East', 'Bono East'),
    ('Oti', 'Oti'),
    ('Ahafo', 'Ahafo'),
    ('Western North', 'Western North'),
    ('North East', 'North East'),

)
class Region(models.Model):
    region_id = models.CharField(max_length=255, blank=True, null=True, unique=True)
    region_name = models.CharField(max_length=255, choices=REGION_NAME_CHOICES,  blank=True, null=True)
    initials = models.CharField(max_length=255,  blank=True, null=True)
    capital = models.CharField(max_length=255,  blank=True, null=True)
    map_image = models.ImageField(upload_to=upload_region_image_path, null=True, blank=True)

def pre_save_region_id_receiver(sender, instance, *args, **kwargs):
    if not instance.region_id:
        instance.region_id = unique_region_id_generator(instance)

pre_save.connect(pre_save_region_id_receiver, sender=Region)





CONSTITUENCY_NAME_CHOICES = (
    ('Abetifi', 'Abetifi'),
    ('Abirem', 'Abirem'),
    ('Ablekuma Central', 'Ablekuma Central'),
    ('Ablekuma North', 'Ablekuma North'),

)

class Constituency(models.Model):
    constituency_id = models.CharField(max_length=255, blank=True, null=True, unique=True)
    region = models.ForeignKey(Region, on_delete=models.CASCADE, related_name='region_constituencies')
    constituency_name = models.CharField(max_length=255, blank=True, null=True)



def pre_save_constituency_id_receiver(sender, instance, *args, **kwargs):
    if not instance.constituency_id:
        instance.constituency_id = unique_constituency_id_generator(instance)

pre_save.connect(pre_save_constituency_id_receiver, sender=Constituency)

