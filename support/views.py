from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.db.models import Q, Count
from django.utils import timezone
from django.contrib.auth.models import User

from .models import SupportCategory, SupportTicket, TicketResponse, FAQ, KnowledgeBaseArticle
from .forms import SupportTicketForm, TicketResponseForm, KnowledgeBaseForm


@login_required
def support_dashboard(request):
    """User support dashboard"""
    user_tickets = SupportTicket.objects.filter(user=request.user).order_by('-created_at')

    # Statistics
    open_tickets = user_tickets.filter(status__in=['open', 'in_progress', 'waiting_customer']).count()
    resolved_tickets = user_tickets.filter(status='resolved').count()
    total_tickets = user_tickets.count()

    # Recent tickets
    recent_tickets = user_tickets[:5]

    context = {
        'open_tickets': open_tickets,
        'resolved_tickets': resolved_tickets,
        'total_tickets': total_tickets,
        'recent_tickets': recent_tickets,
    }
    return render(request, 'support/dashboard.html', context)


@login_required
def create_ticket(request):
    """Create new support ticket"""
    if request.method == 'POST':
        form = SupportTicketForm(request.POST, request.FILES)
        if form.is_valid():
            ticket = form.save(commit=False)
            ticket.user = request.user
            ticket.save()

            messages.success(request,
                             f'Ticket #{ticket.ticket_id} created successfully! We will respond within 24 hours.')
            return redirect('support:ticket_detail', ticket_id=ticket.ticket_id)
    else:
        form = SupportTicketForm()

    categories = SupportCategory.objects.filter(is_active=True)

    context = {
        'form': form,
        'categories': categories,
    }
    return render(request, 'support/create_ticket.html', context)


@login_required
def ticket_list(request):
    """User's ticket list"""
    tickets = SupportTicket.objects.filter(user=request.user).order_by('-created_at')

    # Status filter
    status_filter = request.GET.get('status', '')
    if status_filter:
        tickets = tickets.filter(status=status_filter)

    # Pagination
    paginator = Paginator(tickets, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'tickets': page_obj,
        'status_filter': status_filter,
    }
    return render(request, 'support/ticket_list.html', context)


@login_required
def ticket_detail(request, ticket_id):
    """Ticket detail with responses"""
    ticket = get_object_or_404(SupportTicket, ticket_id=ticket_id, user=request.user)

    if request.method == 'POST':
        form = TicketResponseForm(request.POST, request.FILES)
        if form.is_valid():
            response = form.save(commit=False)
            response.ticket = ticket
            response.user = request.user
            response.save()

            # Update ticket status
            ticket.status = 'waiting_customer'
            ticket.updated_at = timezone.now()
            ticket.save()

            messages.success(request, 'Response added successfully!')
            return redirect('support:ticket_detail', ticket_id=ticket.ticket_id)
    else:
        form = TicketResponseForm()

    responses = ticket.responses.all().order_by('created_at')

    context = {
        'ticket': ticket,
        'responses': responses,
        'form': form,
    }
    return render(request, 'support/ticket_detail.html', context)


def knowledgebase(request):
    """Knowledge base articles"""
    categories = SupportCategory.objects.filter(is_active=True, articles__is_published=True).distinct()
    popular_articles = KnowledgeBaseArticle.objects.filter(
        is_published=True
    ).order_by('-views')[:10]

    context = {
        'categories': categories,
        'popular_articles': popular_articles,
    }
    return render(request, 'support/knowledgebase.html', context)


def knowledgebase_category(request, category_slug):
    """Knowledge base articles by category"""
    category = get_object_or_404(SupportCategory, slug=category_slug, is_active=True)
    articles = KnowledgeBaseArticle.objects.filter(
        category=category,
        is_published=True
    ).order_by('-created_at')

    context = {
        'category': category,
        'articles': articles,
    }
    return render(request, 'support/knowledgebase_category.html', context)


def knowledgebase_article(request, slug):
    """Single knowledge base article"""
    article = get_object_or_404(KnowledgeBaseArticle, slug=slug, is_published=True)

    # Increment views
    article.views += 1
    article.save()

    context = {
        'article': article,
    }
    return render(request, 'support/knowledgebase_article.html', context)


def faq_list(request):
    """FAQ list"""
    categories = SupportCategory.objects.filter(is_active=True, faqs__is_active=True).distinct()

    context = {
        'categories': categories,
    }
    return render(request, 'support/faq_list.html', context)


# Admin Views
@login_required
def admin_ticket_list(request):
    """Admin ticket management"""
    if not request.user.is_staff:
        messages.error(request, 'Access denied.')
        return redirect('support:support_dashboard')

    tickets = SupportTicket.objects.all().order_by('-created_at')

    # Filters
    status_filter = request.GET.get('status', '')
    priority_filter = request.GET.get('priority', '')

    if status_filter:
        tickets = tickets.filter(status=status_filter)
    if priority_filter:
        tickets = tickets.filter(priority=priority_filter)

    # Statistics
    ticket_stats = {
        'open': tickets.filter(status='open').count(),
        'in_progress': tickets.filter(status='in_progress').count(),
        'total': tickets.count(),
    }

    # Pagination
    paginator = Paginator(tickets, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'tickets': page_obj,
        'ticket_stats': ticket_stats,
        'status_filter': status_filter,
        'priority_filter': priority_filter,
    }
    return render(request, 'support/admin_ticket_list.html', context)


@login_required
def admin_ticket_detail(request, ticket_id):
    """Admin ticket detail"""
    if not request.user.is_staff:
        messages.error(request, 'Access denied.')
        return redirect('support:support_dashboard')

    ticket = get_object_or_404(SupportTicket, ticket_id=ticket_id)

    if request.method == 'POST':
        form = TicketResponseForm(request.POST, request.FILES)
        if form.is_valid():
            response = form.save(commit=False)
            response.ticket = ticket
            response.user = request.user

            # Check if internal note
            is_internal = request.POST.get('is_internal', False)
            response.is_internal_note = bool(is_internal)

            response.save()

            # Update ticket status if not internal note
            if not response.is_internal_note:
                ticket.status = 'in_progress'
                ticket.assigned_to = request.user
                ticket.updated_at = timezone.now()
                ticket.save()

            messages.success(request, 'Response added successfully!')
            return redirect('support:admin_ticket_detail', ticket_id=ticket.ticket_id)
    else:
        form = TicketResponseForm()

    responses = ticket.responses.all().order_by('created_at')

    context = {
        'ticket': ticket,
        'responses': responses,
        'form': form,
    }
    return render(request, 'support/admin_ticket_detail.html', context)


@login_required
def update_ticket_status(request, ticket_id):
    """Update ticket status (AJAX)"""
    if not request.user.is_staff:
        return JsonResponse({'success': False, 'message': 'Access denied.'})

    if request.method == 'POST':
        ticket = get_object_or_404(SupportTicket, ticket_id=ticket_id)
        new_status = request.POST.get('status')
        assigned_to = request.POST.get('assigned_to')

        if new_status in dict(SupportTicket.TICKET_STATUS_CHOICES):
            ticket.status = new_status

            if new_status == 'resolved':
                ticket.resolved_at = timezone.now()

            if assigned_to:
                try:
                    user = User.objects.get(id=assigned_to)
                    ticket.assigned_to = user
                except User.DoesNotExist:
                    pass

            ticket.save()

            return JsonResponse({'success': True, 'message': 'Ticket status updated successfully.'})

    return JsonResponse({'success': False, 'message': 'Invalid request.'})