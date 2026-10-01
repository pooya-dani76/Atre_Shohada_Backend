import os
import shutil
import tempfile

from django.test import override_settings
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from gallery.models import Gallery
from gallery.paginations import GalleryPagination
from martyr.models import Martyr
from utils.services import get_temp_image
from utils.test_constants import init_test


TEST_MEDIA_ROOT = tempfile.mkdtemp()

GALLERY_PAGE_SIZE = 10
GALLERY_ITEMS_COUNT = 15


@override_settings(MEDIA_ROOT=TEST_MEDIA_ROOT)
class GalleryAPITestCase(APITestCase):

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(TEST_MEDIA_ROOT, ignore_errors=True)
        super().tearDownClass()

    def setUp(self):
        init_test(self)
        self.martyr_1, created = Martyr.objects.get_or_create(
                    first_name="Test Martyr 1",
                    last_name="Test Martyr Last Name 1",
                )
        self.martyr_2, created = Martyr.objects.get_or_create(
                    first_name="Test Martyr 2",
                    last_name="Test Martyr Last Name 2",
                )
        for i in range(GALLERY_ITEMS_COUNT):
            martyr = self.martyr_1 if i < 12 else self.martyr_2
            Gallery.objects.create(
                martyr=martyr,
                description=f"Test Gallery Image {i+1}",
                image=get_temp_image(),
                is_active=True
            )
        self.list_url = reverse('gallery-list')

    def get_gallery_item(self, description):
        return Gallery.objects.get(description=description)


    def test_get_gallery_list(self):
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['data']), GALLERY_PAGE_SIZE)
        self.assertEqual(response.data['count'], GALLERY_ITEMS_COUNT)

    def test_get_gallery_list_with_martyr_filter(self):
        response = self.client.get(self.list_url, {'martyr': self.martyr_1.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['data']), GALLERY_PAGE_SIZE)
        self.assertEqual(response.data['count'], 12)

    def test_get_gallery_list_with_martyr_filter_no_results(self):
        response = self.client.get(self.list_url, {'martyr': 9999})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['data']), 0)
        self.assertEqual(response.data['count'], 0)


    def test_get_gallery_list_with_inactive_martyr(self):
        self.martyr_1.is_active = False
        self.martyr_1.save()
        response = self.client.get(self.list_url, {'martyr': self.martyr_1.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['data']), 0)
        self.assertEqual(response.data['count'], 0)


    def test_get_gallery_list_with_inactive_gallery(self):
        gallery_item = Gallery.objects.filter(martyr=self.martyr_1).first()
        gallery_item.is_active = False
        gallery_item.save()
        response = self.client.get(self.list_url, {'martyr': self.martyr_1.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['data']), GALLERY_PAGE_SIZE)
        self.assertEqual(response.data['count'], 11)


    def test_model_string_representation(self):
        gallery_item = Gallery.objects.first()
        self.assertEqual(str(gallery_item), f"Image for {gallery_item.martyr.first_name} {gallery_item.martyr.last_name}")

    def test_get_gallery_list_message(self):
        response = self.client.get(self.list_url)
        self.assertEqual(response.data['message'], 'gallery items retrieved successfully')

    def test_get_gallery_list_serialized_fields(self):
        response = self.client.get(self.list_url)
        item = response.data['data'][0]
        self.assertEqual(set(item.keys()), {'martyr', 'description', 'image'})
        self.assertNotIn('is_active', item)

    def test_get_gallery_list_returns_absolute_image_url(self):
        response = self.client.get(self.list_url)
        image_url = response.data['data'][0]['image']
        self.assertTrue(image_url.startswith('http://testserver/media/gallery_images/'))

    def test_get_gallery_list_is_ordered_by_newest_first(self):
        response = self.client.get(self.list_url)
        descriptions = [item['description'] for item in response.data['data']]
        self.assertEqual(descriptions[0], f"Test Gallery Image {GALLERY_ITEMS_COUNT}")
        self.assertEqual(
            descriptions,
            [f"Test Gallery Image {i}" for i in range(GALLERY_ITEMS_COUNT, GALLERY_ITEMS_COUNT - GALLERY_PAGE_SIZE, -1)],
        )

    def test_get_gallery_list_pagination(self):
        first_page = self.client.get(self.list_url)
        self.assertEqual(first_page.data['count'], GALLERY_ITEMS_COUNT)
        self.assertEqual(len(first_page.data['data']), GALLERY_PAGE_SIZE)
        self.assertIsNotNone(first_page.data['next'])
        self.assertIsNone(first_page.data['previous'])

        second_page = self.client.get(self.list_url, {'page': 2})
        self.assertEqual(second_page.data['count'], GALLERY_ITEMS_COUNT)
        self.assertEqual(len(second_page.data['data']), GALLERY_ITEMS_COUNT - GALLERY_PAGE_SIZE)
        self.assertIsNone(second_page.data['next'])
        self.assertIsNotNone(second_page.data['previous'])

    def test_get_gallery_list_with_empty_martyr_filter(self):
        response = self.client.get(self.list_url, {'martyr': ''})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], GALLERY_ITEMS_COUNT)

    def test_get_gallery_list_without_gallery_items(self):
        Gallery.objects.all().delete()
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 0)
        self.assertEqual(response.data['data'], [])

    def test_get_gallery_list_when_image_file_is_missing(self):
        gallery_item = self.get_gallery_item(f"Test Gallery Image {GALLERY_ITEMS_COUNT}")
        os.remove(gallery_item.image.path)

        response = self.client.get(self.list_url)
        item = next(
            entry for entry in response.data['data']
            if entry['description'] == f"Test Gallery Image {GALLERY_ITEMS_COUNT}"
        )
        self.assertIsNone(item['image'])

        gallery_item.refresh_from_db()
        # 'image' is not nullable on the model, so the stored name is kept as is
        # (BaseSafeImageSerializer only nulls the response value in that case)
        self.assertTrue(gallery_item.image.name.startswith('gallery_images/'))

    def test_gallery_pagination_configuration(self):
        paginator = GalleryPagination()
        self.assertEqual(paginator.page_size, GALLERY_PAGE_SIZE)
        self.assertEqual(paginator.max_page_size, 100)

    def test_gallery_is_active_by_default(self):
        gallery_item = Gallery.objects.create(
            martyr=self.martyr_2,
            image=get_temp_image(name="test_gallery_default_active.png"),
        )
        self.assertTrue(gallery_item.is_active)

    def test_gallery_related_name_from_martyr(self):
        self.assertEqual(self.martyr_1.gallery.count(), 12)
        self.assertEqual(self.martyr_2.gallery.count(), 3)

    def test_gallery_items_are_deleted_with_martyr(self):
        martyr_2_id = self.martyr_2.id
        self.martyr_2.delete()

        self.assertEqual(Gallery.objects.filter(martyr_id=martyr_2_id).count(), 0)
        self.assertEqual(Gallery.objects.count(), 12)

    def test_gallery_meta_configuration(self):
        self.assertEqual(Gallery._meta.db_table, 'Gallery')
        self.assertEqual(Gallery._meta.ordering, ['-created_at'])
        self.assertEqual(Gallery._meta.verbose_name, 'Image')
        self.assertEqual(Gallery._meta.verbose_name_plural, 'Gallery')
