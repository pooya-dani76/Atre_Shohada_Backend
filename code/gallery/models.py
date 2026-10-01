from django.db import models
from martyr.models import Martyr
from django_jalali.db import models as jmodels

class Gallery(models.Model):
    '''Model representing a Gallery with its name, description, and image.'''
    
    martyr = models.ForeignKey(Martyr, verbose_name="Associated Martyr", on_delete=models.CASCADE, related_name='gallery')
    description = models.TextField(verbose_name="Description of the Gallery", null=True, blank=True)
    image = models.ImageField(verbose_name="Gallery Image", upload_to='gallery_images/')
    is_active = models.BooleanField(verbose_name="Is Active", default=True)
    created_at = jmodels.jDateTimeField(verbose_name="Created At", auto_now_add=True)
    updated_at = jmodels.jDateTimeField(verbose_name="Updated At", auto_now=True)

    def __str__(self):
        return f"Image for {self.martyr.first_name} {self.martyr.last_name}"
    
    class Meta:
        verbose_name = "Image"
        verbose_name_plural = "Gallery"
        db_table = "Gallery"
        ordering = ['-created_at']