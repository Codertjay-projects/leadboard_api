from django.contrib import admin
from django.urls import path
from .views import home_page

app_name = 'home_pages'
urlpatterns = [
    path('', home_page, name='home_page'),

]
