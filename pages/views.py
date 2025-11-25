from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.http import Http404
from .models import Page
from .forms import PageForm


# Check if user is staff (for page management)
def staff_required(function):
    return user_passes_test(lambda u: u.is_staff)(function)


# Public page detail view
def page_detail(request, slug):
    try:
        # Get published page only
        page = get_object_or_404(Page, slug=slug, status='published')

        # Prepare context
        context = {
            'page': page,
            'title': page.title,
        }

        return render(request, 'pages/page_detail.html', context)

    except Http404:
        # Handle non-existent or unpublished pages
        messages.error(request, "The requested page was not found.")
        return redirect('home')


# Page list view (for staff only)
@staff_required
@login_required
def page_list(request):
    # Get all pages for staff
    pages = Page.objects.all()

    context = {
        'pages': pages,
        'title': 'Manage Pages'
    }

    return render(request, 'pages/page_list.html', context)


# Create new page
@staff_required
@login_required
def create_page(request):
    if request.method == 'POST':
        # Process form submission
        form = PageForm(request.POST, user=request.user)

        if form.is_valid():
            page = form.save(commit=False)
            page.created_by = request.user
            page.save()

            messages.success(request, f'Page "{page.title}" created successfully!')
            return redirect('page_list')
    else:
        # Display empty form
        form = PageForm(user=request.user)

    context = {
        'form': form,
        'title': 'Create New Page'
    }

    return render(request, 'pages/create_page.html', context)


# Edit existing page
@staff_required
@login_required
def edit_page(request, slug):
    # Get page object
    page = get_object_or_404(Page, slug=slug)

    if request.method == 'POST':
        # Process form submission
        form = PageForm(request.POST, instance=page, user=request.user)

        if form.is_valid():
            form.save()
            messages.success(request, f'Page "{page.title}" updated successfully!')
            return redirect('page_list')
    else:
        # Display pre-filled form
        form = PageForm(instance=page, user=request.user)

    context = {
        'form': form,
        'page': page,
        'title': f'Edit {page.title}'
    }

    return render(request, 'pages/edit_page.html', context)


# Delete page
@staff_required
@login_required
def delete_page(request, slug):
    # Get page object
    page = get_object_or_404(Page, slug=slug)

    if request.method == 'POST':
        # Confirm deletion
        page_title = page.title
        page.delete()

        messages.success(request, f'Page "{page_title}" deleted successfully!')
        return redirect('page_list')

    context = {
        'page': page,
        'title': f'Delete {page.title}'
    }

    return render(request, 'pages/delete_page.html', context)