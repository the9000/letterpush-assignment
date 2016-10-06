"""Tests representing the use cases."""

import json

from django.test import TestCase
from django.test.client import RequestFactory

from . import resources


class RestTestMixin(object):

    # Set RESOURCE to the resource class for testing.
    # Set EXPECTED_FIELDS to a set of filed names to expect in the object.
    # set BASE_URI to the expected for the resource (e.g. '/articles/').

    # We use it to generate unique values.
    # NOTE: If we run tests in parallel, we should use a Thread.local().
    _counter = 0

    @classmethod
    def unique_int(cls):
        value = cls._counter
        cls._counter += 1
        return value

    @classmethod
    def unique_string(cls, prefix=''):
        return prefix + str(cls.unique_int())

    @classmethod
    def make_data(cls):
        # We could use factories, etc, but it would make the code even longer.
        raise NotImplementedError("Return a dict of fields to update or create")

    def _request(self, method, path, data, view_type, view_kwargs):
        body = json.dumps(data) if data is not None else ''
        req_factory = RequestFactory()
        req = req_factory.generic(method, path, body,
                                  content_type='application/json')
        response = self.RESOURCE.as_view(view_type)(req, **view_kwargs)
        raw_content = response.getvalue()
        content = json.loads(raw_content) if raw_content else None
        return (response.status_code, content)

    def request_list(self, method, data=None):
        return self._request(method, self.BASE_URI, data, 'list', {})

    def request_detail(self, method, pk, data=None):
        return self._request(method, self.BASE_URI + str(pk) + '/', data,
                             'detail', {'pk': pk})

    def assert_requred_fields_present(self, content):
        self.assertIsNotNone(content)
        fields = set(content)  # we assume it's a dict.
        self.assertEquals(self.EXPECTED_FIELDS, fields)

    def test_post_creates_record(self):
        data = self.make_data()
        status, content = self.request_list('POST', data)
        self.assertEquals(201, status, (status, content))  # Created.
        self.assert_requred_fields_present(content)

    def test_get_accesses_record_list(self):
        data = self.make_data()
        instance = self.RESOURCE.MODEL(**data)
        instance.save()  # Have at least one
        status, content = self.request_list('GET')
        self.assertEquals(200, status, (status, content))
        self.assertGreater(len(content["objects"]), 0)
        self.assert_requred_fields_present(content["objects"][0])

    def test_get_accesses_specific_record(self):
        data = self.make_data()
        instance = self.RESOURCE.MODEL(**data)
        instance.save()  # Have at least one
        status, content = self.request_detail('GET', instance.id)
        self.assertEquals(200, status, (status, content))
        self.assert_requred_fields_present(content)
        known_subset = {name: content[name] for name in data}
        self.assertEquals(data, known_subset)

    def test_delete_removes_specific_record(self):
        data = self.make_data()
        instance = self.RESOURCE.MODEL(**data)
        instance.save()  # Have at least one
        status, content = self.request_detail('DELETE', instance.id)
        self.assertEquals(204, status, (status, content))  # Deleted.
        self.assertIsNone(content)
        self.assertFalse(self.RESOURCE.MODEL.objects.filter(
            id=instance.id).exists())

    def test_put_updates_specific_record(self):
        data = self.make_data()
        instance = self.RESOURCE.MODEL(**data)
        instance.save()  # Have at least one
        new_data = self.make_data()  # Guaranteed to differ.
        status, content = self.request_detail('PUT', instance.id, new_data)
        self.assertEquals(202, status, (status, content))  # Updated.
        known_subset = {name: content[name] for name in new_data}
        self.assertEquals(new_data, known_subset)
        self.assertNotEquals(data, known_subset)


class ImageTest(RestTestMixin, TestCase):
    RESOURCE = resources.ImageResource
    EXPECTED_FIELDS = set((
        'path', 'note', 'id', 'created', 'updated', 'related_resources'))
    BASE_URI = '/images/'

    @classmethod
    def make_data(cls):
        return {"path": cls.unique_string('path/'),
                "note": cls.unique_string('note-'),
        }


class ArticleTest(RestTestMixin, TestCase):
    RESOURCE = resources.ArticleResource
    EXPECTED_FIELDS = set((
        'title', 'body', 'id', 'created', 'updated', 'related_resources'))
    BASE_URI = '/images/'

    @classmethod
    def make_data(cls):
        return {"title": cls.unique_string('TITLE '),
                "body": cls.unique_string('Once upon a time, '),
        }


class ImageLinkTest(RestTestMixin, TestCase):
    RESOURCE = resources.ImageLinkResource
    EXPECTED_FIELDS = set((
        'image_id', 'article_id', 'role', 'id', 'created', 'updated'))
    BASE_URI = '/images/'

    @classmethod
    def make_data(self, **kwargs):
        # We have to create an image and an article first.
        # We have no factories, so we directly reuse sister tests here.
        image = resources.ImageResource.MODEL(**ImageTest.make_data())
        image.save()
        article = resources.ArticleResource.MODEL(**ArticleTest.make_data())
        article.save()
        return {"image_id": image.id,
                "article_id": article.id,
                'role': kwargs.pop('role', 'L'),
        }
