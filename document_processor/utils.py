from datetime import datetime
import re
import qrcode
import io
import base64

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

def generate_qr_code(data):
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

def parse_pasted_schedule(text):
    import re
    schedule = []
    total_p = 0
    total_i = 0
    grand_total_val = 0
    
    if not text:
        return [], "0", "0", "0"
        
    lines = [l.strip() for l in text.strip().splitlines() if l.strip()]
    date_pattern = re.compile(r'(\d{1,2}[./]\d{1,2}[./]\d{2,4})')
    
    def fmt(val):
        try:
            return "{:,.2f}".format(float(val)).replace(",", " ").replace(".00", "")
        except:
            return str(val)
    
    def clean_amount(s):
        if not s: return "0"
        s = s.replace(' ', '').replace("'", "").replace("\xa0", "").strip()
        if s.count(',') == 1 and s.count('.') == 0:
            if len(s.split(',')[1]) in [1, 2]: s = s.replace(',', '.')
            else: s = s.replace(',', '')
        elif s.count(',') > 0 and s.count('.') > 0:
            if s.find(',') < s.find('.'): s = s.replace(',', '')
            else: s = s.replace('.', '').replace(',', '.')
        return s.replace(',', '')

    for line in lines:
        try:
            date_match = date_pattern.search(line)
            if not date_match: continue 
            original_date_str = date_match.group(1)
            date_str = original_date_str
            if '/' in date_str:
                try:
                    parts_d = [int(p) for p in date_str.split('/')]
                    if len(parts_d) == 3:
                        d, m, y = parts_d[0], parts_d[1], parts_d[2]
                        date_str = f"{d:02d}.{m:02d}.{y}"
                except: pass
            parts = [p.strip() for p in line.split('\t') if p.strip()]
            if len(parts) < 4:
                parts = [p.strip() for p in re.split(r'\s{2,}', line) if p.strip()]
            if len(parts) < 4:
                parts = [p.strip() for p in line.split(' ') if p.strip()]
            date_index = -1
            for i, p in enumerate(parts):
                if original_date_str in p:
                    date_index = i
                    break
            if date_index == -1: continue
            num = parts[date_index - 1] if date_index > 0 else str(len(schedule) + 1)
            if not num.replace('.', '').isdigit(): 
                num = str(len(schedule) + 1)
            amounts = parts[date_index + 1:]
            if not amounts: continue
            cleaned = [clean_amount(a) for a in amounts]
            if len(cleaned) >= 4:
                bal, princ, intr, tot = cleaned[0], cleaned[1], cleaned[2], cleaned[3]
            elif len(cleaned) == 3:
                princ, intr, tot = cleaned[0], cleaned[1], cleaned[2]
                bal = "0"
            elif len(cleaned) == 2:
                princ, intr = cleaned[0], cleaned[1]
                try: tot = str(float(princ or 0) + float(intr or 0))
                except: tot = "0"
                bal = "0"
            else: continue
            schedule.append({
                'num': num,
                'date': date_str,
                'balance': fmt(float(bal or 0)),
                'principal': fmt(float(princ or 0)),
                'interest': fmt(float(intr or 0)),
                'total': fmt(float(tot or 0))
            })
            try:
                total_p += float(princ or 0)
                total_i += float(intr or 0)
                grand_total_val += float(tot or 0)
            except: pass
        except Exception:
            continue
    return schedule, fmt(total_p), fmt(total_i), fmt(grand_total_val)

def build_document_context(app_or_payload):
    if hasattr(app_or_payload, 'data'): # LoanWizardApplication instance 
        payload = app_or_payload.data
    elif isinstance(app_or_payload, dict):
        payload = app_or_payload
    else:
        # If it's something else (like legacy LoanApplication), we don't support it anymore
        return {} 
    return build_context_from_payload(payload)

