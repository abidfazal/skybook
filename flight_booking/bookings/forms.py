from django import forms
from django.forms import formset_factory
from .models import Booking, Passenger

class PassengerForm(forms.ModelForm):
    class Meta:
        model = Passenger
        fields = ['first_name', 'last_name', 'email', 'phone', 'date_of_birth', 'passport_number']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'First name'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Last name'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email address'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Phone number'}),
            'date_of_birth': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'passport_number': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'Passport number (optional)'
            }),
        }

PassengerFormSet = formset_factory(PassengerForm, extra=1, min_num=1, validate_min=True)

class PaymentForm(forms.Form):
    card_number = forms.CharField(
        max_length=19,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '1234 5678 9012 3456',
            'pattern': '[0-9\s]{13,19}',
            'maxlength': '19'
        })
    )
    expiry_date = forms.CharField(
        max_length=5,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'MM/YY',
            'pattern': '[0-9]{2}/[0-9]{2}',
            'maxlength': '5'
        })
    )
    cvv = forms.CharField(
        max_length=4,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '123',
            'pattern': '[0-9]{3,4}',
            'maxlength': '4'
        })
    )
    name_on_card = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'John Doe'
        })
    )

    def clean_card_number(self):
        card_number = self.cleaned_data['card_number'].replace(' ', '')
        if not card_number.isdigit() or len(card_number) < 13:
            raise forms.ValidationError("Please enter a valid card number.")
        return card_number

    def clean_expiry_date(self):
        expiry = self.cleaned_data['expiry_date']
        if not expiry or len(expiry) != 5 or expiry[2] != '/':
            raise forms.ValidationError("Please enter expiry date in MM/YY format.")
        
        try:
            month, year = expiry.split('/')
            month, year = int(month), int(year)
            if month < 1 or month > 12:
                raise forms.ValidationError("Invalid month.")
            # Add basic future date validation
            from datetime import date
            current_year = date.today().year % 100
            if year < current_year or (year == current_year and month < date.today().month):
                raise forms.ValidationError("Card has expired.")
        except ValueError:
            raise forms.ValidationError("Please enter a valid expiry date.")
        
        return expiry

    def clean_cvv(self):
        cvv = self.cleaned_data['cvv']
        if not cvv.isdigit() or len(cvv) < 3:
            raise forms.ValidationError("Please enter a valid CVV.")
        return cvv