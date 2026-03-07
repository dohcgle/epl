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

def clean_phone(val):
    if not val: return ''
    # Faqat raqamlarni qoldiramiz
    return ''.join(filter(str.isdigit, str(val)))

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

from django.forms.models import model_to_dict
from .forms import UmumiyMalumotForm

@login_required
def edit_loan(request, loan_id):
    loan = get_object_or_404(LoanApplication, id=loan_id)
    client = loan.client
    details = loan.details if hasattr(loan, 'details') else None
    financial = loan.financial_info if hasattr(loan, 'financial_info') else None
    
    contacts = loan.contacts.all()
    collaterals = loan.collaterals.all()
    
    if request.method == 'POST':
        from .utils import parse_date, clean_int, clean_float, clean_str
        
        # 1. Mijoz ma'lumotlarini yangilash
        if client:
            client.fish = request.POST.get('qarz_oluvchi_fish')
            client.fish_inisiali = request.POST.get('qarz_oluvchi_fish_inisiali')
            client.pasport_seriya = request.POST.get('qarz_oluvchi_pasport_seriya')
            client.pasport_berilgan = request.POST.get('qarz_oluvchi_pasport_berilgan')
            jshshir_val = request.POST.get('qarz_oluvchi_jshshir')
            if jshshir_val: client.jshshir = clean_int(jshshir_val)
            client.tugilgan_sana = parse_date(request.POST.get('qarz_oluvchi_tugilgan_sana'))
            client.jinsi = request.POST.get('qarz_oluvchi_jinsi')
            client.telefon = request.POST.get('qarz_oluvchi_telefon')
            client.manzil = request.POST.get('qarz_oluvchi_manzil')
            client.save()
            
        # 2. Kontaktlar
        for i, contact in enumerate(contacts[:3]):
            contact.fish = request.POST.get(f'kontakt_{i+1}_fish')
            contact.telefon = request.POST.get(f'kontakt_{i+1}_telefon')
            contact.qarindoshlik = request.POST.get(f'kontakt_{i+1}_qarindoshlik')
            contact.save()
            
        # 3. Kredit ma'lumotlari
        if details:
            details.shartnoma_raqami = request.POST.get('shartnoma_raqami')
            details.shartnoma_sanasi = parse_date(request.POST.get('shartnoma_sanasi'))
            details.miqdori = clean_int(request.POST.get('kredit_miqdori'))
            details.miqdori_soz = request.POST.get('kredit_miqdori_soz')
            details.muddat_oy = request.POST.get('kredit_muddat_oy')
            details.muddat_oy_soz = request.POST.get('kredit_muddat_oy_soz')
            details.foiz = request.POST.get('foiz_stavkasi')
            details.foiz_soz = request.POST.get('foiz_stavkasi_soz')
            details.turi = request.POST.get('kredit_turi')
            details.grafik_turi = request.POST.get('grafik')
            details.grafik_matni = request.POST.get('grafik_matni')
            details.save()
            
        # 4. Moliyaviy Holat
        if financial:
            financial.ish_joyi = request.POST.get('qarz_oluvchi_ish_joyi')
            financial.daromad = clean_int(request.POST.get('qarz_oluvchi_daromad'))
            financial.xarajatlar = clean_int(request.POST.get('qarz_oluvchi_xarajatlar'))
            financial.tahminiy_tolov = clean_int(request.POST.get('qarz_oluvchi_tahminiy_tolov'))
            financial.majburiyatlar = request.POST.get('qarz_oluvchi_majburiyatlar')
            
            financial.filial_nomi = request.POST.get('filial_nomi')
            financial.filial_boshligi = request.POST.get('filial_boshligi')
            financial.filial_boshligi_inisiali = request.POST.get('filial_boshligi_inisiali')
            
            financial.tashkilot_nomi = request.POST.get('tashkilot_nomi')
            financial.direktor_fish = request.POST.get('direktor_fish')
            financial.direktor_fish_inisiali = request.POST.get('direktor_fish_inisiali')
            financial.save()

        # 5. Garov ma'lumotlari
        # Avvalgi garovlarni eski tahrirlarda o'chirib yangilarini kiritish xavfsizroq bo'ladi chunki tipi o'zgargan bo'lishi mumkin. Hozircha mavjudni o'zgartiramiz.
        garov_turi = request.POST.get('garov_turi')
        garov_egasi = request.POST.get('garov_egasi')

        for col in collaterals:
            if col.type == 'sugurta':
                if request.POST.get('sugurta_mavjud'):
                    if hasattr(col, 'insurance_detail'):
                        ins = col.insurance_detail
                        ins.kompaniya = request.POST.get('sugurta_kompaniyasi')
                        ins.polis_raqami = request.POST.get('sugurta_polisi')
                        ins.sana = parse_date(request.POST.get('sugurta_sanasi'))
                        ins.summa = clean_int(request.POST.get('sugurta_summasi'))
                        ins.summa_soz = request.POST.get('sugurta_summasi_soz')
                        ins.save()
            else:
                # Agar garov egasi boshqa shaxs bo'lsa uni Client sifatida bazadan izlab yoki yangi yaratib qo'shish kerak.
                owner_type = 'other' if garov_egasi == 'boshqa' else 'borrower'
                col.owner_type = owner_type
                
                # Uchinchi shaxs bo'lsa
                if owner_type == 'other':
                    owner_fish = request.POST.get('garov_egasi_fish')
                    owner_init = request.POST.get('garov_egasi_inisiali')
                    if owner_fish:
                        # Bazadan izlash yoki yangi qo'shish (Hozircha faqat ismidan izlash yoki borini upd qilamiz)
                        if col.owner_client and col.owner_client != client:
                            oc = col.owner_client
                            oc.fish = owner_fish
                            oc.fish_inisiali = owner_init
                            oc.manzil = request.POST.get('garov_egasi_manzil')
                            oc.save()
                        else:
                            from .models import Client
                            new_oc = Client.objects.create(
                                fish=owner_fish, 
                                fish_inisiali=owner_init,
                                manzil=request.POST.get('garov_egasi_manzil')
                            )
                            col.owner_client = new_oc
                            
                    col.notarius_fish = request.POST.get('ishonchnoma_notarius_fish')
                    col.notarius_address = request.POST.get('ishonchnoma_notarius_manzil')
                    col.reestr_number = request.POST.get('ishonchnoma_reestr_raqami')
                    col.reestr_date = parse_date(request.POST.get('ishonchnoma_reestr_sanasi'))
                else:
                    col.owner_client = loan.client
                
                col.save()
                
                if col.type == 'avto' and hasattr(col, 'auto_detail') and garov_turi == 'avto':
                    auto = col.auto_detail
                    auto.nomi = request.POST.get('avto_nomi')
                    auto.davlat_raqami = request.POST.get('avto_raqam')
                    auto.kuzov_turi = request.POST.get('avto_kuzov_turi')
                    auto.kuzov_raqami = request.POST.get('avto_kuzov')
                    auto.dvigatel = request.POST.get('avto_dvigatel')
                    auto.shassi = request.POST.get('avto_shassi')
                    
                    yil = request.POST.get('avto_yil')
                    if yil: auto.yil = clean_int(yil)
                    
                    auto.rang = request.POST.get('avto_rang')
                    if hasattr(auto, 'yurgan'):
                        auto.yurgan = request.POST.get('avto_yurgan')
                    auto.bahosi = clean_int(request.POST.get('avto_bahosi'))
                    auto.texpasport = request.POST.get('avto_texpasport')
                    auto.texpasport_sana = parse_date(request.POST.get('avto_texpasport_sana'))
                    auto.manzil = request.POST.get('avto_manzil')
                    auto.save()
                    
                elif col.type == 'kochmas' and hasattr(col, 'real_estate_detail') and garov_turi == 'kochmas_mulk':
                    mulk = col.real_estate_detail
                    mulk.turi = request.POST.get('mulk_turi')
                    mulk.qurilish_maydon = request.POST.get('mulk_qurilish_maydoni')
                    mulk.umumiy_maydon = request.POST.get('mulk_umumiy_maydoni')
                    mulk.yashash_maydon = request.POST.get('mulk_yashash_maydoni')
                    
                    mulk.reestr_raqami = request.POST.get('mulk_reestr_raqami')
                    mulk.kadastr_raqami = request.POST.get('mulk_kadastr_raqami')
                    mulk.manzil = request.POST.get('mulk_manzili')
                    mulk.bahosi = clean_int(request.POST.get('mulk_bahosi'))
                    mulk.bahosi_soz = request.POST.get('mulk_bahosi_soz')
                    mulk.save()
                    
                elif col.type == 'tilla' and hasattr(col, 'gold_detail') and garov_turi == 'tilla':
                    tilla = col.gold_detail
                    tilla.nomi = request.POST.get('tilla_nomi')
                    tilla.probi = request.POST.get('tilla_probi')
                    tilla.vazni = request.POST.get('tilla_vazni')
                    
                    soni = request.POST.get('tilla_soni')
                    if soni: tilla.soni = clean_int(soni)
                    
                    tilla.bahosi = clean_int(request.POST.get('tilla_bahosi'))
                    tilla.bahosi_soz = request.POST.get('tilla_bahosi_soz')
                    tilla.save()

        # Monitoring
        if request.POST.get('monitoring_sana_1'):
            loan.payload = loan.payload or {}
            loan.payload['monitoring'] = {
                'sana_1': request.POST.get('monitoring_sana_1'),
                'sana_2': request.POST.get('monitoring_sana_2'),
                'sana_3': request.POST.get('monitoring_sana_3'),
                'sana_4': request.POST.get('monitoring_sana_4')
            }
            loan.save()

        return redirect('view_application', loan_id=loan.id)

    # Initial data tayyorlash
    initial_data = {}
    
    if client:
        initial_data.update({
            'qarz_oluvchi_fish': client.fish,
            'qarz_oluvchi_fish_inisiali': client.fish_inisiali,
            'qarz_oluvchi_pasport_seriya': client.pasport_seriya,
            'qarz_oluvchi_pasport_berilgan': client.pasport_berilgan,
            'qarz_oluvchi_jshshir': client.jshshir,
            'qarz_oluvchi_tugilgan_sana': client.tugilgan_sana.strftime('%d.%m.%Y') if client.tugilgan_sana else '',
            'qarz_oluvchi_jinsi': client.jinsi,
            'qarz_oluvchi_telefon': client.telefon,
            'qarz_oluvchi_manzil': client.manzil,
        })
        
    for i, contact in enumerate(contacts[:3]):
        initial_data.update({
            f'kontakt_{i+1}_fish': contact.fish,
            f'kontakt_{i+1}_telefon': contact.telefon,
            f'kontakt_{i+1}_qarindoshlik': contact.qarindoshlik,
        })
        
    if details:
        initial_data.update({
            'shartnoma_raqami': details.shartnoma_raqami,
            'shartnoma_sanasi': details.shartnoma_sanasi.strftime('%d.%m.%Y') if details.shartnoma_sanasi else '',
            'kredit_miqdori': details.miqdori,
            'kredit_miqdori_soz': details.miqdori_soz,
            'kredit_muddat_oy': details.muddat_oy,
            'kredit_muddat_oy_soz': details.muddat_oy_soz,
            'foiz_stavkasi': details.foiz,
            'foiz_stavkasi_soz': details.foiz_soz,
            'kredit_turi': details.turi,
            'grafik': details.grafik_turi,
            'grafik_matni': details.grafik_matni,
        })
        
    if financial:
        initial_data.update({
            'qarz_oluvchi_ish_joyi': financial.ish_joyi,
            'qarz_oluvchi_daromad': financial.daromad,
            'qarz_oluvchi_xarajatlar': financial.xarajatlar,
            'qarz_oluvchi_majburiyatlar': financial.majburiyatlar,
            'qarz_oluvchi_tahminiy_tolov': financial.tahminiy_tolov,
            
            'filial_nomi': financial.filial_nomi,
            'filial_boshligi': financial.filial_boshligi,
            'filial_boshligi_inisiali': financial.filial_boshligi_inisiali,
            
            'tashkilot_nomi': financial.tashkilot_nomi,
            'direktor_fish': financial.direktor_fish,
            'direktor_fish_inisiali': financial.direktor_fish_inisiali,
        })

    # Garovlar bo'yicha ma'lumotlar
    for col in collaterals:
        if col.type == 'sugurta':
            initial_data['sugurta_mavjud'] = True
            if hasattr(col, 'insurance_detail'):
                ins = col.insurance_detail
                initial_data.update({
                    'sugurta_kompaniyasi': ins.kompaniya,
                    'sugurta_polisi': ins.polis_raqami,
                    'sugurta_sanasi': ins.sana.strftime('%d.%m.%Y') if ins.sana else '',
                    'sugurta_summasi': ins.summa,
                    'sugurta_summasi_soz': ins.summa_soz,
                })
        else:
            initial_data['garov_turi'] = col.type
            initial_data['garov_egasi'] = col.owner_type if col.owner_type in ['oz', 'boshqa'] else ('boshqa' if col.owner_type != 'borrower' else 'oz')
            initial_data['uchinchi_shaxs_mavjud'] = (initial_data['garov_egasi'] == 'boshqa')
            
            if initial_data['garov_egasi'] == 'boshqa' or col.owner_type != 'borrower':
                if col.owner_client:
                    initial_data.update({
                        'garov_egasi_fish': col.owner_client.fish,
                        'garov_egasi_inisiali': col.owner_client.fish_inisiali,
                        'garov_egasi_pasport': f"PASPORT SERIYASI {col.owner_client.pasport_seriya} KIM TOMONIDAN BERILGAN {col.owner_client.pasport_berilgan}",
                        'garov_egasi_manzil': col.owner_client.manzil,
                    })
                
                initial_data.update({
                    'ishonchnoma_notarius_fish': col.notarius_fish,
                    'ishonchnoma_notarius_manzil': col.notarius_address,
                    'ishonchnoma_reestr_raqami': col.reestr_number,
                    'ishonchnoma_reestr_sanasi': col.reestr_date.strftime('%d.%m.%Y') if col.reestr_date else '',
                })

            if col.type == 'avto' and hasattr(col, 'auto_detail'):
                auto = col.auto_detail
                initial_data.update({
                    'avto_nomi': auto.nomi,
                    'avto_raqam': auto.davlat_raqami,
                    'avto_kuzov_turi': auto.kuzov_turi,
                    'avto_kuzov': auto.kuzov_raqami,
                    'avto_dvigatel': auto.dvigatel,
                    'avto_shassi': auto.shassi,
                    'avto_yil': auto.yil,
                    'avto_rang': auto.rang,
                    'avto_bahosi': auto.bahosi,
                    'avto_yurgan': getattr(auto, 'yurgan', ''),
                    'avto_texpasport': auto.texpasport,
                    'avto_texpasport_sana': auto.texpasport_sana.strftime('%d.%m.%Y') if auto.texpasport_sana else '',
                    'avto_manzil': auto.manzil,
                })
            elif col.type == 'kochmas' and hasattr(col, 'real_estate_detail'):
                mulk = col.real_estate_detail
                initial_data.update({
                    'mulk_turi': mulk.turi,
                    'mulk_qurilish_maydoni': mulk.qurilish_maydon,
                    'mulk_umumiy_maydoni': mulk.umumiy_maydon,
                    'mulk_yashash_maydoni': mulk.yashash_maydon,
                    'mulk_egasi': col.owner_client.fish if col.owner_client else '',
                    'mulk_reestr_raqami': mulk.reestr_raqami,
                    'mulk_kadastr_raqami': mulk.kadastr_raqami,
                    'mulk_manzili': mulk.manzil,
                    'mulk_bahosi': mulk.bahosi,
                    'mulk_bahosi_soz': mulk.bahosi_soz,
                })
            elif col.type == 'tilla' and hasattr(col, 'gold_detail'):
                tilla = col.gold_detail
                initial_data.update({
                    'tilla_nomi': tilla.nomi,
                    'tilla_probi': tilla.probi,
                    'tilla_vazni': tilla.vazni,
                    'tilla_soni': tilla.soni,
                    'tilla_bahosi': tilla.bahosi,
                    'tilla_bahosi_soz': tilla.bahosi_soz,
                })

    form = UmumiyMalumotForm(initial=initial_data)
    import json
    
    return render(request, 'document_processor/process_audit.html', {
        'form': form,
        'edit_mode': True, 
        'loan': loan,
        'loan_data_json': json.dumps(initial_data, ensure_ascii=False)
    })

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

