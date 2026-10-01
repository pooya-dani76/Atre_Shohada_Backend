import os
import shutil
import tempfile
import unittest

from django.conf import settings
from django.contrib.admin.sites import AdminSite
from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils.text import slugify
from rest_framework import status
from rest_framework.test import APITestCase

from utils.services import get_temp_image
from utils.test_constants import init_test


BLOG_ENABLED = 'blog' in settings.INSTALLED_APPS
BLOG_SKIP_REASON = (
    "The 'blog' app is disabled: add 'blog' to INSTALLED_APPS and include "
    "'blog.urls' in config/urls.py to run these tests."
)

TEST_MEDIA_ROOT = tempfile.mkdtemp()
ADMIN_TEST_MEDIA_ROOT = tempfile.mkdtemp()

BLOG_PAGE_SIZE = 10
BLOG_ITEMS_COUNT = 12


@unittest.skipUnless(BLOG_ENABLED, BLOG_SKIP_REASON)
@override_settings(MEDIA_ROOT=TEST_MEDIA_ROOT)
class BlogAPITestCase(APITestCase):

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(TEST_MEDIA_ROOT, ignore_errors=True)
        super().tearDownClass()

    def setUp(self):
        from blog.models import Blog

        self.blog_model = Blog
        init_test(self)
        self.blog_1 = Blog.objects.create(
            title="Test Blog 1",
            summary="This is First blog Test",
            content="This is First Blog Content",
            image=get_temp_image(),
        )
        self.blog_2 = Blog.objects.create(
            title="Test Blog 2",
            summary="This is Second blog Test",
            content="This is Second Blog Content",
            image=get_temp_image(),
        )
        self.detail_url = reverse("blog-detail", kwargs={"pk": self.blog_1.pk})
        self.detail_url_not_found = reverse("blog-detail", kwargs={"pk": self.blog_1.pk * 10})
        self.search_url = reverse("blog-search")

    def create_blog(self, title, summary="Test Summary", content="Test Content", **kwargs):
        return self.blog_model.objects.create(
            title=title,
            summary=summary,
            content=content,
            image=get_temp_image(name=f"{slugify(title)}.png"),
            **kwargs,
        )

    # ------------------------------------------------------- blog detail API

    def test_get_blog_successfully(self):
        response = self.client.get(self.detail_url, format="json")
        data = response.json()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(data['summary'], "This is First blog Test")
        self.assertEqual(data['content'], "This is First Blog Content")
        self.assertEqual(data['title'], "Test Blog 1")

    def test_get_blog_serialized_fields(self):
        response = self.client.get(self.detail_url, format="json")
        data = response.json()
        self.assertEqual(
            set(data.keys()),
            {'id', 'title', 'slug', 'summary', 'content', 'image', 'image_alt', 'meta_title', 'meta_description'},
        )
        self.assertNotIn('published', data)
        self.assertNotIn('created_at', data)
        self.assertNotIn('updated_at', data)

    def test_get_blog_slug_is_generated_from_title(self):
        response = self.client.get(self.detail_url, format="json")
        self.assertEqual(response.json()['slug'], 'test-blog-1')

    def test_get_blog_not_found(self):
        response = self.client.get(self.detail_url_not_found, format="json")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_unpublished_blog_not_found(self):
        self.blog_1.published = False
        self.blog_1.save()
        response = self.client.get(self.detail_url, format="json")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_blog_returns_relative_image_url(self):
        response = self.client.get(self.detail_url, format="json")
        image_url = response.json()['image']
        self.assertTrue(image_url.startswith('/media/blog_images/'))

    def test_get_blog_when_image_file_is_missing(self):
        os.remove(self.blog_1.image.path)
        response = self.client.get(self.detail_url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsNone(response.json()['image'])

        self.blog_1.refresh_from_db()
        self.assertFalse(self.blog_1.image)

    # --------------------------------------------------------- blog list API

    def test_get_blog_list(self):
        response = self.client.get(self.search_url, format="json")
        data = response.json()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(data['count'], 2)

    def test_get_blog_list_message(self):
        response = self.client.get(self.search_url, format="json")
        self.assertEqual(response.json()['message'], 'blogs retrieved successfully')

    def test_get_blog_list_excludes_unpublished_blogs(self):
        self.blog_1.published = False
        self.blog_1.save()
        response = self.client.get(self.search_url, format="json")
        data = response.json()
        self.assertEqual(data['count'], 1)
        self.assertEqual(data['data'][0]['title'], "Test Blog 2")

    def test_get_blog_list_is_ordered_by_newest_first(self):
        newest_blog = self.create_blog(title="Newest Test Blog")
        response = self.client.get(self.search_url, format="json")
        self.assertEqual(response.json()['data'][0]['id'], newest_blog.id)

    def test_get_blog_list_when_no_blog_exists(self):
        self.blog_model.objects.all().delete()
        response = self.client.get(self.search_url, format="json")
        data = response.json()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(data['count'], 0)
        self.assertEqual(data['data'], [])

    def test_get_searched_blog_list(self):
        response = self.client.get(self.search_url, {'search': "Second"}, format="json")
        data = response.json()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(data['count'], 1)

    def test_get_searched_blog_list_is_case_insensitive(self):
        response = self.client.get(self.search_url, {'search': "SECOND"}, format="json")
        self.assertEqual(response.json()['count'], 1)

    def test_get_searched_blog_list_by_summary(self):
        blog = self.create_blog(title="Summary Search Blog", summary="Unique Summary Marker")
        response = self.client.get(self.search_url, {'search': "Unique Summary Marker"}, format="json")
        data = response.json()
        self.assertEqual(data['count'], 1)
        self.assertEqual(data['data'][0]['id'], blog.id)

    def test_get_searched_blog_list_by_content(self):
        blog = self.create_blog(title="Content Search Blog", summary="No marker here", content="Unique Content Marker")
        response = self.client.get(self.search_url, {'search': "Unique Content Marker"}, format="json")
        data = response.json()
        self.assertEqual(data['count'], 1)
        self.assertEqual(data['data'][0]['id'], blog.id)

    def test_get_searched_blog_list_with_no_results(self):
        response = self.client.get(self.search_url, {'search': "nothing matches this"}, format="json")
        data = response.json()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(data['count'], 0)
        self.assertEqual(data['data'], [])

    def test_pagination_of_blog_search(self):
        response = self.client.get(self.search_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response_results = response.json()
        self.assertIn('next', response_results)
        self.assertIn('previous', response_results)
        self.assertIn('count', response_results)

    def test_get_blog_list_pagination(self):
        for index in range(BLOG_ITEMS_COUNT - 2):
            self.create_blog(title=f"Test Blog Extra {index}")

        first_page = self.client.get(self.search_url)
        self.assertEqual(first_page.data['count'], BLOG_ITEMS_COUNT)
        self.assertEqual(len(first_page.data['data']), BLOG_PAGE_SIZE)
        self.assertIsNotNone(first_page.data['next'])
        self.assertIsNone(first_page.data['previous'])

        second_page = self.client.get(self.search_url, {'page': 2})
        self.assertEqual(len(second_page.data['data']), BLOG_ITEMS_COUNT - BLOG_PAGE_SIZE)
        self.assertIsNone(second_page.data['next'])
        self.assertIsNotNone(second_page.data['previous'])

    # -------------------------------------------------------------- blog model

    def test_blog_string_representation(self):
        self.assertEqual(str(self.blog_1), "Test Blog 1")

    def test_blog_is_published_by_default(self):
        blog = self.create_blog(title="Default Published Blog")
        self.assertTrue(blog.published)

    def test_blog_slug_is_unique(self):
        duplicate_blog = self.create_blog(title="Test Blog 1")
        self.assertEqual(self.blog_1.slug, 'test-blog-1')
        self.assertEqual(duplicate_blog.slug, 'test-blog-1-1')

    def test_blog_slug_is_not_overwritten_when_provided(self):
        blog = self.create_blog(title="Custom Slug Blog", slug="my-custom-slug")
        self.assertEqual(blog.slug, 'my-custom-slug')

    def test_blog_slug_supports_unicode_title(self):
        blog = self.create_blog(title="خبر مهم")
        self.assertEqual(blog.slug, slugify("خبر مهم", allow_unicode=True))

    def test_blog_meta_configuration(self):
        self.assertEqual(self.blog_model._meta.db_table, 'Blog')
        self.assertEqual(self.blog_model._meta.ordering, ['-created_at'])
        self.assertEqual(self.blog_model._meta.verbose_name, 'بلاگ')
        self.assertEqual(self.blog_model._meta.verbose_name_plural, 'بلاگ‌ها')


@unittest.skipUnless(BLOG_ENABLED, BLOG_SKIP_REASON)
@override_settings(MEDIA_ROOT=ADMIN_TEST_MEDIA_ROOT)
class BlogAdminTestCase(TestCase):
    """Tests for the Blog admin configuration"""

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(ADMIN_TEST_MEDIA_ROOT, ignore_errors=True)
        super().tearDownClass()

    def setUp(self):
        from blog.admin import BlogAdmin
        from blog.models import Blog

        self.site = AdminSite()
        self.blog_admin = BlogAdmin(Blog, self.site)

    def test_blog_admin_configuration(self):
        self.assertEqual(self.blog_admin.list_display, ['title', 'slug', 'published'])
        self.assertEqual(self.blog_admin.list_filter, ['title', 'published'])
        self.assertEqual(self.blog_admin.ordering, ['-created_at'])
        self.assertEqual(self.blog_admin.readonly_fields, ('created_at', 'updated_at', 'slug'))
        self.assertEqual(
            self.blog_admin.fields,
            (
                'title', 'content', 'summary',
                'image', 'image_alt', 'meta_title', 'meta_description',
                'published', 'slug', 'created_at', 'updated_at',
            ),
        )
