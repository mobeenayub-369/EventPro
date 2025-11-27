from django import forms


class AdvancedSearchForm(forms.Form):
    query = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'What are you looking for?',
            'id': 'search-input'
        })
    )

    category = forms.ChoiceField(
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    min_price = forms.DecimalField(
        required=False,
        min_value=0,
        max_digits=10,
        decimal_places=2,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Min price'
        })
    )

    max_price = forms.DecimalField(
        required=False,
        min_value=0,
        max_digits=10,
        decimal_places=2,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Max price'
        })
    )

    date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        })
    )

    location = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'City or location'
        })
    )

    SORT_CHOICES = [
        ('relevance', 'Relevance'),
        ('price_low', 'Price: Low to High'),
        ('price_high', 'Price: High to Low'),
        ('date', 'Event Date'),
        ('rating', 'Highest Rated'),
        ('popular', 'Most Popular'),
    ]

    sort_by = forms.ChoiceField(
        choices=SORT_CHOICES,
        initial='relevance',
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    def __init__(self, *args, **kwargs):
        from categories.models import Category
        super().__init__(*args, **kwargs)

        # Dynamic categories
        categories = Category.objects.all()
        category_choices = [('', 'All Categories')] + [(cat.slug, cat.name) for cat in categories]
        self.fields['category'].choices = category_choices