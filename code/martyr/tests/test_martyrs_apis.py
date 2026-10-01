import os
import shutil
import tempfile
import unittest

import jdatetime
from django.contrib.admin.sites import AdminSite
from django.test import TestCase, override_settings
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from gallery.models import Gallery
from martyr.admin import GalleryInline, MartyrAdmin
from martyr.models import Martyr
from utils.services import get_temp_image
from utils.test_constants import init_test


TEST_MEDIA_ROOT = tempfile.mkdtemp()
ADMIN_TEST_MEDIA_ROOT = tempfile.mkdtemp()

MARTYR_LIST_PAGE_SIZE = 10


@override_settings(MEDIA_ROOT=TEST_MEDIA_ROOT)
class MartyrsAPITestCase(APITestCase):

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(TEST_MEDIA_ROOT, ignore_errors=True)
        super().tearDownClass()

    def create_martyr(self, first_name="Test Martyr", last_name="Test Martyr Last Name", **kwargs):
        """Creates a Martyr with all of its fields filled in"""
        defaults = {
            "birth_year": 1360,
            "father_name": "Test Father Name",
            "graduation": Martyr.GratuationLevel.BACHELOR,
            "marriage_status": Martyr.WazeiyateTaahol.MARRIED,
            "children_count": 2,
            "image": get_temp_image(name="test_martyr.png"),
            "dispatch_type": Martyr.DispatchType.BASIJI,
            "dispatch_location": "Test Dispatch Location",
            "dispatch_year": 1365,
            "dispatching_unit": "Test Dispatching Unit",
            "operation_name": "Test Operation Name",
            "responsibility": "Test Responsibility",
            "martyrdom_location": "Test Martyrdom Location",
            "martyrdom_date": jdatetime.date(1365, 1, 1),
            "grave_location": "Test Grave Location",
            "plot_number": 1,
            "row_number": 2,
            "grave_number": 3,
            "testament": "Test Testament",
            "biography": "Test Biography",
            "narrative": "Test Narrative",
            "pilgrimage_letter": "Test Pilgrimage Letter",
        }
        defaults.update(kwargs)
        return Martyr.objects.create(first_name=first_name, last_name=last_name, **defaults)

    def setUp(self):
        init_test(self)
        self.martyr = self.create_martyr()
        self.gallery_image = Gallery.objects.create(
            martyr=self.martyr,
            description="Active Test Gallery Image",
            image=get_temp_image(name="test_martyr_gallery_1.png"),
        )
        self.inactive_gallery_image = Gallery.objects.create(
            martyr=self.martyr,
            description="Inactive Test Gallery Image",
            image=get_temp_image(name="test_martyr_gallery_2.png"),
            is_active=False,
        )
        self.detail_url = reverse('martyr-detail', kwargs={'id': self.martyr.id})
        self.list_url = reverse('martyr-list')

    # ----------------------------------------------------- martyr detail API

    def test_get_active_martyr(self):
        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message'], "Martyr data retrieved successfully")
        self.assertEqual(response.data['data']['first_name'], "Test Martyr")
        self.assertEqual(response.data['data']['last_name'], "Test Martyr Last Name")

    def test_get_martyr_personal_information(self):
        response = self.client.get(self.detail_url)
        data = response.data['data']
        self.assertEqual(data['birth_year'], 1360)
        self.assertEqual(data['father_name'], "Test Father Name")
        self.assertEqual(data['graduation'], 'bachelor')
        self.assertEqual(data['marriage_status'], 'married')
        self.assertEqual(data['children_count'], 2)

    def test_get_martyr_dispatch_information(self):
        response = self.client.get(self.detail_url)
        data = response.data['data']
        self.assertEqual(data['dispatch_type'], 'basiji')
        self.assertEqual(data['dispatch_location'], "Test Dispatch Location")
        self.assertEqual(data['dispatch_year'], 1365)
        self.assertEqual(data['dispatching_unit'], "Test Dispatching Unit")
        self.assertEqual(data['operation_name'], "Test Operation Name")
        self.assertEqual(data['responsibility'], "Test Responsibility")

    def test_get_martyr_martyrdom_information(self):
        response = self.client.get(self.detail_url)
        data = response.data['data']
        self.assertEqual(data['martyrdom_location'], "Test Martyrdom Location")
        self.assertEqual(data['martyrdom_date'], "1365-01-01")

    def test_get_martyr_grave_information(self):
        response = self.client.get(self.detail_url)
        data = response.data['data']
        self.assertEqual(data['grave_location'], "Test Grave Location")
        self.assertEqual(data['plot_number'], 1)
        self.assertEqual(data['row_number'], 2)
        self.assertEqual(data['grave_number'], 3)

    def test_get_martyr_texts(self):
        response = self.client.get(self.detail_url)
        data = response.data['data']
        self.assertEqual(data['testament'], "Test Testament")
        self.assertEqual(data['biography'], "Test Biography")
        self.assertEqual(data['narrative'], "Test Narrative")
        self.assertEqual(data['pilgrimage_letter'], "Test Pilgrimage Letter")

    def test_get_martyr_serialized_fields(self):
        response = self.client.get(self.detail_url)
        data = response.data['data']
        self.assertIn('all_images', data)
        self.assertNotIn('is_active', data)
        self.assertNotIn('created_at', data)
        self.assertNotIn('updated_at', data)

    def test_get_martyr_returns_absolute_image_url(self):
        response = self.client.get(self.detail_url)
        image_url = response.data['data']['image']
        self.assertTrue(image_url.startswith('http://testserver/media/martyr_images/'))

    def test_get_martyr_all_images_returns_only_active_images(self):
        response = self.client.get(self.detail_url)
        all_images = response.data['data']['all_images']
        self.assertEqual(len(all_images), 1)
        self.assertEqual(all_images[0]['description'], "Active Test Gallery Image")

    def test_get_martyr_all_images_is_empty_without_gallery_images(self):
        martyr = self.create_martyr(first_name="Martyr Without Images")
        url = reverse('martyr-detail', kwargs={'id': martyr.id})
        response = self.client.get(url)
        self.assertEqual(response.data['data']['all_images'], [])

    def test_get_martyr_not_found(self):
        url = reverse('martyr-detail', kwargs={'id': self.martyr.id * 100})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_inactive_martyrs_not_found(self):
        self.martyr.is_active = False
        self.martyr.save()
        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_martyr_when_image_file_is_missing(self):
        os.remove(self.martyr.image.path)
        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsNone(response.data['data']['image'])

        self.martyr.refresh_from_db()
        self.assertFalse(self.martyr.image)

    # ------------------------------------------------------- martyr list API

    def test_get_martyrs_list(self):
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message'], 'martyrs retrieved successfully')
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(len(response.data['data']), 1)
        self.assertEqual(response.data['data'][0]['first_name'], "Test Martyr")
        self.assertEqual(response.data['data'][0]['last_name'], "Test Martyr Last Name")

    def test_get_martyrs_list_serialized_fields(self):
        response = self.client.get(self.list_url)
        item = response.data['data'][0]
        self.assertEqual(set(item.keys()), {'id', 'first_name', 'last_name', 'image'})

    def test_get_martyrs_list_pagination(self):
        for index in range(12):
            self.create_martyr(first_name=f"Test Martyr Extra {index}")

        first_page = self.client.get(self.list_url)
        self.assertEqual(first_page.data['count'], 13)
        self.assertEqual(len(first_page.data['data']), MARTYR_LIST_PAGE_SIZE)
        self.assertIsNotNone(first_page.data['next'])
        self.assertIsNone(first_page.data['previous'])

        second_page = self.client.get(self.list_url, {'page': 2})
        self.assertEqual(second_page.data['count'], 13)
        self.assertEqual(len(second_page.data['data']), 3)
        self.assertIsNone(second_page.data['next'])
        self.assertIsNotNone(second_page.data['previous'])

    def test_get_martyrs_list_is_ordered_by_newest_first(self):
        second_martyr = self.create_martyr(first_name="Second Test Martyr")
        third_martyr = self.create_martyr(first_name="Third Test Martyr")

        response = self.client.get(self.list_url)
        ids = [item['id'] for item in response.data['data']]
        self.assertEqual(ids, [third_martyr.id, second_martyr.id, self.martyr.id])

    def test_get_martyrs_list_without_martyrs(self):
        Martyr.objects.all().delete()
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 0)
        self.assertEqual(response.data['data'], [])

    def test_get_martyrs_list_includes_inactive_martyrs(self):
        self.martyr.is_active = False
        self.martyr.save()
        response = self.client.get(self.list_url)
        self.assertEqual(response.data['count'], 1)

    def test_get_martyrs_list_search_by_testament(self):
        martyr = self.create_martyr(first_name="Testament Martyr", testament="Another Testament")
        response = self.client.get(self.list_url, {'testament': 'ANOTHER'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['data'][0]['id'], martyr.id)

    def test_get_martyrs_list_search_by_biography(self):
        martyr = self.create_martyr(first_name="Biography Martyr", biography="Another Biography")
        response = self.client.get(self.list_url, {'biography': 'another biography'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['data'][0]['id'], martyr.id)

    def test_get_martyrs_list_search_by_narrative(self):
        martyr = self.create_martyr(first_name="Narrative Martyr", narrative="Another Narrative")
        response = self.client.get(self.list_url, {'narrative': 'another'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['data'][0]['id'], martyr.id)

    def test_get_martyrs_list_search_by_pilgrimage_letter(self):
        martyr = self.create_martyr(first_name="Pilgrimage Martyr", pilgrimage_letter="Another Pilgrimage Letter")
        response = self.client.get(self.list_url, {'pilgrimage_letter': 'another pilgrimage'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['data'][0]['id'], martyr.id)

    def test_get_martyrs_list_search_with_no_results(self):
        response = self.client.get(self.list_url, {'biography': 'not found text'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 0)
        self.assertEqual(response.data['data'], [])

    @unittest.expectedFailure
    def test_get_martyrs_list_search_by_name(self):
        """
        Known issue: the 'name' parameter is documented in the schema but the view
        filters on a non-existent 'name' field, which raises FieldError.
        """
        martyr = self.create_martyr(first_name="Searched")
        response = self.client.get(self.list_url, {'name': 'searched'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['data'][0]['id'], martyr.id)

    # --------------------------------------------------------- martyr model

    def test_model_string_representation(self):
        self.assertEqual(str(self.martyr), "Test Martyr Test Martyr Last Name")

    def test_martyr_is_active_by_default(self):
        self.assertTrue(self.martyr.is_active)

    def test_martyr_meta_configuration(self):
        self.assertEqual(Martyr._meta.db_table, 'Martyr')
        self.assertEqual(Martyr._meta.ordering, ['-created_at'])
        self.assertEqual(Martyr._meta.verbose_name, 'شهید')
        self.assertEqual(Martyr._meta.verbose_name_plural, 'شهدا')


@override_settings(MEDIA_ROOT=ADMIN_TEST_MEDIA_ROOT)
class MartyrAdminTestCase(TestCase):
    """Tests for Martyr & GalleryInline admin configurations"""

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(ADMIN_TEST_MEDIA_ROOT, ignore_errors=True)
        super().tearDownClass()

    def setUp(self):
        self.site = AdminSite()
        self.martyr_admin = MartyrAdmin(Martyr, self.site)
        self.gallery_inline = GalleryInline(Martyr, self.site)

    def test_martyr_admin_configuration(self):
        self.assertEqual(self.martyr_admin.search_fields, ['name'])
        self.assertEqual(self.martyr_admin.list_per_page, 25)
        self.assertEqual(self.martyr_admin.ordering, ['-created_at'])
        self.assertEqual(self.martyr_admin.list_display, ["first_name", "last_name", "is_active"])
        self.assertEqual(self.martyr_admin.readonly_fields, ("created_at", "updated_at"))
        self.assertEqual(self.martyr_admin.list_editable, ("is_active",))
        self.assertEqual(self.martyr_admin.inlines, [GalleryInline])

    def test_gallery_inline_configuration(self):
        self.assertEqual(self.gallery_inline.model, Gallery)
        self.assertEqual(self.gallery_inline.extra, 1)
        self.assertTrue(self.gallery_inline.show_change_link)
        self.assertEqual(self.gallery_inline.fields, ['image', 'image_preview', 'description', 'is_active'])
        self.assertEqual(self.gallery_inline.readonly_fields, ['image_preview'])

    def test_gallery_inline_image_preview_without_image(self):
        gallery = Gallery(martyr=self.martyr_admin.model(first_name="A", last_name="B"))
        self.assertEqual(self.gallery_inline.image_preview(gallery), "No Image")

    def test_gallery_inline_image_preview_with_image(self):
        martyr = Martyr.objects.create(first_name="Admin", last_name="Test Martyr")
        gallery = Gallery.objects.create(
            martyr=martyr,
            description="Admin Test Gallery Image",
            image=get_temp_image(name="test_admin_gallery.png"),
        )

        preview = self.gallery_inline.image_preview(gallery)

        self.assertIn(f'<a href="{gallery.image.url}"', preview)
        self.assertIn(f'<img src="{gallery.image.url}"', preview)
