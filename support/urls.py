from django.urls import path
from . import views

urlpatterns = [
    path('', views.support_dashboard, name='support_dashboard'),
    path('create/', views.create_ticket, name='create_ticket'),
    path('my-tickets/', views.my_tickets, name='my_tickets'),
    path('faqs/', views.faq_list, name='faq_list'),
    path('staff/tickets/', views.staff_ticket_list, name='staff_ticket_list'),
    path('ticket/<str:ticket_id>/', views.ticket_detail, name='support_ticket_detail'),
]