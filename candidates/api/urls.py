from django.urls import path

from candidates.api.views import add_parliamentary_candidate, get_all_parliamentary_candidate, \
    get_parliamentary_candidate_details, add_presidential_candidate, get_all_presidential_candidate, \
    get_presidential_candidate_details, edit_presidential_candidate_view, edit_parliamentary_candidate_view, \
    delete_presidential_candidate_view, delete_parliamentary_candidate_view, add_presidential_candidates_list, \
    add_parliamentary_candidate_list
from regions.api.views import get_all_regions, get_region_detail, get_region_constituencies, add_region_view, \
    add_constituency_view, get_all_constituencies, get_constituency_detail

app_name = 'candidates'

urlpatterns = [
    path('add-parliamentary-candidate/', add_parliamentary_candidate, name="add_parliamentary_candidate"),
    path('add-parliamentary-candidate-list/', add_parliamentary_candidate_list, name="add_parliamentary_candidate_list"),
    path('edit-parliamentary-candidate/', edit_parliamentary_candidate_view, name="edit_parliamentary_candidate_view"),
    path('get-all-parliamentary-candidate/', get_all_parliamentary_candidate, name="get_all_parliamentary_candidate"),
    path('get-parliamentary-candidate-details/', get_parliamentary_candidate_details, name="get_parliamentary_candidate_details"),
    path('delete-parliamentary-candidate/', delete_parliamentary_candidate_view, name="delete_parliamentary_candidate_view"),

    path('add-presidential-candidate/', add_presidential_candidate, name="add_presidential_candidate"),
    path('add-presidential-candidates-list/', add_presidential_candidates_list, name="add_presidential_candidates_list"),
    path('edit-presidential-candidate/', edit_presidential_candidate_view, name="edit_presidential_candidate_view"),
    path('get-all-presidential-candidate/', get_all_presidential_candidate, name="get_all_presidential_candidate"),
    path('get-presidential-candidate-details/', get_presidential_candidate_details, name="get_presidential_candidate_details"),
    path('delete-presidential-candidate/', delete_presidential_candidate_view, name="delete_presidential_candidate_view"),

]
