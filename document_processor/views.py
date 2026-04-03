from django.shortcuts import render, HttpResponse, redirect, get_object_or_404
from django.conf import settings
from django.utils import timezone
import os
import zipfile
import io
import json
from weasyprint import HTML
from django.template.loader import render_to_string
from django.views.decorators.csrf import csrf_exempt
from datetime import datetime
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import JsonResponse
from django.db.models import Sum

from .models import LoanWizardApplication
from .utils import build_document_context

# --- HELPER FUNCTIONS ---
def is_operator(user):
    return user.groups.filter(name='Operator').exists() or user.is_superuser

def is_moderator(user):
    return user.groups.filter(name='Moderator').exists() or user.is_superuser

def is_director(user):
    return user.groups.filter(name='Director').exists() or user.is_superuser

# --- VIEWS ---

@login_required
def dashboard_view(request):
    user = request.user
    if is_operator(user) and not (is_moderator(user) or is_director(user)):
        loans = LoanWizardApplication.objects.filter(created_by=user)
    else:
        loans = LoanWizardApplication.objects.all()
    
    total_docs = loans.count()
    pending_count = loans.filter(status='pending_moderator').count()
    completed_count = loans.filter(status='approved_director').count()
    
    recent_docs = loans[:10]
    total_amount = (loans.aggregate(Sum('loan_amount'))['loan_amount__sum'] or 0) / 1000

    context = {
        'total_docs': total_docs,
        'pending_count': pending_count,
        'completed_count': completed_count,
        'recent_docs': recent_docs,
        'total_amount': total_amount,
    }
    return render(request, 'document_processor/dashboard.html', context)

@login_required
@user_passes_test(is_operator)
def operator_dashboard(request):
    # Operator faqat o'zi kiritgan arizalarni ko'radi
    # 1. Jarayondagi (Moderator yoki Direktor kutayotganlar)
    active_loans = LoanWizardApplication.objects.filter(
        created_by=request.user, 
        status__in=['pending_moderator', 'approved_moderator']
    ).order_by('-created_at')
    
    # 2. Yakunlangan (Direktor imzolangan) arizalar (oxirgi 50 tasi)
    history_loans = LoanWizardApplication.objects.filter(
        created_by=request.user,
        status='approved_director'
    ).order_by('-director_approved_at')[:50]
    
    return render(request, 'document_processor/operator_dashboard.html', {
        'active_loans': active_loans,
        'history_loans': history_loans
    })

@login_required
def loan_wizard_view(request):
    return render(request, 'document_processor/loan_wizard.html')

