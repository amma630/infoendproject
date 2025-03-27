from django.urls import path
from .views import dashboard_view, home_view

urlpatterns = [
    path('dashboard/', dashboard_view, name='dashboard'),
    path('', home_view, name='home'),
]
