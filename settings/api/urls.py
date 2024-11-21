from django.urls import path

from settings.api.views import reset_demo, reset_votes, reset_region_2024

app_name = 'settings'

urlpatterns = [
    path('reset-votes/', reset_votes, name="reset_votes"),
    path('reset-demo/', reset_demo, name="reset_demo"),
    path('reset-region-2024/', reset_region_2024, name="reset_region_2024")

]
