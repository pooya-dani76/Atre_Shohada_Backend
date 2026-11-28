from django.db import models
from utils.abstracts import TimeStamped


class ContactUs(TimeStamped):
    '''Model representing a contact us message with its details.'''
    
    name = models.CharField(verbose_name="نام", max_length=255)
    email = models.EmailField(verbose_name="ایمیل", blank=True, null=True)
    subject = models.CharField(verbose_name="موضوع", max_length=255)
    message = models.TextField(verbose_name="متن پیام")
    seen = models.BooleanField(verbose_name="دیده شده", default=False)

    def __str__(self):
        return f"Message from {self.name}<{self.email}> - {self.subject}"
    
    class Meta:
        verbose_name = "نظر و پیشنهاد"
        verbose_name_plural = "نظرات و پیشنهادات"
        db_table = "ContactUs"
        ordering = ['-created_at']
