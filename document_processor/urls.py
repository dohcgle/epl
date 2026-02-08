from django.urls import path
from django.contrib.auth import views as auth_views
from .views import (
    dashboard_view, DocumentListView, DocumentUploadView, ApproveDocumentView, 
    process_audit_file, generate_documents,
    create_loan_application, moderator_dashboard, director_dashboard, view_application, approve_application,
    profile_view, view_document_pdf
)

urlpatterns = [
    path('', dashboard_view, name='dashboard'),
    path('documents/', DocumentListView.as_view(), name='document_list'),
    path('upload/', DocumentUploadView.as_view(), name='upload_document'),
    path('approve/<uuid:doc_id>/', ApproveDocumentView.as_view(), name='approve_document'),
    path('generate/', process_audit_file, name='process_audit'),
    path('process/generate/', generate_documents, name='generate_docs'),
    
    # New Workflow URLs
    path('loans/create/', create_loan_application, name='create_loan'),
    path('loans/moderator/', moderator_dashboard, name='moderator_dashboard'),
    path('loans/director/', director_dashboard, name='director_dashboard'),
    path('loans/view/<int:loan_id>/', view_application, name='view_application'),
    path('loans/view/<int:loan_id>/doc/<str:doc_type>/', view_document_pdf, name='view_document_pdf'),
    path('loans/approve/<int:loan_id>/', approve_application, name='approve_application'),
    
    # User Profile & Auth
    path('profile/', profile_view, name='profile'),
    path('accounts/login/', auth_views.LoginView.as_view(), name='login'), # Default django login
    path('accounts/logout/', auth_views.LogoutView.as_view(next_page='/'), name='logout'),
]
