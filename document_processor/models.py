from django.db import models
from django.contrib.auth.models import User

# ==========================================
# 1. MIJOZLAR(SHAXSLAR) BAZASI
# ==========================================
class Client(models.Model):
    JINSI_CHOICES = [
        ('erkak', 'Erkak'),
        ('ayol', 'Ayol'),
    ]

    fish = models.CharField("Shaxs F.I.Sh", max_length=255, blank=True, null=True)
    fish_inisiali = models.CharField("F.I.Sh (Inisiali)", max_length=100, blank=True, null=True)
    pasport_seriya = models.CharField("Pasport seriyasi va raqami", max_length=20, blank=True, null=True)
    pasport_berilgan = models.CharField("Kim tomonidan berilgan", max_length=255, blank=True, null=True)
    jshshir = models.BigIntegerField("JSHSHIR", blank=True, null=True)
    tugilgan_sana = models.DateField("Tug'ilgan sanasi", null=True, blank=True)
    jinsi = models.CharField("Jinsi", max_length=10, choices=JINSI_CHOICES, blank=True, null=True)
    telefon = models.CharField("Telefon raqami", max_length=20, blank=True, null=True)
    manzil = models.TextField("Yashash manzili", blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    class Meta:
        verbose_name = "Mijoz/Shaxs"
        verbose_name_plural = "Mijozlar/Shaxslar"

    def __str__(self):
        return f"{self.fish} ({self.pasport_seriya})"


# ==========================================
# 2. ASOSIY KREDIT ARIZASI (LOAN APPLICATION)
# ==========================================
class LoanApplication(models.Model):
    STATUS_CHOICES = [
        ('pending_moderator', 'Moderator Tasdiqi Kutilmoqda'),
        ('pending_director', 'Direktor Tasdiqi Kutilmoqda'),
        ('completed', 'Tasdiqlandi (Yakunlandi)'),
        ('rejected', 'Rad Etildi'),
    ]

    # Asosiy egasi
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='loan_applications', verbose_name="Qarz Oluvchi", blank=True, null=True)
    
    # Holat va Meta
    status = models.CharField("Holati", max_length=20, choices=STATUS_CHOICES, default='pending_moderator', null=True, blank=True)
    is_deleted = models.BooleanField("O'chirilgan", default=False, null=True, blank=True)
    
    # Workflow
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='created_loans', verbose_name="Operator")
    moderator_approved_at = models.DateTimeField("Moderator tasdiqlagan vaqt", null=True, blank=True)
    moderator_approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='moderated_loans', verbose_name="Moderator")
    director_approved_at = models.DateTimeField("Direktor tasdiqlagan vaqt", null=True, blank=True)
    director_approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='directed_loans', verbose_name="Direktor")
    
    # Payload (Audit)
    payload = models.JSONField("Asl JSON ma'lumotlari", null=True, blank=True)

    # Fayllar
    
    created_at = models.DateTimeField("Yaratilgan vaqti", auto_now_add=True, null=True)
    updated_at = models.DateTimeField("Yangilangan vaqti", auto_now=True, null=True)

    class Meta:
        verbose_name = "Kredit Arizasi"
        verbose_name_plural = "Kredit Arizalari"
        ordering = ['-created_at']

    def __str__(self):
        return f"Ariza #{self.id} - {self.client.fish if self.client else 'Unknown'}"

    # --- Jadvallar uchun Property-lar (Legacy compatibility) ---
    @property
    def personal_fish(self):
        return self.client.fish if self.client else ""

    @property
    def personal_tugilgan_sana(self):
        return self.client.tugilgan_sana if self.client else ""

    @property
    def personal_pasport_seriya(self):
        return self.client.pasport_seriya if self.client else ""

    @property
    def loan_miqdori(self):
        return self.details.miqdori if hasattr(self, 'details') else 0

    @property
    def loan_muddat_oy(self):
        return self.details.muddat_oy if hasattr(self, 'details') else ""

    @property
    def loan_foiz(self):
        return self.details.foiz if hasattr(self, 'details') else ""

    @property
    def loan_grafik_matni(self):
        return self.details.grafik_matni if hasattr(self, 'details') else ""

    @property
    def financial_filial_nomi(self):
        return self.financial_info.filial_nomi if hasattr(self, 'financial_info') else ""

    @property
    def sugurta_mavjud(self):
        return self.collaterals.filter(type='sugurta').exists()

    @property
    def garov_turi(self):
        col = self.collaterals.exclude(type='sugurta').first()
        return col.get_type_display() if col else ""

    @property
    def garov_turi_html(self):
        cols = self.collaterals.all()
        if not cols:
            return ""
        
        html_parts = []
        for col in cols:
            t = col.type
            label = col.get_type_display()
            
            icon = ""
            if t == 'avto':
                icon = '<i class="fas fa-car text-info"></i>'
            elif t == 'kochmas':
                icon = '<i class="fas fa-building text-warning"></i>'
            elif t == 'tilla':
                icon = '<i class="fas fa-coins text-success"></i>'
            elif t == 'sugurta':
                icon = '<i class="fas fa-shield-alt text-primary"></i>'
            
            html_parts.append(f'{icon} {label}')
        
        return " + ".join(html_parts)

    @property
    def garov_egasi_qisqa(self):
        col = self.collaterals.exclude(type='sugurta').first()
        if not col:
            return ""
        
        t_map = {
            'borrower': "O'zi",
            'other': "Boshqa shaxs",
            'general_proxy': "Bosh ishonchnoma"
        }
        t_label = t_map.get(col.owner_type, "")
        initials = col.owner_client.fish_inisiali if col.owner_client else ""
        
        if initials:
            return f"{t_label} | {initials}"
        return t_label


