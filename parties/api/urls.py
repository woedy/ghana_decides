from django.urls import path

from parties.api.views import add_party_view, get_all_parties_view, get_party_detail, edit_party_view, \
    delete_party_view, get_all_party_candidates, get_all_party_presidential_candidates, \
    get_all_party_parliamentary_candidates, add_flag_bearer, add_standing_candidate, add_party_list_view

app_name = 'parties'

urlpatterns = [
    path('add-party/', add_party_view, name="add_party_view"),
    path('add-party-list/', add_party_list_view, name="add_party_list_view"),
    path('add-party-flagbearer/', add_flag_bearer, name="add_flag_bearer"),
    path('add-party-standing-candidate/', add_standing_candidate, name="add_standing_candidate"),
    path('get-all-parties/', get_all_parties_view, name="get_all_parties_view"),
    path('get-all-party-candidates/', get_all_party_candidates, name="get_all_party_candidates"),
    path('get-all-party-presidential-candidates/', get_all_party_presidential_candidates, name="get_all_party_presidential_candidates"),
    path('get-all-party-parliamentary-candidates/', get_all_party_parliamentary_candidates, name="get_all_party_parliamentary_candidates"),
    path('get-party-details/', get_party_detail, name="get_party_detail"),
    path('edit-party/', edit_party_view, name="edit_party_view"),
    path('delete-party/', delete_party_view, name="delete_party_view"),

]
