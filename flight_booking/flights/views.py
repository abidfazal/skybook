from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import JsonResponse
from datetime import date
from .models import Flight
from .forms import FlightSearchForm, FlightForm

def home(request):
    """Home page with flight search"""
    form = FlightSearchForm()
    flights = []
    search_performed = False
    
    if request.method == 'GET' and any(key in request.GET for key in ['origin', 'destination', 'departure_date']):
        form = FlightSearchForm(request.GET)
        if form.is_valid():
            search_performed = True
            origin = form.cleaned_data['origin']
            destination = form.cleaned_data['destination']
            departure_date = form.cleaned_data['departure_date']
            passengers = form.cleaned_data['passengers']
            
            # Search for flights
            flights = Flight.objects.filter(
                origin__icontains=origin,
                destination__icontains=destination,
                departure_date=departure_date,
                available_seats__gte=passengers,
                is_active=True
            ).order_by('departure_time')
    
    # Get popular destinations for autocomplete
    popular_destinations = Flight.objects.filter(
        is_active=True,
        departure_date__gte=date.today()
    ).values_list('destination', flat=True).distinct()[:10]
    
    popular_origins = Flight.objects.filter(
        is_active=True,
        departure_date__gte=date.today()
    ).values_list('origin', flat=True).distinct()[:10]
    
    context = {
        'form': form,
        'flights': flights,
        'search_performed': search_performed,
        'popular_destinations': popular_destinations,
        'popular_origins': popular_origins,
    }
    return render(request, 'flights/home.html', context)

def flight_detail(request, flight_id):
    """Flight detail view"""
    flight = get_object_or_404(Flight, id=flight_id, is_active=True)
    return render(request, 'flights/flight_detail.html', {'flight': flight})

@login_required
def is_admin(user):
    return user.is_admin or user.is_superuser

@user_passes_test(is_admin)
def admin_dashboard(request):
    """Admin dashboard with overview"""
    from bookings.models import Booking
    from django.db.models import Sum, Count
    
    # Statistics
    total_flights = Flight.objects.filter(is_active=True).count()
    total_bookings = Booking.objects.filter(status='confirmed').count()
    total_revenue = Booking.objects.filter(status='confirmed').aggregate(
        total=Sum('total_amount')
    )['total'] or 0
    
    # Recent bookings
    recent_bookings = Booking.objects.select_related('flight', 'user').order_by('-created_at')[:5]
    
    context = {
        'total_flights': total_flights,
        'total_bookings': total_bookings,
        'total_revenue': total_revenue,
        'recent_bookings': recent_bookings,
    }
    return render(request, 'flights/admin_dashboard.html', context)

@user_passes_test(is_admin)
def admin_flights(request):
    """Admin flight management"""
    flights = Flight.objects.all().order_by('-created_at')
    
    # Search functionality
    search_query = request.GET.get('search', '')
    if search_query:
        flights = flights.filter(
            Q(flight_number__icontains=search_query) |
            Q(airline__icontains=search_query) |
            Q(origin__icontains=search_query) |
            Q(destination__icontains=search_query)
        )
    
    # Pagination
    paginator = Paginator(flights, 20)
    page_number = request.GET.get('page')
    flights = paginator.get_page(page_number)
    
    context = {
        'flights': flights,
        'search_query': search_query,
    }
    return render(request, 'flights/admin_flights.html', context)

@user_passes_test(is_admin)
def admin_flight_add(request):
    """Add new flight"""
    if request.method == 'POST':
        form = FlightForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Flight added successfully!')
            return redirect('flights:admin_flights')
    else:
        form = FlightForm()
    
    return render(request, 'flights/admin_flight_form.html', {
        'form': form,
        'title': 'Add New Flight'
    })

@user_passes_test(is_admin)
def admin_flight_edit(request, flight_id):
    """Edit existing flight"""
    flight = get_object_or_404(Flight, id=flight_id)
    
    if request.method == 'POST':
        form = FlightForm(request.POST, instance=flight)
        if form.is_valid():
            form.save()
            messages.success(request, 'Flight updated successfully!')
            return redirect('flights:admin_flights')
    else:
        form = FlightForm(instance=flight)
    
    return render(request, 'flights/admin_flight_form.html', {
        'form': form,
        'flight': flight,
        'title': 'Edit Flight'
    })

@user_passes_test(is_admin)
def admin_flight_delete(request, flight_id):
    """Delete flight"""
    flight = get_object_or_404(Flight, id=flight_id)
    
    if request.method == 'POST':
        flight.delete()
        messages.success(request, 'Flight deleted successfully!')
        return redirect('flights:admin_flights')
    
    return render(request, 'flights/admin_flight_delete.html', {'flight': flight})

def autocomplete_cities(request):
    """AJAX endpoint for city autocomplete"""
    term = request.GET.get('term', '')
    if len(term) >= 2:
        origins = Flight.objects.filter(
            origin__icontains=term,
            is_active=True
        ).values_list('origin', flat=True).distinct()[:10]
        
        destinations = Flight.objects.filter(
            destination__icontains=term,
            is_active=True
        ).values_list('destination', flat=True).distinct()[:10]
        
        cities = list(set(list(origins) + list(destinations)))
        return JsonResponse(cities, safe=False)
    
    return JsonResponse([], safe=False)