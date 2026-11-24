from django.db import models
from django_jalali.db import models as jmodels
from django.core.exceptions import ValidationError



class SocialInfo(models.Model):
    telegram = models.URLField(verbose_name="تلگرام", max_length=200, blank=True, null=True)
    whatsapp = models.URLField(verbose_name="واتساپ", max_length=200, blank=True, null=True)
    instagram = models.URLField(verbose_name="اینستاگرام", max_length=200, blank=True, null=True)
    eita = models.URLField(verbose_name="ایتا", max_length=200, blank=True, null=True)
    bale = models.URLField(verbose_name="بله", max_length=200, blank=True, null=True)
    rubika = models.URLField(verbose_name="روبیکا", max_length=200, blank=True, null=True)
    soroush = models.URLField(verbose_name="سروش", max_length=200, blank=True, null=True)
    email = models.EmailField(verbose_name="ایمیل", max_length=254, blank=True, null=True)
    active = models.BooleanField(verbose_name="فعال", default=True)
    created_at = jmodels.jDateTimeField(verbose_name="ایجاد شده", auto_now_add=True)
    updated_at = jmodels.jDateTimeField(verbose_name="به روز رسانی شده", auto_now=True)

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
    
