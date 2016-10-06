"""
REST resources.

We sometimes add rembedded resources in GET responces that cannot be updated
directly by a POST request to the same URL. This is to save a round-trip.
Anything under "related_resources" is not updatable.
"""

from django.db import IntegrityError

from restless.dj import DjangoResource
from restless.preparers import FieldsPreparer

from .models import Article, Image, ImageLink


class RequestError(Exception):
    """Allow to pass custom status in an exception, as Restless expects."""
    def __init__(self, message, status=500):
        super(self.__class__, self).__init__(message)
        self.status = status


def with_integrity_error_400(func):
    """
    A decorator that raises RequestError(status=400) on IntegrityError.
    On an create / update operation, it's likely bad data, not a server's fault.
    """
    # NOTE: the validation error message ends up being a JSON string.
    # This is not nice, but fixing it is out of scope for now.
    def wrapped(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except IntegrityError as e:
            raise RequestError(str(e), status=400)
    return wrapped


class ModelBasedResource(DjangoResource):

    # Set MODEL to the Django model we're basing off.
    # Set UPDATABLE_FILEDS to a set of names of tields that can be updated.

    # NOTE: creating the preparer from a field list would require a metaclass.
    # Can live without it for now.

    # Dataset for GET <things>/
    def list(self):
        return self.MODEL.objects.all()

    # Dataset for GET <things>/<pk>/
    def detail(self, pk):
        return self.MODEL.objects.get(id=pk)

    def ensure_no_extra_fields(self):
        """Raise a bad request"""
        extra_fields = set(self.data) - self.UPDATABLE_FIELDS
        if extra_fields:
            raise RequestError(
                "Cannot accept field(s) %s" % ", ".join(extra_fields),
                status=400)

    @with_integrity_error_400
    def create(self, *args, **kwargs):
        self.ensure_no_extra_fields()
        thing = self.MODEL(**self.data)
        thing.full_clean()  # Run model's validators.
        thing.save()
        return thing

    @with_integrity_error_400
    def update(self, *args, **kwargs):
        self.ensure_no_extra_fields()
        try:
            thing = self.MODEL.objects.filter(id=kwargs["pk"]).get()
            for attr_name, value in self.data.items():
                setattr(thing, attr_name, value)
            thing.full_clean()  # Run model's validators.
            thing.save()
            return thing
        except self.MODEL.DoesNotExist as e:
            raise RequestError(str(e), status=404)  # Not Found

    @with_integrity_error_400
    def delete(self, *args, **kwargs):
        delete_count, _ = self.MODEL.objects.filter(id=kwargs['pk']).delete()
        if delete_count != 1:
            raise RequestError("Got %d objects" % delete_count, status=404)

    def get_related_data(self, instance):
        """Return a dict of related_data to the object representation."""
        return None  # None means adding nothing.

    def prepare(self, instance):
        """Turns a model into a serializable representation."""
        prepared = super(ModelBasedResource, self).prepare(instance)
        additional = self.get_related_data(instance)
        if additional:
            prepared.setdefault("related_resources", {}).update(additional)
        return prepared

    def is_authenticated(self):
        # NOTE: for demo / debug purposes.
        # self.request is available here so any auth middleware that updates it
        # can be used, and the auth status checked here.
        return True


class ArticleResource(ModelBasedResource):
    MODEL = Article
    UPDATABLE_FIELDS = set(('title', 'body'))
    preparer = FieldsPreparer(fields={
        'id': 'id',
        'title': 'title',
        'body': 'body',
        'created': 'created',
        'updated': 'updated',
    })

    def get_related_data(self, instance):
        return {"image_links": ImageLinkResource.get_from_collection(
            instance.imagelink_set.all())}


class ImageResource(ModelBasedResource):
    MODEL = Image
    UPDATABLE_FIELDS = set(('note', 'path'))
    preparer = FieldsPreparer(fields={  # Bare minimum of properties.
        'id': 'id',
        'note': 'note',
        'path': 'path',
        'created': 'created',
        'updated': 'updated',
    })

    def get_related_data(self, instance):
        return {"image_links": ImageLinkResource.get_from_collection(
            instance.imagelink_set.all())}


class ImageLinkResource(ModelBasedResource):
    MODEL = ImageLink
    UPDATABLE_FIELDS = set(('image_id', 'article_id', 'role'))
    preparer = FieldsPreparer(fields={  # Bare minimum of properties.
        'id': 'id',
        'article_id': 'article_id',
        'image_id': 'image_id',
        'role': 'role',
        'created': 'created',
        'updated': 'updated',
    })

    @classmethod
    def get_from_collection(cls, collection):
        """Returns a list of representations from collection of instances."""
        resource = cls()
        return [resource.prepare(link) for link in collection]
