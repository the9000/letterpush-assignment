"""
REST resources.
"""

from restless.dj import DjangoResource
from restless.preparers import FieldsPreparer

from .models import Article, Image, ImageLink


class ArticleResource(DjangoResource):
    preparer = FieldsPreparer(fields={
        'id': 'id',
        'title': 'title',
        'body': 'body',
        'created': 'created',
        'updated': 'updated',
    })

    # GET /
    def list(self):
        return Article.objects.all()

    # GET /<pk>/
    def detail(self, pk):
        return Article.objects.get(id=pk)
