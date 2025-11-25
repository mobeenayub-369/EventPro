from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.core.paginator import Paginator

from .models import SupportTicket, TicketResponse, FAQ
from .forms import SupportTicketForm, TicketResponseForm


# Support Dashboard View
@login_required
def support_dashboard(request):
    user_tickets = SupportTicket.objects.filter(user=request.user).order_by('-created_at')

    # Ticket statistics
    ticket_stats = {
        'total': user_tickets.count(),
        'open': user_tickets.filter(status='open').count(),
        'in_progress': user_tickets.filter(status='in_progress').count(),
        'resolved': user_tickets.filter(status='resolved').count(),
    }

    context = {
        'tickets': user_tickets[:5],  # Recent 5 tickets
        'ticket_stats': ticket_stats,
    }
    return render(request, 'support/support_dashboard.html', context)


# Create Support Ticket View
@login_required
def create_ticket(request):
    # Form Submit Handle
    if request.method == 'POST':
        form = SupportTicketForm(request.POST)
        if form.is_valid():
            ticket = form.save(commit=False)
            ticket.user = request.user
            ticket.save()

            messages.success(request, 'Support ticket created successfully! We will get back to you soon.')
            return redirect('support_ticket_detail', ticket_id=ticket.ticket_id)

    # Show blank form
    else:
        form = SupportTicketForm()

    return render(request, 'support/create_ticket.html', {'form': form})


# Ticket Detail View
@login_required
def ticket_detail(request, ticket_id):
    ticket = get_object_or_404(SupportTicket, ticket_id=ticket_id)

    # Check if user owns the ticket or is staff
    if not (request.user == ticket.user or request.user.is_staff):
        messages.error(request, 'You do not have permission to view this ticket.')
        return redirect('support_dashboard')

    # Handle response submission
    if request.method == 'POST':
        response_form = TicketResponseForm(request.POST, request.FILES)
        if response_form.is_valid():
            response = response_form.save(commit=False)
            response.ticket = ticket
            response.user = request.user

            # If staff is responding, update ticket status
            if request.user.is_staff and not response.is_internal_note:
                ticket.status = 'in_progress'
                ticket.assigned_to = request.user
                ticket.save()

            response.save()
            messages.success(request, 'Response added successfully!')
            return redirect('support_ticket_detail', ticket_id=ticket.ticket_id)

    else:
        response_form = TicketResponseForm()

    responses = ticket.responses.all().select_related('user')

    context = {
        'ticket': ticket,
        'responses': responses,
        'response_form': response_form,
    }
    return render(request, 'support/ticket_detail.html', context)


# My Tickets View
@login_required
def my_tickets(request):
    tickets = SupportTicket.objects.filter(user=request.user).order_by('-created_at')

    # Status filter
    status_filter = request.GET.get('status')
    if status_filter:
        tickets = tickets.filter(status=status_filter)

    # Pagination
    paginator = Paginator(tickets, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'status_filter': status_filter,
    }
    return render(request, 'support/my_tickets.html', context)


# FAQ List View
def faq_list(request):
    faqs = FAQ.objects.filter(is_active=True).order_by('category', 'order')

    # Group FAQs by category
    faq_categories = {}
    for faq in faqs:
        if faq.category not in faq_categories:
            faq_categories[faq.category] = []
        faq_categories[faq.category].append(faq)

    context = {
        'faq_categories': faq_categories,
    }
    return render(request, 'support/faq_list.html', context)


# Staff Ticket List View (for support staff)
@login_required
def staff_ticket_list(request):
    if not request.user.is_staff:
        messages.error(request, 'Access denied. Staff permission required.')
        return redirect('support_dashboard')

    tickets = SupportTicket.objects.all().order_by('-created_at').select_related('user')

    # Status filter
    status_filter = request.GET.get('status')
    if status_filter:
        tickets = tickets.filter(status=status_filter)

    # Priority filter
    priority_filter = request.GET.get('priority')
    if priority_filter:
        tickets = tickets.filter(priority=priority_filter)

    # Assigned to me filter
    assigned_to_me = request.GET.get('assigned_to_me')
    if assigned_to_me:
        tickets = tickets.filter(assigned_to=request.user)

    # Pagination
    paginator = Paginator(tickets, 15)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'status_filter': status_filter,
        'priority_filter': priority_filter,
        'assigned_to_me': assigned_to_me,
    }
    return render(request, 'support/staff_ticket_list.html', context)