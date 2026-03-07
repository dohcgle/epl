import re

with open("/home/ulugbek/Projects/epl/document_processor/views.py", "r") as f:
    content = f.read()

# Eski edit_loan_vue_page funksiyasi
old_func = """@login_required
def edit_loan_vue_page(request, loan_id):
    loan = get_object_or_404(LoanApplication, id=loan_id)
    return render(request, 'document_processor/loan_edit.html', {'loan_id': loan.id, 'loan': loan})"""

# Yangi funksiya json.dumps bilan birga (get_loan_data_api mantiqiga o'xshash)
new_func = """@login_required
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

    return render(request, 'document_processor/loan_edit.html', context)"""

content = content.replace(old_func, new_func)

with open("/home/ulugbek/Projects/epl/document_processor/views.py", "w") as f:
    f.write(content)

print("views.py edit_loan_vue_page updated")
