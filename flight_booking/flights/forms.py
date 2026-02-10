from django import forms
from datetime import date, timedelta
from .models import Flight

class FlightSearchForm(forms.Form):
    TRIP_CHOICES = [
        ('one-way', 'One Way'),
        ('round-trip', 'Round Trip'),
    ]
    
    origin = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'From where?',
            'list': 'origins'
        })
    )
    destination = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Where to?',
            'list': 'destinations'
        })
    )
    departure_date = forms.DateField(
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date',
            'min': date.today().isoformat()
        })
    )
    return_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date',
            'min': date.today().isoformat()
        })
    )
    passengers = forms.IntegerField(
        min_value=1,
        max_value=9,
        initial=1,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'min': '1',
            'max': '9'
        })
    )
    trip_type = forms.ChoiceField(
        choices=TRIP_CHOICES,
        initial='one-way',
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    def clean(self):
        cleaned_data = super().clean()
        departure_date = cleaned_data.get('departure_date')
        return_date = cleaned_data.get('return_date')
        trip_type = cleaned_data.get('trip_type')

        if departure_date and departure_date < date.today():
            raise forms.ValidationError("Departure date cannot be in the past.")

        if trip_type == 'round-trip':
            if not return_date:
                raise forms.ValidationError("Return date is required for round trip.")
            if return_date and departure_date and return_date <= departure_date:
                raise forms.ValidationError("Return date must be after departure date.")

        return cleaned_data

class FlightForm(forms.ModelForm):
    class Meta:
        model = Flight
        fields = ['airline', 'flight_number', 'origin', 'destination', 
                 'departure_date', 'departure_time', 'arrival_date', 'arrival_time',
                 'duration', 'price', 'total_seats', 'available_seats', 
                 'aircraft', 'layovers', 'is_active']
        widgets = {
            'airline': forms.TextInput(attrs={'class': 'form-control'}),
            'flight_number': forms.TextInput(attrs={'class': 'form-control'}),
            'origin': forms.TextInput(attrs={'class': 'form-control'}),
            'destination': forms.TextInput(attrs={'class': 'form-control'}),
            'departure_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'departure_time': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'arrival_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'arrival_time': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'duration': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., 5h 30m'}),
            'price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'total_seats': forms.NumberInput(attrs={'class': 'form-control'}),
            'available_seats': forms.NumberInput(attrs={'class': 'form-control'}),
            'aircraft': forms.TextInput(attrs={'class': 'form-control'}),
            'layovers': forms.Textarea(attrs={
                'class': 'form-control', 
                'rows': 3,
                'placeholder': 'Comma-separated list of layover cities (optional)'
            }),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        departure_date = cleaned_data.get('departure_date')
        arrival_date = cleaned_data.get('arrival_date')
        departure_time = cleaned_data.get('departure_time')
        arrival_time = cleaned_data.get('arrival_time')
        total_seats = cleaned_data.get('total_seats')
        available_seats = cleaned_data.get('available_seats')

        if departure_date and arrival_date and departure_date > arrival_date:
            raise forms.ValidationError("Arrival date cannot be before departure date.")

        if (departure_date and arrival_date and departure_time and arrival_time and 
            departure_date == arrival_date and departure_time >= arrival_time):
            raise forms.ValidationError("Arrival time must be after departure time on the same day.")

        if total_seats and available_seats and available_seats > total_seats:
            raise forms.ValidationError("Available seats cannot exceed total seats.")

        return cleaned_data