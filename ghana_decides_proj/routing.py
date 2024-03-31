from django.urls import path, re_path

from chat import consumers
from homepage.api.data_admin_dashboard_consumers import DataAdminDashboardConsumers
from regions.api.regions_consumers import RegionsConsumers
from search.api.consumers import SearchSystemConsumers

websocket_urlpatterns = [
    re_path(r"ws/chat/(?P<room_name>\w+)/$", consumers.ChatConsumer.as_asgi()),
    re_path(r"ws/search/", SearchSystemConsumers.as_asgi()),
    re_path(r"ws/data-admin-dashboard/", DataAdminDashboardConsumers.as_asgi()),
    re_path(r"ws/region-consumers/", RegionsConsumers.as_asgi()),

]