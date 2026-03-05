from django.shortcuts import render, HttpResponse, redirect, get_object_or_404
from django.conf import settings
from .forms import UmumiyMalumotForm
import os
import zipfile
import io
import json
from weasyprint import HTML
from django.template.loader import render_to_string
from django.views.decorators.csrf import csrf_exempt
from datetime import datetime, date
from dateutil.relativedelta import relativedelta
from django.views.generic import ListView, CreateView, View
from django.contrib.auth.decorators import login_required, user_passes_test
from django.utils import timezone
from django.db.models import Q, Count, Sum
from django.http import JsonResponse
from .models import (
    Client, LoanApplication, LoanDetails, ContactPerson, FinancialInfo,
    Collateral, AutoCollateral, RealEstateCollateral, GoldCollateral, InsuranceCollateral
)

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
    
    # 1. Base QuerySet
    if is_operator(user) and not (is_director(user) or is_moderator(user)):
        loans = LoanApplication.objects.filter(created_by=user, is_deleted=False).order_by('-created_at')
    else:
        loans = LoanApplication.objects.filter(is_deleted=False).order_by('-created_at')

    total_docs = loans.count()
    pending_count = loans.filter(status__in=['pending_moderator', 'pending_director']).count()
    completed_count = loans.filter(status='completed').count()
    rejected_count = loans.filter(status='rejected').count()

    recent_docs = loans.order_by('-created_at')[:10]

    context = {
        'total_docs': total_docs,
        'pending_count': pending_count,
        'completed_count': completed_count,
        'rejected_count': rejected_count,
        'recent_docs': recent_docs,
    }

    return render(request, 'document_processor/dashboard.html', context)

@login_required
def create_loan_application(request):
    """Eski HTML form formati, hozirda operator faqat Vue dan foydalanadi"""
    return redirect('create_loan_vue')