@login_required
def get_loan_data_api(request, loan_id):
    loan = get_object_or_404(LoanApplication, id=loan_id)
    client = loan.client
    details = loan.details if hasattr(loan, 'details') else None
    financial = loan.financial_info if hasattr(loan, 'financial_info') else None
    contacts = loan.contacts.all()
    collaterals = list(loan.collaterals.all())
    
    # Ma'lumotlarni Vue tushunadigan JSON formatga yig'ish
    data = {"status": "success"}

    # 1. Shaxsiy ma'lumotlar
    personal = {}
    if client:
        personal = {
            "fish": client.fish,
            "fish_inisiali": client.fish_inisiali or '',
            "pasport_seriya": client.pasport_seriya,
            "jshshir": client.jshshir,
            "tugilgan_sana": client.tugilgan_sana.strftime('%d.%m.%Y') if client.tugilgan_sana else '',
            "jinsi": client.jinsi,
            "telefon": client.telefon,
            "pasport_berilgan": client.pasport_berilgan,
            "manzil": client.manzil
        }
    data["personal"] = personal

    # 2. Kontaktlar
    contact_list = []
    for c in contacts:
        contact_list.append({
            "telefon": c.telefon,
            "qarindoshlik": c.qarindoshlik
        })
    # Kamida 2 ta bo'sh kontakt obyekti
    while len(contact_list) < 2:
        contact_list.append({"telefon": "", "qarindoshlik": ""})
    data["contacts"] = contact_list

    # 3. Kredit Ma'lumotlari
    loan_data = {}
    if details:
        loan_data = {
            "shartnoma_raqami": details.shartnoma_raqami,
            "shartnoma_sanasi": details.shartnoma_sanasi.strftime('%d.%m.%Y') if details.shartnoma_sanasi else '',
            "boshlanish_sanasi": details.boshlanish_sanasi.strftime('%d.%m.%Y') if details.boshlanish_sanasi else '',
            "tugash_sanasi": details.tugash_sanasi.strftime('%d.%m.%Y') if details.tugash_sanasi else '',
            "miqdori": details.miqdori,
            "miqdori_soz": details.miqdori_soz,
            "muddat_oy": details.muddat_oy,
            "muddat_oy_soz": details.muddat_oy_soz,
            "foiz": details.foiz,
            "foiz_soz": details.foiz_soz,
            "turi": details.turi if details else '',
            "grafik": details.grafik_turi if details else '',
            "grafik_matni": details.grafik_matni or ''
        }
    data["loan"] = loan_data

    # 4. Garov (Collateral)
    collateral_data = {
        # Garov egasi ma'lumotlari default bo'sh
        "owner_fish": "", "owner_initials": "", "owner_birth_date": "", "owner_passport": "",
        "owner_jshshir": "", "owner_gender": "", "owner_passport_given_by": "", "owner_address": "",
        
        # Ishonchnoma ma'lumotlari default bo'sh
        "notarius_fish": "", "notarius_address": "", "reestr_number": "", "reestr_date": "",
        
        # Elementlar listi
        "selected_types": []
    }
    
    if collaterals:
        # Hamma garovlar bitta egaga yoki bitta ishonchnomaga bog'langan deb hisoblaymiz (soddalashtirilgan)
        first_col = collaterals[0]
        collateral_data["owner_type"] = first_col.egasi
        
        if first_col.egasi != 'borrower':
            collateral_data.update({
                "owner_fish": first_col.uchinchi_shaxs_fish or '',
                "owner_initials": first_col.uchinchi_shaxs_inisiali or '',
                "owner_birth_date": first_col.uchinchi_shaxs_tug_sana.strftime('%d.%m.%Y') if first_col.uchinchi_shaxs_tug_sana else '',
                "owner_passport": first_col.uchinchi_shaxs_pasport or '',
                "owner_jshshir": first_col.uchinchi_shaxs_jshshir or '',
                "owner_gender": first_col.uchinchi_shaxs_jinsi or '',
                "owner_passport_given_by": first_col.uchinchi_shaxs_pasport_kim_tomondan or '',
                "owner_address": first_col.uchinchi_shaxs_manzil or '',
            })
            
        if first_col.egasi == 'general_proxy' and hasattr(first_col, 'ishonchnoma'):
            ishn = first_col.ishonchnoma
            collateral_data.update({
                "notarius_fish": ishn.notarius_fish or '',
                "notarius_address": ishn.notarius_manzil or '',
                "reestr_number": ishn.reestr_raqami or '',
                "reestr_date": ishn.reestr_sanasi.strftime('%d.%m.%Y') if ishn.reestr_sanasi else '',
            })

        for col in collaterals:
            # Avto
            if col.turi == 'avto' and hasattr(col, 'auto_detail'):
                auto = col.auto_detail
                collateral_data["selected_types"].append("avto")
                collateral_data.update({
                    "avto_nomi": auto.nomi or '', "avto_kuzov_turi": auto.kuzov_turi or '',
                    "avto_kuzov": auto.kuzov_raqami or '', "avto_dvigatel": auto.dvigatel or '',
                    "avto_shassi": auto.shassi or '', "avto_rang": auto.rang or '',
                    "avto_yil": auto.yil or '', "avto_texpasport": auto.texpasport or '',
                    "avto_texpasport_sana": auto.texpasport_sana.strftime('%d.%m.%Y') if auto.texpasport_sana else '',
                    "avto_manzil": auto.manzil or '', "avto_raqam": auto.davlat_raqami or '',
                    "avto_bahosi": auto.bahosi or '', "avto_bahosi_soz": auto.bahosi_soz or '',
                })
            # Mulk
            elif col.turi == 'kochmas' and hasattr(col, 'real_estate_detail'):
                mulk = col.real_estate_detail
                collateral_data["selected_types"].append("kochmas")
                collateral_data.update({
                    "mulk_turi": mulk.turi or '', "mulk_umumiy": mulk.umumiy_maydon or '',
                    "mulk_qurilish": mulk.qurilish_maydon or '', "mulk_foydalanish": mulk.foydali_maydon or '',
                    "mulk_yashash": mulk.yashash_maydon or '', "mulk_reestr_raqami": mulk.kadastr_raqami or '',
                    "mulk_kadastr": mulk.kadastr_raqami or '', "mulk_manzil": mulk.manzil or '',
                    "mulk_bahosi": mulk.bahosi or '', "mulk_bahosi_soz": mulk.bahosi_soz or '',
                })
            # Tilla
            elif col.turi == 'tilla' and hasattr(col, 'gold_detail'):
                tilla = col.gold_detail
                collateral_data["selected_types"].append("tilla")
                collateral_data.update({
                    "tilla_nomi": tilla.nomi or '', "tilla_probi": tilla.probi or '',
                    "tilla_vazni": tilla.vazni or '', "tilla_soni": tilla.soni or '',
                    "tilla_bahosi": tilla.bahosi or '', "tilla_bahosi_soz": tilla.bahosi_soz or ''
                })
            # Sugurta
            elif col.turi == 'sugurta' and hasattr(col, 'insurance_detail'):
                sugurta = col.insurance_detail
                collateral_data["selected_types"].append("sugurta")
                collateral_data.update({
                    "sugurta_kompaniya": sugurta.kompaniya_nomi or '', "sugurta_polisi": sugurta.polis_raqami or '',
                    "sugurta_sana": sugurta.polis_sanasi.strftime('%d.%m.%Y') if sugurta.polis_sanasi else '',
                    "sugurta_summa": sugurta.sugurta_summasi or '', "sugurta_summa_soz": sugurta.sugurta_summasi_soz or ''
                })
                
    data["collateral"] = collateral_data

    # 5. Moliyaviy va Tashkilot
    financial_data = {}
    if financial:
        financial_data = {
            "ish_joyi": financial.ish_joyi, "daromad": financial.daromadi,
            "xarajatlar": financial.xarajatlari, "tahminiy_tolov": financial.kredit_tolovi,
            "majburiyatlar": financial.boshqa_majburiyatlar, "tashkilot_nomi": loan.tashkilot_nomi,
            "direktor_fish": loan.direktor_fish, "direktor_fish_inisiali": loan.direktor_inisiali,
            "filial_nomi": loan.filial_nomi or '', "filial_boshligi": loan.filial_boshligi_fish or '',
            "filial_boshligi_inisiali": loan.filial_boshligi_inisiali or ''
        }
    data["financial"] = financial_data
    
    return JsonResponse(data)


