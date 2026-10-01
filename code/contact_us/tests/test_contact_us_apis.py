from django.contrib.admin.sites import AdminSite
from django.test import RequestFactory, TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from contact_us.admin import ContactUsAdmin
from contact_us.models import ContactUs
from utils.test_constants import init_test


class ContactAPITestCase(APITestCase):

    def setUp(self):
        init_test(self)
        self.contact, created = ContactUs.objects.get_or_create(
            name="John Doe",
            email="test@test.com",
            subject="Test Subject",
            message="This is a test message."
        )
        self.url = reverse('contact-us')

        self.create_success_data = {
            "name": "Jane Smith",
            "email": "new_test@test.com",
            "subject": "Inquiry",
            "message": "I would like to know more about your services."
        }

        self.create_without_email_data = {
            "name": "Jane Smith",
            "subject": "Inquiry",
            "message": "I would like to know more about your services."
        }

        self.create_empty_email_data = {
            "name": "Jane Smith",
            "email": "",
            "subject": "Inquiry",
            "message": "I would like to know more about your services."
        }

        self.create_invalid_email_data = {
            "name": "Jane Smith",
            "email": "invalid-email",
            "subject": "Inquiry",
            "message": "I would like to know more about your services."
        }

        self.create_whitespace_data = {
            "name": "   ",
            "email": "   ",
            "subject": "   ",
            "message": "   "
        }

    def test_create_contact_form(self):
        response = self.client.post(self.url, self.create_success_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(ContactUs.objects.count(), 2)
        self.assertEqual(ContactUs.objects.latest('created_at').name, "Jane Smith")

    def test_create_contact_form_response_payload(self):
        response = self.client.post(self.url, self.create_success_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(
            set(response.data.keys()),
            {'id', 'name', 'email', 'subject', 'message', 'seen', 'created_at'},
        )
        self.assertEqual(response.data['name'], "Jane Smith")
        self.assertEqual(response.data['email'], "new_test@test.com")
        self.assertEqual(response.data['subject'], "Inquiry")
        self.assertEqual(response.data['message'], "I would like to know more about your services.")
        self.assertFalse(response.data['seen'])

    def test_create_contact_form_without_email(self):
        """'email' is optional on the model (blank=True, null=True)"""
        response = self.client.post(self.url, self.create_without_email_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIsNone(ContactUs.objects.latest('created_at').email)

    def test_create_contact_form_with_empty_email(self):
        response = self.client.post(self.url, self.create_empty_email_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['email'], '')

    def test_create_contact_form_invalid_email(self):
        response = self.client.post(self.url, self.create_invalid_email_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('email', response.data)

    def test_create_contact_form_empty_payload(self):
        response = self.client.post(self.url, {}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('name', response.data)
        self.assertIn('subject', response.data)
        self.assertIn('message', response.data)
        # 'email' is optional, so it must not be reported as a required field
        self.assertNotIn('email', response.data)

    def test_create_contact_form_whitespace_fields(self):
        response = self.client.post(self.url, self.create_whitespace_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('name', response.data)
        self.assertIn('subject', response.data)
        self.assertIn('message', response.data)
        self.assertNotIn('email', response.data)

    def test_create_contact_form_whitespace_email(self):
        payload = dict(self.create_success_data, email="   ")
        response = self.client.post(self.url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['email'], '')

    def test_create_contact_form_ignores_read_only_fields(self):
        payload = dict(
            self.create_success_data,
            id=999,
            created_at="1400-01-01T00:00:00+03:30",
        )
        response = self.client.post(self.url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertNotEqual(response.data['id'], 999)
        self.assertNotEqual(response.data['created_at'], "1400-01-01T00:00:00+03:30")
        self.assertEqual(ContactUs.objects.latest('created_at').id, response.data['id'])

    def test_create_contact_form_accepts_seen_field(self):
        """Note: 'seen' is currently writable through the public API"""
        payload = dict(self.create_success_data, seen=True)
        response = self.client.post(self.url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(ContactUs.objects.latest('created_at').seen)

    # ---------------------------------------------------- contact us model

    def test_model_string_representation(self):
        self.assertEqual(str(self.contact), f"Message from {self.contact.name}<{self.contact.email}> - {self.contact.subject}")

    def test_model_string_representation_without_email(self):
        message = ContactUs.objects.create(name="No Email", subject="Test Subject", message="Test Message")
        self.assertEqual(str(message), "Message from No Email<None> - Test Subject")

    def test_contact_us_is_not_seen_by_default(self):
        message = ContactUs.objects.create(name="Unseen", subject="Test Subject", message="Test Message")
        self.assertFalse(message.seen)

    def test_contact_us_ordering_is_newest_first(self):
        newest_message = ContactUs.objects.create(name="Newest", subject="Test Subject", message="Test Message")
        self.assertEqual(ContactUs.objects.first().id, newest_message.id)

    def test_contact_us_meta_configuration(self):
        self.assertEqual(ContactUs._meta.db_table, 'ContactUs')
        self.assertEqual(ContactUs._meta.ordering, ['-created_at'])
        self.assertEqual(ContactUs._meta.verbose_name, "نظر و پیشنهاد")
        self.assertEqual(ContactUs._meta.verbose_name_plural, "نظرات و پیشنهادات")


class ContactUsAdminTestCase(TestCase):
    """Tests for the ContactUs admin configuration"""

    def setUp(self):
        self.site = AdminSite()
        self.contact_admin = ContactUsAdmin(ContactUs, self.site)
        self.request = RequestFactory().get('/admin/contact_us/contactus/')
        self.message = ContactUs.objects.create(
            name="Admin Test",
            subject="Admin Test Subject",
            message="Admin Test Message",
        )

    def test_contact_us_admin_configuration(self):
        self.assertEqual(self.contact_admin.list_display, ["name", "email", "subject", "seen"])
        self.assertEqual(self.contact_admin.list_filter, ['seen'])
        self.assertEqual(self.contact_admin.ordering, ['-created_at'])
        self.assertEqual(
            self.contact_admin.readonly_fields,
            ("name", "email", "subject", "message", "seen", "created_at", "updated_at"),
        )

    def test_contact_us_admin_denies_add_permission(self):
        self.assertFalse(self.contact_admin.has_add_permission(self.request))

    def test_contact_us_admin_denies_delete_permission(self):
        self.assertFalse(self.contact_admin.has_delete_permission(self.request))

    def test_contact_us_admin_get_object_marks_message_as_seen(self):
        self.assertFalse(self.message.seen)

        message_object = self.contact_admin.get_object(self.request, str(self.message.id))

        self.assertIsNotNone(message_object)
        self.message.refresh_from_db()
        self.assertTrue(self.message.seen)

    def test_contact_us_admin_get_object_keeps_seen_message_unchanged(self):
        self.message.seen = True
        self.message.save()

        message_object = self.contact_admin.get_object(self.request, str(self.message.id))

        self.assertTrue(message_object.seen)
