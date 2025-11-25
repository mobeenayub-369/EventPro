from django.db import models
from django.contrib.auth import get_user_model
from django.urls import reverse

# User Model Setup
User = get_user_model()


class SupportTicket(models.Model):
    TICKET_STATUS = [
        ('open', 'Open'),
        ('in_progress', 'In Progress'),
        ('resolved', 'Resolved'),
        ('closed', 'Closed'),
    ]

    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    ]

    TICKET_TYPE = [
        ('technical', 'Technical Issue'),
        ('billing', 'Billing/Payment'),
        ('event', 'Event Related'),
        ('account', 'Account Issue'),
        ('general', 'General Inquiry'),
        ('other', 'Other'),
    ]

    ticket_id = models.CharField(max_length=20, unique=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='support_tickets')
    subject = models.CharField(max_length=200)
    description = models.TextField()
    ticket_type = models.CharField(max_length=20, choices=TICKET_TYPE, default='general')
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='medium')
    status = models.CharField(max_length=20, choices=TICKET_STATUS, default='open')
    assigned_to = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                                    related_name='assigned_tickets')
    is_resolved = models.BooleanField(default=False)
    resolution_notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    resolved_at = models.DateTimeField(null=True, blank=True)

    # Admin Panel Configuration
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Support Ticket'
        verbose_name_plural = 'Support Tickets'

    # Show ticket ID to Admin panel & Python
    def __str__(self):
        return f"{self.ticket_id} - {self.subject}"

    # Generate detail page URL of Ticket
    def get_absolute_url(self):
        return reverse('support_ticket_detail', kwargs={'ticket_id': self.ticket_id})

    # Save method to generate ticket ID
    def save(self, *args, **kwargs):
        if not self.ticket_id:
            last_ticket = SupportTicket.objects.order_by('-id').first()
            last_id = int(last_ticket.ticket_id[3:]) if last_ticket else 0
            self.ticket_id = f"TKT{last_id + 1:06d}"
        super().save(*args, **kwargs)


class TicketResponse(models.Model):
    ticket = models.ForeignKey(SupportTicket, on_delete=models.CASCADE, related_name='responses')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField()
    attachment = models.FileField(upload_to='support/attachments/', blank=True, null=True)
    is_internal_note = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    # Admin Panel Configuration
    class Meta:
        ordering = ['created_at']
        verbose_name = 'Ticket Response'
        verbose_name_plural = 'Ticket Responses'

    def __str__(self):
        return f"Response to {self.ticket.ticket_id}"


class FAQ(models.Model):
    CATEGORY_CHOICES = [
        ('general', 'General'),
        ('technical', 'Technical'),
        ('billing', 'Billing & Payments'),
        ('events', 'Events'),
        ('account', 'Account'),
    ]

    question = models.CharField(max_length=300)
    answer = models.TextField()
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='general')
    is_active = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Admin Panel Configuration
    class Meta:
        ordering = ['order', 'created_at']
        verbose_name = 'FAQ'
        verbose_name_plural = 'FAQs'

    def __str__(self):
        return self.question