@login_required
def create_loan_vue(request):
    """
    Yangi JSON arxitekturasi asoida Vue.js dan kelgan so'rovni qabul qiluvchi markaziy funksiya.
    """
    if request.method == 'POST':
        try:
            payload = json.loads(request.body)
            
            def parse_date(date_str):
                if not date_str: return None
                try:
                    return datetime.strptime(date_str.strip(), '%d.%m.%Y').date()
                except:
                    return None
                    
            def clean_int(val):
                if not val: return None
                try:
                    return int(float(str(val).replace(' ', '')))
                except:
                    return None
                    
            def clean_float(val):
                if not val: return None
                try:
                    return float(str(val).replace(' ', '').replace(',', '.'))
                except:
                    return None

            def clean_str(val):
                if val is None: return ''
                return str(val).strip()

            # --- QISMLAR ---
            personal = payload.get('personal') or {}
            loan_obj = payload.get('loan') or {}
            collateral = payload.get('collateral') or {}
            financial = payload.get('financial') or {}
            contacts = payload.get('contacts') or []

            # 1. MIJOZ (CLIENT) yaratish yoki izlash
            # Asosiy kalit sifatishda pasport seriyasi yoki JSHSHIR olinadi
            pasport_seriya = clean_str(personal.get('pasport_seriya'))
            jshshir = clean_int(personal.get('jshshir'))
            
            # Mijozni izlash (faqat pasport bo'yicha yoki yangi yaratish)
            client = None
            if pasport_seriya:
                client = Client.objects.filter(pasport_seriya=pasport_seriya).first()
            if not client and jshshir:
                client = Client.objects.filter(jshshir=jshshir).first()
                
            if not client:
                client = Client.objects.create(
                    fish=clean_str(personal.get('fish')),
                    fish_inisiali=clean_str(personal.get('fish_inisiali')),
                    pasport_seriya=pasport_seriya,
                    pasport_berilgan=clean_str(personal.get('pasport_berilgan')),
                    jshshir=jshshir,
                    tugilgan_sana=parse_date(personal.get('tugilgan_sana')),
                    jinsi=clean_str(personal.get('jinsi')),
                    telefon=clean_str(personal.get('telefon')),
                    manzil=clean_str(personal.get('manzil'))
                )
            
            # 2. LOAN APPLICATION yaratish
            application = LoanApplication.objects.create(
                client=client,
                status='pending_moderator',
                created_by=request.user,
                payload=payload,
            )

            # 3. LOAN DETAILS yaratish
            LoanDetails.objects.create(
                application=application,
                shartnoma_raqami=clean_str(loan_obj.get('shartnoma_raqami')),
                shartnoma_sanasi=parse_date(loan_obj.get('shartnoma_sanasi')),
                boshlanish_sanasi=parse_date(loan_obj.get('boshlanish_sanasi')),
                tugash_sanasi=parse_date(loan_obj.get('tugash_sanasi')),
                miqdori=clean_int(loan_obj.get('miqdori')),
                miqdori_soz=clean_str(loan_obj.get('miqdori_soz')),
                muddat_oy=clean_str(loan_obj.get('muddat_oy')),
                muddat_oy_soz=clean_str(loan_obj.get('muddat_oy_soz')),
                foiz=clean_str(loan_obj.get('foiz')),
                foiz_soz=clean_str(loan_obj.get('foiz_soz')),
                turi=clean_str(loan_obj.get('turi')),
                grafik_turi=clean_str(loan_obj.get('grafik')),
                grafik_matni=clean_str(loan_obj.get('grafik_matni'))
            )

            # 4. FINANCIAL INFO yaratish
            FinancialInfo.objects.create(
                application=application,
                ish_joyi=clean_str(financial.get('ish_joyi')),
                daromad=clean_int(financial.get('daromad')),
                xarajatlar=clean_int(financial.get('xarajatlar')),
                tahminiy_tolov=clean_int(financial.get('tahminiy_tolov')),
                majburiyatlar=clean_str(financial.get('majburiyatlar')),
                
                filial_nomi=clean_str(financial.get('filial_nomi')) or 'Buxoro filiali',
                filial_boshligi=clean_str(financial.get('filial_boshligi')),
                filial_boshligi_inisiali=clean_str(financial.get('filial_boshligi_inisiali')),
                tashkilot_nomi=clean_str(financial.get('tashkilot_nomi')) or "«PULLOL BUSINESS MIKROMOLIYA TASHKILOTI» MChJ",
                direktor_fish=clean_str(financial.get('direktor_fish')) or "OBIDOV ABDULLA SHOKIR O'G'LI",
                direktor_fish_inisiali=clean_str(financial.get('direktor_fish_inisiali')) or "A.SH.OBIDOV"
            )

            # 5. CONTACTS yaratish
            for contact in contacts:
                # Vue da har bir contact dict {} ko'rinishida keladi: fish, telefon, qarindoshlik
                contact_fish = clean_str(contact.get('fish'))
                if contact_fish:
                    ContactPerson.objects.create(
                        application=application,
                        fish=contact_fish,
                        telefon=clean_str(contact.get('telefon')),
                        qarindoshlik=clean_str(contact.get('qarindoshlik'))
                    )

            # 6. COLLATERAL (GAROV) yaratish
            selected_types = payload.get('selectedCollaterals') or collateral.get('selected_types') or []
            sugurta_mavjud = payload.get('sugurtaMavjud') or False
            owner_type = clean_str(payload.get('ownerType') or collateral.get('owner_type') or 'borrower')
            
            # --- GAROV EGASINI ANIQLASH (Owner Client) ---
            owner_client = client # Default: qarz oluvchi
            notarius_fish = ''
            notarius_address = ''
            reestr_number = ''
            reestr_date = None

            if owner_type == 'other' or owner_type == 'general_proxy':
                # Boshqa shaxs pasporti/jshshir izlash
                o_pasport = clean_str(collateral.get('owner_passport'))
                o_jshshir = clean_int(collateral.get('owner_jshshir'))
                o_fish = clean_str(collateral.get('owner_fish'))

                other_client = None
                if o_pasport:
                    other_client = Client.objects.filter(pasport_seriya=o_pasport).first()
                if not other_client and o_jshshir:
                    other_client = Client.objects.filter(jshshir=o_jshshir).first()
                if not other_client and o_fish:
                     other_client = Client.objects.filter(fish__icontains=o_fish).first()
                
                # Agar garov egasi topilmasa, bazaga qo'shamiz
                if not other_client and (o_fish or o_pasport):
                     other_client = Client.objects.create(
                         fish=o_fish,
                         fish_inisiali=clean_str(collateral.get('owner_initials')),
                         pasport_seriya=o_pasport,
                         pasport_berilgan=clean_str(collateral.get('owner_passport_given_by')),
                         jshshir=o_jshshir,
                         tugilgan_sana=parse_date(collateral.get('owner_birth_date')),
                         manzil=clean_str(collateral.get('owner_address')),
                         jinsi=clean_str(collateral.get('owner_gender')).lower() if collateral.get('owner_gender') else None
                     )
                
                if other_client:
                    owner_client = other_client
            
            if owner_type == 'general_proxy':
                notarius_fish = clean_str(collateral.get('notarius_fish'))
                notarius_address = clean_str(collateral.get('notarius_address'))
                reestr_number = clean_str(collateral.get('reestr_number'))
                reestr_date = parse_date(collateral.get('reestr_date'))


            # Har bir tanlangan tur uchun bazaviy va detallarni yaratish
            for c_type in selected_types:
                # Map selected type to database constants
                db_c_type = c_type
                if c_type == 'kochmas_mulk': db_c_type = 'kochmas'
                
                # 6.0 Asosiy Garov Reyestri
                base_col = Collateral.objects.create(
                    application=application,
                    type=db_c_type,
                    owner_type=owner_type,
                    owner_client=owner_client,
                    notarius_fish=notarius_fish,
                    notarius_address=notarius_address,
                    reestr_number=reestr_number,
                    reestr_date=reestr_date
                )

                # 6.1 Avtomobil tafsilotlari
                if db_c_type == 'avto':
                    AutoCollateral.objects.create(
                        collateral=base_col,
                        nomi=clean_str(collateral.get('avto_nomi')),
                        kuzov_turi=clean_str(collateral.get('avto_kuzov_turi')),
                        kuzov_raqami=clean_str(collateral.get('avto_kuzov')),
                        dvigatel=clean_str(collateral.get('avto_dvigatel')),
                        shassi=clean_str(collateral.get('avto_shassi')) or "RAKAMSIZ",
                        rang=clean_str(collateral.get('avto_rang')),
                        yil=clean_int(collateral.get('avto_yil')),
                        texpasport=clean_str(collateral.get('avto_texpasport')),
                        texpasport_sana=parse_date(collateral.get('avto_texpasport_sana')),
                        manzil=clean_str(collateral.get('avto_manzil')),
                        davlat_raqami=clean_str(collateral.get('avto_raqam')),
                        bahosi=clean_int(collateral.get('avto_bahosi')),
                        bahosi_soz=clean_str(collateral.get('avto_bahosi_soz'))
                    )
                
                # 6.2 Ko'chmas mulk
                elif db_c_type == 'kochmas':
                     RealEstateCollateral.objects.create(
                         collateral=base_col,
                         turi=clean_str(collateral.get('mulk_turi')),
                         umumiy_maydon=clean_str(collateral.get('mulk_umumiy')),
                         qurilish_maydon=clean_str(collateral.get('mulk_qurilish')),
                         foydalanish_maydon=clean_str(collateral.get('mulk_foydalanish')), # Note mapping
                         yashash_maydon=clean_str(collateral.get('mulk_yashash')),
                         reestr_raqami=clean_str(collateral.get('mulk_reestr_raqami')),
                         kadastr_raqami=clean_str(collateral.get('mulk_kadastr')),
                         manzil=clean_str(collateral.get('mulk_manzil')),
                         bahosi=clean_int(collateral.get('mulk_bahosi')),
                         bahosi_soz=clean_str(collateral.get('mulk_bahosi_soz'))
                     )

                # 6.3 Tilla buyum
                elif db_c_type == 'tilla':
                     GoldCollateral.objects.create(
                         collateral=base_col,
                         nomi=clean_str(collateral.get('tilla_nomi')),
                         probi=clean_str(collateral.get('tilla_probi')),
                         vazni=clean_str(collateral.get('tilla_vazni')),
                         soni=clean_int(collateral.get('tilla_soni')),
                         bahosi=clean_int(collateral.get('tilla_bahosi')),
                         bahosi_soz=clean_str(collateral.get('tilla_bahosi_soz'))
                     )

                # 6.4 Sug'urta polisi
                elif db_c_type == 'sugurta':
                    InsuranceCollateral.objects.create(
                        collateral=base_col,
                        kompaniya=clean_str(collateral.get('sugurta_kompaniya')),
                        polis_raqami=clean_str(collateral.get('sugurta_polisi')),
                        sana=parse_date(collateral.get('sugurta_sana')),
                        summa=clean_int(collateral.get('sugurta_summa')),
                        summa_soz=clean_str(collateral.get('sugurta_summa_soz'))
                    )

            return JsonResponse({'status': 'success', 'loan_id': str(application.id)})

        except Exception as e:
            import traceback
            print(traceback.format_exc())
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
            
    return render(request, 'document_processor/loan_create.html')

