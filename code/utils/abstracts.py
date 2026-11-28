from io import BytesIO
from pathlib import Path
from django.db import models
from django.db.models.base import ModelBase
from django.core.files.base import ContentFile
from PIL import Image, ImageOps
from django_jalali.db import models as jmodels



class WebPImageModel(models.Model):
    """
    Automatically converts uploaded ImageField files to WebP
    and stores only the WebP version.
    """

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        self._convert_images_to_webp()
        super().save(*args, **kwargs)

    def _convert_images_to_webp(self):
        for field in self._meta.local_fields:

            if not isinstance(field, models.ImageField):
                continue

            image_field = getattr(self, field.name, None)

            if not image_field or not image_field.name:
                continue

            # اگر از قبل WebP است، دوباره تبدیل نکن
            if image_field.name.lower().endswith(".webp"):
                continue

            try:
                image_field.open("rb")

                image = Image.open(image_field)
                image = ImageOps.exif_transpose(image)

                # WebP از RGB/RGBA پشتیبانی می‌کند
                if image.mode not in ("RGB", "RGBA"):
                    image = image.convert("RGBA")

                output = BytesIO()
                image.save(output, format="WEBP", quality=88, method=6)
                output.seek(0)

                original_name = image_field.name
                new_name = f"{original_name.rsplit('.', 1)[0]}.webp"

                image_field.save(new_name, ContentFile(output.read()), save=False)

            except Exception as exc:
                print(f"WebP conversion failed: " f"{self.__class__.__name__}.{field.name}: {exc}")

            finally:
                try:
                    image_field.close()
                except Exception:
                    pass



class TimeStamped(models.Model):
    created_at = jmodels.jDateTimeField(verbose_name="ایجاد شده در تاریخ", auto_now_add=True)
    updated_at = jmodels.jDateTimeField(verbose_name="به روز شده در تاریخ", auto_now=True)
 
    class Meta:
        abstract = True
 
 
class Publishable(models.Model):
    is_published = models.BooleanField(verbose_name="منتشر شده", default=True)
 
    class Meta:
        abstract = True

class Orderable(models.Model):
    order = models.PositiveSmallIntegerField(verbose_name="ترتیب", default=0)
    
    class Meta:
        abstract = True

