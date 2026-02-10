from django.shortcuts import render, HttpResponse, redirect, get_object_or_404
from django.conf import settings
from .forms import UmumiyMalumotForm
import os
import zipfile
import io
from weasyprint import HTML
from django.template.loader import render_to_string
from django.views.decorators.csrf import csrf_exempt
from datetime import datetime, date
from dateutil.relativedelta import relativedelta
from django.views.generic import ListView, CreateView, View
from django.contrib.auth.decorators import login_required, user_passes_test
from django.utils import timezone
from django.db.models import Q
from .models import ProcessedDocument, LoanAgreement

# --- HELPER FUNCTIONS ---
def is_operator(user):
    return user.groups.filter(name='Operator').exists() or user.is_superuser

def is_moderator(user):
    return user.groups.filter(name='Moderator').exists() or user.is_superuser

def is_director(user):
    return user.groups.filter(name='Director').exists() or user.is_superuser

def calculate_schedule(amount, rate, term, start_date_str):
    try:
        if not amount or not rate or not term:
             return [], "0", "0", "0"

        amount = float(str(amount).replace(' ', '').replace(',', '.'))
        rate = float(str(rate).replace(',', '.'))
        term = int(term)
        
        # Monthly rate
        monthly_rate = rate / 12 / 100
        
        # Annuity payment formula: PMT = P * r * (1 + r)^n / ((1 + r)^n - 1)
        if monthly_rate > 0:
            pmt = amount * monthly_rate * ((1 + monthly_rate) ** term) / (((1 + monthly_rate) ** term) - 1)
        else:
            pmt = amount / term

        schedule = []
        balance = amount
        total_p = 0
        total_i = 0
        
        try:
            if isinstance(start_date_str, date):
                current_date = datetime.combine(start_date_str, datetime.min.time())
            else:
                current_date = datetime.strptime(start_date_str, "%d.%m.%Y")
        except:
            current_date = datetime.now()

        for i in range(1, term + 1):
            interest_payment = balance * monthly_rate
            principal_payment = pmt - interest_payment
            
            # Last month adjust
            if i == term:
                principal_payment = balance
                pmt = principal_payment + interest_payment
            
            balance -= principal_payment
            current_date += relativedelta(months=1)
            
            schedule.append({
                'num': i,
                'date': current_date.strftime("%d.%m.%Y"),
                'principal': "{:,.2f}".format(principal_payment).replace(",", " "),
                'interest': "{:,.2f}".format(interest_payment).replace(",", " "),
                'total': "{:,.2f}".format(pmt).replace(",", " "),
                'balance': "{:,.2f}".format(max(0, balance)).replace(",", " ")
            })
            total_p += principal_payment
            total_i += interest_payment

        return schedule, "{:,.2f}".format(total_p).replace(",", " "), "{:,.2f}".format(total_i).replace(",", " "), "{:,.2f}".format(total_p + total_i).replace(",", " ")

    except Exception as e:
        print(f"Error calculating schedule: {e}")
        return [], "0", "0", "0"

def parse_pasted_schedule(text):
    """
    Parses tab-separated text copied from Excel.
    """
    schedule = []
    total_p = 0
    total_i = 0
    grand_total = 0

    lines = text.strip().split('\n')
    for line in lines:
        parts = line.strip().split('\t')
        if len(parts) < 2:
            parts = line.split() 

        def clean_num(s):
            return s.replace(' ', '').replace(',', '.')

        try:
            if not parts[0].strip().isdigit():
                continue

            num = parts[0]
            date = parts[1]
            if len(parts) >= 6:
                balance_str = parts[2]
                principal_str = parts[3]
                interest_str = parts[4]
                total_str = parts[5]
                
                total_p += float(clean_num(principal_str))
                total_i += float(clean_num(interest_str))
                
                schedule.append({
                    'num': num,
                    'date': date,
                    'balance': balance_str,
                    'principal': principal_str,
                    'interest': interest_str,
                    'total': total_str
                })
        except Exception:
            continue
            
    grand_total = total_p + total_i
    return schedule, "{:,.2f}".format(total_p).replace(",", " "), "{:,.2f}".format(total_i).replace(",", " "), "{:,.2f}".format(grand_total).replace(",", " ")

# --- VIEWS ---

@login_required
def dashboard_view(request):
    if is_director(request.user):
        return redirect('director_dashboard')
    elif is_moderator(request.user):
        return redirect('moderator_dashboard')
    else:
        # Operator
        return redirect('process_audit')

@login_required
def create_loan_application(request):
    """
    Operator uchun: Yangi ariza kiritish
    """
    if request.method == 'POST':
        form = UmumiyMalumotForm(request.POST)
        if form.is_valid():
            try:
                # Calculate text fields if missing
                from .utils import number_to_text_uz, cleaner
                data = form.cleaned_data
                
                # --- FIX: Bo'sh stringlarni None ga o'zgartirish ---
                integer_fields = [
                    'qarz_oluvchi_daromad', 
                    'qarz_oluvchi_xarajatlar', 
                    'qarz_oluvchi_tahminiy_tolov',
                    'qarz_oluvchi_jshshir',
                    'kredit_miqdori',
                    'avto_yil',
                    'avto_bahosi',
                    'mulk_bahosi',
                    'tilla_bahosi',
                    'sugurta_summasi'
                ]
                
                for field in integer_fields:
                    if field in data and data[field] == '':
                        data[field] = None
                # --- END FIX ---
                
                if not data.get('kredit_miqdori_soz'):
                    data['kredit_miqdori_soz'] = number_to_text_uz(cleaner(data.get('kredit_miqdori')))
                if not data.get('foiz_stavkasi_soz'):
                    data['foiz_stavkasi_soz'] = number_to_text_uz(cleaner(data.get('foiz_stavkasi')))
                
                # Handle avto_bahosi_soz if present (now in model)
                if data.get('avto_bahosi') and not data.get('avto_bahosi_soz'):
                     data['avto_bahosi_soz'] = number_to_text_uz(cleaner(data.get('avto_bahosi')))

                loan = LoanAgreement.objects.create(
                    created_by=request.user,
                    status='pending_moderator',
                    **data
                )
                return redirect('dashboard') # Yoki success page
            except Exception as e:
                print(f"Error creating loan: {e}")
        else:
            return render(request, 'document_processor/process_audit.html', {'form': form})
    else:
        form = UmumiyMalumotForm()
    
    return render(request, 'document_processor/process_audit.html', {'form': form})

# Alias for old URL
process_audit_file = create_loan_application

@login_required
@user_passes_test(is_moderator)
def moderator_dashboard(request):
    loans = LoanAgreement.objects.all().order_by('-created_at')
    return render(request, 'document_processor/moderator_dashboard.html', {'loans': loans})

@login_required
@user_passes_test(is_director)
def director_dashboard(request):
    # Direktorga tegishli barcha arizalar
    loans = LoanAgreement.objects.all().order_by('-created_at')
    return render(request, 'document_processor/director_dashboard.html', {'loans': loans})

@login_required
def view_application(request, loan_id):
    loan = get_object_or_404(LoanAgreement, id=loan_id)
    
    # Contextni form formatida tayyorlash (agar o'zgartirish kerak bo'lsa)
    # Hozircha shunchaki ko'rish rejimi
    
    return render(request, 'document_processor/view_application.html', {'loan': loan})

@login_required
def profile_view(request):
    return render(request, 'document_processor/profile.html')

@login_required
def approve_application(request, loan_id):
    loan = get_object_or_404(LoanAgreement, id=loan_id)
    user = request.user
    
    if request.method == 'POST':
        action = request.POST.get('action') 
        
        if action == 'reject':
            loan.status = 'rejected'
            loan.save()
            return redirect('dashboard')

        if is_moderator(user) and loan.status == 'pending_moderator':
            loan.status = 'pending_director'
            loan.moderator_approved_by = user
            loan.moderator_approved_at = timezone.now()
            loan.save()
            return redirect('moderator_dashboard')
            
        elif is_director(user) and loan.status == 'pending_director':
            loan.status = 'completed'
            loan.director_approved_by = user
            loan.director_approved_at = timezone.now()
            loan.save()
            
            # --- ZIP GENERATION REMOVED AS PER REQUEST ---
            # generate_loan_docs(request, loan)
            # ---------------------------------------------
            
            return redirect('director_dashboard')
            
            return redirect('director_dashboard')
            
    return redirect('dashboard')


