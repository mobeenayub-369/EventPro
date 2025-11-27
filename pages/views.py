from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.db.models import Q

from .models import Page, FAQ, ContactSubmission
from .forms import PageForm, ContactForm, FAQForm


# Public Views
def page_detail(request, slug):
    """Dynamic page detail view - for page_detail.html"""
    page = get_object_or_404(Page, slug=slug, is_active=True)

    context = {
        'page': page,
    }
    return render(request, 'pages/page_detail.html', context)


def faq_list(request):
    """FAQ page"""
    faqs = FAQ.objects.filter(is_active=True)

    # Group by category
    categories = {}
    for faq in faqs:
        if faq.category not in categories:
            categories[faq.category] = []
        categories[faq.category].append(faq)

    context = {
        'categories': categories,
    }
    return render(request, 'pages/faq.html', context)


def contact(request):
    """Contact Us page"""
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            submission = form.save(commit=False)
            submission.ip_address = get_client_ip(request)
            submission.user_agent = request.META.get('HTTP_USER_AGENT', '')
            submission.save()

            messages.success(request, 'Thank you for your message! We will get back to you within 24 hours.')
            return redirect('pages:contact')
    else:
        form = ContactForm()

    context = {
        'form': form,
    }
    return render(request, 'pages/contact.html', context)


# Admin Views
@login_required
@user_passes_test(lambda u: u.is_staff)
def page_list(request):
    """Page list for admin - for page_list.html"""
    pages = Page.objects.all().order_by('order', 'title')

    # Filter by type
    page_type = request.GET.get('type', '')
    if page_type:
        pages = pages.filter(page_type=page_type)

    context = {
        'pages': pages,
        'page_type_filter': page_type,
    }
    return render(request, 'pages/page_list.html', context)


@login_required
@user_passes_test(lambda u: u.is_staff)
def create_page(request):
    """Create new page - for create_page.html"""
    if request.method == 'POST':
        form = PageForm(request.POST)
        if form.is_valid():
            page = form.save(commit=False)
            page.created_by = request.user
            page.updated_by = request.user
            page.save()

            messages.success(request, f'Page "{page.title}" created successfully!')
            return redirect('pages:page_list')
    else:
        form = PageForm()

    context = {
        'form': form,
        'title': 'Create New Page'
    }
    return render(request, 'pages/create_page.html', context)


@login_required
@user_passes_test(lambda u: u.is_staff)
def edit_page(request, slug):
    """Edit page - for edit_page.html"""
    page = get_object_or_404(Page, slug=slug)

    if request.method == 'POST':
        form = PageForm(request.POST, instance=page)
        if form.is_valid():
            updated_page = form.save(commit=False)
            updated_page.updated_by = request.user
            updated_page.save()

            messages.success(request, f'Page "{updated_page.title}" updated successfully!')
            return redirect('pages:page_list')
    else:
        form = PageForm(instance=page)

    context = {
        'form': form,
        'page': page,
        'title': f'Edit {page.title}'
    }
    return render(request, 'pages/edit_page.html', context)


@login_required
@user_passes_test(lambda u: u.is_staff)
def delete_page(request, slug):
    """Delete page - for delete_page.html"""
    page = get_object_or_404(Page, slug=slug)

    if request.method == 'POST':
        page_title = page.title
        page.delete()
        messages.success(request, f'Page "{page_title}" deleted successfully!')
        return redirect('pages:page_list')

    context = {
        'page': page,
    }
    return render(request, 'pages/delete_page.html', context)


# FAQ Management
@login_required
@user_passes_test(lambda u: u.is_staff)
def faq_management(request):
    """FAQ management for admin"""
    faqs = FAQ.objects.all().order_by('category', 'order')

    category_filter = request.GET.get('category', '')
    if category_filter:
        faqs = faqs.filter(category=category_filter)

    if request.method == 'POST':
        form = FAQForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'FAQ added successfully!')
            return redirect('pages:faq_management')
    else:
        form = FAQForm()

    # Get unique categories
    categories = FAQ.objects.values_list('category', flat=True).distinct()

    context = {
        'faqs': faqs,
        'form': form,
        'categories': categories,
        'category_filter': category_filter,
    }
    return render(request, 'pages/faq_management.html', context)


@login_required
@user_passes_test(lambda u: u.is_staff)
def contact_submissions(request):
    """Contact submissions management"""
    submissions = ContactSubmission.objects.all().order_by('-created_at')

    status_filter = request.GET.get('status', '')
    if status_filter:
        submissions = submissions.filter(status=status_filter)

    # Pagination
    paginator = Paginator(submissions, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'submissions': page_obj,
        'status_filter': status_filter,
    }
    return render(request, 'pages/contact_submissions.html', context)


@login_required
@user_passes_test(lambda u: u.is_staff)
def update_submission_status(request, submission_id):
    """Update contact submission status"""
    if request.method == 'POST':
        submission = get_object_or_404(ContactSubmission, id=submission_id)
        new_status = request.POST.get('status')

        if new_status in dict(ContactSubmission.STATUS_CHOICES):
            submission.status = new_status
            submission.save()

            return JsonResponse({'success': True, 'message': 'Status updated successfully!'})

    return JsonResponse({'success': False, 'message': 'Invalid request.'})


# Utility functions
def get_client_ip(request):
    """Get client IP address"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip