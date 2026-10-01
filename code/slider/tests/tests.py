import os
import shutil
import tempfile

from PIL import Image
from django.contrib.admin.sites import AdminSite
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from slider.admin import SliderAdmin, SliderSettingAdmin
from slider.models import Slider, SliderSetting
from utils.services import get_temp_image
from utils.test_constants import init_test


TEST_MEDIA_ROOT = tempfile.mkdtemp()
ADMIN_TEST_MEDIA_ROOT = tempfile.mkdtemp()

MAX_ACTIVE_SLIDERS = 3
SLIDERS_COUNT = 6


def get_temp_transparent_image(name='test_rgba.png'):
    """Creates a temporary transparent (RGBA mode) image"""
    image = Image.new('RGBA', (150, 150), color=(255, 0, 0, 128))
    temp_file = tempfile.NamedTemporaryFile(suffix='.png')
    image.save(temp_file, format='PNG')
    temp_file.seek(0)
    return SimpleUploadedFile(name, temp_file.read(), content_type='image/png')


@override_settings(MEDIA_ROOT=TEST_MEDIA_ROOT)
class SlidersAPITestCase(APITestCase):
    """Tests for the slider list API along with Slider & SliderSetting models"""

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(TEST_MEDIA_ROOT, ignore_errors=True)
        super().tearDownClass()

    def setUp(self):
        init_test(self)
        self.slider_setting = SliderSetting.objects.create(
            max_active_sliders=MAX_ACTIVE_SLIDERS
        )
        self.published_sliders = []
        self.unpublished_sliders = []

        for index in range(SLIDERS_COUNT):
            slider = Slider.objects.create(
                title=f"Test Slider {index}",
                image=get_temp_image(name=f"test_slider_{index}.png"),
                image_alt=f"Test Slider Alt {index}",
                published=index % 2 == 0,
            )

            if slider.published:
                self.published_sliders.append(slider)
            else:
                self.unpublished_sliders.append(slider)

        self.list_url = reverse('slider-list')

    def remove_all_sliders(self):
        Slider.objects.all().delete()

    def set_active_sliders_limit(self, limit):
        self.slider_setting.max_active_sliders = limit
        self.slider_setting.save()

    # --------------------------------------------------- slider list API tests

    def test_get_slider_list(self):
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message'], "Sliders retrieved successfully")
        self.assertEqual(len(response.data['data']), MAX_ACTIVE_SLIDERS)

    def test_get_slider_list_returns_only_published_sliders(self):
        response = self.client.get(self.list_url)
        titles = [item['title'] for item in response.data['data']]

        for slider in self.published_sliders:
            self.assertIn(slider.title, titles)

        for slider in self.unpublished_sliders:
            self.assertNotIn(slider.title, titles)

    def test_get_slider_list_is_ordered_by_newest_first(self):
        response = self.client.get(self.list_url)
        titles = [item['title'] for item in response.data['data']]
        self.assertEqual(titles, ["Test Slider 4", "Test Slider 2", "Test Slider 0"])

    def test_get_slider_list_serialized_fields(self):
        response = self.client.get(self.list_url)
        item = response.data['data'][0]
        self.assertEqual(set(item.keys()), {'id', 'title', 'image', 'image_alt'})

        for excluded_field in ('published', 'created_at', 'updated_at'):
            self.assertNotIn(excluded_field, item)

    def test_get_slider_list_returns_absolute_image_url(self):
        response = self.client.get(self.list_url)
        image_url = response.data['data'][0]['image']
        self.assertTrue(image_url.startswith('http://testserver/media/slider_images/'))
        self.assertTrue(image_url.endswith('.jpg'))

    def test_get_slider_list_when_no_slider_exists(self):
        self.remove_all_sliders()
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['data'], [])

    def test_get_slider_list_with_slider_without_image(self):
        self.set_active_sliders_limit(MAX_ACTIVE_SLIDERS + 1)
        Slider.objects.create(title="Published Without Image", published=True)

        response = self.client.get(self.list_url)
        item = next(
            slider for slider in response.data['data']
            if slider['title'] == "Published Without Image"
        )
        self.assertIsNone(item['image'])

    def test_get_slider_list_when_image_file_is_missing(self):
        slider = self.published_sliders[0]
        os.remove(slider.image.path)

        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        item = next(
            slider_data for slider_data in response.data['data']
            if slider_data['id'] == slider.id
        )
        self.assertIsNone(item['image'])

        slider.refresh_from_db()
        self.assertFalse(slider.image)

    # ------------------------------------------------------ slider model tests

    def test_slider_string_representation(self):
        self.assertEqual(str(self.published_sliders[0]), "Test Slider 0")

    def test_slider_setting_string_representation(self):
        self.assertEqual(str(self.slider_setting), "تنظیمات اسلایدر")

    def test_slider_setting_default_max_active_sliders(self):
        setting = SliderSetting.objects.create()
        self.assertEqual(setting.max_active_sliders, 10)

    def test_slider_without_image_is_saved(self):
        slider = Slider.objects.create(title="Slider Without Image")
        self.assertFalse(slider.image)

    def test_slider_image_is_resized_and_converted_to_jpeg(self):
        slider = Slider.objects.create(
            title="Slider With Processed Image",
            image=get_temp_image(name="test_slider_wide.png"),
        )
        self.assertTrue(slider.image.name.endswith('.jpg'))

        with Image.open(slider.image.path) as image:
            self.assertEqual(image.size, (1920, 600))
            self.assertEqual(image.format, "JPEG")

    def test_slider_transparent_image_is_converted_to_rgb_jpeg(self):
        slider = Slider.objects.create(
            title="Slider With Transparent Image",
            image=get_temp_transparent_image("test_slider_transparent.png"),
        )
        self.assertTrue(slider.image.name.endswith('.jpg'))

        with Image.open(slider.image.path) as image:
            self.assertEqual(image.mode, "RGB")
            self.assertEqual(image.size, (1920, 600))
            self.assertEqual(image.format, "JPEG")

    def test_published_slider_limit_uses_setting_value(self):
        with self.assertRaises(ValidationError) as error:
            Slider.objects.create(title="Extra Published Slider", published=True)

        self.assertIn(f"only {MAX_ACTIVE_SLIDERS} sliders can be active", str(error.exception))
        self.assertEqual(Slider.objects.filter(published=True).count(), MAX_ACTIVE_SLIDERS)

    def test_published_slider_limit_uses_default_when_no_setting_exists(self):
        self.remove_all_sliders()
        SliderSetting.objects.all().delete()

        for index in range(10):
            Slider.objects.create(title=f"Published Slider {index}", published=True)

        with self.assertRaises(ValidationError) as error:
            Slider.objects.create(title="Published Slider 10", published=True)

        self.assertIn("only 10 sliders can be active", str(error.exception))
        self.assertEqual(Slider.objects.filter(published=True).count(), 10)

    def test_unpublished_sliders_do_not_count_towards_limit(self):
        self.remove_all_sliders()
        self.set_active_sliders_limit(1)

        for index in range(3):
            Slider.objects.create(title=f"Unpublished Slider {index}", published=False)

        Slider.objects.create(title="Published Slider 0", published=True)

        with self.assertRaises(ValidationError):
            Slider.objects.create(title="Published Slider 1", published=True)

        self.assertEqual(Slider.objects.filter(published=True).count(), 1)

    def test_saving_published_slider_does_not_count_itself(self):
        self.remove_all_sliders()
        self.set_active_sliders_limit(1)
        slider = Slider.objects.create(title="Published Slider", published=True)

        slider.title = "Published Slider Updated"
        slider.save()
        slider.refresh_from_db()

        self.assertEqual(slider.title, "Published Slider Updated")
        self.assertEqual(Slider.objects.filter(published=True).count(), 1)

    def test_unpublishing_slider_is_allowed_when_limit_is_reached(self):
        self.remove_all_sliders()
        self.set_active_sliders_limit(1)
        slider = Slider.objects.create(title="Published Slider", published=True)

        slider.published = False
        slider.save()
        slider.refresh_from_db()

        self.assertFalse(slider.published)

    def test_slider_meta_configuration(self):
        self.assertEqual(Slider._meta.ordering, ['-created_at'])
        self.assertEqual(Slider._meta.db_table, 'Slider')
        self.assertEqual(SliderSetting._meta.db_table, 'Slider_Setting')


