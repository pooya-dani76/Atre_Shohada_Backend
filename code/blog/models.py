from django.db import models
from django_ckeditor_5.fields import CKEditor5Field
from django.utils.text import slugify
from django_jalali.db import models as jmodels


class Blog(models.Model):
    title = models.CharField("Title", max_length=100)
    slug = models.SlugField(verbose_name="slug", unique=True)
    summary = models.TextField("Summary", null=True, blank=True)
    content = CKEditor5Field(verbose_name="Content") 
    image = models.ImageField(verbose_name="Blog image", upload_to="blog_images", null=True, blank=True)
    image_alt = models.CharField(verbose_name="Image Alt", max_length=50, null=True, blank=True)
    meta_title = models.CharField(verbose_name="Meta Title", max_length=50, null=True, blank=True)
    meta_description = models.CharField(verbose_name="Meta Description", max_length=200, null=True, blank=True)
    published = models.BooleanField(verbose_name="Published", default=True)
    created_at = jmodels.jDateTimeField(verbose_name="Created At", auto_now=False, auto_now_add=True)
    updated_at = jmodels.jDateTimeField(verbose_name="Updated At", auto_now=True, auto_now_add=False)

    class Meta:
        db_table = 'Blog'
        verbose_name = 'بلاگ'
        verbose_name_plural = 'بلاگ‌ها'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.title}'
    

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title, allow_unicode=True)
            slug = base_slug
            counter = 1
            while Blog.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)  
      

    def clean(self):
        return super().clean()    