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
    list_display = ('qarz_oluvchi_fish', 'shartnoma_raqami', 'kredit_miqdori', 'garov_turi', 'created_at')
    list_filter = ('garov_turi', 'created_at', 'sugurta_mavjud')
    search_fields = ('qarz_oluvchi_fish', 'shartnoma_raqami', 'qarz_oluvchi_pasport_seriya')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ("Shaxsiy Ma'lumotlar", {
            'fields': ('qarz_oluvchi_fish', 'qarz_oluvchi_pasport_seriya', 'qarz_oluvchi_pasport_berilgan', 'qarz_oluvchi_manzil', 'qarz_oluvchi_tugilgan_sana')
        }),
        ("Kredit Ma'lumotlari", {
            'fields': ('shartnoma_raqami', 'shartnoma_sanasi', 'kredit_miqdori', 'kredit_miqdori_soz', 'kredit_muddat_oy', 'foiz_stavkasi', 'foiz_stavkasi_soz')
        }),
        ("Garov Asosiy", {
            'fields': ('garov_turi', 'sugurta_mavjud', 'uchinchi_shaxs_mavjud', 'garov_egasi')
        }),
        ("Garov Egasi (Agar uchinchi shaxs bo'lsa)", {
            'classes': ('collapse',),
            'fields': ('garov_egasi_fish', 'garov_egasi_pasport', 'garov_egasi_manzil')
        }),
        ("Avtomobil Ma'lumotlari", {
            'classes': ('collapse',),
            'fields': ('avto_nomi', 'avto_raqam', 'avto_kuzov', 'avto_dvigatel', 'avto_yil', 'avto_rang', 'avto_bahosi', 'avto_yurgan', 'avto_texpasport')
        }),
        ("Ko'chmas Mulk Ma'lumotlari", {
            'classes': ('collapse',),
            'fields': ('mulk_manzili', 'mulk_qurilish_maydoni', 'mulk_umumiy_maydoni', 'mulk_yashash_maydoni', 'mulk_turi', 'mulk_bahosi', 'mulk_bahosi_soz', 'mulk_dalolatnoma_raqami', 'mulk_dalolatnoma_sanasi')
        }),
        ("Tilla Buyumlar Ma'lumotlari", {
            'classes': ('collapse',),
            'fields': ('tilla_nomi', 'tilla_probi', 'tilla_vazni', 'tilla_soni', 'tilla_bahosi', 'tilla_bahosi_soz')
        }),
        ("Sug'urta Ma'lumotlari", {
            'classes': ('collapse',),
            'fields': ('sugurta_kompaniyasi', 'sugurta_polisi', 'sugurta_sanasi', 'sugurta_summasi', 'sugurta_summasi_soz')
        }),
        ("Qo'shimcha", {
            'fields': ('filial_boshligi', 'ishonchnoma_sanasi', 'grafik_matni')
        }),
        ("Monitoring", {
            'fields': ('monitoring_sana_1', 'monitoring_sana_2', 'monitoring_sana_3', 'monitoring_sana_4')
        }),
    )
