from django.db import models
from django_jalali.db import models as jmodels
from django.core.exceptions import ValidationError



class SocialInfo(models.Model):
    telegram = models.URLField(verbose_name="Telegram", max_length=200, blank=True, null=True)
    whatsapp = models.URLField(verbose_name="WhatsApp", max_length=200, blank=True, null=True)
    instagram = models.URLField(verbose_name="Instagram", max_length=200, blank=True, null=True)
    eita = models.URLField(verbose_name="Eita", max_length=200, blank=True, null=True)
    bale = models.URLField(verbose_name="Bale", max_length=200, blank=True, null=True)
    rubika = models.URLField(verbose_name="Rubika", max_length=200, blank=True, null=True)
    soroush = models.URLField(verbose_name="Soroush", max_length=200, blank=True, null=True)
    email = models.EmailField(verbose_name="Email", max_length=254, blank=True, null=True)
    active = models.BooleanField(verbose_name="Active", default=True)
    created_at = jmodels.jDateTimeField(verbose_name="Created At", auto_now_add=True)
    updated_at = jmodels.jDateTimeField(verbose_name="Updated At", auto_now=True)

    class Meta:
        verbose_name = 'شبکه اجتماعی'
        verbose_name_plural = 'شبکه‌های اجتماعی'
        db_table = "SocialInfo"
        ordering = ['-created_at'] 
        
        
    def __str__(self):
        return f"Social Info - {self.email}" if self.email else "Social Info"    
        
        
    def save(self, *args, **kwargs):
        social_exists = SocialInfo.objects.exclude(pk=self.pk).exists()

        if social_exists:
            raise ValidationError("Only one instance of SocialInfo is allowed")

        super().save(*args, **kwargs)        
    
