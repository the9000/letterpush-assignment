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


class ArticleResource(DjangoResource):
    preparer = FieldsPreparer(fields={  # Bare minimum of properties.
        'id': 'id',
        'title': 'title',
        'body': 'body',
        'created': 'created',
        'updated': 'updated',
    })

    UPDATABLE_FIELDS = set(('title', 'body'))

    def prepare(self, instance):
        """Turns a model into a serializable representation."""
        prepared = super(self.__class__, self).prepare(instance)
        return self.addRelated(instance, prepared)

    def addRelated(self, instance, prepared_data):
        # Embed image resources as nested.
        # Restless does not have a notion of embedded resources.
        img_res = ImageResource()
        prepared_images = {role: map(img_res.prepare, images)
                           for role, images in instance.imagesByRole().items()}
        prepared_data.setdefault("related_resources", {})["images"] = prepared_images
        return prepared_data

    # Dataset for GET articles/
    def list(self):
        return Article.objects.all()

    # Dataset for GET articles/<pk>/
    def detail(self, pk):
        return Article.objects.get(id=pk)

    def create(self, *args, **kwargs):
        extra_fields = set(self.data) - self.UPDATABLE_FIELDS
        if extra_fields:
            raise RequestError(
                "Cannot accept field(s) %s" % ", ".join(extra_fields),
                status=400)
        article = Article(**self.data)
        article.save()
        return article

    def delete(self, *args, **kwargs):
        delete_count, _ = Article.objects.filter(id=kwargs['pk']).delete()
        if delete_count != 1:
            raise RequestError("Got %d objects" % delete_count, status=404)

    def is_authenticated(self):
        return True  # NOTE: for demo / debug purposes.


class ImageResource(DjangoResource):
    preparer = FieldsPreparer(fields={  # Bare minimum of properties.
        'id': 'id',
        'note': 'note',
        'path': 'path',
        'created': 'created',
        'updated': 'updated',
    })

    def list(self):
        return Image.objects.all()
