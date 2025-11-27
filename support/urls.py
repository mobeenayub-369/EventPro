from django.urls import path
from . import views

app_name = 'support'

urlpatterns = [
    # User Support
    path('', views.support_dashboard, name='support_dashboard'),
    path('create-ticket/', views.create_ticket, name='create_ticket'),
    path('tickets/', views.ticket_list, name='ticket_list'),
    path('tickets/<str:ticket_id>/', views.ticket_detail, name='ticket_detail'),

    # Knowledge Base
    path('knowledgebase/', views.knowledgebase, name='knowledgebase'),
    path('knowledgebase/category/<slug:category_slug>/', views.knowledgebase_category, name='knowledgebase_category'),
    path('knowledgebase/article/<slug:slug>/', views.knowledgebase_article, name='knowledgebase_article'),
    path('faqs/', views.faq_list, name='faq_list'),

    # Admin Support
    path('admin/tickets/', views.admin_ticket_list, name='admin_ticket_list'),
    path('admin/tickets/<str:ticket_id>/', views.admin_ticket_detail, name='admin_ticket_detail'),
    path('admin/tickets/<str:ticket_id>/update-status/', views.update_ticket_status, name='update_ticket_status'),
]