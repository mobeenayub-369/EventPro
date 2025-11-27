from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView, DetailView
from .models import Category


class CategoryListView(ListView):
    """
    View to display all active categories in a list format.
    Only shows categories that are marked as active.
    """

    model = Category
    template_name = 'categories/category_list.html'
    context_object_name = 'categories'  # Variable name in template

    def get_queryset(self):
        """
        Override to return only active categories, ordered by name.
        """
        return Category.objects.filter(is_active=True).order_by('name')


class CategoryDetailView(DetailView):
    """
    View to display detailed information about a specific category.
    Shows category details and will eventually show events in this category.
    """

    model = Category
    template_name = 'categories/category_detail.html'
    context_object_name = 'category'  # Variable name in template

    def get_queryset(self):
        """
        Override to return only active categories.
        Prevents access to inactive categories via direct URL.
        """
        return Category.objects.filter(is_active=True)

    def get_context_data(self, **kwargs):
        """
        Add additional context data to the template.
        Currently prepares for future integration with events.
        """
        context = super().get_context_data(**kwargs)
        category = self.get_object()

        # TODO: Add related events when events app is integrated
        # context['events'] = category.event_set.filter(is_active=True)

        return context