#coding=utf-8
from datetime import datetime

from django.contrib.comments.forms import  COMMENT_MAX_LENGTH, CommentDetailsForm
from django.contrib.contenttypes.models import ContentType
from django.conf import settings
from django.utils.encoding import force_unicode
from django.utils.translation import ugettext as _
from django.forms.models import ModelForm
from django import forms

from blogs.models import BlogPost


class BlogPostForm(ModelForm):
    class Meta:
        model = BlogPost
        fields = ('content', 'tags')
