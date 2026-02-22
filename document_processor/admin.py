from django.contrib import admin
from .models import ProcessedDocument, DocumentTemplate, LoanAgreement

@admin.register(ProcessedDocument)
class ProcessedDocumentAdmin(admin.ModelAdmin):
    list_display = ('id', 'status', 'created_at')
    list_filter = ('status', 'created_at')

@admin.register(DocumentTemplate)
class DocumentTemplateAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'created_at')

@admin.register(LoanAgreement)
class LoanAgreementAdmin(admin.ModelAdmin):
    list_display = ('qarz_oluvchi_fish', 'shartnoma_raqami', 'kredit_miqdori', 'status', 'created_at')
    list_filter = ('status', 'garov_turi', 'filial_nomi', 'created_at')
    search_fields = ('qarz_oluvchi_fish', 'shartnoma_raqami', 'qarz_oluvchi_pasport_seriya', 'qarz_oluvchi_jshshir')
    readonly_fields = ('created_at', 'updated_at', 'moderator_approved_at', 'director_approved_at')
    
    fieldsets = (
        ("Shaxsiy Ma'lumotlar", {
            'fields': (
                'qarz_oluvchi_fish', 'qarz_oluvchi_fish_inisiali', 'qarz_oluvchi_jinsi', 
                'qarz_oluvchi_tugilgan_sana', 'qarz_oluvchi_jshshir', 'qarz_oluvchi_pasport_seriya', 
                'qarz_oluvchi_pasport_berilgan', 'qarz_oluvchi_manzil', 'qarz_oluvchi_telefon',
                'qarz_oluvchi_ish_joyi', 'qarz_oluvchi_daromad', 'qarz_oluvchi_xarajatlar', 
                'qarz_oluvchi_majburiyatlar', 'qarz_oluvchi_tahminiy_tolov'
            )
        }),
        ("Bog'lanish uchun shaxslar", {
            'classes': ('collapse',),
            'fields': (
                ('kontakt_1_fish', 'kontakt_1_telefon', 'kontakt_1_qarindoshlik'),
                ('kontakt_2_fish', 'kontakt_2_telefon', 'kontakt_2_qarindoshlik'),
                ('kontakt_3_fish', 'kontakt_3_telefon', 'kontakt_3_qarindoshlik'),
            )
        }),
        ("Kredit Ma'lumotlari", {
            'fields': (
                'shartnoma_raqami', 'shartnoma_sanasi', 'kredit_turi', 'grafik',
                'kredit_miqdori', 'kredit_miqdori_soz', 'kredit_muddat_oy', 'kredit_muddat_oy_soz',
                'foiz_stavkasi', 'foiz_stavkasi_soz'
            )
        }),
        ("Garov Umumiy", {
            'fields': ('garov_turi', 'garov_egasi', 'uchinchi_shaxs_mavjud', 'sugurta_mavjud')
        }),
        ("Garov Egasi va Ishonchnoma", {
            'classes': ('collapse',),
            'fields': (
                'garov_egasi_fish', 'garov_egasi_inisiali', 'garov_egasi_pasport', 'garov_egasi_manzil', 
                'ishonchnoma_notarius_fish', 'ishonchnoma_notarius_manzil', 'ishonchnoma_reestr_raqami', 'ishonchnoma_reestr_sanasi'
            )
        }),
        ("Avtomobil Ma'lumotlari", {
            'classes': ('collapse',),
            'fields': (
                'avto_nomi', 'avto_raqam', 'avto_kuzov_turi', 'avto_kuzov', 'avto_dvigatel', 
                'avto_shassi', 'avto_yil', 'avto_rang', 'avto_bahosi', 'avto_bahosi_soz', 
                'avto_yurgan', 'avto_texpasport', 'avto_texpasport_sana', 'avto_manzil'
            )
        }),
        ("Ko'chmas Mulk Ma'lumotlari", {
            'classes': ('collapse',),
            'fields': (
                'mulk_egasi', 'mulk_reestr_raqami', 'mulk_kadastr_raqami', 'mulk_manzili', 
                'mulk_qurilish_maydoni', 'mulk_umumiy_maydoni', 'mulk_yashash_maydoni', 
                'mulk_turi', 'mulk_bahosi', 'mulk_bahosi_soz'
            )
        }),
        ("Tilla Buyumlar Ma'lumotlari", {
            'classes': ('collapse',),
            'fields': ('tilla_nomi', 'tilla_probi', 'tilla_vazni', 'tilla_soni', 'tilla_bahosi', 'tilla_bahosi_soz')
        }),
        ("Sug'urta Ma'lumotlari", {
            'classes': ('collapse',),
            'fields': ('sugurta_kompaniyasi', 'sugurta_polisi', 'sugurta_sanasi', 'sugurta_summasi', 'sugurta_summasi_soz')
        }),
        ("Filial va Rahbarlar", {
            'fields': ('filial_nomi', 'filial_boshligi', 'filial_boshligi_inisiali', 'tashkilot_nomi', 'direktor_fish', 'direktor_fish_inisiali')
        }),
        ("Monitoring va Grafik", {
            'classes': ('collapse',),
            'fields': ('grafik_matni', 'monitoring_sana_1', 'monitoring_sana_2', 'monitoring_sana_3', 'monitoring_sana_4')
        }),
        ("Tizim Ma'lumotlari", {
            'fields': ('status', 'is_deleted', 'created_by', 'moderator_approved_by', 'moderator_approved_at', 'director_approved_by', 'director_approved_at', 'pdf_file', 'created_at', 'updated_at')
        }),
    )
