#coding=utf-8
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.db.models.signals import pre_save, post_save
from django.utils.encoding import smart_unicode, smart_str
from django.utils.translation import ugettext_lazy as _
from django.db import models
from django.contrib.contenttypes import generic
from django.core.exceptions import ValidationError

import pytils
from taggit.managers import TaggableManager
from ratings.models import RatedItem
from blogs.permissions import BlogPostPermissions

class BlogManager(models.Manager):

    def get_by_author_slug(self, author, slug):
        try:
            if author is None:
                return self.model.objects.get(author__isnull=True, slug=slug)
            else:
                return self.model.objects.get(author__username=author, slug=slug)
        except:
            return None


class Blog(models.Model):
    author = models.ForeignKey(User, verbose_name=_(u'Владелец блога'), related_name='blogs', blank=True, null=True)
    title = models.CharField(verbose_name=_(u'Заголовок'), max_length=255, validators=[])
    slug = models.CharField(verbose_name=_(u'Слэг'), max_length=255, blank=True, null=False)

    moderators = models.ManyToManyField(User, related_name='moderated_blogs', blank=True)
    created = models.DateTimeField(verbose_name=_(u'Дата создания'), auto_now_add=True)

    objects = BlogManager()

    def __unicode__(self):
        return self.title

    class Meta:
        verbose_name = _(u'блог')
        verbose_name_plural = _(u'блоги')
        unique_together = (('author', 'title'),)

    @classmethod
    def create_slug(cls, instance, raw, using, **kwargs):
        instance.slug = pytils.translit.slugify(instance.title)
        return instance

    def clean(self):
        blogs = self.__class__.objects.filter(author=self.author, title=self.title)[:2]
        if blogs and not (len(blogs) == 1 and blogs[0].pk == self.pk):
            raise ValidationError('У данного автора (%s) уже имеется блог с таким же названием.' % smart_str(self.author))

    def user_can_post(self, user):
        """
        Может ли постить в блог пользователь :user ?
        """
        return True

    @models.permalink
    def get_absolute_url(self):
        if self.author:
            kwargs = dict(slug=self.slug, author=self.author.username)
        else:
            kwargs = dict(slug=self.slug)
        return ('blogs_index', [], kwargs)

pre_save.connect(Blog.create_slug, Blog)


class BlogPost(models.Model):
    blog = models.ForeignKey(Blog, related_name='posts')
    title = models.CharField(max_length=255, blank=True, null=True)
    slug = models.CharField(verbose_name=_(u'Слэг'), max_length=255, unique=True, blank=True, null=False)
    content = models.TextField()

    tags = TaggableManager(blank=True)
    ratings = generic.GenericRelation(RatedItem)
    created = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return self.title or self.content[:255]

    class Meta:
        verbose_name = _(u'пост')
        verbose_name_plural = _(u'посты')


    @classmethod
    def create_slug(cls, instance, raw, created, using, **kwargs):
        """Создать слэг на основе instance.title и записать его в instance.slug"""
        title = getattr(instance, 'title')
        pk = instance.pk
        if title:
            cutted_title = pytils.translit.slugify(smart_unicode(instance.title)[:100])
            words = cutted_title.split('-')
            if len(instance.title) > len(cutted_title):
                words = words[:-1]
            slug = '-'.join([str(instance.pk)] + words)
            slug = smart_unicode(slug)
        else:
            slug = str(pk)
        instance.__class__.objects.filter(pk=pk).update(slug=slug)

    @property
    def permissions(self):
        if not getattr(self, "_permissions_obj", None):
            self._permissions_obj = BlogPostPermissions(self)
        return self._permissions_obj

        
post_save.connect(BlogPost.create_slug, BlogPost)


class BlogSubscription(models.Model):
    user = models.ForeignKey(User)
    blog = models.ForeignKey(Blog)
    created = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return "{0}: {1}".format(self.blog, self.user.username)

    class Meta:
        verbose_name = _(u'подписка')
        verbose_name_plural = _(u'подписки')

