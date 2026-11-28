from django.db import models
from django.db.models.signals import post_delete
from django.dispatch import receiver

from utils.abstracts import WebPImageModel


@receiver(post_delete)
def delete_model_images(sender, instance, **kwargs):

    if not isinstance(sender, type) or not issubclass(
        sender,
        WebPImageModel
    ):
        return

    if sender._meta.abstract:
        return

    for field in sender._meta.local_fields:

        if not isinstance(field, models.ImageField):
            continue

        image = getattr(instance, field.name, None)

        if image and image.name:
            image.delete(save=False)