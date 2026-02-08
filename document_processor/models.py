from django.db import models
import uuid
from django.contrib.auth.models import User

class ProcessedDocument(models.Model):
    STATUS_CHOICES = [
        ('pending_moderator', 'Moderator Kutilmoqda'),
        ('pending_director', 'Direktor Kutilmoqda'),
        ('processing', 'Jarayonda'),
        ('completed', 'Yakunlandi'),
        ('rejected', 'Rad Etildi'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    original_file = models.FileField(upload_to='uploads/')
    processed_file = models.FileField(upload_to='processed/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending_moderator')
    
    # Workflow logging
    uploaded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='uploaded_docs')
    moderator_approved_at = models.DateTimeField(null=True, blank=True)
    moderator_approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='moderated_docs')
    director_approved_at = models.DateTimeField(null=True, blank=True)
    director_approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='directed_docs')
    
    
    # Configuration
    generation_config = models.JSONField(default=dict, blank=True)
    
    # Metadata extracted from Excel
    borrower_name = models.CharField(max_length=255, blank=True, null=True, verbose_name="Qarz oluvchi FIO")
    credit_amount = models.CharField(max_length=100, blank=True, null=True, verbose_name="Kredit summasi")
    collateral_name = models.CharField(max_length=255, blank=True, null=True, verbose_name="Garov nomi")

    def __str__(self):
        return f"Document {self.id} - {self.status}"

