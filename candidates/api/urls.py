from django.urls import path

from regions.api.views import get_all_regions, get_region_detail, get_region_constituencies, add_region_view, \
    add_constituency_view, get_all_constituencies, get_constituency_detail

app_name = 'candidates'

urlpatterns = [
    path('add-parliamentary-candidate/', add_parliamentary_candidate, name="add_parliamentary_candidate"),

]
