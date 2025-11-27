from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class SupportCategory(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    order = models.IntegerField(default=0)

    class Meta:
        ordering = ['order', 'name']
        verbose_name = 'Support Category'
        verbose_name_plural = 'Support Categories'

    def __str__(self):
        return self.name


class SupportTicket(models.Model):
    TICKET_STATUS = (
        ('open', 'Open'),
        ('in_progress', 'In Progress'),
        ('waiting_customer', 'Waiting for Customer'),
        ('resolved', 'Resolved'),
        ('closed', 'Closed'),
    )

    PRIORITY_LEVELS = (
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    )

    # Ticket Information
    ticket_id = models.CharField(max_length=20, unique=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='support_tickets')
    category = models.ForeignKey(SupportCategory, on_delete=models.SET_NULL, null=True)
    subject = models.CharField(max_length=200)
    description = models.TextField()
    priority = models.CharField(max_length=20, choices=PRIORITY_LEVELS, default='medium')
    status = models.CharField(max_length=20, choices=TICKET_STATUS, default='open')

    # Attachments
    attachment = models.FileField(upload_to='support_attachments/', null=True, blank=True)

    # Timestamps
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    resolved_at = models.DateTimeField(null=True, blank=True)

    # Admin fields
    assigned_to = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                                    related_name='assigned_tickets')
    admin_notes = models.TextField(blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.ticket_id} - {self.subject}"

    def save(self, *args, **kwargs):
        if not self.ticket_id:
            self.ticket_id = self.generate_ticket_id()
        super().save(*args, **kwargs)

    def generate_ticket_id(self):
        import uuid
        return f"TKT{uuid.uuid4().hex[:8].upper()}"

    def get_days_open(self):
        return (timezone.now() - self.created_at).days


class TicketResponse(models.Model):
    ticket = models.ForeignKey(SupportTicket, on_delete=models.CASCADE, related_name='responses')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField()
    attachment = models.FileField(upload_to='ticket_responses/', null=True, blank=True)
    is_internal_note = models.BooleanField(default=False)

    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"Response to {self.ticket.ticket_id}"


class FAQ(models.Model):
    category = models.ForeignKey(SupportCategory, on_delete=models.CASCADE, related_name='faqs')
    question = models.CharField(max_length=300)
    answer = models.TextField()
    order = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    views = models.IntegerField(default=0)

    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['category', 'order', 'question']
        verbose_name = 'FAQ'
        verbose_name_plural = 'FAQs'

    def __str__(self):
        return self.question

    def increment_views(self):
        self.views += 1
        self.save()


class KnowledgeBaseArticle(models.Model):
    category = models.ForeignKey(SupportCategory, on_delete=models.CASCADE, related_name='articles')
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    content = models.TextField()
    is_published = models.BooleanField(default=False)
    views = models.IntegerField(default=0)
    helpful_count = models.IntegerField(default=0)
    not_helpful_count = models.IntegerField(default=0)

    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('support:knowledgebase_article', kwargs={'slug': self.slug})