@override_settings(MEDIA_ROOT=ADMIN_TEST_MEDIA_ROOT)
class SliderAdminTestCase(TestCase):
    """Tests for Slider & SliderSetting admin configurations"""

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(ADMIN_TEST_MEDIA_ROOT, ignore_errors=True)
        super().tearDownClass()

    def setUp(self):
        self.site = AdminSite()
        self.slider_admin = SliderAdmin(Slider, self.site)
        self.setting_admin = SliderSettingAdmin(SliderSetting, self.site)

    def test_slider_setting_admin_allows_add_when_no_setting_exists(self):
        self.assertTrue(self.setting_admin.has_add_permission(None))

    def test_slider_setting_admin_denies_add_when_setting_exists(self):
        SliderSetting.objects.create(max_active_sliders=MAX_ACTIVE_SLIDERS)
        self.assertFalse(self.setting_admin.has_add_permission(None))

    def test_slider_setting_admin_list_display(self):
        self.assertEqual(self.setting_admin.list_display, ("max_active_sliders",))

    def test_slider_admin_image_preview_without_image(self):
        slider = Slider.objects.create(title="Slider Without Image")
        self.assertEqual(self.slider_admin.image_preview(slider), "No Image")

    def test_slider_admin_image_preview_with_image(self):
        slider = Slider.objects.create(
            title="Slider With Image",
            image=get_temp_image(name="test_slider_preview.png"),
        )

        preview = self.slider_admin.image_preview(slider)

        self.assertIn(f'<a href="{slider.image.url}"', preview)
        self.assertIn(f'<img src="{slider.image.url}"', preview)

    def test_slider_admin_configuration(self):
        self.assertEqual(self.slider_admin.search_fields, ['title'])
        self.assertEqual(self.slider_admin.list_per_page, 25)
        self.assertEqual(self.slider_admin.list_editable, ("published",))
        self.assertEqual(self.slider_admin.ordering, ['-created_at'])
        self.assertIn("image_preview", self.slider_admin.list_display)
        self.assertIn("published", self.slider_admin.list_display)
        self.assertIn("created_at", self.slider_admin.readonly_fields)
        self.assertIn("updated_at", self.slider_admin.readonly_fields)
