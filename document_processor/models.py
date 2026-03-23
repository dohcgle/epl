from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

# ==========================================
# 7. WIZARD YORDAMIDA YIG'ILGAN YAXLIT DATA
# ==========================================
class LoanWizardApplication(models.Model):
    STATUS_CHOICES = [
        ('new', 'Yangi'),
        ('pending_moderator', 'Moderatorga yuborilgan'),
        ('approved_moderator', 'Moderator tasdiqlagan'),
        ('approved_director', 'Direktor tasdiqlagan (Yakunlangan)'),
        ('rejected', 'Rad etilgan'),
    ]

    data = models.JSONField("Barcha to'plangan ma'lumotlar (JSON)", null=True, blank=True)
    
    # Qidirish qulay bo'lishi uchun ayrim meta ma'lumotlar
    client_name = models.CharField("Mijoz F.I.Sh", max_length=255, blank=True, null=True)
    loan_amount = models.BigIntegerField("Kredit summasi", blank=True, null=True)
    
    status = models.CharField("Holat", max_length=50, choices=STATUS_CHOICES, default='new')
    
    # Operator (Kim yaratgan)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='wizard_created', verbose_name="Operator")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Moderator (Kim tasdiqlagan)
    moderator_approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='wizard_moderated', verbose_name="Moderator")
    moderator_approved_at = models.DateTimeField("Moderator tasdiqlagan vaqt", null=True, blank=True)

    # Direktor (Kim yakuniy imzo qo'ygan)
    director_approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='wizard_directed', verbose_name="Direktor")
    director_approved_at = models.DateTimeField("Direktor tasdiqlagan vaqt", null=True, blank=True)

    class Meta:
        verbose_name = "Wizard Arizasi"
        verbose_name_plural = "Wizard Arizalari"
        ordering = ['-created_at']

    def __str__(self):
        return f"Wizard #{self.id} - {self.client_name or 'Noma`lum'}"
