from django.db import models
from django_jalali.db import models as jmodels
from utils.abstracts import WebPImageModel
from utils.abstracts import Publishable, TimeStamped



class MarriageStatus(models.TextChoices):
        SINGLE = 'single', 'مجرد'
        MARRIED = 'married', 'متأهل'

class DispatchType(models.TextChoices):
    SARBAZ = 'sarbaz', 'سرباز'
    BASIJI = 'basiji', 'بسیجی'
    PASDAR = 'pasdar', 'پاسدار'
    KARMAND = 'karmand', 'کارمند'
    DAAVTALAB = 'davtalab', 'داوطلب'
    MARDOMI = 'mardomi', 'مردمی'
    MARZBAN = 'marzban', 'مرزبان'
    ROUHANI = 'rouhani', 'روحانی'
    ARTESHI = 'arteshi', 'ارتشی'
    
class GraduationLevel(models.TextChoices):
    BELOW_DIPLOMA = 'below_diploma', 'زیر دیپلم'
    DIPLOMA = 'diploma', 'دیپلم'
    ASSOCIATE = 'associate', 'فوق دیپلم'
    BACHELOR = 'bachelor', 'لیسانس'
    MASTER = 'master', 'فوق لیسانس'
    PHD = 'phd', 'دکترا'  
    POST_DOCTORAL = 'post_doctoral', 'فوق دکترا'
    HOZAVI = 'hozavi', 'حوزوی'
    

class MartyrCategory(models.TextChoices):
    RAMADAN = 'ramadan', 'شهید جنگ رمضان',
    TWELVE_DAYS = 'twelve', 'شهید دوازده روزه'
    HOLY_DEFENSE = 'holy_defense', 'شهید دفاع مقدس'
    SECYRITY = 'security', 'شهید امنیت'
    AUTHORITY = 'authority', 'شهید اقتدار'
    
     


class Martyr(WebPImageModel, Publishable, TimeStamped):
    '''Model representing a Martyr with their information, testament, biography, and narrative.'''
    
    # Martyr's personal information
    first_name = models.CharField(verbose_name="نام شهید", max_length=255)
    last_name = models.CharField(verbose_name="نام خانوادگی شهید", max_length=255)
    birth_year = models.PositiveSmallIntegerField(verbose_name='سال تولد', null=True, blank=True)
    father_name = models.CharField(verbose_name="نام پدر شهید", max_length=255, null=True, blank=True)
    graduation = models.CharField(verbose_name="تحصیلات شهید", choices=GraduationLevel.choices, max_length=20, null=True, blank=True)
    marriage_status = models.CharField(verbose_name="وضعیت تاهل شهید", choices=MarriageStatus.choices, max_length=20, null=True, blank=True)
    children_count = models.PositiveIntegerField(verbose_name="تعداد فرزندان شهید", null=True, blank=True)
    image = models.ImageField(verbose_name="تصویر شهید", upload_to='martyr_images/', null=True, blank=True)
    cover_image = models.ImageField(verbose_name="تصویر کاوری شهید", upload_to='martyr_cover_images/', null=True, blank=True)
    identity_image = models.ImageField(verbose_name="تصویر شناسنامه شهید", upload_to='martyr_identity_images/', null=True, blank=True)
    category = models.CharField(verbose_name='دسته بندی', max_length=20, choices=MartyrCategory.choices, null=True, blank=True)
    
    # Martyr's dispatch information
    dispatch_type = models.CharField(verbose_name='نوع اعزام', max_length=20, choices=DispatchType.choices, null=True, blank=True)
    dispatch_location = models.CharField(verbose_name='محل اعزام', max_length=150, null=True, blank=True)
    dispatch_year = models.PositiveSmallIntegerField(verbose_name='تاریخ اعزام', null=True, blank=True)
    dispatching_unit = models.CharField(verbose_name='یگان اعزام کننده', max_length=100, null=True, blank=True)
    operation_name = models.CharField(verbose_name='نام عملیات', max_length=150, null=True, blank=True)
    responsibility = models.CharField(verbose_name='مسئولیت', max_length=100, null=True, blank=True)
    
    # Martyr's martyrdom information
    martyrdom_location = models.CharField(verbose_name='محل شهادت', max_length=150, null=True, blank=True)
    martyrdom_date = jmodels.jDateField(verbose_name="تاریخ شهادت", auto_now=False, auto_now_add=False, null=True, blank=True)
    
    # Martyr's grave information
    grave_location = models.CharField(verbose_name='مشخصات مزار', max_length=200, null=True, blank=True)
    plot_number = models.PositiveIntegerField(verbose_name='قطعه', null=True, blank=True)
    row_number = models.PositiveSmallIntegerField(verbose_name='ردیف', null=True, blank=True)
    grave_number = models.PositiveSmallIntegerField(verbose_name='شماره', null=True, blank=True)

    testament = models.TextField(verbose_name="وصیت نامه", null=True, blank=True)
    biography = models.TextField(verbose_name="زندگینامه", null=True, blank=True)
    narrative = models.TextField(verbose_name="روایت نامه", null=True, blank=True)

    def __str__(self):
        '''Return the name of the Martyr for display purposes.'''
        return f"{self.first_name} {self.last_name}"  
    
    class Meta:
        verbose_name = 'شهید'
        verbose_name_plural = 'شهدا'
        db_table = "Martyr"
        ordering = ['-created_at']       
        unique_together = ('first_name', 'last_name')
