"""leaderboard_api URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import to include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include, re_path

from django.conf import urls

from home_pages import views as homepages_view

urls.handler4503 = homepages_view.view_503

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("home_pages.urls")),
    path("api/v1/users/", include("users.urls")),
    path("api/v1/companies/", include("companies.urls")),
    path("api/v1/leads/", include("leads.urls")),
    path("api/v1/schedules/", include("schedules.urls")),
    path("api/v1/feedbacks/", include("feedbacks.urls")),
    path("api/v1/high_value_contents/", include("high_value_contents.urls")),
    path("api/v1/events/", include("events.urls")),
    path("api/v1/contacts/", include("contacts.urls")),
    path("api/v1/careers/", include("careers.urls")),
    path("api/v1/communications/", include("communications.urls")),
    path('api/v1/easy_tax_ussds/', include('easy_tax_ussds.urls')),

    # for maintenance mode
    re_path(r"^maintenance-mode/", include("maintenance_mode.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL,
                          document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
