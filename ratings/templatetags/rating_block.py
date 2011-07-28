#coding=utf-8
from django import template

from classytags.helpers import InclusionTag
from classytags.core import Tag, Options
from classytags.arguments import Argument

from ratings.models import RatedItem


class RatingBlock(InclusionTag):
    name = 'rating'
    template = 'ratings/rating.html'

    options = Options(
        Argument('obj', required=True),
    )

    def get_context(self, context, obj):
        if not hasattr(obj, '_meta') or not hasattr(obj, 'pk'):
            raise ValueError("Ожидался экземпляр django.models.Model, а получили %s." % type(obj))
        return {
            'content_type': str(obj._meta),
            'obj_pk': obj.pk,
            'score': RatedItem.objects.score_for_obj(obj),
        }


register = template.Library()
register.tag(RatingBlock)