# ==========================================
# 3. KREDIT TAFSILOTLARI VA GRAFIK
# ==========================================
class LoanDetails(models.Model):
    application = models.OneToOneField(LoanApplication, on_delete=models.CASCADE, related_name='details', null=True, blank=True)

    shartnoma_raqami = models.CharField("Kredit shartnomasi raqami", max_length=50, blank=True, null=True)
    shartnoma_sanasi = models.DateField("Shartnoma sanasi", null=True, blank=True)
    boshlanish_sanasi = models.DateField("Boshlanish sanasi", null=True, blank=True)
    tugash_sanasi = models.DateField("Tugash sanasi", null=True, blank=True)
    
    miqdori = models.BigIntegerField("Kredit miqdori (raqam bilan)", blank=True, null=True)
    miqdori_soz = models.CharField("Kredit miqdori (so'z bilan)", max_length=255, blank=True, null=True)
    
    muddat_oy = models.CharField("Kredit muddati (oy)", max_length=10, blank=True, null=True)
    muddat_oy_soz = models.CharField("Kredit muddati (so'z bilan)", max_length=255, blank=True, null=True)
    
    foiz = models.CharField("Foiz stavkasi (raqam)", max_length=10, blank=True, null=True)
    foiz_soz = models.CharField("Foiz stavkasi (so'z bilan)", max_length=255, blank=True, null=True)

    KREDIT_TURI_CHOICES = [
        ('mikroqarz', 'Mikroqarz'),
        ('mikrokredit', 'Mikrokredit'),
    ]
    GRAFIK_CHOICES = [
        ('annuitet', 'Annuitet'),
        ('differensial', 'Differensial'),
    ]
    
    turi = models.CharField("Kredit turi", max_length=20, choices=KREDIT_TURI_CHOICES, default='mikroqarz', null=True, blank=True)
    grafik_turi = models.CharField("To'lov grafigi", max_length=20, choices=GRAFIK_CHOICES, default='differensial', null=True, blank=True)
    grafik_matni = models.TextField("Grafik jadvali (Exceldan)", blank=True, null=True)

    def __str__(self):
        return f"Details - {self.shartnoma_raqami}"


# ==========================================
# 4. KONTAKTLAR (BOG'LANISH UCHUN SHAXSLAR)
# ==========================================
class ContactPerson(models.Model):
    QARINDOSHLIK_CHOICES = [
        ('turmush_ortogi', "Turmush o'rtog'i"),
        ('ota', 'Ota'),
        ('ona', 'Ona'),
        ('aka', 'Aka'),
        ('uka', 'Uka'),
        ('opa', 'Opa'),
        ('singil', 'Singil')        
    ]

    application = models.ForeignKey(LoanApplication, on_delete=models.CASCADE, related_name='contacts', null=True, blank=True)
    fish = models.CharField("F.I.Sh", max_length=255, blank=True, null=True)
    telefon = models.CharField("Telefon raqami", max_length=20, blank=True, null=True)
    qarindoshlik = models.CharField("Qarindoshligi", max_length=50, choices=QARINDOSHLIK_CHOICES, blank=True, null=True)

    def __str__(self):
        return f"Contact {self.fish} for App #{self.application.id if self.application else 'Unknown'}"


