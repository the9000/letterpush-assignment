"""
REST resources.
"""

from restless.dj import DjangoResource
from restless.preparers import FieldsPreparer

from .models import Article, Image, ImageLink


class ArticleResource(DjangoResource):
    preparer = FieldsPreparer(fields={  # Bare minimum of properties.
        'id': 'id',
        'title': 'title',
        'body': 'body',
        'created': 'created',
        'updated': 'updated',
    })

    def prepare(self, inatance):
        """Turns a model into a serializable representation."""
        prepared = super(self.__class__, self).prepare(inatance)
        # Embed image resources as nested.
        img_res = ImageResource()
        prepared_images = {role: map(img_res.prepare, images)
                           for role, images in inatance.imagesByRole().items()}
        prepared["images"] = prepared_images
        return prepared

    # GET /
    def list(self):
        return Article.objects.all()

    # GET /<pk>/
    def detail(self, pk):
        return Article.objects.get(id=pk)


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
