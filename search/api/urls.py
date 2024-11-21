from django.urls import path

from regions.api.views import get_all_regions, get_region_detail, get_region_constituencies, add_region_view, \
    add_constituency_view, get_all_constituencies, get_constituency_detail, delete_region_view, edit_region_view
from search.api.views import general_search_view

app_name = 'search'

urlpatterns = [
    path('', general_search_view, name="general_search_view"),
]