def view_document_pdf(request, loan_id, doc_type):
    """
    Generates and returns a specific document as PDF for inline viewing.
    """
    loan = get_object_or_404(LoanAgreement, id=loan_id)
    
    # --- FIX: Bo'sh stringlarni None ga o'zgartirish (eski ma'lumotlar uchun) ---
    integer_fields = [
        'qarz_oluvchi_daromad', 
        'qarz_oluvchi_xarajatlar', 
        'qarz_oluvchi_tahminiy_tolov',
        'qarz_oluvchi_jshshir',
        'kredit_miqdori',
        'avto_yil',
        'avto_bahosi',
        'mulk_bahosi',
        'tilla_bahosi',
        'sugurta_summasi'
    ]
    
    for field in integer_fields:
        val = getattr(loan, field, None)
        if val == '':
            setattr(loan, field, None)
    # --- END FIX ---
    
    # Context tayyorlash
    context = {}
    for field in LoanAgreement._meta.get_fields():
        if field.concrete and not field.many_to_many and not field.one_to_many:
            val = getattr(loan, field.name)
            if val is not None:
                context[field.name] = val

    context['garov_boshqa_shaxs'] = (loan.garov_egasi == 'boshqa')
    context['is_avto'] = (loan.garov_turi == 'avto')
    context['is_kochmas'] = (loan.garov_turi == 'kochmas_mulk')
    context['is_sugurta'] = loan.sugurta_mavjud
    
    # ----------------------------------------------------
    # FIX: Ma'lumotlarni to'ldirish (Garov egasi, Summa so'z bilan)
    # ----------------------------------------------------
    from .utils import number_to_text_uz, cleaner
    
    # 1. Garov egasi
    if loan.garov_egasi == 'oz' and not loan.garov_egasi_fish:
        loan.garov_egasi_fish = loan.qarz_oluvchi_fish
        loan.garov_egasi_fish = loan.qarz_oluvchi_fish
        context['garov_egasi_fish'] = loan.qarz_oluvchi_fish

    # 1.5 QR Codes for Signatures (Placeholder for now)
    try:
        from .utils import generate_qr_code
        doc_url = f"https://epl.pullol.uz/loans/view/{loan.id}/doc/{doc_type}/"
        
        context['qr_obidov'] = generate_qr_code(doc_url)
        context['qr_akramov'] = generate_qr_code(doc_url)
        context['qr_eshbekov'] = generate_qr_code(doc_url)
        context['qr_manager'] = generate_qr_code(doc_url)
    except Exception as e:
        print(f"QR Code Error: {e}")
        context['qr_obidov'] = ""
        context['qr_akramov'] = ""
        context['qr_eshbekov'] = ""
    
    # 2. Summalar so'z bilan
    if not loan.kredit_miqdori_soz:
        val = cleaner(loan.kredit_miqdori)
        loan.kredit_miqdori_soz = number_to_text_uz(val)
        context['kredit_miqdori_soz'] = loan.kredit_miqdori_soz

    # Safe check for avto_bahosi_soz (now in model)
    if not loan.avto_bahosi_soz:
         val = cleaner(loan.avto_bahosi)
         loan.avto_bahosi_soz = number_to_text_uz(val)
         context['avto_bahosi_soz'] = loan.avto_bahosi_soz

    if not loan.foiz_stavkasi_soz:
         val = cleaner(loan.foiz_stavkasi)
         loan.foiz_stavkasi_soz = number_to_text_uz(val)
         context['foiz_stavkasi_soz'] = loan.foiz_stavkasi_soz
         
    # Save to DB so it is permanently there ("bazadan olib kelsin")
    loan.save()

    # Update loan object in context
    context['loan'] = loan 
    # ----------------------------------------------------
    
    # Schedule
    grafik_matni = loan.grafik_matni.strip() if loan.grafik_matni else ''
    if grafik_matni:
        try:
            schedule, total_p, total_i, grand_total = parse_pasted_schedule(grafik_matni)
        except:
             schedule, total_p, total_i, grand_total = [], "0", "0", "0"
    else:
        schedule, total_p, total_i, grand_total = calculate_schedule(
            loan.kredit_miqdori,
            loan.foiz_stavkasi,
            loan.kredit_muddat_oy,
            loan.shartnoma_sanasi or '01.01.2026'
        )
    
    context['schedule'] = schedule
    context['total_principal'] = total_p
    context['total_interest'] = total_i
    context['grand_total'] = grand_total
    
    # Shablonni aniqlash
    template_map = {
        'kredit_shartnoma': 'documents/shartnoma.html',
        'garov_shartnoma': 'documents/garov.html', 
        'qaror': 'documents/qaror.html',
        'xulosa': 'documents/xulosa.html',
        'dalolatnoma': 'documents/dalolatnoma.html',
        'grafik': 'documents/grafik.html',
        'buyruq': 'documents/buyruq.html',
        'monitoring_1': 'documents/monitoring_1.html',
        'monitoring_2': 'documents/monitoring_2.html',
        'monitoring_3': 'documents/monitoring_3.html',
        'monitoring_4': 'documents/monitoring_4.html',
        # New documents
        'muqova': 'documents/muqova.html',
        'mijoz_anketasi': 'documents/mijoz_anketasi.html',
        'kredit_ariza': 'documents/kredit_ariza.html',
        'anketa': 'documents/anketa.html',
        'majburiyatnoma': 'documents/majburiyatnoma.html',
        'garov_ariza': 'documents/garov_ariza.html',
    }
    
    template_name = template_map.get(doc_type)
    
    if not template_name:
        return HttpResponse(f"Hujjat topilmadi: {doc_type}", status=404)
    
    # Render HTML
    html_string = render_to_string(template_name, context)
    
    # Generate PDF
    base_url = request.build_absolute_uri('/')
    pdf_file = HTML(string=html_string, base_url=base_url).write_pdf()
    
    response = HttpResponse(pdf_file, content_type='application/pdf')
    # inline = browserda ochish, attachment = yuklab olish. Bizga inline kerak.
    response['Content-Disposition'] = f'inline; filename="{doc_type}_{loan.id}.pdf"'
    return response

