from django.contrib import admin
from .models import SearchQuery, PopularSearch, SearchFilter

@admin.register(SearchQuery)
class SearchQueryAdmin(admin.ModelAdmin):
    list_display = ['query', 'user', 'results_count', 'ip_address', 'created_at']
    list_filter = ['created_at', 'user']
    search_fields = ['query', 'user__username']
    readonly_fields = ['created_at']
    list_per_page = 20

@admin.register(PopularSearch)
class PopularSearchAdmin(admin.ModelAdmin):
    list_display = ['query', 'search_count', 'last_searched']
    list_filter = ['last_searched']
    search_fields = ['query']
    readonly_fields = ['last_searched']
    list_editable = ['search_count']

@admin.register(SearchFilter)
class SearchFilterAdmin(admin.ModelAdmin):
    list_display = ['search_query', 'filter_type', 'filter_value']
    list_filter = ['filter_type']
    search_fields = ['filter_value', 'search_query__query']