from django import forms


# Search Filter Form
class SearchFilterForm(forms.Form):
    SORT_CHOICES = [
        ('relevance', 'Relevance'),
        ('date_asc', 'Date (Oldest First)'),
        ('date_desc', 'Date (Newest First)'),
        ('price_asc', 'Price (Low to High)'),
        ('price_desc', 'Price (High to Low)'),
        ('popular', 'Most Popular'),
    ]

    EVENT_TYPE_CHOICES = [
        ('', 'All Events'),
        ('free', 'Free Events'),
        ('paid', 'Paid Events'),
        ('featured', 'Featured Events'),
    ]

    # Search query
    q = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'placeholder': 'Search events, categories, locations...',
            'class': 'search-input'
        })
    )

    # Filters
    category = forms.ChoiceField(
        required=False,
        choices=[],
        widget=forms.Select(attrs={'class': 'filter-select'})
    )

    location = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'placeholder': 'City or venue...',
            'class': 'filter-input'
        })
    )

    date_from = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'filter-input'
        })
    )

    date_to = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'filter-input'
        })
    )

    price_min = forms.DecimalField(
        required=False,
        min_value=0,
        widget=forms.NumberInput(attrs={
            'placeholder': 'Min price',
            'class': 'filter-input',
            'step': '0.01'
        })
    )

    price_max = forms.DecimalField(
        required=False,
        min_value=0,
        widget=forms.NumberInput(attrs={
            'placeholder': 'Max price',
            'class': 'filter-input',
            'step': '0.01'
        })
    )

    event_type = forms.ChoiceField(
        required=False,
        choices=EVENT_TYPE_CHOICES,
        widget=forms.Select(attrs={'class': 'filter-select'})
    )

    sort_by = forms.ChoiceField(
        required=False,
        choices=SORT_CHOICES,
        widget=forms.Select(attrs={'class': 'filter-select'})
    )

    def __init__(self, *args, **kwargs):
        categories = kwargs.pop('categories', [])
        super().__init__(*args, **kwargs)

        # Set dynamic category choices
        category_choices = [('', 'All Categories')]
        category_choices.extend([(cat.slug, cat.name) for cat in categories])
        self.fields['category'].choices = category_choices