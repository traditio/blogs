#coding=utf-8
from django import template

from classytags.helpers import InclusionTag
from classytags.core import Tag, Options
from classytags.arguments import Argument

from ratings.models import RatedItem
from blogs.permissions import Permissions

class RatingBlock(InclusionTag):
    name = 'rating'
    template = 'ratings/rating.html'

    options = Options(
        Argument('obj', required=True),
    )

    def get_context(self, context, obj):
        if not hasattr(obj, '_meta') or not hasattr(obj, 'pk'):
            raise ValueError("Ожидался экземпляр django.models.Model, а получили %s." % type(obj))
        can_vote = True
        if 'user' in context and\
           getattr(obj, 'permissions', None) and\
           isinstance(obj.permissions, Permissions) and\
           hasattr(obj.permissions, 'can_vote'):
            can_vote = obj.permissions.can_vote(context['user'])
        return {
            'content_type': str(obj._meta),
            'obj_pk': obj.pk,
            'can_vote': can_vote,
            'score': RatedItem.objects.score_for_obj(obj),
        }


register = template.Library()
register.tag(RatingBlock)