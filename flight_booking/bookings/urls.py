from django.urls import path
from . import views

app_name = 'bookings'

urlpatterns = [
    path('book/<int:flight_id>/', views.book_flight, name='book_flight'),
    path('confirmation/<uuid:booking_id>/', views.booking_confirmation, name='booking_confirmation'),
    path('my-bookings/', views.my_bookings, name='my_bookings'),
    path('booking/<uuid:booking_id>/', views.booking_detail, name='booking_detail'),
    path('booking/<uuid:booking_id>/cancel/', views.cancel_booking, name='cancel_booking'),
    
    # Admin URLs
    path('admin/bookings/', views.admin_bookings, name='admin_bookings'),
    path('admin/booking/<uuid:booking_id>/', views.admin_booking_detail, name='admin_booking_detail'),
]