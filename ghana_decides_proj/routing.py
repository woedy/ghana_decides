from django.urls import re_path

#from candidates.api.parl_candidate_consumers import ParliamentaryCandidateConsumers
#from candidates.api.prez_candidate_consumers import PresidentialCandidateConsumers
#from chat import consumers
from elections.api.consumers.live_map_consumers import LiveMapConsumers
from elections.api.consumers.presenter_dashboard_consumers import PresenterDashboardConsumers
#from elections.api.consumers.elections_consumers import ElectionConsumers
#from elections.api.consumers.votes_consumers import Election2024Consumers
#from homepage.api.data_admin_dashboard_consumers import DataAdminDashboardConsumers
#from parties.api.parties_consumers import PartyConsumers
#from regions.api.constituencies_consumers import ConstituencyConsumers
#from regions.api.electoral_area_consumers import ElectoralAreaConsumers
#from regions.api.polling_station_consumers import PollingStationConsumer
#from regions.api.regions_consumers import RegionsConsumers
#from search.api.consumers import SearchSystemConsumers

websocket_urlpatterns = [
    #re_path(r"ws/chat/(?P<room_name>\w+)/$", consumers.ChatConsumer.as_asgi()),
    #re_path(r"ws/search/", SearchSystemConsumers.as_asgi()),
    #re_path(r"ws/data-admin-dashboard/", DataAdminDashboardConsumers.as_asgi()),

    #re_path(r"ws/region-consumers/", RegionsConsumers.as_asgi()),
    #re_path(r"ws/constituency-consumers/", ConstituencyConsumers.as_asgi()),
    #re_path(r"ws/electoral-area-consumers/", ElectoralAreaConsumers.as_asgi()),
    #re_path(r"ws/polling-station-consumers/", PollingStationConsumer.as_asgi()),

    #re_path(r"ws/party-consumers/", PartyConsumers.as_asgi()),
    #re_path(r"ws/presidential-candidate-consumers/", PresidentialCandidateConsumers.as_asgi()),
    #re_path(r"ws/parliamentary-candidate-consumers/", ParliamentaryCandidateConsumers.as_asgi()),

    #re_path(r"ws/elections-consumers/", ElectionConsumers.as_asgi()),
    #re_path(r"ws/2024-election-consumers/", Election2024Consumers.as_asgi()),
    re_path(r"ws/presenter-dashboard/", PresenterDashboardConsumers.as_asgi()),
    re_path(r"ws/live-map-consumer/", LiveMapConsumers.as_asgi()),


]