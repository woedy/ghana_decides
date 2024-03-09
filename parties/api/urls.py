from django.urls import path

from parties.api.views import add_party_view, get_all_parties_view, get_party_detail

app_name = 'parties'

urlpatterns = [
    path('add-party/', add_party_view, name="add_party_view"),
    path('get-all-parties/', get_all_parties_view, name="get_all_parties_view"),
    path('get-party-details/', get_party_detail, name="get_party_detail"),

]