# ==========================================
# 5. MOLIYAVIY HOLAT VA TASHKILOT
# ==========================================
class FinancialInfo(models.Model):
    FILIAL_CHOICES = [
        ('Buxoro filiali', 'Buxoro filiali'),
        ('Samarqand filiali', 'Samarqand filiali'),
        ('Toshkent shahar filiali', 'Toshkent shahar filiali'),
        ('Andijon filiali', 'Andijon filiali'),
        ('Farg\'ona filiali', 'Farg\'ona filiali'),
        ('Namangan filiali', 'Namangan filiali'),
        ('Qashqadaryo filiali', 'Qashqadaryo filiali'),
        ('Surxondaryo filiali', 'Surxondaryo filiali'),
        ('Jizzax filiali', 'Jizzax filiali'),
        ('Navoiy filiali', 'Navoiy filiali'),
        ('Xorazm filiali', 'Xorazm filiali'),
        ("To'rtko'l filiali", "To'rtko'l filiali"),
    ]

    application = models.OneToOneField(LoanApplication, on_delete=models.CASCADE, related_name='financial_info', null=True, blank=True)
    
    # Moliyaviy
    ish_joyi = models.TextField("Ish joyi va lavozimi", blank=True, null=True)
    daromad = models.BigIntegerField("Oylik daromad", blank=True, null=True)
    xarajatlar = models.BigIntegerField("Oylik xarajatlar", blank=True, null=True)
    tahminiy_tolov = models.BigIntegerField("Tahminiy oylik to'lov", blank=True, null=True)
    majburiyatlar = models.TextField("Miyjud qarz majburiyatlari", blank=True, null=True)

    # Tashkilot (Filial & MChJ)
    filial_nomi = models.CharField("Filial nomi", max_length=100, choices=FILIAL_CHOICES, default='Buxoro filiali', null=True, blank=True)
    filial_boshligi = models.CharField("Filial boshlig'i F.I.Sh", max_length=255, blank=True, null=True)
    filial_boshligi_inisiali = models.CharField("Filial boshlig'i Inisiali", max_length=100, blank=True, null=True)
    
    tashkilot_nomi = models.CharField("Tashkilot nomi", max_length=255, default='«PULLOL BUSINESS MIKROMOLIYA TASHKILOTI» MChJ', null=True, blank=True)
    direktor_fish = models.CharField("Direktor F.I.Sh", max_length=255, default="OBIDOV ABDULLA SHOKIR O'G'LI", blank=True, null=True)
    direktor_fish_inisiali = models.CharField("Direktor Inisiali", max_length=100, default="A.SH.OBIDOV", blank=True, null=True)

    def __str__(self):
        return f"Financials for App #{self.application.id if self.application else 'Unknown'}"


# ==========================================
# 6. GAROV BAZAVIY MODEL (COLLATERAL BASE)
# ==========================================
class Collateral(models.Model):
    COLLATERAL_TYPES = [
        ('avto', 'Avtomobil'),
        ('kochmas', "Ko'chmas mulk"),
        ('tilla', 'Tilla buyumlar'),
        ('sugurta', "Sug'urta polisi"),
    ]
    OWNER_TYPES = [
        ('borrower', "O'zi (Qarz oluvchi)"),
        ('other', "Uchinchi shaxs"),
        ('general_proxy', "Bosh ishonchnoma (Notarius)"),
    ]

    application = models.ForeignKey(LoanApplication, on_delete=models.CASCADE, related_name='collaterals', null=True, blank=True)
    type = models.CharField("Garov Turi", max_length=20, choices=COLLATERAL_TYPES, null=True, blank=True)
    owner_type = models.CharField("Garov egasi turi", max_length=20, choices=OWNER_TYPES, default='borrower', null=True, blank=True)
    
    # Garov egasi ham bazadan biriktiriladi
    owner_client = models.ForeignKey(Client, on_delete=models.SET_NULL, null=True, blank=True, related_name='owned_collaterals')

    # Agar Ishonchnoma (general_proxy) orqali bo'lsa
    notarius_fish = models.CharField("Notarius F.I.Sh", max_length=255, blank=True, null=True)
    notarius_address = models.CharField("Notarius manzili", max_length=255, blank=True, null=True)
    reestr_number = models.CharField("Reestr raqami", max_length=100, blank=True, null=True)
    reestr_date = models.DateField("Reestr sanasi", null=True, blank=True)

    def __str__(self):
        return f"{self.get_type_display()} for App #{self.application.id if self.application else 'Unknown'}"