class DocumentTemplate(models.Model):
    name = models.CharField(max_length=255, verbose_name="Shablon nomi")
    file = models.FileField(upload_to='templates/', verbose_name="Word fayl (.docx)")
    code = models.CharField(max_length=50, unique=True, verbose_name="Kod (unikal)")
    description = models.TextField(blank=True, verbose_name="Tavsif")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class LoanAgreement(models.Model):
    # --- SHAXSIY MA'LUMOTLAR (Qarz oluvchi) ---
    qarz_oluvchi_fish = models.CharField("Qarz oluvchi F.I.Sh", max_length=255)
    qarz_oluvchi_pasport_seriya = models.CharField("Pasport seriyasi va raqami", max_length=20)
    qarz_oluvchi_pasport_berilgan = models.TextField("Kim tomonidan va qachon berilgan")
    qarz_oluvchi_manzil = models.TextField("Doimiy yashash manzili")
    qarz_oluvchi_ish_joyi = models.TextField("Ish joyi va lavozimi", blank=True)
    qarz_oluvchi_daromad = models.BigIntegerField("O'rtacha oylik daromad", blank=True, null=True)
    qarz_oluvchi_xarajatlar = models.BigIntegerField("O'rtacha oylik xarajatlar", blank=True, null=True)
    qarz_oluvchi_majburiyatlar = models.TextField("Mavjud kredit va qarz majburiyatlari", blank=True)
    qarz_oluvchi_tahminiy_tolov = models.BigIntegerField("Mikroqarz bo‘yicha oylik differensial to‘lovi miqdori (tahminiy)", blank=True, null=True)
    qarz_oluvchi_tugilgan_sana = models.DateField("Tug'ilgan sanasi", null=True, blank=True)
    qarz_oluvchi_jshshir = models.BigIntegerField("JSHSHIR", blank=True, null=True)
    qarz_oluvchi_telefon = models.CharField("Telefon raqami", max_length=20, blank=True)
    
    # --- BOG'LANISH UCHUN SHAXSLAR ---
    kontakt_1_fish = models.CharField("1-kontakt F.I.Sh", max_length=255, blank=True)
    kontakt_1_telefon = models.CharField("1-kontakt Telefoni", max_length=20, blank=True)
    kontakt_1_qarindoshlik = models.CharField("1-kontakt Qarindoshligi", max_length=50, blank=True)
    
    kontakt_2_fish = models.CharField("2-kontakt F.I.Sh", max_length=255, blank=True)
    kontakt_2_telefon = models.CharField("2-kontakt Telefoni", max_length=20, blank=True)
    kontakt_2_qarindoshlik = models.CharField("2-kontakt Qarindoshligi", max_length=50, blank=True)
    
    kontakt_3_fish = models.CharField("3-kontakt F.I.Sh", max_length=255, blank=True)
    kontakt_3_telefon = models.CharField("3-kontakt Telefoni", max_length=20, blank=True)
    kontakt_3_qarindoshlik = models.CharField("3-kontakt Qarindoshligi", max_length=50, blank=True)

    # --- KREDIT MA'LUMOTLARI ---
    shartnoma_raqami = models.CharField("Kredit shartnomasi raqami", max_length=50, blank=True)
    shartnoma_sanasi = models.DateField("Shartnoma sanasi", null=True, blank=True)
    kredit_miqdori = models.BigIntegerField("Kredit miqdori (raqam bilan)", blank=True, null=True)
    kredit_miqdori_soz = models.CharField("Kredit miqdori (so'z bilan)", max_length=255, blank=True)
    kredit_muddat_oy = models.CharField("Kredit muddati (oy)", max_length=10, blank=True)
    foiz_stavkasi = models.CharField("Foiz stavkasi (raqam)", max_length=10, blank=True)
    foiz_stavkasi_soz = models.CharField("Foiz stavkasi (so'z bilan)", max_length=255, blank=True)
    
    KREDIT_TURI_CHOICES = [
        ('mikroqarz', 'Mikroqarz'),
        ('mikrokredit', 'Mikrokredit'),
    ]
    GRAFIK_CHOICES = [
        ('annuitet', 'Annuitet'),
        ('differensial', 'Differensial'),
    ]
    
    kredit_turi = models.CharField("Kredit turi", max_length=20, choices=KREDIT_TURI_CHOICES, default='mikroqarz')
    grafik = models.CharField("To'lov grafigi", max_length=20, choices=GRAFIK_CHOICES, default='differensial')

    # --- GAROV MA'LUMOTLARI ---
    GAROV_TURI_CHOICES = [
        ('avto', 'Avtomobil'),
        ('kochmas_mulk', "Ko'chmas mulk"),
        ('tilla', 'Tilla buyumlar'),
    ]
    GAROV_EGASI_CHOICES = [
        ('oz', 'O\'zi (Qarz oluvchi)'),
        ('boshqa', 'Uchinchi shaxs'),
    ]

    garov_turi = models.CharField("Garov turi", max_length=20, choices=GAROV_TURI_CHOICES, default='avto')
    sugurta_mavjud = models.BooleanField("Sug'urta polisi bormi?", default=False)
    uchinchi_shaxs_mavjud = models.BooleanField("Garov mulkdori uchinchi shaxsmi?", default=False)
    garov_egasi = models.CharField("Garov mulkdori", max_length=10, choices=GAROV_EGASI_CHOICES, default='oz')

    # --- UCHINCHI SHAXS MA'LUMOTLARI ---
    garov_egasi_fish = models.CharField("Garov egasi F.I.Sh", max_length=255, blank=True)
    garov_egasi_pasport = models.TextField("Garov egasi pasport ma'lumotlari", blank=True)
    garov_egasi_manzil = models.TextField("Garov egasi manzili", blank=True)

    # --- AVTOMOBIL MA'LUMOTLARI ---
    avto_nomi = models.CharField("Avtomobil modeli", max_length=100, blank=True)
    avto_raqam = models.CharField("Davlat raqami", max_length=20, blank=True)
    avto_kuzov_turi = models.CharField("Kuzov turi", max_length=50, blank=True)
    avto_kuzov = models.CharField("Kuzov raqami", max_length=50, blank=True)
    avto_dvigatel = models.CharField("Dvigatel raqami", max_length=50, blank=True)
    avto_shassi = models.CharField("Shassi raqami", max_length=50, blank=True, default='RAKAMSIZ')
    avto_yil = models.IntegerField("Ishlab chiqarilgan yili", blank=True, null=True)
    avto_rang = models.CharField("Rangi", max_length=50, blank=True)
    avto_bahosi = models.BigIntegerField("Baholangan qiymati", blank=True, null=True)
    avto_bahosi_soz = models.CharField("Baholangan qiymati (so'z bilan)", max_length=255, blank=True)
    avto_yurgan = models.CharField("Yurgan masofasi", max_length=50, blank=True)
    avto_texpasport = models.CharField("Texpasport", max_length=50, blank=True)
    avto_texpasport_sana = models.DateField("Texpasport berilgan sanasi", null=True, blank=True)
    avto_manzil = models.CharField("Avto ro'yxatdan o'tgan manzili", max_length=255, blank=True)

    # --- KO'CHMAS MULK MA'LUMOTLARI ---
    mulk_manzili = models.TextField("Ko'chmas mulk manzili", blank=True)
    mulk_qurilish_maydoni = models.CharField("Qurilish osti maydoni", max_length=50, blank=True)
    mulk_umumiy_maydoni = models.CharField("Umumiy maydoni", max_length=50, blank=True)
    mulk_yashash_maydoni = models.CharField("Yashash maydoni", max_length=50, blank=True)
    mulk_turi = models.CharField("Ko'chmas mulk turi", max_length=100, blank=True)
    mulk_bahosi = models.BigIntegerField("Kelishilgan garov qiymati (raqam)", blank=True, null=True)
    mulk_bahosi_soz = models.CharField("Kelishilgan garov qiymati (so'z bilan)", max_length=255, blank=True)
    mulk_dalolatnoma_raqami = models.CharField("Baholash dalolatnoma raqami", max_length=50, blank=True)
    mulk_dalolatnoma_sanasi = models.DateField("Baholash dalolatnoma sanasi", null=True, blank=True)

    # --- TILLA BUYUMLAR MA'LUMOTLARI ---
    tilla_nomi = models.TextField("Tilla buyumlar nomi", blank=True)
    tilla_probi = models.CharField("Probsi", max_length=20, blank=True)
    tilla_vazni = models.CharField("Umumiy vazni (gr)", max_length=50, blank=True)
    tilla_soni = models.CharField("Soni (dona)", max_length=50, blank=True)
    tilla_bahosi = models.BigIntegerField("Baholangan qiymati", blank=True, null=True)
    tilla_bahosi_soz = models.CharField("Baholangan qiymati (so'z bilan)", max_length=255, blank=True)

    # --- SUG'URTA MA'LUMOTLARI ---
    sugurta_kompaniyasi = models.CharField("Sug'urta kompaniyasi nomi", max_length=255, blank=True)
    sugurta_polisi = models.CharField("Sug'urta polisi raqami", max_length=50, blank=True)
    sugurta_sanasi = models.DateField("Sug'urta sanasi", null=True, blank=True)
    sugurta_summasi = models.BigIntegerField("Sug'urta summasi (raqam)", blank=True, null=True)
    sugurta_summasi_soz = models.CharField("Sug'urta summasi (so'z bilan)", max_length=255, blank=True)

    # --- TASHKILOT (MCHJ) MA'LUMOTLARI ---
    FILIAL_CHOICES = [
        ('Buxoro filiali', 'Buxoro filiali'),
        ('Samarqand filiali', 'Samarqand filiali'),
        ('Toshkent filiali', 'Toshkent filiali'),
        ('Andijon filiali', 'Andijon filiali'),
        ('Farg\'ona filiali', 'Farg\'ona filiali'),
        ('Namangan filiali', 'Namangan filiali'),
        ('Qashqadaryo filiali', 'Qashqadaryo filiali'),
        ('Surxondaryo filiali', 'Surxondaryo filiali'),
        ('Jizzax filiali', 'Jizzax filiali'),
        ('Navoiy filiali', 'Navoiy filiali'),
        ('Xorazm filiali', 'Xorazm filiali'),
    ]
    
    filial_nomi = models.CharField("Filial nomi", max_length=50, choices=FILIAL_CHOICES, default='Buxoro filiali', blank=True)
    filial_boshligi = models.CharField("Filial boshlig'i F.I.Sh", max_length=100, blank=True)
    ishonchnoma_sanasi = models.DateField("Ishonchnoma sanasi", null=True, blank=True)

    # --- GRAFIK (Exceldan nusxa) ---
    grafik_matni = models.TextField("Grafik jadvali (Exceldan)", blank=True)
    
    # --- MONITORING SANALARI ---
    monitoring_sana_1 = models.DateField("1-monitoring sanasi", null=True, blank=True)
    monitoring_sana_2 = models.DateField("2-monitoring sanasi", null=True, blank=True)
    monitoring_sana_3 = models.DateField("3-monitoring sanasi", null=True, blank=True)
    monitoring_sana_4 = models.DateField("4-monitoring sanasi", null=True, blank=True)

    # --- WORKFLOW & META ---
    STATUS_CHOICES = [
        ('pending_moderator', 'Moderator Tasdiqi Kutilmoqda'),
        ('pending_director', 'Direktor Tasdiqi Kutilmoqda'),
        ('completed', 'Tasdiqlandi (Yakunlandi)'),
        ('rejected', 'Rad Etildi'),
    ]
    
    status = models.CharField("Holati", max_length=20, choices=STATUS_CHOICES, default='pending_moderator')
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_loans', verbose_name="Kiritdi (Operator)")
    
    moderator_approved_at = models.DateTimeField("Moderator tasdiqlagan vaqt", null=True, blank=True)
    moderator_approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='moderated_loans', verbose_name="Moderator")
    
    director_approved_at = models.DateTimeField("Direktor tasdiqlagan vaqt", null=True, blank=True)
    director_approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='directed_loans', verbose_name="Direktor")
    
    pdf_file = models.FileField("Hujjatlar To'plami (ZIP)", upload_to='loan_docs/', null=True, blank=True)

    created_at = models.DateTimeField("Yaratilgan vaqti", auto_now_add=True)
    updated_at = models.DateTimeField("Yangilangan vaqti", auto_now=True)

    class Meta:
        verbose_name = "Kredit Shartnomasi"
        verbose_name_plural = "Kredit Shartnomalari"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.qarz_oluvchi_fish} - {self.shartnoma_raqami}"
