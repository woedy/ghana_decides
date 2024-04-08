"""
URL configuration for ghana_decides_proj project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),
    path("chat/", include("chat.urls")),

    path('api/accounts/', include('accounts.api.urls', 'accounts_api')),
    path('api/regions/', include('regions.api.urls', 'regions_api')),
    path('api/parties/', include('parties.api.urls', 'parties_api')),
    path('api/candidates/', include('candidates.api.urls', 'candidates_api')),
    path('api/elections/', include('elections.api.urls', 'elections_api')),
    path('api/search/', include('search.api.urls', 'search_api')),
    path('api/settings/', include('settings.api.urls', 'settings_api')),
]

if settings.DEBUG:
    urlpatterns = urlpatterns + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns = urlpatterns + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
