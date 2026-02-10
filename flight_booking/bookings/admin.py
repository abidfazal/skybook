from django.contrib import admin
from .models import Booking, Passenger, Payment

class PassengerInline(admin.TabularInline):
    model = Passenger
    extra = 0
    readonly_fields = ('created_at',)

class PaymentInline(admin.StackedInline):
    model = Payment
    extra = 0
    readonly_fields = ('created_at', 'processed_at')

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('confirmation_code', 'user', 'flight', 'status', 'total_amount', 'created_at')
    list_filter = ('status', 'created_at', 'flight__airline')
    search_fields = ('confirmation_code', 'user__email', 'user__first_name', 'user__last_name', 
                    'flight__flight_number', 'flight__airline')
    readonly_fields = ('id', 'confirmation_code', 'created_at', 'updated_at')
    inlines = [PassengerInline, PaymentInline]
    date_hierarchy = 'created_at'
    ordering = ('-created_at',)
    
    fieldsets = (
        ('Booking Information', {
            'fields': ('id', 'confirmation_code', 'user', 'flight', 'status')
        }),
        ('Payment', {
            'fields': ('total_amount', 'payment_method', 'payment_reference')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )

@admin.register(Passenger)
class PassengerAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'booking', 'email', 'phone', 'date_of_birth')
    list_filter = ('booking__status', 'created_at')
    search_fields = ('first_name', 'last_name', 'email', 'booking__confirmation_code')
    readonly_fields = ('created_at',)

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('transaction_id', 'booking', 'amount', 'payment_method', 'status', 'created_at')
    list_filter = ('status', 'payment_method', 'created_at')
    search_fields = ('transaction_id', 'booking__confirmation_code')
    readonly_fields = ('created_at', 'processed_at')