@login_required
def edit_loan_vue_api(request, loan_id):
    if request.method == 'POST':
        try:
            loan = get_object_or_404(LoanApplication, id=loan_id)
            data = json.loads(request.body)

            # 1. Shaxsiy ma'lumotlar (Personal)
            p_data = data.get('personal') or {}
            client = loan.client
            if client:
                client.fish = clean_str(p_data.get('fish'))
                client.fish_inisiali = clean_str(p_data.get('fish_inisiali'))
                client.pasport_seriya = clean_str(p_data.get('pasport_seriya'))
                client.pasport_berilgan = clean_str(p_data.get('pasport_berilgan'))
                client.jshshir = clean_int(p_data.get('jshshir'))
                client.tugilgan_sana = parse_date(p_data.get('tugilgan_sana'))
                client.jinsi = clean_str(p_data.get('jinsi'))
                client.telefon = clean_phone(p_data.get('telefon'))
                client.manzil = clean_str(p_data.get('manzil'))
                client.save()

            # 2. Kontaktlar - Eskilarni o'chirib yangilarini yozamiz
            loan.contacts.all().delete()
            contacts_data = data.get('contacts') or []
            for c in contacts_data:
                c_fish = clean_str(c.get('fish')) # Ba'zan fish ham kelishi mumkin
                if c_fish or c.get('telefon'):
                    ContactPerson.objects.create(
                        application=loan,
                        fish=c_fish,
                        telefon=clean_phone(c.get('telefon')),
                        qarindoshlik=clean_str(c.get('qarindoshlik'))
                    )

            # 3. Kredit Ma'lumotlari (Loan Details)
            l_d = data.get('loan') or {}
            details, _ = LoanDetails.objects.get_or_create(application=loan)
            details.shartnoma_raqami = clean_str(l_d.get('shartnoma_raqami'))
            details.shartnoma_sanasi = parse_date(l_d.get('shartnoma_sanasi'))
            details.boshlanish_sanasi = parse_date(l_d.get('boshlanish_sanasi'))
            details.tugash_sanasi = parse_date(l_d.get('tugash_sanasi'))
            details.miqdori = clean_int(l_d.get('miqdori'))
            details.miqdori_soz = clean_str(l_d.get('miqdori_soz'))
            details.muddat_oy = clean_str(l_d.get('muddat_oy'))
            details.muddat_oy_soz = clean_str(l_d.get('muddat_oy_soz'))
            details.foiz = clean_str(l_d.get('foiz'))
            details.foiz_soz = clean_str(l_d.get('foiz_soz'))
            details.turi = clean_str(l_d.get('turi'))
            details.grafik_turi = clean_str(l_d.get('grafik'))
            details.grafik_matni = clean_str(l_d.get('grafik_matni'))
            details.save()

            # 4. Moliyaviy va Tashkilot (Financial Info)
            f_data = data.get('financial') or {}
            fin_info, _ = FinancialInfo.objects.get_or_create(application=loan)
            fin_info.ish_joyi = clean_str(f_data.get('ish_joyi'))
            fin_info.daromad = clean_int(f_data.get('daromad'))
            fin_info.xarajatlar = clean_int(f_data.get('xarajatlar'))
            fin_info.tahminiy_tolov = clean_int(f_data.get('tahminiy_tolov'))
            fin_info.majburiyatlar = clean_str(f_data.get('majburiyatlar'))
            fin_info.filial_nomi = clean_str(f_data.get('filial_nomi')) or fin_info.filial_nomi
            fin_info.filial_boshligi = clean_str(f_data.get('filial_boshligi'))
            fin_info.filial_boshligi_inisiali = clean_str(f_data.get('filial_boshligi_inisiali'))
            fin_info.tashkilot_nomi = clean_str(f_data.get('tashkilot_nomi')) or fin_info.tashkilot_nomi
            fin_info.direktor_fish = clean_str(f_data.get('direktor_fish')) or fin_info.direktor_fish
            fin_info.direktor_fish_inisiali = clean_str(f_data.get('direktor_fish_inisiali')) or fin_info.direktor_fish_inisiali
            fin_info.save()

            # 5. Garov (Collateral) - To'liq o'chirib qayta yaratish
            loan.collaterals.all().delete()
            collateral_payload = data.get('collateral') or {}
            selected_types = collateral_payload.get('selected_types') or []
            owner_type = clean_str(collateral_payload.get('owner_type') or 'borrower')

            # Garov egasini aniqlash
            owner_client = loan.client
            if owner_type != 'borrower':
                o_pasport = clean_str(collateral_payload.get('owner_passport'))
                o_jshshir = clean_int(collateral_payload.get('owner_jshshir'))
                o_fish = clean_str(collateral_payload.get('owner_fish'))

                other_client = None
                if o_pasport:
                    other_client = Client.objects.filter(pasport_seriya=o_pasport).first()
                if not other_client and o_jshshir:
                    other_client = Client.objects.filter(jshshir=o_jshshir).first()
                if not other_client and o_fish:
                    other_client = Client.objects.filter(fish__icontains=o_fish).first()

                if not other_client and (o_fish or o_pasport):
                    other_client = Client.objects.create(
                        fish=o_fish,
                        fish_inisiali=clean_str(collateral_payload.get('owner_initials')),
                        pasport_seriya=o_pasport,
                        pasport_berilgan=clean_str(collateral_payload.get('owner_passport_given_by')),
                        jshshir=o_jshshir,
                        tugilgan_sana=parse_date(collateral_payload.get('owner_birth_date')),
                        manzil=clean_str(collateral_payload.get('owner_address')),
                        jinsi=clean_str(collateral_payload.get('owner_gender'))
                    )
                if other_client:
                    owner_client = other_client

            for c_type in selected_types:
                db_c_type = c_type
                if c_type == 'kochmas_mulk': db_c_type = 'kochmas'

                base_col = Collateral.objects.create(
                    application=loan,
                    type=db_c_type,
                    owner_type=owner_type,
                    owner_client=owner_client,
                    notarius_fish=clean_str(collateral_payload.get('notarius_fish')),
                    notarius_address=clean_str(collateral_payload.get('notarius_address')),
                    reestr_number=clean_str(collateral_payload.get('reestr_number')),
                    reestr_date=parse_date(collateral_payload.get('reestr_date'))
                )

                if db_c_type == 'avto':
                    AutoCollateral.objects.create(
                        collateral=base_col,
                        nomi=clean_str(collateral_payload.get('avto_nomi')),
                        kuzov_turi=clean_str(collateral_payload.get('avto_kuzov_turi')),
                        kuzov_raqami=clean_str(collateral_payload.get('avto_kuzov')),
                        dvigatel=clean_str(collateral_payload.get('avto_dvigatel')),
                        shassi=clean_str(collateral_payload.get('avto_shassi')) or "RAKAMSIZ",
                        rang=clean_str(collateral_payload.get('avto_rang')),
                        yil=clean_int(collateral_payload.get('avto_yil')),
                        texpasport=clean_str(collateral_payload.get('avto_texpasport')),
                        texpasport_sana=parse_date(collateral_payload.get('avto_texpasport_sana')),
                        manzil=clean_str(collateral_payload.get('avto_manzil')),
                        davlat_raqami=clean_str(collateral_payload.get('avto_raqam')),
                        bahosi=clean_int(collateral_payload.get('avto_bahosi')),
                        bahosi_soz=clean_str(collateral_payload.get('avto_bahosi_soz'))
                    )
                elif db_c_type == 'kochmas':
                    RealEstateCollateral.objects.create(
                        collateral=base_col,
                        turi=clean_str(collateral_payload.get('mulk_turi')),
                        umumiy_maydon=clean_str(collateral_payload.get('mulk_umumiy')),
                        qurilish_maydon=clean_str(collateral_payload.get('mulk_qurilish')),
                        foydali_maydon=clean_str(collateral_payload.get('mulk_foydalanish')),
                        yashash_maydon=clean_str(collateral_payload.get('mulk_yashash')),
                        kadastr_raqami=clean_str(collateral_payload.get('mulk_kadastr')),
                        reestr_raqami=clean_str(collateral_payload.get('mulk_reestr_raqami')),
                        manzil=clean_str(collateral_payload.get('mulk_manzil')),
                        bahosi=clean_int(collateral_payload.get('mulk_bahosi')),
                        bahosi_soz=clean_str(collateral_payload.get('mulk_bahosi_soz'))
                    )
                elif db_c_type == 'tilla':
                    GoldCollateral.objects.create(
                        collateral=base_col,
                        nomi=clean_str(collateral_payload.get('tilla_nomi')),
                        probi=clean_str(collateral_payload.get('tilla_probi')),
                        vazni=clean_str(collateral_payload.get('tilla_vazni')),
                        soni=clean_int(collateral_payload.get('tilla_soni')),
                        bahosi=clean_int(collateral_payload.get('tilla_bahosi')),
                        bahosi_soz=clean_str(collateral_payload.get('tilla_bahosi_soz'))
                    )
                elif db_c_type == 'sugurta':
                    InsuranceCollateral.objects.create(
                        collateral=base_col,
                        kompaniya=clean_str(collateral_payload.get('sugurta_kompaniya')),
                        polis_raqami=clean_str(collateral_payload.get('sugurta_polisi')),
                        sana=parse_date(collateral_payload.get('sugurta_sana')),
                        summa=clean_int(collateral_payload.get('sugurta_summa')),
                        summa_soz=clean_str(collateral_payload.get('sugurta_summa_soz'))
                    )

            return JsonResponse({'status': 'success', 'loan_id': loan.id})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    return JsonResponse({'status': 'error', 'message': 'Invalid method'}, status=400)

