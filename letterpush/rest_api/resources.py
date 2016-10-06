"""
REST resources.

We sometimes add rembedded resources in GET responces that cannot be updated
directly by a POST request to the same URL. This is to save a round-trip.
Anything under "related_resources" is not updatable.
"""

from restless.dj import DjangoResource
from restless.preparers import FieldsPreparer

from .models import Article, Image, ImageLink


class RequestError(Exception):
    """Allow to pass custom status in an exception, as Restless expects."""
    def __init__(self, message, status=500):
        super(self.__class__, self).__init__(message)
        self.status = status


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

    def create(self, *args, **kwargs):
        extra_fields = set(self.data) - self.UPDATABLE_FIELDS
        if extra_fields:
            raise RequestError(
                "Cannot accept field(s) %s" % ", ".join(extra_fields),
                status=400)
        thing = self.MODEL(**self.data)
        thing.save()
        return thing

    def delete(self, *args, **kwargs):
        delete_count, _ = self.MODEL.objects.filter(id=kwargs['pk']).delete()
        if delete_count != 1:
            raise RequestError("Got %d objects" % delete_count, status=404)

    def is_authenticated(self):
        return True  # NOTE: for demo / debug purposes.


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

    def prepare(self, instance):
        """Turns a model into a serializable representation."""
        prepared = super(self.__class__, self).prepare(instance)
        return self.add_related(instance, prepared)

    def add_related(self, instance, prepared_data):
        # Embed image resources as nested.
        # Restless does not have a notion of embedded resources.
        img_res = ImageResource()
        prepared_images = {role: map(img_res.prepare, images)
                           for role, images in instance.imagesByRole().items()}
        prepared_data.setdefault("related_resources", {})["images"] = prepared_images
        return prepared_data


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
