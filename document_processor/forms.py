from django import forms
from .models import LoanAgreement

class UmumiyMalumotForm(forms.Form):
    # --- SHAXSIY MA'LUMOTLAR (Qarz oluvchi) ---
    qarz_oluvchi_fish = forms.CharField(label="Qarz oluvchi F.I.Sh", max_length=255, required=False, widget=forms.TextInput(attrs={'required': 'required', 'oninvalid': "this.setCustomValidity('Iltimos, ushbu maydonni to\\'ldiring')", 'oninput': "this.setCustomValidity('')"}))
    qarz_oluvchi_pasport_seriya = forms.CharField(label="Pasport seriyasi va raqami", max_length=20, required=False, widget=forms.TextInput(attrs={'required': 'required', 'oninvalid': "this.setCustomValidity('Iltimos, ushbu maydonni to\\'ldiring')", 'oninput': "this.setCustomValidity('')"}))
    qarz_oluvchi_pasport_berilgan = forms.CharField(label="Kim tomonidan va qachon berilgan", widget=forms.Textarea(attrs={'rows': 2, 'required': 'required', 'oninvalid': "this.setCustomValidity('Iltimos, ushbu maydonni to\\'ldiring')", 'oninput': "this.setCustomValidity('')"}), required=False)
    qarz_oluvchi_manzil = forms.CharField(label="Doimiy yashash manzili", widget=forms.Textarea(attrs={'rows': 2, 'required': 'required', 'oninvalid': "this.setCustomValidity('Iltimos, ushbu maydonni to\\'ldiring')", 'oninput': "this.setCustomValidity('')"}), required=False)
    qarz_oluvchi_ish_joyi = forms.CharField(label="Ish joyi va lavozimi", widget=forms.Textarea(attrs={'rows': 2, 'required': 'required', 'oninvalid': "this.setCustomValidity('Iltimos, ushbu maydonni to\\'ldiring')", 'oninput': "this.setCustomValidity('')"}), required=False)
    qarz_oluvchi_daromad = forms.IntegerField(label="O'rtacha oylik daromad (so'm)", widget=forms.TextInput(attrs={'required': 'required', 'oninvalid': "this.setCustomValidity('Iltimos, ushbu maydonni to\\'ldiring')", 'oninput': "this.setCustomValidity('')"}), required=False)
    qarz_oluvchi_xarajatlar = forms.IntegerField(label="O'rtacha oylik xarajatlar (so'm)", widget=forms.TextInput(attrs={'required': 'required', 'oninvalid': "this.setCustomValidity('Iltimos, ushbu maydonni to\\'ldiring')", 'oninput': "this.setCustomValidity('')"}), required=False)
    qarz_oluvchi_majburiyatlar = forms.CharField(label="Mavjud kredit va qarz majburiyatlari", widget=forms.Textarea(attrs={'rows': 2, 'required': 'required', 'oninvalid': "this.setCustomValidity('Iltimos, ushbu maydonni to\\'ldiring')", 'oninput': "this.setCustomValidity('')"}), required=False)
    qarz_oluvchi_tahminiy_tolov = forms.IntegerField(label="Mikroqarz bo‘yicha oylik differensial to‘lovi miqdori (tahminiy)", widget=forms.TextInput(attrs={'required': 'required', 'oninvalid': "this.setCustomValidity('Iltimos, ushbu maydonni to\\'ldiring')", 'oninput': "this.setCustomValidity('')"}), required=False)
    qarz_oluvchi_tugilgan_sana = forms.DateField(label="Tug'ilgan sanasi", widget=forms.DateInput(attrs={'class': 'date-mask', 'placeholder': 'dd.mm.yyyy', 'required': 'required', 'oninvalid': "this.setCustomValidity('Iltimos, ushbu maydonni to\\'ldiring')", 'oninput': "this.setCustomValidity('')"}), input_formats=['%d.%m.%Y'], required=False)
    qarz_oluvchi_jshshir = forms.CharField(label="JSHSHIR", max_length=14, required=False, widget=forms.TextInput(attrs={'required': 'required', 'oninvalid': "this.setCustomValidity('Iltimos, ushbu maydonni to\\'ldiring')", 'oninput': "this.setCustomValidity('')"}))
    qarz_oluvchi_telefon = forms.CharField(label="Telefon raqami", required=False, widget=forms.TextInput(attrs={'required': 'required', 'oninvalid': "this.setCustomValidity('Iltimos, ushbu maydonni to\\'ldiring')", 'oninput': "this.setCustomValidity('')"}))

    # --- KONTAKT SHAXSLAR ---
    # --- KONTAKT SHAXSLAR ---
    kontakt_1_fish = forms.CharField(label="1-kontakt F.I.Sh", required=False)
    kontakt_1_telefon = forms.CharField(label="1-kontakt Telefoni", required=False)
    kontakt_1_qarindoshlik = forms.ChoiceField(label="1-kontakt Qarindoshligi", choices=[('', 'Tanlang...')] + LoanAgreement.QARINDOSHLIK_CHOICES, required=False)

    kontakt_2_fish = forms.CharField(label="2-kontakt F.I.Sh", required=False)
    kontakt_2_telefon = forms.CharField(label="2-kontakt Telefoni", required=False)
    kontakt_2_qarindoshlik = forms.ChoiceField(label="2-kontakt Qarindoshligi", choices=[('', 'Tanlang...')] + LoanAgreement.QARINDOSHLIK_CHOICES, required=False)

    kontakt_3_fish = forms.CharField(label="3-kontakt F.I.Sh", required=False)
    kontakt_3_telefon = forms.CharField(label="3-kontakt Telefoni", required=False)
    kontakt_3_qarindoshlik = forms.ChoiceField(label="3-kontakt Qarindoshligi", choices=[('', 'Tanlang...')] + LoanAgreement.QARINDOSHLIK_CHOICES, required=False)

    # --- KREDIT MA'LUMOTLARI ---
    shartnoma_raqami = forms.CharField(label="Kredit shartnomasi raqami", max_length=50, required=False, widget=forms.TextInput(attrs={'required': 'required', 'oninvalid': "this.setCustomValidity('Iltimos, ushbu maydonni to\\'ldiring')", 'oninput': "this.setCustomValidity('')"}))
    shartnoma_sanasi = forms.DateField(label="Shartnoma sanasi", widget=forms.DateInput(attrs={'class': 'date-mask', 'placeholder': 'dd.mm.yyyy', 'required': 'required', 'oninvalid': "this.setCustomValidity('Iltimos, ushbu maydonni to\\'ldiring')", 'oninput': "this.setCustomValidity('')"}), input_formats=['%d.%m.%Y'], required=False)
    kredit_miqdori = forms.IntegerField(label="Kredit miqdori (raqam bilan)", widget=forms.TextInput(attrs={'required': 'required', 'oninvalid': "this.setCustomValidity('Iltimos, ushbu maydonni to\\'ldiring')", 'oninput': "this.setCustomValidity('')"}), required=False)
    kredit_miqdori_soz = forms.CharField(label="Kredit miqdori (so'z bilan)", widget=forms.TextInput(attrs={'readonly': 'readonly'}), required=False)
    kredit_muddat_oy = forms.CharField(label="Kredit muddati (oy)", required=False, widget=forms.TextInput(attrs={'required': 'required', 'oninvalid': "this.setCustomValidity('Iltimos, ushbu maydonni to\\'ldiring')", 'oninput': "this.setCustomValidity('')"}))
    foiz_stavkasi = forms.CharField(label="Foiz stavkasi (raqam)", required=False, widget=forms.TextInput(attrs={'required': 'required', 'oninvalid': "this.setCustomValidity('Iltimos, ushbu maydonni to\\'ldiring')", 'oninput': "this.setCustomValidity('')"}))
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
    garov_egasi = forms.ChoiceField(label="Garov mulkdori", choices=GAROV_EGASI_CHOICES, widget=forms.RadioSelect, initial='oz')

    # --- UCHINCHI SHAXS MA'LUMOTLARI (Agar garov egasi boshqa bo'lsa) ---
    garov_egasi_fish = forms.CharField(label="Garov egasi F.I.Sh", max_length=255, required=False, widget=forms.TextInput(attrs={'required': 'required', 'oninvalid': "this.setCustomValidity('Iltimos, ushbu maydonni to\\'ldiring')", 'oninput': "this.setCustomValidity('')"}))
    garov_egasi_pasport = forms.CharField(label="Garov egasi pasport ma'lumotlari", widget=forms.Textarea(attrs={'rows': 2, 'required': 'required', 'oninvalid': "this.setCustomValidity('Iltimos, ushbu maydonni to\\'ldiring')", 'oninput': "this.setCustomValidity('')"}), required=False)
    garov_egasi_manzil = forms.CharField(label="Garov egasi manzili", widget=forms.Textarea(attrs={'rows': 2, 'required': 'required', 'oninvalid': "this.setCustomValidity('Iltimos, ushbu maydonni to\\'ldiring')", 'oninput': "this.setCustomValidity('')"}), required=False)

    # --- AVTOMOBIL MA'LUMOTLARI (Agar garov turi avto bo'lsa) ---
    avto_nomi = forms.CharField(label="Avtomobil modeli (masalan Cobalt)", required=False, widget=forms.TextInput(attrs={'required': 'required', 'oninvalid': "this.setCustomValidity('Iltimos, ushbu maydonni to\\'ldiring')", 'oninput': "this.setCustomValidity('')"}))
    avto_raqam = forms.CharField(label="Davlat raqami", required=False, widget=forms.TextInput(attrs={'required': 'required', 'oninvalid': "this.setCustomValidity('Iltimos, ushbu maydonni to\\'ldiring')", 'oninput': "this.setCustomValidity('')"}))
    avto_kuzov_turi = forms.CharField(label="Kuzov turi (masalan Sedan)", widget=forms.TextInput(attrs={'style': 'text-transform:uppercase', 'oninput': 'this.value = this.value.toUpperCase()', 'required': 'required', 'oninvalid': "this.setCustomValidity('Iltimos, ushbu maydonni to\\'ldiring')", 'oninput': "this.setCustomValidity('')"}), required=False)
    avto_kuzov = forms.CharField(label="Kuzov raqami", required=False, widget=forms.TextInput(attrs={'required': 'required', 'oninvalid': "this.setCustomValidity('Iltimos, ushbu maydonni to\\'ldiring')", 'oninput': "this.setCustomValidity('')"}))
    avto_dvigatel = forms.CharField(label="Dvigatel raqami", required=False, widget=forms.TextInput(attrs={'required': 'required', 'oninvalid': "this.setCustomValidity('Iltimos, ushbu maydonni to\\'ldiring')", 'oninput': "this.setCustomValidity('')"}))
    avto_shassi = forms.CharField(label="Shassi raqami", initial="RAKAMSIZ", widget=forms.TextInput(attrs={'style': 'text-transform:uppercase', 'oninput': 'this.value = this.value.toUpperCase()', 'required': 'required', 'oninvalid': "this.setCustomValidity('Iltimos, ushbu maydonni to\\'ldiring')", 'oninput': "this.setCustomValidity('')"}), required=False)
    avto_yil = forms.IntegerField(label="Ishlab chiqarilgan yili", required=False, widget=forms.TextInput(attrs={'required': 'required', 'oninvalid': "this.setCustomValidity('Iltimos, ushbu maydonni to\\'ldiring')", 'oninput': "this.setCustomValidity('')"}))
    avto_rang = forms.CharField(label="Rangi", required=False, widget=forms.TextInput(attrs={'required': 'required', 'oninvalid': "this.setCustomValidity('Iltimos, ushbu maydonni to\\'ldiring')", 'oninput': "this.setCustomValidity('')"}))
    avto_bahosi = forms.IntegerField(label="Baholangan qiymati", widget=forms.TextInput(attrs={'required': 'required', 'oninvalid': "this.setCustomValidity('Iltimos, ushbu maydonni to\\'ldiring')", 'oninput': "this.setCustomValidity('')"}), required=False)
    avto_yurgan = forms.CharField(label="Yurgan masofasi (km)", required=False, widget=forms.TextInput(attrs={'required': 'required', 'oninvalid': "this.setCustomValidity('Iltimos, ushbu maydonni to\\'ldiring')", 'oninput': "this.setCustomValidity('')"}))
    avto_texpasport = forms.CharField(label="Texpasport seriyasi (Masalan AAF 1234567)", required=False, widget=forms.TextInput(attrs={'required': 'required', 'oninvalid': "this.setCustomValidity('Iltimos, ushbu maydonni to\\'ldiring')", 'oninput': "this.setCustomValidity('')"}))
    avto_texpasport_sana = forms.DateField(label="Texpasport berilgan sanasi", widget=forms.DateInput(attrs={'class': 'date-mask', 'placeholder': 'dd.mm.yyyy', 'required': 'required', 'oninvalid': "this.setCustomValidity('Iltimos, ushbu maydonni to\\'ldiring')", 'oninput': "this.setCustomValidity('')"}), input_formats=['%d.%m.%Y'], required=False)
    avto_manzil = forms.CharField(label="Roʻyxatdan oʻtgan manzili/garaj manzili", widget=forms.Textarea(attrs={'rows': 2, 'required': 'required', 'oninvalid': "this.setCustomValidity('Iltimos, ushbu maydonni to\\'ldiring')", 'oninput': "this.setCustomValidity('')"}), required=False)

    # --- KO'CHMAS MULK MA'LUMOTLARI ---
    mulk_manzili = forms.CharField(label="Ko'chmas mulk manzili", widget=forms.Textarea(attrs={'rows': 2, 'required': 'required', 'oninvalid': "this.setCustomValidity('Iltimos, ushbu maydonni to\\'ldiring')", 'oninput': "this.setCustomValidity('')"}), required=False)
    mulk_qurilish_maydoni = forms.CharField(label="Qurilish osti maydoni", required=False, widget=forms.TextInput(attrs={'required': 'required', 'oninvalid': "this.setCustomValidity('Iltimos, ushbu maydonni to\\'ldiring')", 'oninput': "this.setCustomValidity('')"}))
    mulk_umumiy_maydoni = forms.CharField(label="Umumiy maydoni", required=False, widget=forms.TextInput(attrs={'required': 'required', 'oninvalid': "this.setCustomValidity('Iltimos, ushbu maydonni to\\'ldiring')", 'oninput': "this.setCustomValidity('')"}))
    mulk_yashash_maydoni = forms.CharField(label="Yashash maydoni", required=False, widget=forms.TextInput(attrs={'required': 'required', 'oninvalid': "this.setCustomValidity('Iltimos, ushbu maydonni to\\'ldiring')", 'oninput': "this.setCustomValidity('')"}))
    mulk_turi = forms.CharField(label="Ko'chmas mulk turi (masalan: Yakka tartibdagi turarjoy)", required=False, widget=forms.TextInput(attrs={'required': 'required', 'oninvalid': "this.setCustomValidity('Iltimos, ushbu maydonni to\\'ldiring')", 'oninput': "this.setCustomValidity('')"}))
    mulk_bahosi = forms.IntegerField(label="Kelishilgan garov qiymati (raqam)", widget=forms.TextInput(attrs={'required': 'required', 'oninvalid': "this.setCustomValidity('Iltimos, ushbu maydonni to\\'ldiring')", 'oninput': "this.setCustomValidity('')"}), required=False)
    mulk_bahosi_soz = forms.CharField(label="Kelishilgan garov qiymati (so'z bilan)", required=False)
    mulk_dalolatnoma_raqami = forms.CharField(label="Baholash dalolatnoma raqami", initial="1", required=False, widget=forms.TextInput(attrs={'required': 'required', 'oninvalid': "this.setCustomValidity('Iltimos, ushbu maydonni to\\'ldiring')", 'oninput': "this.setCustomValidity('')"}))
    mulk_dalolatnoma_sanasi = forms.DateField(label="Baholash dalolatnoma sanasi", widget=forms.DateInput(attrs={'class': 'date-mask', 'placeholder': 'dd.mm.yyyy', 'required': 'required', 'oninvalid': "this.setCustomValidity('Iltimos, ushbu maydonni to\\'ldiring')", 'oninput': "this.setCustomValidity('')"}), input_formats=['%d.%m.%Y'], required=False)

    # --- TILLA BUYUMLAR MA'LUMOTLARI ---
    tilla_nomi = forms.CharField(label="Tilla buyumlar nomi", widget=forms.Textarea(attrs={'rows': 2, 'required': 'required', 'oninvalid': "this.setCustomValidity('Iltimos, ushbu maydonni to\\'ldiring')", 'oninput': "this.setCustomValidity('')"}), required=False)
    tilla_probi = forms.CharField(label="Probsi (masalan 583)", required=False, widget=forms.TextInput(attrs={'required': 'required', 'oninvalid': "this.setCustomValidity('Iltimos, ushbu maydonni to\\'ldiring')", 'oninput': "this.setCustomValidity('')"}))
    tilla_vazni = forms.CharField(label="Umumiy vazni (gr)", required=False, widget=forms.TextInput(attrs={'required': 'required', 'oninvalid': "this.setCustomValidity('Iltimos, ushbu maydonni to\\'ldiring')", 'oninput': "this.setCustomValidity('')"}))
    tilla_soni = forms.CharField(label="Soni (dona)", required=False, widget=forms.TextInput(attrs={'required': 'required', 'oninvalid': "this.setCustomValidity('Iltimos, ushbu maydonni to\\'ldiring')", 'oninput': "this.setCustomValidity('')"}))
    tilla_bahosi = forms.IntegerField(label="Baholangan qiymati", widget=forms.TextInput(attrs={'required': 'required', 'oninvalid': "this.setCustomValidity('Iltimos, ushbu maydonni to\\'ldiring')", 'oninput': "this.setCustomValidity('')"}), required=False)
    tilla_bahosi_soz = forms.CharField(label="Baholangan qiymati (so'z bilan)", required=False)

    # --- SUG'URTA MA'LUMOTLARI ---
    sugurta_kompaniyasi = forms.CharField(label="Sug'urta kompaniyasi nomi", required=False, widget=forms.TextInput(attrs={'required': 'required', 'oninvalid': "this.setCustomValidity('Iltimos, ushbu maydonni to\\'ldiring')", 'oninput': "this.setCustomValidity('')"}))
    sugurta_polisi = forms.CharField(label="Sug'urta polisi raqami", required=False, widget=forms.TextInput(attrs={'required': 'required', 'oninvalid': "this.setCustomValidity('Iltimos, ushbu maydonni to\\'ldiring')", 'oninput': "this.setCustomValidity('')"}))
    sugurta_sanasi = forms.DateField(label="Sug'urta sanasi", widget=forms.DateInput(attrs={'class': 'date-mask', 'placeholder': 'dd.mm.yyyy', 'required': 'required', 'oninvalid': "this.setCustomValidity('Iltimos, ushbu maydonni to\\'ldiring')", 'oninput': "this.setCustomValidity('')"}), input_formats=['%d.%m.%Y'], required=False)
    sugurta_summasi = forms.IntegerField(label="Sug'urta summasi (raqam)", widget=forms.TextInput(attrs={'required': 'required', 'oninvalid': "this.setCustomValidity('Iltimos, ushbu maydonni to\\'ldiring')", 'oninput': "this.setCustomValidity('')"}), required=False)
    sugurta_summasi_soz = forms.CharField(label="Sug'urta summasi (so'z bilan)", required=False)

    # --- TASHKILOT (MCHJ) MA'LUMOTLARI ---
    FILIAL_CHOICES = [
        ('Buxoro filiali', 'Buxoro filiali'),
        #('Samarqand filiali', 'Samarqand filiali'),
        ('Toshkent shahar filiali', 'Toshkent shahar filiali'),
        #('Andijon filiali', 'Andijon filiali'),
        #('Farg\'ona filiali', 'Farg\'ona filiali'),
        #('Namangan filiali', 'Namangan filiali'),
        #('Qashqadaryo filiali', 'Qashqadaryo filiali'),
        #('Surxondaryo filiali', 'Surxondaryo filiali'),
        #('Jizzax filiali', 'Jizzax filiali'),
        ('Navoiy filiali', 'Navoiy filiali'),
        ('Xorazm filiali', 'Xorazm filiali'),
        ("Tortko'l filiali", "Tortko'l filiali"),
    ]
    
    filial_nomi = forms.ChoiceField(label="Filial nomi", choices=FILIAL_CHOICES, initial='Buxoro filiali', widget=forms.Select(attrs={'required': 'required', 'oninvalid': "this.setCustomValidity('Iltimos, ushbu maydonni to\\'ldiring')", 'oninput': "this.setCustomValidity('')"}))
    filial_boshligi = forms.CharField(label="Filial boshlig'i F.I.Sh", initial="IKROMOV B.A.", required=False, widget=forms.TextInput(attrs={'required': 'required', 'oninvalid': "this.setCustomValidity('Iltimos, ushbu maydonni to\\'ldiring')", 'oninput': "this.setCustomValidity('')"}))
    filial_boshligi_inisiali = forms.CharField(label="Filial boshlig'i F.I.Sh (Inisiali)", initial="B.A.IKROMOV", required=False, widget=forms.TextInput(attrs={'style': 'text-transform:uppercase', 'oninput': 'this.value = this.value.toUpperCase(); this.setCustomValidity("")', 'required': 'required', 'oninvalid': "this.setCustomValidity('Iltimos, ushbu maydonni to\\'ldiring')"}))
    
    direktor_fish = forms.CharField(label="Direktor F.I.Sh", initial="OBIDOV ABDULLA SHOKIR O'G'LI", required=False, widget=forms.TextInput(attrs={'readonly': 'readonly', 'required': 'required', 'oninvalid': "this.setCustomValidity('Iltimos, ushbu maydonni to\\'ldiring')", 'oninput': "this.setCustomValidity('')"}))
    direktor_fish_inisiali = forms.CharField(label="Direktor F.I.Sh (Inisiali)", initial="A.SH.OBIDOV", required=False, widget=forms.TextInput(attrs={'readonly': 'readonly', 'required': 'required', 'oninvalid': "this.setCustomValidity('Iltimos, ushbu maydonni to\\'ldiring')", 'oninput': "this.setCustomValidity('')"}))
    
    ishonchnoma_sanasi = forms.DateField(label="Ishonchnoma sanasi", widget=forms.DateInput(attrs={'class': 'date-mask', 'placeholder': 'dd.mm.yyyy', 'required': 'required', 'oninvalid': "this.setCustomValidity('Iltimos, ushbu maydonni to\\'ldiring')", 'oninput': "this.setCustomValidity('')"}), input_formats=['%d.%m.%Y'], required=False)

    # --- GRAFIK (Exceldan nusxa) ---
    grafik_matni = forms.CharField(
        label="Grafik jadvali (Exceldan nusxalab tashlang)", 
        widget=forms.Textarea(attrs={'rows': 10, 'placeholder': "Exceldan jadvalni belgilab, shu yerga tashlang (Ctrl+V)...", 'required': 'required', 'oninvalid': "this.setCustomValidity('Iltimos, ushbu maydonni to\\'ldiring')", 'oninput': "this.setCustomValidity('')"}), 
        required=False,
        help_text="Format: № | Sana | Qoldiq | Asosiy qarz | Foiz | Jami"
    )
    
    # --- MONITORING SANALARI ---
    monitoring_sana_1 = forms.DateField(label="1-monitoring sanasi", widget=forms.DateInput(attrs={'class': 'date-mask', 'placeholder': 'dd.mm.yyyy'}), input_formats=['%d.%m.%Y'], required=False)
    monitoring_sana_2 = forms.DateField(label="2-monitoring sanasi", widget=forms.DateInput(attrs={'class': 'date-mask', 'placeholder': 'dd.mm.yyyy'}), input_formats=['%d.%m.%Y'], required=False)
    monitoring_sana_3 = forms.DateField(label="3-monitoring sanasi", widget=forms.DateInput(attrs={'class': 'date-mask', 'placeholder': 'dd.mm.yyyy'}), input_formats=['%d.%m.%Y'], required=False)
    monitoring_sana_4 = forms.DateField(label="4-monitoring sanasi", widget=forms.DateInput(attrs={'class': 'date-mask', 'placeholder': 'dd.mm.yyyy'}), input_formats=['%d.%m.%Y'], required=False)
