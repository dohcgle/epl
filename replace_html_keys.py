import os
import re

MAPPING = {
    # personal (Client)
    'loan.personal_fish_inisiali': 'loan.client.fish_inisiali',
    'loan.personal_pasport_seriya': 'loan.client.pasport_seriya',
    'loan.personal_pasport_berilgan': 'loan.client.pasport_berilgan',
    'loan.personal_jshshir': 'loan.client.jshshir',
    'loan.personal_tugilgan_sana': 'loan.client.tugilgan_sana',
    'loan.personal_jinsi': 'loan.client.jinsi',
    'loan.personal_telefon': 'loan.client.telefon',
    'loan.personal_manzil': 'loan.client.manzil',
    'loan.personal_fish': 'loan.client.fish',
    'loan.qarz_oluvchi_telefon_2': 'loan.client.telefon',
    'loan.qarz_oluvchi_fish_inisiali': 'loan.client.fish_inisiali',
    'loan.qarz_oluvchi_pasport_seriya': 'loan.client.pasport_seriya',
    'loan.qarz_oluvchi_pasport_berilgan': 'loan.client.pasport_berilgan',
    'loan.qarz_oluvchi_manzil': 'loan.client.manzil',
    'loan.qarz_oluvchi_tugilgan_sana': 'loan.client.tugilgan_sana',
    'loan.qarz_oluvchi_jinsi': 'loan.client.jinsi',
    'loan.qarz_oluvchi_jshshir': 'loan.client.jshshir',
    'loan.qarz_oluvchi_telefon': 'loan.client.telefon',
    'loan.qarz_oluvchi_fish': 'loan.client.fish',

    # loan (LoanDetails)
    'loan.loan_shartnoma_raqami': 'loan.details.shartnoma_raqami',
    'loan.loan_shartnoma_sanasi': 'loan.details.shartnoma_sanasi',
    'loan.loan_miqdori_soz': 'loan.details.miqdori_soz',
    'loan.loan_miqdori': 'loan.details.miqdori',
    'loan.loan_muddat_oy_soz': 'loan.details.muddat_oy_soz',
    'loan.loan_muddat_oy': 'loan.details.muddat_oy',
    'loan.loan_foiz_soz': 'loan.details.foiz_soz',
    'loan.loan_foiz': 'loan.details.foiz',
    'loan.get_grafik_display': 'loan.details.get_grafik_turi_display',
    'loan.kredit_miqdori_soz': 'loan.details.miqdori_soz',
    'loan.kredit_miqdori': 'loan.details.miqdori',
    'loan.kredit_muddat_oy_soz': 'loan.details.muddat_oy_soz',
    'loan.kredit_muddat_oy': 'loan.details.muddat_oy',
    'loan.foiz_stavkasi_soz': 'loan.details.foiz_soz',
    'loan.foiz_stavkasi': 'loan.details.foiz',
    'loan.shartnoma_raqami': 'loan.details.shartnoma_raqami',
    'loan.shartnoma_sanasi': 'loan.details.shartnoma_sanasi',

    # financial (FinancialInfo)
    'loan.financial_ish_joyi': 'loan.financial_info.ish_joyi',
    'loan.financial_tashkilot_nomi': 'loan.financial_info.tashkilot_nomi',
    'loan.financial_filial_nomi': 'loan.financial_info.filial_nomi',
    'loan.financial_filial_boshligi': 'loan.financial_info.filial_boshligi',
    'loan.financial_direktor_fish_inisiali': 'loan.financial_info.direktor_fish_inisiali',
    'loan.financial_daromad': 'loan.financial_info.daromad',
    'loan.financial_xarajatlar': 'loan.financial_info.xarajatlar',
    'loan.financial_majburiyatlar': 'loan.financial_info.majburiyatlar',
    'loan.financial_tahminiy_tolov': 'loan.financial_info.tahminiy_tolov',
    'loan.qarz_oluvchi_ish_joyi': 'loan.financial_info.ish_joyi',
    'loan.qarz_oluvchi_daromad': 'loan.financial_info.daromad',
    'loan.qarz_oluvchi_xarajatlar': 'loan.financial_info.xarajatlar',
    'loan.qarz_oluvchi_majburiyatlar': 'loan.financial_info.majburiyatlar',
    'loan.qarz_oluvchi_tahminiy_tolov': 'loan.financial_info.tahminiy_tolov',
    'loan.filial_nomi': 'loan.financial_info.filial_nomi',
    'loan.filial_boshligi_inisiali': 'loan.financial_info.filial_boshligi_inisiali',
    'loan.filial_boshligi': 'loan.financial_info.filial_boshligi',
    'loan.tashkilot_nomi': 'loan.financial_info.tashkilot_nomi',
    'loan.direktor_fish_inisiali': 'loan.financial_info.direktor_fish_inisiali',
    'loan.direktor_fish': 'loan.financial_info.direktor_fish',

    # contacts
    'loan.get_kontakt_1_qarindoshlik_display': 'contact_1.get_qarindoshlik_display',
    'loan.contacts_0_telefon': 'contact_1.telefon',
    'loan.contacts_0_fish': 'contact_1.fish',
    'loan.get_kontakt_2_qarindoshlik_display': 'contact_2.get_qarindoshlik_display',
    'loan.contacts_1_telefon': 'contact_2.telefon',
    'loan.contacts_1_fish': 'contact_2.fish',
    'loan.get_kontakt_3_qarindoshlik_display': 'contact_3.get_qarindoshlik_display',
    'loan.contacts_2_telefon': 'contact_3.telefon',
    'loan.contacts_2_fish': 'contact_3.fish',
    'loan.kontakt_1_fish': 'contact_1.fish',
    'loan.kontakt_1_telefon': 'contact_1.telefon',
    'loan.kontakt_1_qarindoshlik': 'contact_1.qarindoshlik',
    'loan.kontakt_2_fish': 'contact_2.fish',
    'loan.kontakt_2_telefon': 'contact_2.telefon',
    'loan.kontakt_2_qarindoshlik': 'contact_2.qarindoshlik',
    'loan.kontakt_3_fish': 'contact_3.fish',
    'loan.kontakt_3_telefon': 'contact_3.telefon',
    'loan.kontakt_3_qarindoshlik': 'contact_3.qarindoshlik',

    # Collateral base
    'loan.garov_turi': 'collateral.type',
    'loan.collateral_owner_inisiali': 'collateral.owner_client.fish_inisiali',
    'loan.collateral_owner_fish': 'collateral.owner_client.fish',
    'loan.garov_egasi_inisiali': 'collateral.owner_client.fish_inisiali',
    'loan.garov_egasi_fish': 'collateral.owner_client.fish',
    'loan.garov_egasi_manzil': 'collateral.owner_client.manzil',
    'loan.garov_egasi_pasport': 'collateral_owner_pasport',
    'loan.ishonchnoma_notarius_fish': 'collateral.notarius_fish',
    'loan.collateral_notarius_fish': 'collateral.notarius_fish',
    'loan.ishonchnoma_notarius_manzil': 'collateral.notarius_address',
    'loan.collateral_notarius_address': 'collateral.notarius_address',
    'loan.ishonchnoma_reestr_raqami': 'collateral.reestr_number',
    'loan.reestr_raqami': 'collateral.reestr_number',
    'loan.ishonchnoma_reestr_sanasi': 'collateral.reestr_date',
    'loan.reestr_sanasi': 'collateral.reestr_date',

    # auto
    'loan.collateral_avto_nomi': 'avto.nomi',
    'loan.avto_nomi': 'avto.nomi',
    'loan.collateral_avto_yil': 'avto.yil',
    'loan.avto_yil': 'avto.yil',
    'loan.collateral_avto_rang': 'avto.rang',
    'loan.avto_rang': 'avto.rang',
    'loan.collateral_avto_dvigatel': 'avto.dvigatel',
    'loan.avto_dvigatel': 'avto.dvigatel',
    'loan.avto_shassi': 'avto.shassi',
    'loan.avto_kuzov_turi': 'avto.kuzov_turi',
    'loan.collateral_avto_kuzov': 'avto.kuzov_raqami',
    'loan.avto_kuzov': 'avto.kuzov_raqami',
    'loan.collateral_avto_raqam': 'avto.davlat_raqami',
    'loan.avto_raqam': 'avto.davlat_raqami',
    'loan.collateral_avto_bahosi': 'avto.bahosi',
    'loan.avto_bahosi_soz': 'avto.bahosi_soz',
    'loan.avto_bahosi': 'avto.bahosi',
    'loan.collateral_avto_texpasport_sana': 'avto.texpasport_sana',
    'loan.collateral_avto_texpasport': 'avto.texpasport',
    'loan.avto_texpasport_sana': 'avto.texpasport_sana',
    'loan.avto_texpasport': 'avto.texpasport',
    'loan.avto_manzil': 'avto.manzil',

    # mulk
    'loan.collateral_mulk_turi': 'mulk.turi',
    'loan.mulk_turi': 'mulk.turi',
    'loan.collateral_mulk_umumiy': 'mulk.umumiy_maydon',
    'loan.mulk_umumiy': 'mulk.umumiy_maydon',
    'loan.collateral_mulk_qurilish': 'mulk.qurilish_maydoni',
    'loan.mulk_qurilish': 'mulk.qurilish_maydoni',
    'loan.collateral_mulk_yashash': 'mulk.yashash_maydoni',
    'loan.mulk_yashash': 'mulk.yashash_maydoni',
    'loan.collateral_mulk_manzil': 'mulk.manzil',
    'loan.mulk_manzil': 'mulk.manzil',
    'loan.collateral_mulk_kadastr': 'mulk.kadastr_raqami',
    'loan.mulk_kadastr_raqami': 'mulk.kadastr_raqami',
    'loan.mulk_reestr_raqami': 'collateral.reestr_number',
    'loan.collateral_mulk_bahosi': 'mulk.bahosi',
    'loan.mulk_bahosi_soz': 'mulk.bahosi_soz',
    'loan.mulk_bahosi': 'mulk.bahosi',

    # sugurta
    'loan.collateral_sugurta_kompaniya': 'sugurta.kompaniya',
    'loan.sugurta_kompaniya': 'sugurta.kompaniya',
    'loan.collateral_sugurta_polisi': 'sugurta.polis_raqami',
    'loan.sugurta_polisi': 'sugurta.polis_raqami',
    'loan.sugurta_sana': 'sugurta.sana',
    'loan.collateral_sugurta_summa_soz': 'sugurta.summa_soz',
    'loan.collateral_sugurta_summa': 'sugurta.summa',
    'loan.sugurta_summa_soz': 'sugurta.summa_soz',
    'loan.sugurta_summa': 'sugurta.summa',
    'loan.sugurta_mavjud': 'is_sugurta_mavjud',
}

