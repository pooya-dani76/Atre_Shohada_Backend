from django.db import models
from django_jalali.db import models as jmodels
from django.core.exceptions import ValidationError
from utils.abstracts import OptimizedImageModel


class SliderSetting(models.Model):
    max_active_sliders = models.PositiveIntegerField(
        default=10,
        verbose_name="حداکثر اسلایدر فعال",
    )
    
    class Meta:
        db_table = 'Slider_Setting'
        verbose_name = "تنظیمات اسلایدر"
        verbose_name_plural = "تنظیمات اسلایدر"

    def __str__(self):
        return "تنظیمات اسلایدر"


class Slider(OptimizedImageModel):
    title = models.CharField("Title", max_length=100)
    image = models.ImageField(verbose_name="عکس اسلایدر", upload_to="slider_images/", null=True, blank=True)
    image_alt = models.CharField(verbose_name="Alt عکس", max_length=50, null=True, blank=True)
    published = models.BooleanField(verbose_name="انتشار", default=False)
    created_at = jmodels.jDateTimeField(verbose_name="ایجاد شده", auto_now=False, auto_now_add=True)
    updated_at = jmodels.jDateTimeField(verbose_name="به روز رسانی شده", auto_now=True, auto_now_add=False)

    class Meta:
        db_table = 'Slider'
        verbose_name = 'اسلایدر'
        verbose_name_plural = 'اسلایدر‌ها'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.title}'
    
    
    def save(self, *args, **kwargs):
        if self.published:
            setting = SliderSetting.objects.first()

            max_active = (
                setting.max_active_sliders
                if setting
                else 10
            )

            active_count = (
                Slider.objects
                .filter(published=True)
                .exclude(pk=self.pk)
                .count()
            )

            if active_count >= max_active:
                raise ValidationError(f"only {max_active} sliders can be active at the same time.")

        super().save(*args, **kwargs)