def generate_loan_docs(request, loan):
    """
    Helper function to generate PDF docs for a approved loan.
    Saves the ZIP file to the loan instance.
    """
    # --- FIX: Bo'sh stringlarni None ga o'zgartirish (eski ma'lumotlar uchun) ---
    integer_fields = [
        'qarz_oluvchi_daromad', 
        'qarz_oluvchi_xarajatlar', 
        'qarz_oluvchi_tahminiy_tolov',
        'qarz_oluvchi_jshshir',
        'kredit_miqdori',
        'avto_yil',
        'avto_bahosi',
        'mulk_bahosi',
        'tilla_bahosi',
        'sugurta_summasi'
    ]
    
    for field in integer_fields:
        val = getattr(loan, field, None)
        if val == '':
            setattr(loan, field, None)
    # --- END FIX ---
    
    # 1. Prepare context from loan object
    # We need to convert model fields back to context dict expected by templates
    context = {}
    
    # Auto-fill from model attributes
    for field in LoanAgreement._meta.get_fields():
        if field.concrete and not field.many_to_many and not field.one_to_many:
            val = getattr(loan, field.name)
            if val is not None:
                context[field.name] = val

    context['loan'] = loan

    # Extra logic
    context['garov_boshqa_shaxs'] = (loan.garov_egasi == 'boshqa')
    context['is_avto'] = (loan.garov_turi == 'avto')
    context['is_kochmas'] = (loan.garov_turi == 'kochmas_mulk')
    context['is_sugurta'] = loan.sugurta_mavjud
    
    # Schedule
    grafik_matni = loan.grafik_matni.strip() if loan.grafik_matni else ''
    if grafik_matni:
        schedule, total_p, total_i, grand_total = parse_pasted_schedule(grafik_matni)
    else:
        schedule, total_p, total_i, grand_total = calculate_schedule(
            loan.kredit_miqdori,
            loan.foiz_stavkasi,
            loan.kredit_muddat_oy,
            loan.shartnoma_sanasi or '01.01.2026'
        )
    
    context['schedule'] = schedule
    context['total_principal'] = total_p
    context['total_interest'] = total_i
    context['grand_total'] = grand_total
    
    # Generate PDFs
    templates = [
        'muqova', 
        'anketa', 
        'mijoz_anketasi', 
        'kredit_ariza', 
        'majburiyatnoma', 
        'garov_ariza', 
        'xulosa', 
        'qaror', 
        'shartnoma', 
        'grafik', 
        'dalolatnoma', 
        'buyruq', 
        'monitoring_1', 
        'monitoring_2', 
        'monitoring_3', 
        'monitoring_4'
    ]
    
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, 'a', zipfile.ZIP_DEFLATED, allowZip64=False) as zip_file:
        for temp_name in templates:
            # handle specialized mapping if needed
            if temp_name == 'shartnoma':
                 template_path = 'documents/shartnoma.html'
            else:
                 template_path = f'documents/{temp_name}.html'
            
            # Check if template exists before rendering to avoid crash
            try:
                html_string = render_to_string(template_path, context)
                
                # Make sure base_url is correct for images/css
                base_url = request.build_absolute_uri('/') # Root URL
                
                pdf_file = HTML(string=html_string, base_url=base_url).write_pdf()
                zip_file.writestr(f"{temp_name}.pdf", pdf_file)
            except Exception as e:
                print(f"Skipping {temp_name} due to error: {e}")
    
    # Save ZIP to model
    from django.core.files.base import ContentFile
    zip_buffer.seek(0)
    filename = f"hujjatlar_{loan.id}.zip"
    loan.pdf_file.save(filename, ContentFile(zip_buffer.read()), save=True)

