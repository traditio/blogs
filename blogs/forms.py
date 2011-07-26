#coding=utf-8

from django.forms.fields import CharField
from django.forms.models import ModelForm
from blogs.models import BlogPost


class BlogPostForm(ModelForm):

    class Meta:
        model = BlogPost
        fields = ('title', 'content', 'tags')