@csrf_exempt
@login_required
def save_wizard_data(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            client_name = data.get('client_info', {}).get('fish', 'Noma`lum')
            loan_details = data.get('loan_details', {})
            loan_amount_raw = loan_details.get('summa') or loan_details.get('miqdori', 0)
            
            try:
                # Tozalash: probellar va boshqa belgilarni olib tashlash
                loan_amount_str = str(loan_amount_raw).replace(' ', '').replace(',', '').replace('\xa0', '')
                loan_amount = int(float(loan_amount_str))
            except:
                loan_amount = 0

            submission = LoanWizardApplication.objects.create(
                data=data,
                client_name=client_name,
                loan_amount=loan_amount,
                status='pending_moderator',
                created_by=request.user
            )
            return JsonResponse({'status': 'success', 'id': submission.id})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
    return JsonResponse({'status': 'error', 'message': 'POST only'}, status=405)

@login_required
@user_passes_test(is_moderator)
def moderator_dashboard(request):
    # Kutilayotgan
    wizard_loans = LoanWizardApplication.objects.filter(status='pending_moderator').order_by('-created_at')
    # Tarix (Imzolanganlar)
    history_loans = LoanWizardApplication.objects.filter(status__in=['approved_moderator', 'approved_director']).order_by('-moderator_approved_at')[:50]
    
    return render(request, 'document_processor/moderator_dashboard.html', {
        'wizard_loans': wizard_loans,
        'history_loans': history_loans
    })

@login_required
@user_passes_test(is_director)
def director_dashboard(request):
    # Imzolanishi kerak
    wizard_loans = LoanWizardApplication.objects.filter(status='approved_moderator').order_by('-created_at')
    # Yakunlangan (Tarix)
    history_loans = LoanWizardApplication.objects.filter(status='approved_director').order_by('-director_approved_at')[:50]
    
    return render(request, 'document_processor/director_dashboard.html', {
        'wizard_loans': wizard_loans,
        'history_loans': history_loans
    })

@login_required
def view_wizard_application(request, wizard_id):
    wizard = get_object_or_404(LoanWizardApplication, id=wizard_id)
    return render(request, 'document_processor/view_wizard_application.html', {'wizard': wizard})

@login_required
def approve_wizard_moderator(request, wizard_id):
    wizard = get_object_or_404(LoanWizardApplication, id=wizard_id)
    if request.method == 'POST':
        wizard.status = 'approved_moderator'
        wizard.moderator_approved_by = request.user
        wizard.moderator_approved_at = timezone.now()
        wizard.save()
        return redirect('moderator_dashboard')
    return render(request, 'document_processor/view_wizard_application.html', {'wizard': wizard})

@login_required
def approve_wizard_director(request, wizard_id):
    wizard = get_object_or_404(LoanWizardApplication, id=wizard_id)
    if request.method == 'POST':
        wizard.status = 'approved_director'
        wizard.director_approved_by = request.user
        wizard.director_approved_at = timezone.now()
        wizard.save()
        return redirect('director_dashboard')
    return render(request, 'document_processor/view_wizard_application.html', {'wizard': wizard})

def generate_pdf(request, wizard_id, doc_type):
    print(f"DEBUG: generate_pdf hit! id={wizard_id}, doc={doc_type}, user={request.user}")
    wizard = get_object_or_404(LoanWizardApplication, id=wizard_id)
    templates = {
        'xulosa': 'documents/xulosa.html',
        'buyruq': 'documents/buyruq.html',
        'protokol': 'documents/protokol.html',
        'shartnoma': 'documents/shartnoma.html',
        'grafik': 'documents/grafik.html',
        'dalolatnoma': 'documents/dalolatnoma.html',
    }
    template_path = templates.get(doc_type)
    if not template_path:
        return HttpResponse("Hujjat turi topilmadi", status=404)
        
    full_url = request.build_absolute_uri().replace("http://localhost", "https://epl.pullol.uz")
    context = build_document_context(wizard, doc_url=full_url)
    html_string = render_to_string(template_path, context)
    
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename="{doc_type}_{wizard.id}.pdf"'
    HTML(string=html_string, base_url=request.build_absolute_uri()).write_pdf(response)
    return response

@login_required
def generate_all_pdfs(request, wizard_id):
    wizard = get_object_or_404(LoanWizardApplication, id=wizard_id)
    doc_types = ['xulosa', 'buyruq', 'protokol', 'shartnoma', 'grafik', 'dalolatnoma']
    doc_url_base = request.build_absolute_uri('/')[:-1] # Base domain
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w') as zip_file:
        # We need a context for each doc because QR will be different
        templates = {
            'xulosa': 'documents/xulosa.html',
            'buyruq': 'documents/buyruq.html',
            'protokol': 'documents/protokol.html',
            'shartnoma': 'documents/shartnoma.html',
            'grafik': 'documents/grafik.html',
            'dalolatnoma': 'documents/dalolatnoma.html',
        }
        for doc_type in doc_types:
            # Build specific URL for this document type
            doc_url = request.build_absolute_uri(f'/loans/view/{wizard_id}/doc/{doc_type}/').replace("http://localhost", "https://epl.pullol.uz")
            context = build_document_context(wizard, doc_url=doc_url)
            template_path = templates.get(doc_type)
            html_string = render_to_string(template_path, context)
            pdf_buffer = io.BytesIO()
            HTML(string=html_string, base_url=request.build_absolute_uri()).write_pdf(pdf_buffer)
            zip_file.writestr(f"{doc_type}_{wizard.id}.pdf", pdf_buffer.getvalue())
            
    zip_buffer.seek(0)
    response = HttpResponse(zip_buffer, content_type='application/zip')
    response['Content-Disposition'] = f'attachment; filename="documents_{wizard.id}.zip"'
    return response

@login_required
def profile_view(request):
    return render(request, 'document_processor/profile.html')
