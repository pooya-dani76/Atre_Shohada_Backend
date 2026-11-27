from io import BytesIO
from pathlib import Path
from django.db import models
from django.db.models.base import ModelBase
from django.core.files.base import ContentFile
from PIL import Image, ImageOps
from rest_framework import serializers



# ------------------------------------------Models------------------------------------------------

class OptimizedImageModelBase(ModelBase):

    def __new__(mcls, name, bases, attrs, **kwargs):

        meta = attrs.get("Meta")
        is_abstract = getattr(meta, "abstract", False)

        if not is_abstract and name != "OptimizedImageModel":

            image_fields = {}

            # بررسی فیلدهای والد بدون استفاده از get_fields
            for base in bases:
                if hasattr(base, "_meta"):
                    for field in base._meta.local_fields:
                        if isinstance(field, models.ImageField):
                            image_fields[field.name] = field

            # بررسی فیلدهای تعریف‌شده در کلاس فعلی
            for field_name, value in attrs.items():
                if isinstance(value, models.ImageField):
                    image_fields[field_name] = value

            # ایجاد خودکار فیلدهای optimized
            for field_name, image_field in image_fields.items():

                optimized_name = f"{field_name}_optimized"

                if optimized_name not in attrs:
                    attrs[optimized_name] = models.ImageField(
                        upload_to="",
                        storage=image_field.storage,
                        blank=True,
                        null=True,
                        editable=False,
                    )

        return super().__new__(mcls, name, bases, attrs, **kwargs)



class OptimizedImageModel(models.Model, metaclass=OptimizedImageModelBase):

    class Meta:
        abstract = True

    def generate_optimized_images(self):

        updated_fields = []

        for field in self._meta.get_fields():

            if not isinstance(field, models.ImageField):
                continue

            if field.name.endswith("_optimized"):
                continue

            original = getattr(self, field.name, None)

            if not original or not original.name:
                continue

            optimized_name = f"{Path(original.name).with_suffix('.webp')}"

            optimized_field_name = f"{field.name}_optimized"
            optimized = getattr(self, optimized_field_name, None)

            storage = field.storage

            # اگر نسخه بهینه وجود دارد و همان فایل قبلی است
            if (
                optimized
                and optimized.name == optimized_name
                and storage.exists(optimized_name)
            ):
                continue

            try:
                with original.open("rb") as source:
                    image = Image.open(source)
                    image = ImageOps.exif_transpose(image)
                    image.load()

                if image.mode not in ("RGB", "RGBA"):
                    image = image.convert(
                        "RGBA" if "transparency" in image.info else "RGB"
                    )

                output = BytesIO()

                image.save(
                    output,
                    format="WEBP",
                    quality=90,
                    method=6,
                )

                output.seek(0)

                # حذف نسخه قدیمی در صورت وجود
                if storage.exists(optimized_name):
                    storage.delete(optimized_name)

                saved_name = storage.save(
                    optimized_name,
                    ContentFile(output.read()),
                )

                setattr(self, optimized_field_name, saved_name)
                updated_fields.append(optimized_field_name)

            except Exception as error:
                print(
                    f"WebP conversion failed: "
                    f"{self.__class__.__name__}.{field.name}: {error}"
                )

        if updated_fields:
            super().save(update_fields=updated_fields)

    def save(self, *args, **kwargs):

        super().save(*args, **kwargs)

        self.generate_optimized_images()





# ------------------------------------------Serializers--------------------------------------------

class OptimizedImageModelSerializer(serializers.ModelSerializer):

    def to_representation(self, instance):

        data = super().to_representation(instance)

        request = self.context.get("request")

        for field in instance._meta.get_fields():

            if not isinstance(field, models.ImageField):
                continue

            if field.name.endswith("_optimized"):
                continue

            optimized = getattr(
                instance,
                f"{field.name}_optimized",
                None,
            )

            if optimized and optimized.name:
                if optimized.storage.exists(optimized.name):

                    url = optimized.url

                    if request:
                        url = request.build_absolute_uri(url)

                    data[field.name] = url

            # مخفی نگه داشتن فیلد داخلی
            data.pop(f"{field.name}_optimized", None)

        return data