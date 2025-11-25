from django import forms
from .models import Wishlist, WishlistItem


# Wishlist item form (for adding events to wishlist)
class WishlistItemForm(forms.ModelForm):
    class Meta:
        model = WishlistItem
        fields = ['event']

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        # Limit events to active events only
        if self.user:
            from events.models import Event
            self.fields['event'].queryset = Event.objects.filter(is_active=True)

    def clean(self):
        cleaned_data = super().clean()
        event = cleaned_data.get('event')

        # Check if event is already in user's wishlist
        if event and self.user:
            if WishlistItem.objects.filter(wishlist=self.user.wishlist, event=event).exists():
                raise forms.ValidationError('This event is already in your wishlist.')

        return cleaned_data

    def save(self, commit=True):
        instance = super().save(commit=False)
        if self.user:
            instance.wishlist = self.user.wishlist
        if commit:
            instance.save()
        return instance