#coding=utf-8
#Author: Dmitri Patrakov <traditio@gmail.com>
#Created at 01.08.11
from annoying.functions import get_object_or_None
from django import template
from django.contrib.auth.models import User
from blogs.models import BlogPostView, BlogPost

register = template.Library()


def new_comments_count(post, user):
    if not isinstance(post, BlogPost) or not isinstance(user, User):
        raise ValueError
    view = get_object_or_None(BlogPostView, post=post, user=user)
    if view is None:
        return post.comments_count
    else:
        return post.comments.filter(submit_date__gte=view.timestamp).count()

register.filter('new_comments_count', new_comments_count)