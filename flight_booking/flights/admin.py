from django.contrib import admin
from .models import Flight, Airport, Airline

@admin.register(Flight)
class FlightAdmin(admin.ModelAdmin):
    list_display = ('flight_number', 'airline', 'origin', 'destination', 
                   'departure_date', 'departure_time', 'price', 'available_seats', 'is_active')
    list_filter = ('airline', 'origin', 'destination', 'departure_date', 'is_active')
    search_fields = ('flight_number', 'airline', 'origin', 'destination')
    list_editable = ('price', 'available_seats', 'is_active')
    date_hierarchy = 'departure_date'
    ordering = ('-departure_date', 'departure_time')
    
    fieldsets = (
        ('Flight Information', {
            'fields': ('airline', 'flight_number', 'aircraft')
        }),
        ('Route', {
            'fields': ('origin', 'destination', 'layovers')
        }),
        ('Schedule', {
            'fields': ('departure_date', 'departure_time', 'arrival_date', 'arrival_time', 'duration')
        }),
        ('Capacity & Pricing', {
            'fields': ('total_seats', 'available_seats', 'price')
        }),
        ('Status', {
            'fields': ('is_active',)
        })
    )

@admin.register(Airport)
class AirportAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'city', 'country', 'is_active')
    list_filter = ('country', 'is_active')
    search_fields = ('code', 'name', 'city', 'country')
    list_editable = ('is_active',)
    ordering = ('city', 'name')

@admin.register(Airline)
class AirlineAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('name', 'code')
    list_editable = ('is_active',)
    ordering = ('name',)