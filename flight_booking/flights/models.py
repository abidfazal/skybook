from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

class Flight(models.Model):
    airline = models.CharField(max_length=100)
    flight_number = models.CharField(max_length=20, unique=True)
    origin = models.CharField(max_length=100)
    destination = models.CharField(max_length=100)
    departure_time = models.TimeField()
    arrival_time = models.TimeField()
    departure_date = models.DateField()
    arrival_date = models.DateField()
    duration = models.CharField(max_length=20)
    price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    total_seats = models.PositiveIntegerField(validators=[MinValueValidator(1), MaxValueValidator(500)])
    available_seats = models.PositiveIntegerField(validators=[MinValueValidator(0)])
    aircraft = models.CharField(max_length=100)
    layovers = models.TextField(blank=True, help_text="Comma-separated list of layover cities")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['departure_date', 'departure_time']
        indexes = [
            models.Index(fields=['origin', 'destination', 'departure_date']),
            models.Index(fields=['departure_date']),
            models.Index(fields=['is_active']),
        ]

    def __str__(self):
        return f"{self.airline} {self.flight_number} - {self.origin} to {self.destination}"

    @property
    def layover_list(self):
        """Return layovers as a list"""
        if self.layovers:
            return [layover.strip() for layover in self.layovers.split(',') if layover.strip()]
        return []

    @property
    def is_direct(self):
        """Check if flight is direct (no layovers)"""
        return len(self.layover_list) == 0

    @property
    def seats_booked(self):
        """Calculate number of seats booked"""
        return self.total_seats - self.available_seats

    @property
    def occupancy_rate(self):
        """Calculate occupancy rate as percentage"""
        if self.total_seats > 0:
            return (self.seats_booked / self.total_seats) * 100
        return 0

    def clean(self):
        from django.core.exceptions import ValidationError
        if self.available_seats > self.total_seats:
            raise ValidationError('Available seats cannot exceed total seats.')

class Airport(models.Model):
    """Model to store airport information"""
    code = models.CharField(max_length=10, unique=True)
    name = models.CharField(max_length=200)
    city = models.CharField(max_length=100)
    country = models.CharField(max_length=100)
    timezone = models.CharField(max_length=50, default='UTC')
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['city', 'name']

    def __str__(self):
        return f"{self.city} ({self.code})"

class Airline(models.Model):
    """Model to store airline information"""
    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=10, unique=True)
    logo = models.ImageField(upload_to='airlines/', blank=True, null=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name