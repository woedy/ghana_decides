import os
import random

from django.db import models
from django.db.models.signals import pre_save, post_save

from ghana_decides_proj.utils import unique_region_id_generator, unique_constituency_id_generator, \
    unique_electoral_area_id_generator, unique_polling_station_id_generator


def get_file_ext(filepath):
    base_name = os.path.basename(filepath)
    name, ext = os.path.splitext(base_name)
    return name, ext


def upload_region_image_path(instance, filename):
    new_filename = random.randint(1, 3910209312)
    name, ext = get_file_ext(filename)
    final_filename = '{new_filename}{ext}'.format(new_filename=new_filename, ext=ext)
    return "region/{new_filename}".format(
        new_filename=new_filename,
        final_filename=final_filename
    )



class Region(models.Model):
    region_id = models.CharField(max_length=255, blank=True, null=True, unique=True)
    region_name = models.CharField(max_length=255,  blank=True, null=True)
    initials = models.CharField(max_length=255,  blank=True, null=True)
    capital = models.CharField(max_length=255,  blank=True, null=True)
    map_image = models.ImageField(upload_to=upload_region_image_path, null=True, blank=True)

    election_year = models.CharField(max_length=255, blank=True, null=True)
    parliamentary_submitted = models.BooleanField(default=False)
    presidential_submitted = models.BooleanField(default=False)

    central_lat = models.DecimalField(max_digits=30, decimal_places=15, null=True, blank=True)
    central_lng = models.DecimalField(max_digits=30, decimal_places=15, null=True, blank=True)


    def __str__(self):
        return f"{self.region_name}"



def pre_save_region_id_receiver(sender, instance, *args, **kwargs):
    if not instance.region_id:
        instance.region_id = unique_region_id_generator(instance)

pre_save.connect(pre_save_region_id_receiver, sender=Region)


class RegionLayerCoordinate(models.Model):
    region = models.ForeignKey(Region, on_delete=models.CASCADE, related_name='region_coordinates')
    lat = models.DecimalField(max_digits=30, decimal_places=15, null=True, blank=True)
    lng = models.DecimalField(max_digits=30, decimal_places=15, null=True, blank=True)



class RegionalVotersParticipation(models.Model):
    region = models.ForeignKey(Region, on_delete=models.CASCADE, related_name='region_registered_voters')

    registered_voters = models.IntegerField(default=0)
    voters = models.IntegerField(default=0)
    non_voters = models.IntegerField(default=0)
    turn_out_percent = models.DecimalField(max_digits=30, decimal_places=15, null=True, blank=True)








class Constituency(models.Model):
    constituency_id = models.CharField(max_length=255, blank=True, null=True, unique=True)
    region = models.ForeignKey(Region, on_delete=models.CASCADE, related_name='region_constituencies')
    constituency_name = models.CharField(max_length=255, blank=True, null=True)

    election_year = models.CharField(max_length=255, blank=True, null=True)


    parliamentary_submitted = models.BooleanField(default=False)
    presidential_submitted = models.BooleanField(default=False)

    central_lat = models.DecimalField(max_digits=30, decimal_places=15, null=True, blank=True)
    central_lng = models.DecimalField(max_digits=30, decimal_places=15, null=True, blank=True)


    def __str__(self):
        return f"{self.constituency_name} - {self.region.region_name}"


class ConstituencyLayerCoordinate(models.Model):
    constituency = models.ForeignKey(Constituency, on_delete=models.CASCADE, related_name='constituency_coordinates')
    lat = models.DecimalField(max_digits=30, decimal_places=15, null=True, blank=True)
    lng = models.DecimalField(max_digits=30, decimal_places=15, null=True, blank=True)


def pre_save_constituency_id_receiver(sender, instance, *args, **kwargs):
    if not instance.constituency_id:
        instance.constituency_id = unique_constituency_id_generator(instance)

pre_save.connect(pre_save_constituency_id_receiver, sender=Constituency)


