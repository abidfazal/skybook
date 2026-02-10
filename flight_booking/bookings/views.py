from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.db import transaction
from django.http import Http404
from django.core.paginator import Paginator
from flights.models import Flight
from .models import Booking, Passenger, Payment
from .forms import PassengerFormSet, PaymentForm
import uuid
from datetime import datetime

@login_required
def book_flight(request, flight_id):
    """Flight booking process"""
    flight = get_object_or_404(Flight, id=flight_id, is_active=True)
    passengers_count = int(request.GET.get('passengers', 1))
    
    if passengers_count > flight.available_seats:
        messages.error(request, 'Not enough seats available for this flight.')
        return redirect('flights:flight_detail', flight_id=flight.id)
    
    if request.method == 'POST':
        passenger_formset = PassengerFormSet(request.POST)
        payment_form = PaymentForm(request.POST)
        
        if passenger_formset.is_valid() and payment_form.is_valid():
            try:
                with transaction.atomic():
                    # Create booking
                    total_amount = flight.price * len(passenger_formset.forms)
                    booking = Booking.objects.create(
                        user=request.user,
                        flight=flight,
                        total_amount=total_amount,
                        status='confirmed',
                        payment_method=f"**** **** **** {payment_form.cleaned_data['card_number'][-4:]}"
                    )
                    
                    # Create passengers
                    for form in passenger_formset:
                        if form.cleaned_data:
                            passenger = form.save(commit=False)
                            passenger.booking = booking
                            passenger.save()
                    
                    # Create payment record
                    Payment.objects.create(
                        booking=booking,
                        amount=total_amount,
                        payment_method='Credit Card',
                        transaction_id=str(uuid.uuid4()),
                        status='completed',
                        processed_at=datetime.now()
                    )
                    
                    # Update flight availability
                    flight.available_seats -= len(passenger_formset.forms)
                    flight.save()
                    
                    messages.success(request, f'Booking confirmed! Your confirmation code is {booking.confirmation_code}')
                    return redirect('bookings:booking_confirmation', booking_id=booking.id)
                    
            except Exception as e:
                messages.error(request, 'An error occurred while processing your booking. Please try again.')
    else:
        # Initialize formset with the number of passengers
        passenger_formset = PassengerFormSet()
        # Adjust formset to match passenger count
        passenger_formset.extra = passengers_count
        payment_form = PaymentForm()
    
    context = {
        'flight': flight,
        'passenger_formset': passenger_formset,
        'payment_form': payment_form,
        'passengers_count': passengers_count,
        'total_amount': flight.price * passengers_count,
    }
    return render(request, 'bookings/book_flight.html', context)

@login_required
def booking_confirmation(request, booking_id):
    """Booking confirmation page"""
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)
    return render(request, 'bookings/booking_confirmation.html', {'booking': booking})

@login_required
def my_bookings(request):
    """User's booking history"""
    bookings = Booking.objects.filter(user=request.user).select_related('flight').order_by('-created_at')
    
    # Pagination
    paginator = Paginator(bookings, 10)
    page_number = request.GET.get('page')
    bookings = paginator.get_page(page_number)
    
    return render(request, 'bookings/my_bookings.html', {'bookings': bookings})

@login_required
def booking_detail(request, booking_id):
    """Detailed view of a specific booking"""
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)
    return render(request, 'bookings/booking_detail.html', {'booking': booking})

@login_required
def cancel_booking(request, booking_id):
    """Cancel a booking"""
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)
    
    if booking.status != 'confirmed':
        messages.error(request, 'This booking cannot be cancelled.')
        return redirect('bookings:booking_detail', booking_id=booking.id)
    
    if request.method == 'POST':
        with transaction.atomic():
            booking.status = 'cancelled'
            booking.save()
            
            # Return seats to flight
            booking.flight.available_seats += booking.passenger_count
            booking.flight.save()
            
            messages.success(request, 'Booking cancelled successfully.')
            return redirect('bookings:my_bookings')
    
    return render(request, 'bookings/cancel_booking.html', {'booking': booking})

def is_admin(user):
    return user.is_admin or user.is_superuser

@user_passes_test(is_admin)
def admin_bookings(request):
    """Admin view of all bookings"""
    bookings = Booking.objects.select_related('user', 'flight').order_by('-created_at')
    
    # Filter by status
    status_filter = request.GET.get('status')
    if status_filter:
        bookings = bookings.filter(status=status_filter)
    
    # Search functionality
    search_query = request.GET.get('search', '')
    if search_query:
        bookings = bookings.filter(
            models.Q(confirmation_code__icontains=search_query) |
            models.Q(user__email__icontains=search_query) |
            models.Q(user__first_name__icontains=search_query) |
            models.Q(user__last_name__icontains=search_query) |
            models.Q(flight__flight_number__icontains=search_query)
        )
    
    # Pagination
    paginator = Paginator(bookings, 20)
    page_number = request.GET.get('page')
    bookings = paginator.get_page(page_number)
    
    context = {
        'bookings': bookings,
        'status_filter': status_filter,
        'search_query': search_query,
        'status_choices': Booking.STATUS_CHOICES,
    }
    return render(request, 'bookings/admin_bookings.html', context)

@user_passes_test(is_admin)
def admin_booking_detail(request, booking_id):
    """Admin detailed view of a booking"""
    booking = get_object_or_404(Booking, id=booking_id)
    return render(request, 'bookings/admin_booking_detail.html', {'booking': booking})