def replace_in_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Sort keys by length descending to prevent partial replacement
    for key in sorted(MAPPING.keys(), key=len, reverse=True):
        val = MAPPING[key]
        # Match {{ loan.xxx }} safely with varying spaces or single variable occurrences
        content = re.sub(r'\{\{\s*' + re.escape(key) + r'\s*\}\}', f'{{{{ {val} }}}}', content)
        # also match without {{ if it's used inside {% if ... %}
        content = re.sub(r'\b' + re.escape(key) + r'\b', val, content)

    # Some variables like qarz_oluvchi_manzil or shartnoma_sanasi might exist
    # without prefix "loan." if it was created from context directly in some templates.
    # Handle direct context mappings that were in build_legacy_context.
    DIRECT_MAP = {
        'qarz_oluvchi_fish': 'loan.client.fish',
        'qarz_oluvchi_manzil': 'loan.client.manzil',
        'kredit_miqdori_soz': 'loan.details.miqdori_soz',
        'kredit_miqdori': 'loan.details.miqdori',
        'shartnoma_sanasi': 'loan.details.shartnoma_sanasi',
        'shartnoma_raqami': 'loan.details.shartnoma_raqami',
        'kredit_muddat_oy': 'loan.details.muddat_oy',
        'kredit_muddat_oy_soz': 'loan.details.muddat_oy_soz',
        'foiz_stavkasi': 'loan.details.foiz',
        'foiz_stavkasi_soz': 'loan.details.foiz_soz',
    }
    for key in sorted(DIRECT_MAP.keys(), key=len, reverse=True):
        val = DIRECT_MAP[key]
        content = re.sub(r'\{\{\s*' + re.escape(key) + r'\s*\}\}', f'{{{{ {val} }}}}', content)

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)

if __name__ == "__main__":
    templates_dir = '/home/ulugbek/Projects/epl/templates/documents'
    for filename in os.listdir(templates_dir):
        if filename.endswith('.html'):
            replace_in_file(os.path.join(templates_dir, filename))
    print("All template files processed successfully.")
