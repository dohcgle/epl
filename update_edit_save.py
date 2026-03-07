import re

with open("/home/ulugbek/Projects/epl/document_processor/views.py", "r") as f:
    content = f.read()

old_post = """    if request.method == 'POST':
        # Saqlash mantiqi bu yerda yoziladi 
        # Hozircha faqat ko'shib tahrirlab create_loan ishlamasligi uchun qoldiramiz.
        pass"""

new_post = """    if request.method == 'POST':
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

        return redirect('view_application', loan_id=loan.id)"""

content = content.replace(old_post, new_post)
with open("/home/ulugbek/Projects/epl/document_processor/views.py", "w") as f:
    f.write(content)

print("success view update")
