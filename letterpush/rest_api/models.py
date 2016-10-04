from __future__ import unicode_literals

from collections import namedtuple

from django.db import models

# Create your models here.


class DateTrackingModel(models.Model):
    """Adds commom .created and .updated fields."""
    class Meta:
        abstract = True
    created = models.DateTimeField(auto_now_add=True, blank=True)
    updated = models.DateTimeField(auto_now=True, blank=True)


class Article(DateTrackingModel):
    """Stores an individual article."""
    title = models.CharField(max_length=200)
    # NOTE: in a real project, body would be stored differently.
    body = models.CharField(max_length=2000)

    def imagesByRole(self):
        """
        Eagerly load and group images as a dict keyed by role.
        Ignores link info except the role name.
        """
        links = {role: [] for role in ImageLink.ROLES}
        role_label = dict(ImageLink.ROLE_CHOICES)  # Map .role value to label.
        for image_link in self.imagelink_set.all().prefetch_related("image"):
            links[role_label[image_link.role]].append(image_link.image)
        return links



class Image(DateTrackingModel):
    """Stores an image meta info."""
    note = models.CharField(max_length=200)
    path = models.CharField(max_length=200, unique=True,
                            help_text="Part on top of /static/images")
    # TODO: Add filesystem access methods.


class ImageLink(DateTrackingModel):
    """Stores a link between an image and an article (M:N)."""
    ROLE_CHOICES = (
        ("G", "gallery"),
        ("L", "lead"),
        ("S", "social"),
    )
    # Role choices as a nicer enum-like object: e.g. ROLES.gallery == "G".
    ROLES = namedtuple('enum', [name for name, _ in ROLE_CHOICES])(
        *[value for _, value in ROLE_CHOICES])
    image = models.ForeignKey(Image, on_delete=models.PROTECT)
    article = models.ForeignKey(Article, on_delete=models.PROTECT)
    role = models.CharField(max_length=1, choices=ROLE_CHOICES)