def build_context_from_payload(payload):
    personal = payload.get('client_info') or payload.get('personal') or {}
    loan_obj = payload.get('loan_details') or payload.get('loan') or {}
    coll = payload.get('collateral') or {}
    financial = payload.get('financial_info') or payload.get('financial') or {}
    admin = payload.get('administrative') or {}
    
    if 'muddat' in loan_obj and 'muddat_oy' not in loan_obj:
        loan_obj['muddat_oy'] = loan_obj['muddat']
    if 'muddat_soz' in loan_obj and 'muddat_oy_soz' not in loan_obj:
        loan_obj['muddat_oy_soz'] = loan_obj['muddat_soz']
    if 'summa' in loan_obj and 'miqdori' not in loan_obj:
        loan_obj['miqdori'] = loan_obj['summa']
    if 'summa_soz' in loan_obj and 'miqdori_soz' not in loan_obj:
        loan_obj['miqdori_soz'] = loan_obj['summa_soz']
        
    

    # Sanalarni Date obyektiga o'tkazish
    if 'sana' in loan_obj: 
        loan_obj['shartnoma_sanasi'] = parse_date(loan_obj['sana'])
    
    if 'boshlanish_sanasi' in loan_obj:
        loan_obj['boshlanish_sanasi'] = parse_date(loan_obj['boshlanish_sanasi'])
        
    if 'tugash_sanasi' in loan_obj:
        loan_obj['tugash_sanasi'] = parse_date(loan_obj['tugash_sanasi'])


    if 'boshlanish_sanasi' in loan_obj and isinstance(loan_obj['boshlanish_sanasi'], str):
        loan_obj['shartnoma_sanasi'] = parse_date(loan_obj['boshlanish_sanasi']) # Fallback
    
    if 'pasport' in personal and 'pasport_seriya' not in personal:
        personal['pasport_seriya'] = personal['pasport']
    if 'tugilgan_sana' in personal:
        personal['tugilgan_sana'] = parse_date(personal['tugilgan_sana'])
    
    if 'turi' in loan_obj: loan_obj['get_turi_display'] = str(loan_obj['turi']).capitalize()
    if 'grafik' in loan_obj: loan_obj['get_grafik_turi_display'] = str(loan_obj['grafik']).capitalize()
        
    if 'daromad_jami' in financial and 'daromad' not in financial: financial['daromad'] = financial['daromad_jami']
    if 'xarajat_jami' in financial and 'xarajatlar' not in financial: financial['xarajatlar'] = financial['xarajat_jami']

    f_info = {**financial, **admin}
    if 'filial' in admin: f_info['filial_nomi'] = admin['filial']
    if 'filial_boshlig_fish' in admin: f_info['filial_boshligi'] = admin['filial_boshlig_fish']
    if 'filial_boshlig_fish_inisiali' in admin: f_info['filial_boshligi_inisiali'] = admin['filial_boshlig_fish_inisiali']

    c_at = payload.get('created_at')
    c_at = parse_date(c_at) if c_at and isinstance(c_at, str) else datetime.now()

    selected_types = coll.get('selected_types') or []
    collateral_data = coll.get('data') or {}

    ctx = {
        'loan': {
            'id': 'vizard',
            'client': personal,
            'personal_fish': personal.get('fish'),
            'details': loan_obj,
            'financial_info': f_info,
            'created_at': c_at,
        },
        'sugurta': collateral_data if 'sugurta' in selected_types else {},
        'qr_manager': generate_qr_code('S.O.Eshbekov'),
        'qr_akramov': generate_qr_code('R.N.Akramov'),
        'qr_filial_boshligi': generate_qr_code(f_info.get('filial_boshligi_inisiali', 'Filial Boshlig\'i')),
        'qr_obidov': generate_qr_code(f_info.get('direktor_fish_inisiali', 'A.Sh.Obidov')),
    }

    grafik_text = loan_obj.get('grafik_matni')
    if grafik_text:
        sch, tp, ti, gt = parse_pasted_schedule(grafik_text)
        ctx['schedule'] = sch
        ctx['total_principal'] = tp
        ctx['total_interest'] = ti
        ctx['grand_total'] = gt
    else:
        ctx['schedule'] = []
    
    mock_collateral = {
        'type': selected_types[0] if selected_types else '',
        'selected_types': selected_types,
        'owner_type': coll.get('owner_type', 'borrower'),
        'owner_client': {
            'fish': collateral_data.get('owner_fish'),
            'pasport_seriya': collateral_data.get('owner_pasport'),
        },
        'reestr_number': collateral_data.get('reestr_number', '')
    }
    ctx['collateral'] = mock_collateral
    ctx['selected_types'] = selected_types
    ctx['is_avto'] = 'avto' in selected_types
    ctx['is_kochmas'] = any(t in selected_types for t in ['kochmas', 'mulk', 'kochmas_mulk'])
    ctx['is_tilla'] = 'tilla' in selected_types
    
    if ctx['is_avto']:
        ctx['avto'] = collateral_data
        for key, val in list(collateral_data.items()):
            if key.startswith('avto_'):
                new_key = key.replace('avto_', '')
                if new_key == 'raqam': new_key = 'davlat_raqami'
                if new_key == 'kuzov': new_key = 'kuzov_raqami'
                collateral_data[new_key] = val

    if ctx['is_kochmas']:
        ctx['mulk'] = collateral_data
        for key, val in list(collateral_data.items()):
            if key.startswith('mulk_'):
                new_key = key.replace('mulk_', '')
                if new_key == 'umumiy_yer_maydoni': new_key = 'umumiy_maydon'
                if new_key == 'qurilish_osti_maydoni': new_key = 'qurilish_maydon'
                if new_key == 'umumiy_foydalanish_maydoni': new_key = 'yashash_maydon'
                if new_key == 'yashash_maydoni': new_key = 'yashash_maydon'
                if new_key == 'manzili': new_key = 'manzil'
                if new_key == 'nomi' and not val: val = "KO'CHMAS MULK"
                collateral_data[new_key] = val
            
    ctx['is_sugurta_mavjud'] = 'sugurta' in selected_types
    ctx['is_sugurta'] = ctx['is_sugurta_mavjud']
    # Garov boshqa shaxs bo'lsa (other yoki proxy), demak 3-tomon bor
    owner_type = coll.get('owner_type', 'borrower')
    ctx['garov_boshqa_shaxs'] = owner_type in ['other', 'proxy']
    
    if ctx['is_sugurta_mavjud']:
        for key, val in list(collateral_data.items()):
            if key.startswith('sugurta_'):
                collateral_data[key.replace('sugurta_', '')] = val
        ctx['sugurta'] = collateral_data

    contacts_list = personal.get('contacts', [])
    for i, c in enumerate(contacts_list[:3], 1):
        if isinstance(c, dict):
            c['get_qarindoshlik_display'] = c.get('qarindoshlik', '')
            ctx[f'contact_{i}'] = c
    personal['contact_persons'] = contacts_list

    return ctx