# Keep other classes for compatibility if needed, but they seem unused for main flow
@login_required
def document_list_view(request):
    """
    Barcha foydalanuvchilar (Operator, Moderator, Direktor) uchun arizalar ro'yxati.
    """
    user = request.user
    
    if is_director(user):
        # Direktor hamma narsani ko'ra oladi
        loans = LoanAgreement.objects.all().order_by('-created_at')
    elif is_moderator(user):
        # Moderator hamma narsani ko'ra oladi (yoki faqat pending_moderator dan keyingilarni)
        # Hozircha hamma narsani ko'rsatamiz
        loans = LoanAgreement.objects.all().order_by('-created_at')
    else:
        # Operator o'zi kiritgan arizalarni ko'radi
        loans = LoanAgreement.objects.filter(created_by=user).order_by('-created_at')
        
    return render(request, 'document_processor/document_list.html', {'documents': loans})

class DocumentListView(ListView):
    # Bu klassni yuqoridagi funksiya bilan almashtiramiz yoki o'zgartiramiz
    model = LoanAgreement
    template_name = 'document_processor/document_list.html'
    context_object_name = 'documents'

    def get_queryset(self):
        user = self.request.user
        if is_director(user) or is_moderator(user):
            return LoanAgreement.objects.all().order_by('-created_at')
        return LoanAgreement.objects.filter(created_by=user).order_by('-created_at')


class DocumentUploadView(CreateView):
    model = ProcessedDocument
    fields = ['file']
    template_name = 'document_processor/upload_document.html'

class ApproveDocumentView(View):
    def post(self, request, doc_id):
        return HttpResponse("Approved")

@csrf_exempt
def generate_documents(request):
    """Legacy view, redirect or keep for debug"""
    return create_loan_application(request)

