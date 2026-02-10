from django.urls import path
from . import views

app_name = 'flights'

urlpatterns = [
    path('', views.home, name='home'),
    path('flight/<int:flight_id>/', views.flight_detail, name='flight_detail'),
    path('autocomplete/cities/', views.autocomplete_cities, name='autocomplete_cities'),
    
    # Admin URLs
    path('admin/dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('admin/flights/', views.admin_flights, name='admin_flights'),
    path('admin/flights/add/', views.admin_flight_add, name='admin_flight_add'),
    path('admin/flights/<int:flight_id>/edit/', views.admin_flight_edit, name='admin_flight_edit'),
    path('admin/flights/<int:flight_id>/delete/', views.admin_flight_delete, name='admin_flight_delete'),
]