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
from django.db.models import Q, Count, Sum
from django.db.models.functions import TruncMonth
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
    import re
    schedule = []
    total_p = 0
    total_i = 0
    grand_total = 0

    # Satrlarga ajratish
    import re
    schedule = []
    total_p = 0
    total_i = 0
    grand_total = 0

    # Satrlarga ajratish
    lines = [l.strip() for l in text.strip().splitlines() if l.strip()]
    
    # Sana patterni (dd.mm.yyyy yoki d.m.yyyy)
    date_pattern = re.compile(r'(\d{1,2}[./]\d{1,2}[./]\d{2,4})')

    for line in lines:
        try:
            # 1. Qatorda sana bormi?
            date_match = date_pattern.search(line)
            if not date_match:
                continue 

            original_date_str = date_match.group(1)
            date_str = original_date_str
            
            # --- Date Normalization ---
            # Agar sana '/' bilan kelsa (masalan 2/16/2026 -> 16.02.2026)
            if '/' in date_str:
                try:
                    parts = [int(p) for p in date_str.split('/')]
                    if len(parts) == 3:
                        if parts[0] > 12: # DD/MM/YYYY (16/02/2026)
                            d, m, y = parts[0], parts[1], parts[2]
                        else: # MM/DD/YYYY (02/16/2026 - US Format)
                            m, d, y = parts[0], parts[1], parts[2]
                            # Xavfsizlik uchun: agar 2-qism > 12 bo'lsa, aniq M/D/Y
                            # Agar 1-qism > 12 bo'lsa, aniq D/M/Y (yuqorida tekshirildi)
                        
                        date_str = f"{d:02d}.{m:02d}.{y}"
                except:
                    pass
            # --------------------------
            
            # 2. Ustunlarga ajratish strategiyasi
            # A) Tab bo'yicha
            parts = [p.strip() for p in line.split('\t') if p.strip()]
            
            # B) Agar parts kam bo'lsa (tab yo'q), 2 yoki undan ortiq bo'shliq bo'yicha
            if len(parts) < 3:
                parts = [p.strip() for p in re.split(r'\s{2,}', line) if p.strip()]
            
            # C) Agar hali ham kam bo'lsa, va sana bor bo'lsa, demak raqamlar orasida tab/katta bo'shliq yo'q.
            # Bu holda qiyin, lekin harakat qilamiz.
            if len(parts) < 3:
                 # Oxirgi chora: oddiy split, lekin bu xavfli (1 000 000 ni 3 bo'lak qiladi)
                 # Shuning uchun bu yerni o'zgartirmaymiz, faqat yuqoridagi 2 metodga tayanamiz.
                 # Lekin shuni e'tiborga olish kerakki, Exceldan olinganda 1 000 000 odatda "1 000 000" (quote ichida) yoki shunchaki text bo'ladi.
                 pass

            # Sana qaysi partda?
            date_index = -1
            for i, p in enumerate(parts):
                if original_date_str in p:
                    date_index = i
                    break
            
            if date_index == -1:
                # Agar sana split qilingan bo'lsa (kamdan kam holat), qaytadan qidiramiz
                continue

            # 3. Ma'lumotlarni olish
            # Tartib raqami
            num = parts[date_index - 1] if date_index > 0 else str(len(schedule) + 1)
            if not num.replace('.', '').isdigit():
                 num = str(len(schedule) + 1)

            # Summalar (sanadan keyingi ustunlar)
            amounts = parts[date_index + 1:]
            
            # Agar summalar kam bo'lsa (masalan "Jami" ustuni qolib ketgan bo'lsa)
            # Bizga kamida 4 ta ustun kerak: Qoldiq, Asosiy, Foiz, Jami
            
            def clean_amount(s):
                # Bo'shliqlarni olib tashlash
                s = s.replace(' ', '').replace("'", "").strip()
                
                # Agar hech narsa bo'lmasa -> 0
                if not s:
                    return "0"

                # 1. Minglik ajratuvchilar (multiple nuqta yoki vergul)
                if s.count(',') > 1: s = s.replace(',', '')
                if s.count('.') > 1: s = s.replace('.', '')
                
                # 2. Aralash belgilar (. va ,)
                if ',' in s and '.' in s:
                    if s.rfind(',') < s.rfind('.'): # 1,200.00 (vergul minglik)
                        s = s.replace(',', '')
                    else: # 1.200,00 (nuqta minglik)
                        s = s.replace('.', '').replace(',', '.')
                
                # 3. Yagona belgi qolganda
                elif ',' in s:
                    # Agar faqat vergul bo'lsa (1200,00 yoki 1,200)
                    # Odatda 3 ta digitdan keyin bo'lmasa bu decimal.
                    # Lekin float(s) uchun nuqta kerak
                    s = s.replace(',', '.')
                
                return s

            balance_str = amounts[0] if len(amounts) > 0 else "0"
            principal_str = amounts[1] if len(amounts) > 1 else "0"
            interest_str = amounts[2] if len(amounts) > 2 else "0"
            total_str = amounts[3] if len(amounts) > 3 else "0"
            
            # Agar Jami bo'sh bo'lsa, lekin Asosiy va Foiz bor bo'lsa, hisoblaymiz
            p_val = 0
            i_val = 0
            t_val = 0
            
            try: p_val = float(clean_amount(principal_str))
            except: pass
            
            try: i_val = float(clean_amount(interest_str))
            except: pass
            
            try: t_val = float(clean_amount(total_str))
            except: pass
            
            # Agar total 0 bo'lsa, o'zimiz hisoblaymiz
            if t_val == 0 and (p_val > 0 or i_val > 0):
                t_val = p_val + i_val
                # Formatlash uchun stringga o'tkazamiz
                total_str = "{:,.2f}".format(t_val) # Vergul minglik, nuqta decimal

            total_p += p_val
            total_i += i_val

            schedule.append({
                'num': num,
                'date': date_str,
                'balance': balance_str,
                'principal': principal_str,
                'interest': interest_str,
                'total': total_str # Original string yoki hisoblangan
            })
        except Exception:
            continue

    grand_total = total_p + total_i
    
    return schedule, "{:,.2f}".format(total_p).replace(",", " "), "{:,.2f}".format(total_i).replace(",", " "), "{:,.2f}".format(grand_total).replace(",", " ")

