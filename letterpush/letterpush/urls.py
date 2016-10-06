"""letterpush URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import patterns, url, include
from django.contrib import admin

from rest_api import resources


urlpatterns = [
    url(r'^admin/', admin.site.urls),  # Retained to easily inspect the DB.
    url(r'^api/articles/', include(resources.ArticleResource.urls())),
    url(r'^api/images/', include(resources.ImageResource.urls())),
    url(r'^api/image_links/', include(resources.ImageLinkResource.urls())),
]
