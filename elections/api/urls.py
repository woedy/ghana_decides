from django.urls import path

from elections.api.views import add_election_view, get_all_election_history_view, get_election_details

app_name = 'elections'

urlpatterns = [
    path('add-election/', add_election_view, name="add_election_view"),
    path('get-all-elections-history/', get_all_election_history_view, name="get_all_election_view"),
    path('get-election-details/', get_election_details, name="get_election_details"),

]