# --- VIEWS ---

@login_required
@login_required
@login_required
def dashboard_view(request):
    user = request.user
    
    # 1. Base QuerySet
    if is_operator(user) and not (is_director(user) or is_moderator(user)):
        loans = LoanAgreement.objects.filter(created_by=user, is_deleted=False)
    else:
        loans = LoanAgreement.objects.filter(is_deleted=False)

    # 2. Key Metrics (Info Boxes)
    total_docs = loans.count()
    raw_amount = loans.aggregate(Sum('kredit_miqdori'))['kredit_miqdori__sum'] or 0
    total_amount = raw_amount / 1000  # Show in ming so'm
    pending_count = loans.filter(status__in=['pending_moderator', 'pending_director']).count()
    completed_count = loans.filter(status='completed').count()
    rejected_count = loans.filter(status='rejected').count()

    # 3. Charts Data

    # A) Age Distribution (Qarz oluvchi yoshi)
    # Calculate age in python for simplicity
    today = date.today()
    age_groups = {
        '18-25': 0,
        '26-35': 0,
        '36-50': 0,
        '50+': 0
    }
    
    # Fetch dates only to minimize memory
    birth_dates = loans.values_list('qarz_oluvchi_tugilgan_sana', flat=True)
    
    for bdate in birth_dates:
        if bdate:
            age = relativedelta(today, bdate).years
            if 18 <= age <= 25:
                age_groups['18-25'] += 1
            elif 26 <= age <= 35:
                age_groups['26-35'] += 1
            elif 36 <= age <= 50:
                age_groups['36-50'] += 1
            elif age > 50:
                age_groups['50+'] += 1

    age_labels = list(age_groups.keys())
    age_data = list(age_groups.values())

    # B) Credit Duration (Kredit muddati)
    duration_stats = loans.values('kredit_muddat_oy').annotate(count=Count('id')).order_by('kredit_muddat_oy')
    duration_labels = []
    duration_data = []
    for entry in duration_stats:
        if entry['kredit_muddat_oy']:
            duration_labels.append(f"{entry['kredit_muddat_oy']} oy")
            duration_data.append(entry['count'])

    # C) Payment Schedule (Grafik usuli)
    schedule_stats = loans.values('grafik').annotate(count=Count('id'))
    schedule_labels = []
    schedule_data = []
    grafik_map = dict(LoanAgreement.GRAFIK_CHOICES)
    for entry in schedule_stats:
        schedule_labels.append(grafik_map.get(entry['grafik'], entry['grafik']))
        schedule_data.append(entry['count'])

    # D) Collateral Type (Garov turi)
    collateral_stats = loans.values('garov_turi').annotate(count=Count('id'))
    collateral_labels = []
    collateral_data = []
    garov_map = dict(LoanAgreement.GAROV_TURI_CHOICES)
    for entry in collateral_stats:
        collateral_labels.append(garov_map.get(entry['garov_turi'], entry['garov_turi']))
        collateral_data.append(entry['count'])

    # E) Credit Type (Kredit turi)
    credit_type_stats = loans.values('kredit_turi').annotate(count=Count('id'))
    credit_type_labels = []
    credit_type_data = []
    kredit_map = dict(LoanAgreement.KREDIT_TURI_CHOICES)
    for entry in credit_type_stats:
        credit_type_labels.append(kredit_map.get(entry['kredit_turi'], entry['kredit_turi']))
        credit_type_data.append(entry['count'])

    # F) Collateral Owner (Garov egasi)
    owner_stats = loans.values('garov_egasi').annotate(count=Count('id'))
    owner_labels = []
    owner_data = []
    owner_map = dict(LoanAgreement.GAROV_EGASI_CHOICES)
    for entry in owner_stats:
        owner_labels.append(owner_map.get(entry['garov_egasi'], entry['garov_egasi']))
        owner_data.append(entry['count'])

    # G) Branch Distribution (Filial)
    branch_stats = loans.values('filial_nomi').annotate(count=Count('id'))
    branch_labels = []
    branch_data = []
    # Filial choices is list of tuples, handle it
    filial_map = dict(LoanAgreement.FILIAL_CHOICES)
    for entry in branch_stats:
        branch_labels.append(filial_map.get(entry['filial_nomi'], entry['filial_nomi']))
        branch_data.append(entry['count'])

    # 4. Recent Docs
    recent_docs = loans.order_by('-created_at')[:5]

    context = {
        'total_docs': total_docs,
        'total_amount': total_amount,
        'pending_count': pending_count,
        'completed_count': completed_count,
        'rejected_count': rejected_count,
        'recent_docs': recent_docs,
        
        # Charts Context
        'age_labels': age_labels,
        'age_data': age_data,
        
        'duration_labels': duration_labels,
        'duration_data': duration_data,
        
        'schedule_labels': schedule_labels,
        'schedule_data': schedule_data,
        
        'collateral_labels': collateral_labels,
        'collateral_data': collateral_data,
        
        'credit_type_labels': credit_type_labels,
        'credit_type_data': credit_type_data,
        
        'owner_labels': owner_labels,
        'owner_data': owner_data,
        
        'branch_labels': branch_labels,
        'branch_data': branch_data,
    }

    return render(request, 'document_processor/dashboard.html', context)

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

                # --- YANGI MAYDONLAR FIX ---
                if data.get('filial_boshligi_inisiali'):
                    data['filial_boshligi_inisiali'] = data['filial_boshligi_inisiali'].upper()
                
                if not data.get('direktor_fish'):
                    data['direktor_fish'] = "OBIDOV ABDULLA SHOKIR O'G'LI"
                
                if not data.get('direktor_fish_inisiali'):
                    data['direktor_fish_inisiali'] = "A.SH.OBIDOV"
                # ---------------------------

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
    loans = LoanAgreement.objects.filter(is_deleted=False).order_by('-created_at')
    return render(request, 'document_processor/moderator_dashboard.html', {'loans': loans})