@login_required
def edit_loan_vue_page(request, loan_id):
    import json
    loan = get_object_or_404(LoanApplication, id=loan_id)
    client = loan.client
    details = loan.details if hasattr(loan, 'details') else None
    financial = loan.financial_info if hasattr(loan, 'financial_info') else None
    contacts = loan.contacts.all()
    collaterals = list(loan.collaterals.all())
    
    # 1. Shaxsiy ma'lumotlar
    personal = {}
    if client:
        personal = {
            "fish": client.fish or '',
            "fish_inisiali": client.fish_inisiali or '',
            "pasport_seriya": client.pasport_seriya or '',
            "jshshir": client.jshshir or '',
            "tugilgan_sana": client.tugilgan_sana.strftime('%d.%m.%Y') if client.tugilgan_sana else '',
            "jinsi": client.jinsi or '',
            "telefon": client.telefon or '',
            "pasport_berilgan": client.pasport_berilgan or '',
            "manzil": client.manzil or ''
        }

    # 2. Kontaktlar
    contact_list = []
    for c in contacts:
        contact_list.append({
            "telefon": c.telefon or '',
            "qarindoshlik": c.qarindoshlik or ''
        })
    while len(contact_list) < 2:
        contact_list.append({"telefon": "", "qarindoshlik": ""})

    # 3. Kredit Ma'lumotlari
    loan_data = {}
    if details:
        loan_data = {
            "shartnoma_raqami": details.shartnoma_raqami or '',
            "shartnoma_sanasi": details.shartnoma_sanasi.strftime('%d.%m.%Y') if details.shartnoma_sanasi else '',
            "boshlanish_sanasi": details.boshlanish_sanasi.strftime('%d.%m.%Y') if details.boshlanish_sanasi else '',
            "tugash_sanasi": details.tugash_sanasi.strftime('%d.%m.%Y') if details.tugash_sanasi else '',
            "miqdori": details.miqdori or '',
            "miqdori_soz": details.miqdori_soz or '',
            "muddat_oy": details.muddat_oy or '',
            "muddat_oy_soz": details.muddat_oy_soz or '',
            "foiz": details.foiz or '',
            "foiz_soz": details.foiz_soz or '',
            "turi": details.turi or '',
            "grafik": details.grafik_turi or '',
            "grafik_matni": details.grafik_matni or ''
        }

    # 4. Garov (Collateral)
    collateral_data = {
        "owner_fish": "", "owner_initials": "", "owner_birth_date": "", "owner_passport": "",
        "owner_jshshir": "", "owner_gender": "", "owner_passport_given_by": "", "owner_address": "",
        "notarius_fish": "", "notarius_address": "", "reestr_number": "", "reestr_date": "",
        "selected_types": []
    }
    
    if collaterals:
        first_col = collaterals[0]
        collateral_data["owner_type"] = first_col.owner_type if hasattr(first_col, 'owner_type') and first_col.owner_type else 'borrower'
        
        if collateral_data["owner_type"] != 'borrower' and first_col.owner_client:
            oc = first_col.owner_client
            collateral_data.update({
                "owner_fish": oc.fish or '',
                "owner_initials": oc.fish_inisiali or '',
                "owner_birth_date": oc.tugilgan_sana.strftime('%d.%m.%Y') if oc.tugilgan_sana else '',
                "owner_passport": oc.pasport_seriya or '',
                "owner_jshshir": oc.jshshir or '',
                "owner_gender": oc.jinsi or '',
                "owner_passport_given_by": oc.pasport_berilgan or '',
                "owner_address": oc.manzil or '',
            })
            
        if collateral_data["owner_type"] == 'general_proxy':
            collateral_data.update({
                "notarius_fish": first_col.notarius_fish or '',
                "notarius_address": first_col.notarius_address or '',
                "reestr_number": first_col.reestr_number or '',
                "reestr_date": first_col.reestr_date.strftime('%d.%m.%Y') if first_col.reestr_date else '',
            })

        for col in collaterals:
            # Avto
            if col.type == 'avto' and hasattr(col, 'auto_detail'):
                auto = col.auto_detail
                collateral_data["selected_types"].append("avto")
                collateral_data.update({
                    "avto_nomi": auto.nomi or '', "avto_kuzov_turi": auto.kuzov_turi or '',
                    "avto_kuzov": auto.kuzov_raqami or '', "avto_dvigatel": auto.dvigatel or '',
                    "avto_shassi": auto.shassi or '', "avto_rang": auto.rang or '',
                    "avto_yil": auto.yil or '', "avto_texpasport": auto.texpasport or '',
                    "avto_texpasport_sana": auto.texpasport_sana.strftime('%d.%m.%Y') if auto.texpasport_sana else '',
                    "avto_manzil": auto.manzil or '', "avto_raqam": auto.davlat_raqami or '',
                    "avto_bahosi": auto.bahosi or '', "avto_bahosi_soz": auto.bahosi_soz or '',
                })
            # Mulk
            elif col.type == 'kochmas' and hasattr(col, 'real_estate_detail'):
                mulk = col.real_estate_detail
                collateral_data["selected_types"].append("kochmas")
                collateral_data.update({
                    "mulk_turi": mulk.turi or '', "mulk_umumiy": mulk.umumiy_maydon or '',
                    "mulk_qurilish": mulk.qurilish_maydon or '', "mulk_foydalanish": mulk.foydali_maydon or '',
                    "mulk_yashash": mulk.yashash_maydon or '', "mulk_reestr_raqami": mulk.reestr_raqami or '',
                    "mulk_kadastr": mulk.kadastr_raqami or '', "mulk_manzil": mulk.manzil or '',
                    "mulk_bahosi": mulk.bahosi or '', "mulk_bahosi_soz": mulk.bahosi_soz or '',
                })
            # Tilla
            elif col.type == 'tilla' and hasattr(col, 'gold_detail'):
                tilla = col.gold_detail
                collateral_data["selected_types"].append("tilla")
                collateral_data.update({
                    "tilla_nomi": tilla.nomi or '', "tilla_probi": tilla.probi or '',
                    "tilla_vazni": tilla.vazni or '', "tilla_soni": tilla.soni or '',
                    "tilla_bahosi": tilla.bahosi or '', "tilla_bahosi_soz": tilla.bahosi_soz or ''
                })
            # Sugurta
            elif col.type == 'sugurta' and hasattr(col, 'insurance_detail'):
                sugurta = col.insurance_detail
                collateral_data["selected_types"].append("sugurta")
                collateral_data.update({
                    "sugurta_kompaniya": sugurta.kompaniya or '', "sugurta_polisi": sugurta.polis_raqami or '',
                    "sugurta_sana": sugurta.sana.strftime('%d.%m.%Y') if sugurta.sana else '',
                    "sugurta_summa": sugurta.summa or '', "sugurta_summa_soz": sugurta.summa_soz or ''
                })

    # 5. Moliyaviy va Tashkilot
    financial_data = {}
    if financial:
        financial_data = {
            "ish_joyi": financial.ish_joyi or '', "daromad": financial.daromad or '',
            "xarajatlar": financial.xarajatlar or '', "tahminiy_tolov": financial.tahminiy_tolov or '',
            "majburiyatlar": financial.majburiyatlar or '', "tashkilot_nomi": financial.tashkilot_nomi or '',
            "direktor_fish": financial.direktor_fish or '', "direktor_fish_inisiali": financial.direktor_fish_inisiali or '',
            "filial_nomi": financial.filial_nomi or '', "filial_boshligi": financial.filial_boshligi or '',
            "filial_boshligi_inisiali": financial.filial_boshligi_inisiali or ''
        }

    # Asosiy Data Dict
    full_data = {
        "personal": personal,
        "contacts": contact_list,
        "loan": loan_data,
        "collateral": collateral_data,
        "financial": financial_data
    }
    
    context = {
        'loan_id': loan.id,
        'loan': loan,
        'loan_data_json': json.dumps(full_data, ensure_ascii=False)
    }

    return render(request, 'document_processor/loan_edit.html', context)

