from django.urls import path
from .views import (
    dashboard_view, loan_wizard_view, save_wizard_data, 
    operator_dashboard, # <-- SHUNI QO'SHDIK
    moderator_dashboard, director_dashboard, view_wizard_application,
    approve_wizard_moderator, approve_wizard_director, 
    generate_pdf, generate_all_pdfs, profile_view
)

urlpatterns = [
    path('', dashboard_view, name='dashboard'),
    
    # Wizard Workflow
    path('loans/wizard/', loan_wizard_view, name='loan_wizard'),
    path('loans/wizard/save/', save_wizard_data, name='save_wizard_data'),
    path('loans/wizard/view/<int:wizard_id>/', view_wizard_application, name='view_wizard_application'),
    
    # Moderator & Director
    path('loans/operator/', operator_dashboard, name='operator_dashboard'),
    path('loans/moderator/', moderator_dashboard, name='moderator_dashboard'),
    path('loans/director/', director_dashboard, name='director_dashboard'),
    
    # Approvals
    path('loans/wizard/approve/moderator/<int:wizard_id>/', approve_wizard_moderator, name='approve_wizard_moderator'),
    path('loans/wizard/approve/director/<int:wizard_id>/', approve_wizard_director, name='approve_wizard_director'),
    
    # PDF Generation
    path('loans/view/<int:wizard_id>/doc/<str:doc_type>/', generate_pdf, name='generate_pdf'),
    path('loans/view/<int:wizard_id>/all/', generate_all_pdfs, name='generate_all_pdfs'),
    
    # User Profile
    path('profile/', profile_view, name='profile'),
]
