from django.urls import path

from regions.api.views import get_all_regions, get_region_detail, get_region_constituencies, add_region_view, \
    add_constituency_view, get_all_constituencies, get_constituency_detail, delete_region_view, edit_region_view, \
    get_constituency_zone, add_zone_view, edit_constituency_view, delete_constituency_view, get_all_zones_view, \
    get_zone_detail_view, edit_zone_view, delete_zone_view, get_zone_polling_stations, add_polling_station_view, \
    get_all_polling_stations, get_polling_station_detail, edit_polling_station_view, delete_polling_station_view, \
    add_polling_station_participation

app_name = 'region'

urlpatterns = [
    path('get-all-regions/', get_all_regions, name="get_all_regions"),
    path('region-details/', get_region_detail , name="get_region_detail"),
    path('get-regional-constituencies/', get_region_constituencies , name="get_region_constituencies"),
    path('add-region/', add_region_view , name="add_region_view"),
    path('edit-region/', edit_region_view, name="edit_region_view"),
    path('delete-region/', delete_region_view , name="delete_region_view"),


    path('add-constituency/', add_constituency_view , name="add_constituency_view"),
    path('get-all-constituencies/', get_all_constituencies, name="get_all_constituencies"),
    path('constituency-details/', get_constituency_detail, name="get_constituency_detail"),
    path('get-constituency-zone/', get_constituency_zone, name="get_constituency_zone"),
    path('edit-constituency/', edit_constituency_view, name="edit_constituency_view"),
    path('delete-constituency/', delete_constituency_view, name="delete_constituency_view"),

    path('add-zone/', add_zone_view, name="add_zone_view"),
    path('get-all-zones/', get_all_zones_view, name="get_all_zones_view"),
    path('zone-details/', get_zone_detail_view, name="get_zone_details_view"),
    path('edit-zone/', edit_zone_view, name="edit_zone_view"),
    path('delete-zone/', delete_zone_view, name="delete_constituency_view"),
    path('get-zone-polling-stations/', get_zone_polling_stations, name="get_zone_polling_stations"),

    path('add-polling-station/', add_polling_station_view, name="add_polling_station_view"),
    path('get-all-polling-stations/', get_all_polling_stations, name="get_all_polling_stations"),
    path('polling-station-details/', get_polling_station_detail, name="get_polling_station_detail"),
    path('edit-polling-station/', edit_polling_station_view, name="get_polling_station_detail"),
    path('delete-polling-station/', delete_polling_station_view, name="delete_polling_station_view"),

    path('add-polling-station-participation/', add_polling_station_participation, name="add_polling_station_participation_view"),

]