# 6.1 Avtomobil
class AutoCollateral(models.Model):
    collateral = models.OneToOneField(Collateral, on_delete=models.CASCADE, related_name='auto_detail', null=True, blank=True)
    nomi = models.CharField("Modeli", max_length=100, blank=True, null=True)
    kuzov_turi = models.CharField("Kuzov turi", max_length=50, blank=True, null=True)
    kuzov_raqami = models.CharField("Kuzov raqami", max_length=50, blank=True, null=True)
    dvigatel = models.CharField("Dvigatel", max_length=50, blank=True, null=True)
    shassi = models.CharField("Shassi", max_length=50, blank=True, null=True, default='RAKAMSIZ')
    rang = models.CharField("Rangi", max_length=50, blank=True, null=True)
    yil = models.IntegerField("Ishlab chiqarilgan yili", blank=True, null=True)
    
    texpasport = models.CharField("Texpasport", max_length=50, blank=True, null=True)
    texpasport_sana = models.DateField("Texpasport sanasi", null=True, blank=True)
    manzil = models.CharField("Ro'yxatdan o'tgan manzil", max_length=255, blank=True, null=True)
    davlat_raqami = models.CharField("Davlat raqami", max_length=20, blank=True, null=True)
    
    bahosi = models.BigIntegerField("Baholangan qiymati", blank=True, null=True)
    bahosi_soz = models.CharField("Qiymat so'z bilan", max_length=255, blank=True, null=True)


# 6.2 Ko'chmas Mulk
class RealEstateCollateral(models.Model):
    collateral = models.OneToOneField(Collateral, on_delete=models.CASCADE, related_name='real_estate_detail', null=True, blank=True)
    turi = models.CharField("Mulk turi (Uy/Kvartira)", max_length=100, blank=True, null=True)
    umumiy_maydon = models.CharField("Umumiy maydon", max_length=50, blank=True, null=True)
    qurilish_maydon = models.CharField("Qurilish maydoni", max_length=50, blank=True, null=True)
    foydalanish_maydon = models.CharField("Foydalanish maydoni", max_length=50, blank=True, null=True)
    yashash_maydon = models.CharField("Yashash maydoni", max_length=50, blank=True, null=True)
    
    reestr_raqami = models.CharField("Mulk reestr raqami", max_length=50, blank=True, null=True)
    kadastr_raqami = models.CharField("Kadastr raqami", max_length=100, blank=True, null=True)
    manzil = models.TextField("Mulk manzili", blank=True, null=True)
    
    bahosi = models.BigIntegerField("Garov qiymati", blank=True, null=True)
    bahosi_soz = models.CharField("Garov qiymati so'z bilan", max_length=255, blank=True, null=True)


# 6.3 Tilla Buyumlar
class GoldCollateral(models.Model):
    collateral = models.OneToOneField(Collateral, on_delete=models.CASCADE, related_name='gold_detail', null=True, blank=True)
    nomi = models.TextField("Buyumlar nomi/tavsifi", blank=True, null=True)
    probi = models.CharField("Probsi", max_length=20, blank=True, null=True)
    vazni = models.CharField("Vazni (gr)", max_length=50, blank=True, null=True)
    soni = models.IntegerField("Soni (dona)", blank=True, null=True)
    
    bahosi = models.BigIntegerField("Baholangan qiymati", blank=True, null=True)
    bahosi_soz = models.CharField("Garov qiymati so'z bilan", max_length=255, blank=True, null=True)


# 6.4 Sug'urta Polisi
class InsuranceCollateral(models.Model):
    collateral = models.OneToOneField(Collateral, on_delete=models.CASCADE, related_name='insurance_detail', null=True, blank=True)
    kompaniya = models.CharField("Sug'urta kompaniyasi", max_length=255, blank=True, null=True)
    polis_raqami = models.CharField("Polis raqami", max_length=50, blank=True, null=True)
    sana = models.DateField("Sug'urta sanasi", null=True, blank=True)
    
    summa = models.BigIntegerField("Sug'urta summasi", blank=True, null=True)
    summa_soz = models.CharField("Sug'urta summasi so'z bilan", max_length=255, blank=True, null=True)


# Eski ProcessedDocument va DocumentTemplate ni saqlab qolamiz
class ProcessedDocument(models.Model):
    pass # bu jadval ishlatilmaydi aytganingizdek 


class DocumentTemplate(models.Model):
    name = models.CharField(max_length=255, verbose_name="Shablon nomi", null=True, blank=True)
    file = models.FileField(upload_to='templates/', verbose_name="Word fayl (.docx)", null=True, blank=True)
    code = models.CharField(max_length=50, unique=True, verbose_name="Kod (unikal)", null=True, blank=True)
    description = models.TextField(blank=True, verbose_name="Tavsif", null=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)

    def __str__(self):
        return str(self.name)

