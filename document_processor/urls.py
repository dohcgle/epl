from django.urls import path
from django.contrib.auth import views as auth_views
from .views import (
    dashboard_view, DocumentListView, DocumentUploadView, ApproveDocumentView, 
    process_audit_file, generate_documents,
    process_audit_file, generate_documents,
    create_loan_application, moderator_dashboard, director_dashboard, view_application, approve_application,
        profile_view, view_document_pdf, delete_loan, edit_loan, create_loan_vue,
    get_loan_data_api, edit_loan_vue_api, edit_loan_vue_page
)
from .api_views import (
    LoanApplicationCreateAPIView, LoanApplicationUpdateAPIView, LoanApplicationDetailAPIView
)
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

urlpatterns = [
    path('', dashboard_view, name='dashboard'),
    path('documents/', DocumentListView.as_view(), name='document_list'),
    path('upload/', DocumentUploadView.as_view(), name='upload_document'),
    path('approve/<uuid:doc_id>/', ApproveDocumentView.as_view(), name='approve_document'),
    path('generate/', process_audit_file, name='process_audit'),
    path('process/generate/', generate_documents, name='generate_docs'),
    
    # New Workflow URLs
    path('loans/create/', create_loan_application, name='create_loan'),
    path('loans/create-vue/', create_loan_vue, name='create_loan_vue'),
    path('loans/moderator/', moderator_dashboard, name='moderator_dashboard'),
    path('loans/director/', director_dashboard, name='director_dashboard'),
    path('loans/view/<int:loan_id>/', view_application, name='view_application'),
    path('loans/view/<int:loan_id>/doc/<str:doc_type>/', view_document_pdf, name='view_document_pdf'),
    path('loans/approve/<int:loan_id>/', approve_application, name='approve_application'),
    path('loans/delete/<int:loan_id>/', delete_loan, name='delete_loan'),
    path('loans/edit/<int:loan_id>/', edit_loan, name='edit_loan'),
    path('loans/edit-vue/<int:loan_id>/', edit_loan_vue_page, name='edit_loan_vue_page'),
    path('api/loans/<int:loan_id>/', get_loan_data_api, name='get_loan_data_api'),
    path('api/loans/update/<int:loan_id>/', edit_loan_vue_api, name='edit_loan_vue_api'),
    
    # DRF API V2
    path('api/v2/loans/create/', LoanApplicationCreateAPIView.as_view(), name='api_loan_create'),
    path('api/v2/loans/<int:loan_id>/', LoanApplicationDetailAPIView.as_view(), name='api_loan_detail'),
    path('api/v2/loans/update/<int:loan_id>/', LoanApplicationUpdateAPIView.as_view(), name='api_loan_update'),

    # Swagger Documentation
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    
    # User Profile & Auth
    path('profile/', profile_view, name='profile'),
]

