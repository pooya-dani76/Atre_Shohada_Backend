from django.db import models
from django_jalali.db import models as jmodels


class ContactUs(models.Model):
    '''Model representing a contact us message with its details.'''
    
    name = models.CharField(verbose_name="Name", max_length=255)
    email = models.EmailField(verbose_name="Email", blank=True, null=True)
    subject = models.CharField(verbose_name="Subject", max_length=255)
    message = models.TextField(verbose_name="Message")
    seen = models.BooleanField(verbose_name="Is Seen", default=False)
    created_at = jmodels.jDateTimeField(verbose_name="Created At", auto_now_add=True)
    updated_at = jmodels.jDateTimeField(verbose_name="Updated At", auto_now=True)

    def __str__(self):
        return f"Message from {self.name}<{self.email}> - {self.subject}"
    
    class Meta:
        verbose_name = "نظر و پیشنهاد"
        verbose_name_plural = "نظرات و پیشنهادات"
        db_table = "ContactUs"
        ordering = ['-created_at']
