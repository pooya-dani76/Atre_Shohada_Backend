from django.db import models
from django_jalali.db import models as jmodels
from io import BytesIO
from PIL import Image, ImageOps
from django.core.files.base import ContentFile
from django.core.exceptions import ValidationError


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


class Slider(models.Model):
    title = models.CharField("Title", max_length=100)
    image = models.ImageField(verbose_name="Slider image", upload_to="slider_images/", null=True, blank=True)
    image_alt = models.CharField(verbose_name="Image Alt", max_length=50, null=True, blank=True)
    published = models.BooleanField(verbose_name="Published", default=False)
    created_at = jmodels.jDateTimeField(verbose_name="Created At", auto_now=False, auto_now_add=True)
    updated_at = jmodels.jDateTimeField(verbose_name="Updated At", auto_now=True, auto_now_add=False)

    class Meta:
        db_table = 'Slider'
        verbose_name = 'اسلایدر'
        verbose_name_plural = 'اسلایدر‌ها'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.title}'
    
    
    def save(self, *args, **kwargs):
        # if self.image:
        #     image = Image.open(self.image)

        #     target_size = (1920, 600)

        #     image = ImageOps.fit(
        #         image,
        #         target_size,
        #         method=Image.Resampling.LANCZOS,
        #         centering=(0.5, 0.5),
        #     )

        #     if image.mode != "RGB":
        #         image = image.convert("RGB")

        #     output = BytesIO()

        #     image.save(
        #         output,
        #         format="JPEG",
        #         quality=90,
        #         optimize=True,
        #     )

        #     self.image = ContentFile(
        #         output.getvalue(),
        #         name=f"{self.image.name.rsplit('.', 1)[0]}.jpg",
        #     )
        
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
