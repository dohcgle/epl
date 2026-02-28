from django import forms
from .models import LoanApplication, LoanDetails, FinancialInfo

class UmumiyMalumotForm(forms.Form):
    # --- SHAXSIY MA'LUMOTLAR (Qarz oluvchi) ---
    qarz_oluvchi_fish = forms.CharField(label="Qarz oluvchi F.I.Sh", max_length=255, required=False)
    qarz_oluvchi_fish_inisiali = forms.CharField(label="Qarz oluvchi F.I.Sh (Inisiali)", max_length=100, required=False, widget=forms.TextInput(attrs={'style': 'text-transform:uppercase', 'oninput': 'this.value = this.value.toUpperCase()'}))
    qarz_oluvchi_pasport_seriya = forms.CharField(label="Pasport seriyasi va raqami", max_length=20, required=False)
    qarz_oluvchi_pasport_berilgan = forms.CharField(label="Kim tomonidan va qachon berilgan", widget=forms.Textarea(attrs={'rows': 2}), required=False)
    qarz_oluvchi_manzil = forms.CharField(label="Doimiy yashash manzili", widget=forms.Textarea(attrs={'rows': 2}), required=False)
    qarz_oluvchi_ish_joyi = forms.CharField(label="Ish joyi va lavozimi", widget=forms.Textarea(attrs={'rows': 2}), required=False)
    qarz_oluvchi_daromad = forms.IntegerField(label="O'rtacha oylik daromad (so'm)", required=False)
    qarz_oluvchi_xarajatlar = forms.IntegerField(label="O'rtacha oylik xarajatlar (so'm)", required=False)
    qarz_oluvchi_majburiyatlar = forms.CharField(label="Mavjud kredit va qarz majburiyatlari", widget=forms.Textarea(attrs={'rows': 2}), required=False)
    qarz_oluvchi_tahminiy_tolov = forms.IntegerField(label="Mikroqarz bo‘yicha oylik differensial to‘lovi miqdori (tahminiy)", required=False)
    qarz_oluvchi_tugilgan_sana = forms.DateField(label="Tug'ilgan sanasi", widget=forms.DateInput(attrs={'class': 'date-mask', 'placeholder': 'dd.mm.yyyy'}), input_formats=['%d.%m.%Y'], required=False)
    
    JINSI_CHOICES = [
        ('erkak', 'Erkak'),
        ('ayol', 'Ayol'),
    ]
    qarz_oluvchi_jinsi = forms.ChoiceField(label="Jinsi", choices=[('', 'Tanlang...')] + JINSI_CHOICES, required=False)
    qarz_oluvchi_jshshir = forms.CharField(label="JSHSHIR", max_length=14, required=False)
    qarz_oluvchi_telefon = forms.CharField(label="Telefon raqami", required=False)

    QARINDOSHLIK_CHOICES = [
        ('turmush_ortogi', "Turmush o'rtog'i"),
        ('ota', 'Ota'),
        ('ona', 'Ona'),
        ('aka', 'Aka'),
        ('uka', 'Uka'),
        ('opa', 'Opa'),
        ('singil', 'Singil')        
    ]

    # --- KONTAKT SHAXSLAR ---
    kontakt_1_fish = forms.CharField(label="1-kontakt F.I.Sh", required=False)
    kontakt_1_telefon = forms.CharField(label="1-kontakt Telefoni", required=False)
    kontakt_1_qarindoshlik = forms.ChoiceField(label="1-kontakt Qarindoshligi", choices=[('', 'Tanlang...')] + QARINDOSHLIK_CHOICES, required=False)

    kontakt_2_fish = forms.CharField(label="2-kontakt F.I.Sh", required=False)
    kontakt_2_telefon = forms.CharField(label="2-kontakt Telefoni", required=False)
    kontakt_2_qarindoshlik = forms.ChoiceField(label="2-kontakt Qarindoshligi", choices=[('', 'Tanlang...')] + QARINDOSHLIK_CHOICES, required=False)

    kontakt_3_fish = forms.CharField(label="3-kontakt F.I.Sh", required=False)
    kontakt_3_telefon = forms.CharField(label="3-kontakt Telefoni", required=False)
    kontakt_3_qarindoshlik = forms.ChoiceField(label="3-kontakt Qarindoshligi", choices=[('', 'Tanlang...')] + QARINDOSHLIK_CHOICES, required=False)

    # --- KREDIT MA'LUMOTLARI ---
    shartnoma_raqami = forms.CharField(label="Kredit shartnomasi raqami", max_length=50, required=False)
    shartnoma_sanasi = forms.DateField(label="Shartnoma sanasi", widget=forms.DateInput(attrs={'class': 'date-mask', 'placeholder': 'dd.mm.yyyy'}), input_formats=['%d.%m.%Y'], required=False)
    kredit_miqdori = forms.IntegerField(label="Kredit miqdori (raqam bilan)", required=False)
    kredit_miqdori_soz = forms.CharField(label="Kredit miqdori (so'z bilan)", widget=forms.TextInput(attrs={'readonly': 'readonly'}), required=False)
    kredit_muddat_oy = forms.CharField(label="Kredit muddati (oy)", required=False)
    kredit_muddat_oy_soz = forms.CharField(label="Kredit muddati (so'z bilan)", widget=forms.TextInput(attrs={'readonly': 'readonly'}), required=False)
    foiz_stavkasi = forms.CharField(label="Foiz stavkasi (raqam)", required=False)
    foiz_stavkasi_soz = forms.CharField(label="Foiz stavkasi (so'z bilan)", widget=forms.TextInput(attrs={'readonly': 'readonly'}), required=False)
    
    KREDIT_TURI_CHOICES = [
        ('mikroqarz', 'Mikroqarz'),
        ('mikrokredit', 'Mikrokredit'),
    ]
    GRAFIK_CHOICES = [
        ('annuitet', 'Annuitet'),
        ('differensial', 'Differensial'),
    ]
    
    kredit_turi = forms.ChoiceField(label="Kredit turi", choices=KREDIT_TURI_CHOICES, initial='mikroqarz')
    grafik = forms.ChoiceField(label="Grafik", choices=GRAFIK_CHOICES, initial='annuitet')

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

    garov_turi = forms.ChoiceField(label="Garov turi", choices=GAROV_TURI_CHOICES, initial='avto')
    sugurta_mavjud = forms.BooleanField(label="Sug'urta polisi bormi?", required=False, widget=forms.CheckboxInput(attrs={'class': 'custom-control-input'})) # Checkbox
    uchinchi_shaxs_mavjud = forms.BooleanField(label="Garov mulkdori uchinchi shaxsmi?", required=False, widget=forms.CheckboxInput(attrs={'class': 'custom-control-input'}))
    garov_egasi = forms.ChoiceField(label="Garov mulkdori", choices=GAROV_EGASI_CHOICES, widget=forms.HiddenInput, initial='oz')

    # --- GAROV EGASI VA ISHONCHNOMA MA'LUMOTLARI ---
    garov_egasi_fish = forms.CharField(label="Garov egasi F.I.Sh", max_length=255, required=False, widget=forms.TextInput(attrs={'style': 'text-transform:uppercase', 'oninput': 'this.value = this.value.toUpperCase()'}))
    garov_egasi_inisiali = forms.CharField(label="Garov egasining inisiali", required=False, widget=forms.TextInput(attrs={'style': 'text-transform:uppercase', 'oninput': 'this.value = this.value.toUpperCase()'}))
    garov_egasi_pasport = forms.CharField(label="Garov egasi pasport ma'lumotlari", widget=forms.Textarea(attrs={'rows': 2}), required=False)
    garov_egasi_manzil = forms.CharField(label="Garov egasi manzili", widget=forms.Textarea(attrs={'rows': 2}), required=False)

    ishonchnoma_notarius_fish = forms.CharField(label="Notarius F.I.Sh", required=False, widget=forms.TextInput(attrs={'style': 'text-transform:uppercase', 'oninput': 'this.value = this.value.toUpperCase()'}))
    ishonchnoma_notarius_manzil = forms.CharField(label="Notarius manzili", required=False)
    ishonchnoma_reestr_raqami = forms.CharField(label="Reestr raqami", required=False)
    ishonchnoma_reestr_sanasi = forms.DateField(label="Reestr sanasi", widget=forms.DateInput(attrs={'class': 'date-mask', 'placeholder': 'dd.mm.yyyy'}), input_formats=['%d.%m.%Y'], required=False)

    avto_nomi = forms.CharField(label="Avtomobil modeli (masalan Cobalt)", required=False)
    avto_raqam = forms.CharField(label="Davlat raqami", required=False)
    avto_kuzov_turi = forms.CharField(label="Kuzov turi (masalan Sedan)", widget=forms.TextInput(attrs={'style': 'text-transform:uppercase', 'oninput': 'this.value = this.value.toUpperCase()'}), required=False)
    avto_kuzov = forms.CharField(label="Kuzov raqami", required=False)
    avto_dvigatel = forms.CharField(label="Dvigatel raqami", required=False)
    avto_shassi = forms.CharField(label="Shassi raqami", initial="RAKAMSIZ", widget=forms.TextInput(attrs={'style': 'text-transform:uppercase', 'oninput': 'this.value = this.value.toUpperCase()'}), required=False)
    avto_yil = forms.IntegerField(label="Ishlab chiqarilgan yili", required=False)
    avto_rang = forms.CharField(label="Rangi", required=False)
    avto_bahosi = forms.IntegerField(label="Baholangan qiymati", required=False)
    avto_yurgan = forms.CharField(label="Yurgan masofasi (km)", required=False)
    avto_texpasport = forms.CharField(label="Texpasport seriyasi (Masalan AAF 1234567)", required=False)
    avto_texpasport_sana = forms.DateField(label="Texpasport berilgan sanasi", widget=forms.DateInput(attrs={'class': 'date-mask', 'placeholder': 'dd.mm.yyyy'}), input_formats=['%d.%m.%Y'], required=False)
    avto_manzil = forms.CharField(label="Roʻyxatdan oʻtgan manzili/garaj manzili", widget=forms.Textarea(attrs={'rows': 2}), required=False)

    mulk_turi = forms.CharField(label="Nomi", required=False, widget=forms.TextInput(attrs={'style': 'text-transform:uppercase', 'oninput': 'this.value = this.value.toUpperCase()'}))
    mulk_qurilish_maydoni = forms.FloatField(label="Qurilish osti maydoni", required=False)
    mulk_umumiy_maydoni = forms.FloatField(label="Umumiy maydon", required=False)
    mulk_yashash_maydoni = forms.FloatField(label="Yashash maydon", required=False)
    mulk_egasi = forms.CharField(label="Ko'chmas mulk egasi", required=False, widget=forms.TextInput(attrs={'style': 'text-transform:uppercase', 'oninput': 'this.value = this.value.toUpperCase()'}))
    mulk_reestr_raqami = forms.CharField(label="Reestr raqami", required=False, widget=forms.TextInput(attrs={'style': 'text-transform:uppercase', 'oninput': 'this.value = this.value.toUpperCase()'}))
    mulk_kadastr_raqami = forms.CharField(label="Kadastr raqami", required=False)
    mulk_manzili = forms.CharField(label="Manzil", widget=forms.Textarea(attrs={'rows': 2, 'style': 'text-transform:uppercase', 'oninput': 'this.value = this.value.toUpperCase()'}), required=False)
    mulk_bahosi = forms.IntegerField(label="Kelishilgan garov qiymati (raqam)", required=False)
    mulk_bahosi_soz = forms.CharField(label="Kelishilgan garov qiymati (so'z bilan)", widget=forms.TextInput(attrs={'readonly': 'readonly'}), required=False)

    tilla_nomi = forms.CharField(label="Tilla buyumlar nomi", widget=forms.Textarea(attrs={'rows': 2}), required=False)
    tilla_probi = forms.CharField(label="Probsi (masalan 583)", required=False)
    tilla_vazni = forms.CharField(label="Umumiy vazni (gr)", required=False)
    tilla_soni = forms.CharField(label="Soni (dona)", required=False)
    tilla_bahosi = forms.IntegerField(label="Baholangan qiymati", required=False)
    tilla_bahosi_soz = forms.CharField(label="Baholangan qiymati (so'z bilan)", required=False)

    sugurta_kompaniyasi = forms.CharField(label="Sug'urta kompaniyasi nomi", required=False)
    sugurta_polisi = forms.CharField(label="Sug'urta polisi raqami", required=False)
    sugurta_sanasi = forms.DateField(label="Sug'urta sanasi", widget=forms.DateInput(attrs={'class': 'date-mask', 'placeholder': 'dd.mm.yyyy'}), input_formats=['%d.%m.%Y'], required=False)
    sugurta_summasi = forms.IntegerField(label="Sug'urta summasi (raqam)", required=False)
    sugurta_summasi_soz = forms.CharField(label="Sug'urta summasi (so'z bilan)", required=False)

    filial_nomi = forms.ChoiceField(label="Filial nomi", choices=FinancialInfo.FILIAL_CHOICES, initial='Buxoro filiali')
    filial_boshligi = forms.CharField(label="Filial boshlig'i F.I.Sh", initial="IKROMOV B.A.", required=False)
    filial_boshligi_inisiali = forms.CharField(label="Filial boshlig'i F.I.Sh (Inisiali)", initial="B.A.IKROMOV", required=False, widget=forms.TextInput(attrs={'style': 'text-transform:uppercase', 'oninput': 'this.value = this.value.toUpperCase(); this.setCustomValidity("")'}))
    
    tashkilot_nomi = forms.CharField(label="Tashkilot nomi", initial='«PULLOL BUSINESS MIKROMOLIYA TASHKILOTI» MChJ', required=False, widget=forms.TextInput(attrs={'readonly': 'readonly'}))
    direktor_fish = forms.CharField(label="Direktor F.I.Sh", initial="OBIDOV ABDULLA SHOKIR O'G'LI", required=False, widget=forms.TextInput(attrs={'readonly': 'readonly'}))
    direktor_fish_inisiali = forms.CharField(label="Direktor F.I.Sh (Inisiali)", initial="A.SH.OBIDOV", required=False, widget=forms.TextInput(attrs={'readonly': 'readonly'}))

    grafik_matni = forms.CharField(
        label="Grafik jadvali (Exceldan nusxalab tashlang)", 
        widget=forms.Textarea(attrs={'rows': 10, 'placeholder': "Exceldan jadvalni belgilab, shu yerga tashlang (Ctrl+V)..."}), 
        required=False,
        help_text="Format: № | Sana | Qoldiq | Asosiy qarz | Foiz | Jami"
    )
    
    monitoring_sana_1 = forms.DateField(label="1-monitoring sanasi", widget=forms.DateInput(attrs={'class': 'date-mask', 'placeholder': 'dd.mm.yyyy'}), input_formats=['%d.%m.%Y'], required=False)
    monitoring_sana_2 = forms.DateField(label="2-monitoring sanasi", widget=forms.DateInput(attrs={'class': 'date-mask', 'placeholder': 'dd.mm.yyyy'}), input_formats=['%d.%m.%Y'], required=False)
    monitoring_sana_3 = forms.DateField(label="3-monitoring sanasi", widget=forms.DateInput(attrs={'class': 'date-mask', 'placeholder': 'dd.mm.yyyy'}), input_formats=['%d.%m.%Y'], required=False)
    monitoring_sana_4 = forms.DateField(label="4-monitoring sanasi", widget=forms.DateInput(attrs={'class': 'date-mask', 'placeholder': 'dd.mm.yyyy'}), input_formats=['%d.%m.%Y'], required=False)
