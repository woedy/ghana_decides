import os
import random

from django.conf import settings
from django.db import models
from django.db.models.signals import post_save

User = settings.AUTH_USER_MODEL



def get_file_ext(filepath):
    base_name = os.path.basename(filepath)
    name, ext = os.path.splitext(base_name)
    return name, ext


def upload_image_path(instance, filename):
    new_filename = random.randint(1, 3910209312)
    name, ext = get_file_ext(filename)
    final_filename = '{new_filename}{ext}'.format(new_filename=new_filename, ext=ext)
    return "users/{new_filename}/{final_filename}".format(
        new_filename=new_filename,
        final_filename=final_filename
    )



def get_default_profile_image():
    return "defaults/default_profile_image.png"


GENDER_CHOICES = (
    ('Male', 'Male'),
    ('Female', 'Female'),

)

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='personal_info')
    #room = models.ForeignKey(PrivateChatRoom, on_delete=models.SET_NULL, null=True, blank=True, related_name="user_room")
    gender = models.CharField(max_length=100, choices=GENDER_CHOICES, blank=True, null=True)
    photo = models.ImageField(upload_to=upload_image_path, null=True, blank=True, default=get_default_profile_image)
    phone = models.CharField(max_length=255, null=True, blank=True)
    about_me = models.TextField(blank=True, null=True)

    country = models.CharField(max_length=255, blank=True, null=True)


    profile_complete = models.BooleanField(default=False)
    verified = models.BooleanField(default=False)

    location_name = models.CharField(max_length=200, null=True, blank=True)
    lat = models.DecimalField(max_digits=30, decimal_places=15, null=True, blank=True)
    lng = models.DecimalField(max_digits=30, decimal_places=15, null=True, blank=True)

    active = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.user.email


def post_save_personal_info(sender, instance, *args, **kwargs):
    if not instance.photo:
        instance.photo = get_default_profile_image()

post_save.connect(post_save_personal_info, sender=UserProfile)