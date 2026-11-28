from django.db import models
from martyr.models import Martyr
from utils.abstracts import WebPImageModel
from utils.abstracts import Publishable, TimeStamped


class Gallery(WebPImageModel, Publishable, TimeStamped):
    '''Model representing a Gallery with its name, description, and image.'''
    
    martyr = models.ForeignKey(Martyr, verbose_name="شهید", on_delete=models.CASCADE, related_name='gallery')
    description = models.TextField(verbose_name="توضیحات", null=True, blank=True)
    image = models.ImageField(verbose_name="عکس", upload_to='gallery_images/')

    def __str__(self):
        return f"Image for {self.martyr.first_name} {self.martyr.last_name}"
    
    class Meta:
        verbose_name = "Image"
        verbose_name_plural = "Gallery"
        db_table = "Gallery"
        ordering = ['-created_at']