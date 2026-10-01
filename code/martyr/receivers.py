from django.db.models.signals import post_delete, pre_save
from django.dispatch import receiver

from .models import Martyr


@receiver(pre_save, sender=Martyr)
def delete_old_images_on_change(sender, instance, **kwargs):
    """
    Delete old image files when image or cover_image is changed.
    """
    if not instance.pk:
        return

    try:
        old_instance = Martyr.objects.get(pk=instance.pk)
    except Martyr.DoesNotExist:
        return

    for field_name in ["image", "cover_image", "identity_image"]:
        old_image = getattr(old_instance, field_name)
        new_image = getattr(instance, field_name)

        if old_image and old_image != new_image:
            old_image.delete(save=False)


@receiver(post_delete, sender=Martyr)
def delete_martyr_images(sender, instance, **kwargs):
    """
    Delete image files when Martyr instance is deleted.
    """
    for field_name in ["image", "cover_image", "identity_image"]:
        image = getattr(instance, field_name)

        if image:
            image.delete(save=False)