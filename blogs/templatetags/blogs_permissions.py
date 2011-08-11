#coding=utf-8
#Author: Dmitri Patrakov <traditio@gmail.com>
#Created at 01.08.11
#coding=utf-8
from django import template
from blogs.models import BlogPost
from django.contrib.auth.models import User, AnonymousUser

register = template.Library()

def _can_vote_for_post(user, post):
    if not isinstance(post, BlogPost):
        raise ValueError
    if user.id == post.author_id:
        return False
    return True


def can_vote_for(user, obj):
    if not isinstance(user, (User, AnonymousUser)):
        raise ValueError
    accepted_objs_types = {
        BlogPost: _can_vote_for_post
    }
    if obj.__class__ not in accepted_objs_types.keys():
        raise ValueError
    return accepted_objs_types[obj.__class__](user, obj)
register.filter('can_vote_for', can_vote_for)


def can_post_to(user, blog):
    return blog.permissions.can_post(user)
register.filter('can_post_to', can_post_to)