@login_required
@user_passes_test(is_director)
def director_dashboard(request):
    # Direktorga tegishli barcha arizalar
    loans = LoanAgreement.objects.filter(is_deleted=False).order_by('-created_at')
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
            
            # --- ZIP GENERATION REMOVED AS PER REQUEST ---
            # generate_loan_docs(request, loan)
            # ---------------------------------------------
            
            return redirect('director_dashboard')
            
            return redirect('director_dashboard')
            
    return redirect('dashboard')


@login_required
def delete_loan(request, loan_id):
    """
    Soft delete loan application.
    """
    loan = get_object_or_404(LoanAgreement, id=loan_id)
    loan.is_deleted = True
    loan.save()
    return redirect('dashboard')

@login_required
def edit_loan(request, loan_id):
    """
    Edit loan application. 
    Locked if status is 'completed'.
    """
    loan = get_object_or_404(LoanAgreement, id=loan_id)
    
    # Check if locked
    if loan.status == 'completed':
        # You might want to show a message or redirect
        return redirect('view_application', loan_id=loan.id)

    if request.method == 'POST':
        form = UmumiyMalumotForm(request.POST)
        if form.is_valid():
            try:
                from .utils import number_to_text_uz, cleaner
                data = form.cleaned_data
                
                # Update fields manually or iterate
                # Better approach: Iterate over form data and set attributes
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
                
                for field, value in data.items():
                    if field in integer_fields and value == '':
                        setattr(loan, field, None)
                    else:
                        setattr(loan, field, value)

                if not loan.kredit_miqdori_soz: # Or always update if changed? Let's check logic
                    loan.kredit_miqdori_soz = number_to_text_uz(cleaner(loan.kredit_miqdori))
                if not loan.foiz_stavkasi_soz:
                    loan.foiz_stavkasi_soz = number_to_text_uz(cleaner(loan.foiz_stavkasi))
                
                 # Handle avto_bahosi_soz if present (now in model)
                if loan.avto_bahosi and not loan.avto_bahosi_soz:
                     loan.avto_bahosi_soz = number_to_text_uz(cleaner(loan.avto_bahosi))
                
                # If editing a rejected loan, maybe reset status to pending_moderator?
                # Usually yes, so moderator can check again.
                if loan.status == 'rejected':
                    loan.status = 'pending_moderator'
                    loan.moderator_approved_at = None
                    loan.moderator_approved_by = None
                    loan.director_approved_at = None
                    loan.director_approved_by = None
                
                loan.save()
                return redirect('dashboard')
            except Exception as e:
                print(f"Error editing loan: {e}")
        else:
             return render(request, 'document_processor/process_audit.html', {'form': form, 'edit_mode': True, 'loan': loan})

    else:
        # Pre-populate form
        initial_data = {}
        for field in LoanAgreement._meta.get_fields():
            if field.concrete and not field.many_to_many and not field.one_to_many:
                val = getattr(loan, field.name)
                initial_data[field.name] = val
        
        form = UmumiyMalumotForm(initial=initial_data)

    return render(request, 'document_processor/process_audit.html', {'form': form, 'edit_mode': True, 'loan': loan})


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
        loans = LoanAgreement.objects.filter(is_deleted=False).order_by('-created_at')
    elif is_moderator(user):
        # Moderator hamma narsani ko'ra oladi (yoki faqat pending_moderator dan keyingilarni)
        # Hozircha hamma narsani ko'rsatamiz
        loans = LoanAgreement.objects.filter(is_deleted=False).order_by('-created_at')
    else:
        # Operator o'zi kiritgan arizalarni ko'radi
        loans = LoanAgreement.objects.filter(created_by=user, is_deleted=False).order_by('-created_at')
        
    return render(request, 'document_processor/document_list.html', {'documents': loans})

class DocumentListView(ListView):
    # Bu klassni yuqoridagi funksiya bilan almashtiramiz yoki o'zgartiramiz
    model = LoanAgreement
    template_name = 'document_processor/document_list.html'
    context_object_name = 'documents'

    def get_queryset(self):
        user = self.request.user
        if is_director(user) or is_moderator(user):
            return LoanAgreement.objects.filter(is_deleted=False).order_by('-created_at')
        return LoanAgreement.objects.filter(created_by=user, is_deleted=False).order_by('-created_at')


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

