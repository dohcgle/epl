from django.contrib import admin
from django.apps import apps

# document_processor ilovasidagi barcha modellarni olish
app_models = apps.get_app_config('document_processor').get_models()

for model in app_models:
    try:
        # Agar model allaqachon ro'yxatdan o'tgan bo'lsa, uni chiqarib yuboramiz
        admin.site.unregister(model)
    except admin.sites.NotRegistered:
        pass

    # Dinamik tarzda Admin klassini yaratish
    @admin.register(model)
    class DynamicAdmin(admin.ModelAdmin):
        # Barcha fieldlarni (many-to-many dan tashqari) list_display ga qo'shish,
        # JSON mallumotlari xunuk qib tashlamasligi u-n "payload" olinmaydi
        list_display = [
            field.name for field in model._meta.fields 
            if field.name != 'payload'
        ]
        # Qidiruv maydonlarini aniqlash (faqat CharField va TextField uchun)
        search_fields = [
            field.name for field in model._meta.fields 
            if field.get_internal_type() in ['CharField', 'TextField']
        ]
        # Filterlar (faqat Boolean, Date va Choice bo'lganlar uchun)
        list_filter = [
            field.name for field in model._meta.fields 
            if field.get_internal_type() in ['BooleanField', 'DateField', 'DateTimeField'] or getattr(field, 'choices', None)
        ]