process_audit_file = create_loan_application

@login_required
@user_passes_test(is_moderator)
def moderator_dashboard(request):
    loans = LoanApplication.objects.filter(is_deleted=False).order_by('-created_at')
    return render(request, 'document_processor/moderator_dashboard.html', {'loans': loans})

@login_required
@user_passes_test(is_director)
def director_dashboard(request):
    loans = LoanApplication.objects.filter(is_deleted=False).order_by('-created_at')
    return render(request, 'document_processor/director_dashboard.html', {'loans': loans})

@login_required
def view_application(request, loan_id):
    loan = get_object_or_404(LoanApplication, id=loan_id)
    return render(request, 'document_processor/view_application.html', {'loan': loan})

@login_required
def profile_view(request):
    return render(request, 'document_processor/profile.html')

@login_required
def approve_application(request, loan_id):
    loan = get_object_or_404(LoanApplication, id=loan_id)
    user = request.user
    
    if request.method == 'POST':
        action = request.POST.get('action') 
        
        if action == 'reject':
            loan.status = 'rejected'
            loan.save()
            return redirect('director_dashboard')

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

            return redirect('director_dashboard')
            
    return redirect('dashboard')


@login_required
def delete_loan(request, loan_id):
    if not (is_director(request.user) or request.user.is_superuser):
        return redirect('dashboard')
    loan = get_object_or_404(LoanApplication, id=loan_id)
    loan.is_deleted = True
    loan.save()
    return redirect('dashboard')

