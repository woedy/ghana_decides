from django.urls import path

from settings.api.views import reset_votes

app_name = 'settings'

urlpatterns = [
    path('reset-votes/', reset_votes, name="reset_votes")

]
