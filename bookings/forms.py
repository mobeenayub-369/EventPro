from django import forms
from .models import Booking, BookingTicket

# Booking Form (Meta class & Widget customization)
class BookingForm(forms.ModelForm):
    class Meta:
        model= Booking
        fields= ['ticket_count', 'special_requests']
        widgets= {
            'special_requests': forms.Textarea(attrs= {
                'rows': 4,
                'palceholder': 'Any special requirements or requests...'
            }),
            'ticket_count': forms.TextInput(attrs= {
                'min': 1,
                'max': 10
            })
        }


# Ticket Booking Form
class TicketBookingForm(forms.Form):
    ticket_type= forms.ChoiceField(choices=[])
    quantity= forms.IntegerField(min_value=1, max_value=10, initial=1)

# Custom init Method
    def __init__(self, *args, **kwargs):
        ticket_choices= kwargs.pop('ticket_choices',[])
        super().__init__(*args, **kwargs)
        self.fields['ticket_type'].choices= ticket_choices
