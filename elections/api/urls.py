from django.urls import path

from elections.api.election_view import add_election_presidential_candidate_view, get_all_election_parliamentary_marginal_constituency_view, get_all_election_parliamentary_swing_constituency_view, get_all_election_presidential_candidate_constituency_view, get_all_election_presidential_candidate_electoral_area_view, get_all_election_presidential_candidate_polling_station_view, get_all_election_presidential_candidate_regional_view, \
    get_all_election_presidential_candidate_view, add_election_parliamentary_candidate_view, \
    get_all_election_parliamentary_candidate_view, add_election_presidential_vote_view, get_all_election_presidential_marginal_constituency_view, get_all_election_presidential_swing_constituency_view, get_all_election_skirt_and_blouse_constituency_view, \
    get_election_2024_dashboard_view, add_election_parliamentary_vote_view, \
    add_election_presidential_candidate_list_view, add_election_parliamentary_candidate_list_view
from elections.api.views import add_election_view, get_all_election_history_view, get_election_details, \
    add_election_2024_view, get_regional_presidential_votes

app_name = 'elections'

urlpatterns = [
    path('add-election/', add_election_view, name="add_election_view"),
    path('get-all-elections-history/', get_all_election_history_view, name="get_all_election_view"),
    path('get-election-details/', get_election_details, name="get_election_details"),

    path('add-election-2024/', add_election_2024_view, name="add_election_view"),

    path('add-election-presidential-candidate/', add_election_presidential_candidate_view, name="add_election_presidential_candidate_view"),
    path('add-election-presidential-candidate-list/', add_election_presidential_candidate_list_view, name="add_election_presidential_candidate_list_view"),
    path('get-all-election-presidential-candidates/', get_all_election_presidential_candidate_view, name="get_all_election_presidential_candidate_view"),
    path('get-all-election-presidential-candidates-regional/', get_all_election_presidential_candidate_regional_view, name="get_all_election_presidential_candidate_regional_view"),
    path('get-all-election-presidential-candidates-constituency/', get_all_election_presidential_candidate_constituency_view, name="get_all_election_presidential_candidate_constituency_view"),
    path('get-all-election-presidential-candidates-electoral-area/', get_all_election_presidential_candidate_electoral_area_view, name="get_all_election_presidential_candidate_electoral_area_view"),
    path('get-all-election-presidential-candidates-polling-station/', get_all_election_presidential_candidate_polling_station_view, name="get_all_election_presidential_candidate_polling_station_view"),
    
    

    path('add-election-parliamentary-candidate/', add_election_parliamentary_candidate_view,
         name="add_election_parliamentary_candidate_view"),

    path('add-election-parliamentary-candidate-list/', add_election_parliamentary_candidate_list_view,
         name="add_election_parliamentary_candidate_list_view"),
    path('get-all-election-parliamentary-candidates/', get_all_election_parliamentary_candidate_view,
         name="get_all_election_parliamentary_candidate_view"),

    path('add-presidential-vote/', add_election_presidential_vote_view,
         name="add_election_presidential_vote_view"),


    path('get-election-2024-dashboard/', get_election_2024_dashboard_view,
         name="get_election_2024_dashboard_view"),

    path('add-parliamentary-vote/', add_election_parliamentary_vote_view,
         name="add_election_parliamentary_vote_view"),

    path('get-regional-presidential-votes/', get_regional_presidential_votes,
         name="get_regional_presidential_votes"),





     path('get-all-election-parliamentary-swing-constituencies/', get_all_election_parliamentary_swing_constituency_view, name="get_all_election_parliamentary_swing_constituency_view"),
    path('get-all-election-presidential-swing-constituencies/', get_all_election_presidential_swing_constituency_view, name="get_all_election_parliamentary_swing_constituency_view"),
    
    path('get-all-election-parliamentary-marginal-constituencies/', get_all_election_parliamentary_marginal_constituency_view, name="get_all_election_parliamentary_marginal_constituency_view"),
    path('get-all-election-presidential-marginal-constituencies/', get_all_election_presidential_marginal_constituency_view, name="get_all_election_presidential_marginal_constituency_view"),
    
    path('get-all-election-skirt-and-blouse-constituencies/', get_all_election_skirt_and_blouse_constituency_view, name="get_all_election_skirt_and_blouse_constituency_view"),


]
