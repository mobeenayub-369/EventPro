from django.urls import path
from . import views

app_name = 'pages'

urlpatterns = [
    # Public Pages
    path('page/<slug:slug>/', views.page_detail, name='page_detail'),
    path('faq/', views.faq_list, name='faq'),
    path('contact/', views.contact, name='contact'),

    # Page Management (Admin Only)
    path('admin/pages/', views.page_list, name='page_list'),
    path('admin/pages/create/', views.create_page, name='create_page'),
    path('admin/pages/edit/<slug:slug>/', views.edit_page, name='edit_page'),
    path('admin/pages/delete/<slug:slug>/', views.delete_page, name='delete_page'),

    # FAQ Management (Admin Only)
    path('admin/faqs/', views.faq_management, name='faq_management'),

    # Contact Submissions (Admin Only)
    path('admin/contact-submissions/', views.contact_submissions, name='contact_submissions'),
    path('admin/contact-submissions/update-status/<int:submission_id>/',
         views.update_submission_status, name='update_submission_status'),
]