class ConstituencyVotersParticipation(models.Model):
    constituency = models.ForeignKey(Constituency, on_delete=models.CASCADE, related_name='constituency_registered_voters')

    registered_voters = models.IntegerField(default=0)
    voters = models.IntegerField(default=0)
    non_voters = models.IntegerField(default=0)
    turn_out_percent = models.DecimalField(max_digits=30, decimal_places=15, null=True, blank=True)




class ElectoralArea(models.Model):
    electoral_area_id = models.CharField(max_length=255, blank=True, null=True, unique=True)
    constituency = models.ForeignKey(Constituency, on_delete=models.CASCADE, related_name='constituency_electoral_area')
    electoral_area_name = models.CharField(max_length=255, blank=True, null=True)

    election_year = models.CharField(max_length=255, blank=True, null=True)


    parliamentary_submitted = models.BooleanField(default=False)
    presidential_submitted = models.BooleanField(default=False)

    central_lat = models.DecimalField(max_digits=30, decimal_places=15, null=True, blank=True)
    central_lng = models.DecimalField(max_digits=30, decimal_places=15, null=True, blank=True)


    def __str__(self):
        return f"{self.electoral_area_name} - {self.constituency.constituency_name} - {self.constituency.region.region_name}"

class ElectoralAreaLayerCoordinate(models.Model):
    electoral_area = models.ForeignKey(ElectoralArea, on_delete=models.CASCADE, related_name='electoral_area_coordinates')
    lat = models.DecimalField(max_digits=30, decimal_places=15, null=True, blank=True)
    lng = models.DecimalField(max_digits=30, decimal_places=15, null=True, blank=True)


class ElectoralVotersParticipation(models.Model):
    electoral_area = models.ForeignKey(ElectoralArea, on_delete=models.CASCADE, related_name='electoral_area_registered_voters')

    registered_voters = models.IntegerField(default=0)
    voters = models.IntegerField(default=0)
    non_voters = models.IntegerField(default=0)
    turn_out_percent = models.DecimalField(max_digits=30, decimal_places=15, null=True, blank=True)





def pre_save_electoral_area_id_receiver(sender, instance, *args, **kwargs):
    if not instance.electoral_area_id:
        instance.electoral_area_id = unique_electoral_area_id_generator(instance)

pre_save.connect(pre_save_electoral_area_id_receiver, sender=ElectoralArea)


class PollingStation(models.Model):
    polling_station_id = models.CharField(max_length=255, blank=True, null=True, unique=True)
    electoral_area = models.ForeignKey(ElectoralArea, on_delete=models.CASCADE, related_name='electoral_area_polling_stations')
    polling_station_name = models.CharField(max_length=255, blank=True, null=True)
    election_year = models.CharField(max_length=255, blank=True, null=True)

    parliamentary_submitted = models.BooleanField(default=False)
    presidential_submitted = models.BooleanField(default=False)

    central_lat = models.DecimalField(max_digits=30, decimal_places=15, null=True, blank=True)
    central_lng = models.DecimalField(max_digits=30, decimal_places=15, null=True, blank=True)



    def __str__(self):
        return f"{self.polling_station_name} - {self.electoral_area.electoral_area_name} - {self.electoral_area.constituency.constituency_name} - {self.electoral_area.constituency.region.region_name}"


def pre_save_polling_station_id_receiver(sender, instance, *args, **kwargs):
    if not instance.polling_station_id:
        instance.polling_station_id = unique_polling_station_id_generator(instance)

pre_save.connect(pre_save_polling_station_id_receiver, sender=PollingStation)


class PollingStationLayerCoordinate(models.Model):
    polling_station = models.ForeignKey(PollingStation, on_delete=models.CASCADE, related_name='polling_station_coordinates')
    lat = models.DecimalField(max_digits=30, decimal_places=15, null=True, blank=True)
    lng = models.DecimalField(max_digits=30, decimal_places=15, null=True, blank=True)



class PollingStationVotersParticipation(models.Model):
    polling_station = models.ForeignKey(PollingStation, on_delete=models.CASCADE, related_name='polling_station_registered_voters')

    registered_voters = models.IntegerField(default=0)
    voters = models.IntegerField(default=0)
    non_voters = models.IntegerField(default=0)
    turn_out_percent = models.DecimalField(max_digits=30, decimal_places=15, null=True, blank=True)




