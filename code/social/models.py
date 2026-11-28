from django.db import models
from django.core.exceptions import ValidationError
from utils.abstracts import TimeStamped



class SocialInfo(TimeStamped):
    telegram = models.URLField(verbose_name="تلگرام", max_length=200, blank=True, null=True)
    whatsapp = models.URLField(verbose_name="واتساپ", max_length=200, blank=True, null=True)
    instagram = models.URLField(verbose_name="اینستاگرام", max_length=200, blank=True, null=True)
    eita = models.URLField(verbose_name="ایتا", max_length=200, blank=True, null=True)
    bale = models.URLField(verbose_name="بله", max_length=200, blank=True, null=True)
    rubika = models.URLField(verbose_name="روبیکا", max_length=200, blank=True, null=True)
    soroush = models.URLField(verbose_name="سروش", max_length=200, blank=True, null=True)
    email = models.EmailField(verbose_name="ایمیل", max_length=254, blank=True, null=True)

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
    