@login_required
def edit_loan(request, loan_id):
    loan = get_object_or_404(LoanApplication, id=loan_id)
    if loan.status == 'completed':
        return redirect('view_application', loan_id=loan.id)
    return render(request, 'document_processor/process_audit.html', {'edit_mode': True, 'loan': loan})

def view_document_pdf(request, loan_id, doc_type):
    """
    Generates and returns a specific document as PDF for inline viewing.
    """
    loan = get_object_or_404(LoanApplication, id=loan_id)
    
    from .utils import build_document_context
    try:
        from .utils import parse_pasted_schedule, calculate_schedule
    except ImportError:
        def parse_pasted_schedule(text): return [], "0", "0", "0"
        def calculate_schedule(*args): return [], "0", "0", "0"
        
    context = build_document_context(loan)
    
    # QR Codes
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

    # Schedule
    grafik_matni = loan.loan_grafik_matni
    if grafik_matni:
        try:
            schedule, total_p, total_i, grand_total = parse_pasted_schedule(grafik_matni)
        except:
             schedule, total_p, total_i, grand_total = [], "0", "0", "0"
    else:
        schedule, total_p, total_i, grand_total = calculate_schedule(
            loan.loan_miqdori,
            loan.loan_foiz,
            loan.loan_muddat_oy,
            loan.details.shartnoma_sanasi or '01.01.2026'
        )
    
    context['schedule'] = schedule
    context['total_principal'] = total_p
    context['total_interest'] = total_i
    context['grand_total'] = grand_total
    
    # Shablonni aniqlash
    template_map = {
        'kredit_shartnoma': 'documents/shartnoma.html',
        'garov_shartnoma': 'documents/garov.html', 
        'protokol': 'documents/protokol.html',
        'xulosa': 'documents/xulosa.html',
        'dalolatnoma': 'documents/dalolatnoma.html',
        'grafik': 'documents/grafik.html',
        'loan_grafik': 'documents/grafik.html',
        'buyruq': 'documents/buyruq.html',
        'monitoring_1': 'documents/monitoring_1.html',
        'monitoring_2': 'documents/monitoring_2.html',
        'monitoring_3': 'documents/monitoring_3.html',
        'monitoring_4': 'documents/monitoring_4.html',
        'muqova': 'documents/muqova.html',
        'mijoz_anketasi': 'documents/mijoz_anketasi.html',
        'kredit_ariza': 'documents/kredit_ariza.html',
        'anketa': 'documents/anketa.html',
        'majburiyatnoma': 'documents/majburiyatnoma.html',
        'garov_ariza': 'documents/garov_ariza.html',
        'mijoz_ariza': 'documents/mijoz_ariza.html',
    }
    
    template_name = template_map.get(doc_type)
    
    if not template_name:
        return HttpResponse(f"Hujjat topilmadi: {doc_type}", status=404)
    
    # Render HTML
    html_string = render_to_string(template_name, context)
    
    # Generate PDF
    base_url = request.build_absolute_uri('/')
    try:
        pdf_file = HTML(string=html_string, base_url=base_url).write_pdf()
        response = HttpResponse(pdf_file, content_type='application/pdf')
        response['Content-Disposition'] = f'inline; filename="{doc_type}_{loan.id}.pdf"'
        return response
    except Exception as e:
        import traceback
        return HttpResponse(f"PDF GENERATION ERROR: {e}<br><pre>{traceback.format_exc()}</pre>", status=500)



@login_required
def document_list_view(request):
    user = request.user
    if is_director(user) or is_moderator(user):
        loans = LoanApplication.objects.filter(is_deleted=False).order_by('-created_at')
    else:
        loans = LoanApplication.objects.filter(created_by=user, is_deleted=False).order_by('-created_at')
        
    return render(request, 'document_processor/document_list.html', {'documents': loans})

class DocumentListView(ListView):
    model = LoanApplication
    template_name = 'document_processor/document_list.html'
    context_object_name = 'documents'

    def get_queryset(self):
        user = self.request.user
        if is_director(user) or is_moderator(user):
            return LoanApplication.objects.filter(is_deleted=False).order_by('-created_at')
        return LoanApplication.objects.filter(created_by=user, is_deleted=False).order_by('-created_at')

class DocumentUploadView(CreateView):
    # Bu logikalar eski modelda uzatib borilardi. Hozircha bo'sh qo'yamiz.
    pass

class ApproveDocumentView(View):
    def post(self, request, doc_id):
        return HttpResponse("Approved")

@csrf_exempt
def generate_documents(request):
    return create_loan_application(request)
