from datetime import datetime
import re

def parse_date(date_str):
    if not date_str: return None
    if isinstance(date_str, datetime): return date_str.date()
    try:
        return datetime.strptime(date_str.strip(), '%d.%m.%Y').date()
    except:
        return None

def clean_int(val):
    if not val: return None
    try:
        return int(float(str(val).replace(' ', '').replace('\u00A0', '')))
    except:
        return None

def clean_float(val):
    if not val: return None
    try:
        return float(str(val).replace(' ', '').replace('\u00A0', '').replace(',', '.'))
    except:
        return None

def clean_str(val):
    if val is None: return ''
    return str(val).strip()

def clean_phone(val):
    if not val: return ''
    return ''.join(filter(str.isdigit, str(val)))

import qrcode
import io
import base64

def generate_qr_code(data):
    """
    Generates a QR code base64 string for embedding in HTML.
    """
    qr = qrcode.QRCode(
        version=None,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=1,
    )
    qr.add_data(data)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")
    
    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    img_str = base64.b64encode(buffer.getvalue()).decode()
    
    return f"data:image/png;base64,{img_str}"

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
        
        from datetime import datetime, date
        from dateutil.relativedelta import relativedelta
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
                 pass

            # Sana qaysi partda?
            date_index = -1
            for i, p in enumerate(parts):
                if original_date_str in p:
                    date_index = i
                    break
            
            if date_index == -1:
                continue

            # 3. Ma'lumotlarni olish
            # Tartib raqami
            num = parts[date_index - 1] if date_index > 0 else str(len(schedule) + 1)
            if not num.replace('.', '').isdigit():
                 num = str(len(schedule) + 1)

            # Summalar (sanadan keyingi ustunlar)
            amounts = parts[date_index + 1:]
            
            def clean_amount(s):
                s = s.replace(' ', '').replace("'", "").strip()
                if not s: return "0"
                if s.count(',') > 1: s = s.replace(',', '')
                if s.count('.') > 1: s = s.replace('.', '')
                if ',' in s and '.' in s:
                    if s.rfind(',') < s.rfind('.'): s = s.replace(',', '')
                    else: s = s.replace('.', '').replace(',', '.')
                elif ',' in s:
                    s = s.replace(',', '.')
                return s

            balance_str = amounts[0] if len(amounts) > 0 else "0"
            principal_str = amounts[1] if len(amounts) > 1 else "0"
            interest_str = amounts[2] if len(amounts) > 2 else "0"
            total_str = amounts[3] if len(amounts) > 3 else "0"
            
            p_val = 0
            i_val = 0
            t_val = 0
            
            try: p_val = float(clean_amount(principal_str))
            except: pass
            try: i_val = float(clean_amount(interest_str))
            except: pass
            try: t_val = float(clean_amount(total_str))
            except: pass
            
            if t_val == 0 and (p_val > 0 or i_val > 0):
                t_val = p_val + i_val
                total_str = "{:,.2f}".format(t_val)

            total_p += p_val
            total_i += i_val

            schedule.append({
                'num': num,
                'date': date_str,
                'balance': balance_str,
                'principal': principal_str,
                'interest': interest_str,
                'total': total_str
            })
        except Exception:
            continue

    grand_total = total_p + total_i
    
    return schedule, "{:,.2f}".format(total_p).replace(",", " "), "{:,.2f}".format(total_i).replace(",", " "), "{:,.2f}".format(grand_total).replace(",", " ")


def build_document_context(app):
    ctx = { 'loan': app }
    
    # Barcha sug'urta bo'lmagan garovlar ro'yxati
    collaterals = app.collaterals.exclude(type='sugurta')
    ctx['collaterals'] = collaterals
    
    # Backward compatibility uchun birinchisini ham qoldiramiz (eski shablonlar buzilmasligi uchun)
    collateral = collaterals.first()
    ctx['collateral'] = collateral
    
    ctx['garov_boshqa_shaxs'] = False
    if collateral:
        ctx['garov_boshqa_shaxs'] = collateral.owner_type != 'borrower'
    
    # Eski o'zgaruvchilar (legacy)
    ctx['is_avto'] = False
    ctx['is_kochmas'] = False
    ctx['avto'] = None
    ctx['mulk'] = None
    ctx['tilla'] = None
    ctx['sugurta'] = None
    ctx['collateral_owner_pasport'] = ''
    
    if collateral:
        ctx['is_avto'] = collateral.type == 'avto'
        ctx['is_kochmas'] = collateral.type == 'kochmas' or collateral.type == 'kochmas_mulk'
        
        if collateral.owner_client:
            ctx['collateral_owner_pasport'] = f"{collateral.owner_client.pasport_seriya} {collateral.owner_client.pasport_berilgan}"
            
        if hasattr(collateral, 'auto_detail') and collateral.auto_detail:
            ctx['avto'] = collateral.auto_detail
        if hasattr(collateral, 'real_estate_detail') and collateral.real_estate_detail:
            ctx['mulk'] = collateral.real_estate_detail
        if hasattr(collateral, 'gold_detail') and collateral.gold_detail:
            ctx['tilla'] = collateral.gold_detail
            
    sugurtalar = app.collaterals.filter(type='sugurta')
    ctx['is_sugurta_mavjud'] = False
    if sugurtalar.exists():
        s = sugurtalar.first()
        ctx['is_sugurta_mavjud'] = True
        if hasattr(s, 'insurance_detail') and s.insurance_detail:
            ctx['sugurta'] = s.insurance_detail
            
    contacts = app.contacts.all()
    ctx['contact_1'] = contacts[0] if len(contacts) > 0 else None
    ctx['contact_2'] = contacts[1] if len(contacts) > 1 else None
    ctx['contact_3'] = contacts[2] if len(contacts) > 2 else None
    
    return ctx
