from django.db import models
from utils.abstracts import Publishable, TimeStamped, Orderable



class Website(Publishable, TimeStamped, Orderable):
    title = models.CharField(verbose_name="عنوان", max_length=100)
    url = models.URLField(verbose_name="آدرس وبسایت", max_length=200)

    class Meta:
        db_table = 'website'
        verbose_name = 'وب‌سایت'
        verbose_name_plural = 'وب‌سایت‌ها'
        ordering = ['order']

    def __str__(self):
        return f'{self.title}'