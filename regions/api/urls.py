from django.urls import path

from regions.api.views import get_all_regions, get_region_detail, get_region_constituencies, add_region_view, \
    add_constituency_view, get_all_constituencies, get_constituency_detail

app_name = 'region'

urlpatterns = [
    path('get-all-regions/', get_all_regions, name="get_all_regions"),
    path('region-details/', get_region_detail , name="get_region_detail"),
    path('get-regional-constituencies/', get_region_constituencies , name="get_region_constituencies"),
    path('add-region/', add_region_view , name="add_region_view"),


    path('add-constituency/', add_constituency_view , name="add_constituency_view"),
    path('get-all-constituencies/', get_all_constituencies, name="get_all_constituencies"),
    path('constituency-details/', get_constituency_detail, name="get_constituency_detail"),

]
