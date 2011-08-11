#coding=utf-8
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from django.db.models import Sum
import datetime

class RatedItemManager(models.Manager):

    def _create_vote(self, direction, direction_scores, obj, user):
        self.model.objects.create(
            content_object=obj,
            user=user,
            score=direction_scores[direction],
            created=datetime.datetime.now()
        )

    def vote(self, user, obj, direction):
        """
        Сохранить голос :user за объект :obj
        :direction - 'up' или 'down' (+1 или -1)
        """
        assert direction in ['up', 'down']
        direction_scores = {
            'up': 1,
            'down': -1
        }
        content_type = ContentType.objects.get_for_model(obj)
        try:
            vote = self.model.objects.get(content_type__pk=content_type.id, object_id=obj.id, user=user)
        except ObjectDoesNotExist:
            self._create_vote(direction, direction_scores, obj, user)
        except MultipleObjectsReturned:
            self.model.objects.filter(content_type__pk=content_type.id, object_id=obj.id, user=user).delete()
            self._create_vote(direction, direction_scores, obj, user)
        else:
            vote.score = direction_scores[direction]
            vote.save()

    def score_for_obj(self, obj):
        """Получить рейтинг объекта"""

        if not hasattr(obj, '_cached_rating_score'):
            content_type = ContentType.objects.get_for_model(obj)
            score = self.model.objects\
                    .filter(content_type__id=content_type.id, object_id=obj.id)\
                    .aggregate(Sum('score'))\
                    .get('score__sum') or 0
            return score
        else:
            return obj._cached_rating_score


class RatedItem(models.Model):
    user = models.ForeignKey(User) # анонимусы голосовать не могут
    score = models.IntegerField()
    created = models.DateTimeField(auto_now=True)

    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    content_object = generic.GenericForeignKey('content_type', 'object_id')

    objects = RatedItemManager()

    def __unicode__(self):
        return "{0}: {1}".format(self.user.username, self.rating)