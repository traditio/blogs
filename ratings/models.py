#coding=utf-8
from django.contrib.auth.models import User
from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic


class RatedItemManager(models.Manager):

    def vote(self, user, object, direction):
        assert direction in ['up', 'down']

    def score_for_obj(self, obj):
        pass


class RatedItem(models.Model):
    user = models.ForeignKey(User) # анонимусы голосовать не могут
    rating = models.IntegerField()
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    content_object = generic.GenericForeignKey('content_type', 'object_id')

    objects = RatedItemManager()

    def __unicode__(self):
        return "{0}: {1}".format(self.user.username, self.rating)