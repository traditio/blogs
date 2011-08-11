#coding=utf-8
from django.contrib.auth.models import User
from django.contrib.comments.signals import comment_was_posted
from django.db.models.expressions import F
from django.db.models.signals import pre_save, post_save, pre_delete
from django.utils.encoding import smart_unicode
from django.utils.translation import ugettext_lazy as _
from django.db import models
from django.contrib.contenttypes import generic
from django.core.exceptions import ValidationError

import pytils
from taggit.managers import TaggableManager
from ratings.models import RatedItem
from blogs.permissions import BlogPostPermissions, BlogPermissions
from comments import get_model
from datetime import datetime
from djangosphinx.models import SphinxSearch
from queryset_transform import TransformManager

class Blog(models.Model):
    author = models.ForeignKey(User, verbose_name=_(u'Владелец блога'), related_name='blogs', blank=True, null=True)
    title = models.CharField(verbose_name=_(u'Заголовок'), max_length=255)
    slug = models.CharField(verbose_name=_(u'Слэг'), max_length=255, db_index=True)

    moderators = models.ManyToManyField(User, related_name='moderated_blogs', blank=True)
    created = models.DateTimeField(verbose_name=_(u'Дата создания'), auto_now_add=True)

    def __unicode__(self):
        return self.title

    class Meta:
        verbose_name = _(u'блог')
        verbose_name_plural = _(u'блоги')
        unique_together = (('author', 'title'),)

    def clean(self):
        if not self.pk and self.__class__.objects.filter(title=self.title).exists():
            raise ValidationError('Уже имеется блог с таким же названием.')

    #noinspection PyUnusedLocal
    @classmethod
    def create_slug(cls, instance, raw, using, **kwargs):
        if instance.slug: return
        instance.slug = pytils.translit.slugify(instance.title)
        if not instance.pk and instance.__class__.objects.filter(slug=instance.slug).exists():
            instance.slug = "{0}-{1}".format(str(instance.pk), instance.slug)
        return instance

    @property
    def permissions(self):
        if not getattr(self, "_permissions_obj", None):
            self._permissions_obj = BlogPermissions(self)
        return self._permissions_obj

    @models.permalink
    def get_absolute_url(self):
        return 'blogs_blog_index', [], dict(slug=self.slug)

pre_save.connect(Blog.create_slug, Blog)


class BlogPost(models.Model):
    author = models.ForeignKey(User, verbose_name=_(u'Автор'))
    blog = models.ForeignKey(Blog, verbose_name=_(u'Блог'), related_name='posts', db_index=True)
    content = models.TextField(verbose_name=_(u'Текст'))

    tags = TaggableManager(verbose_name=_(u'Теги'), blank=True)
    tags_as_str = models.TextField(verbose_name=_(u'Теги в виде строки'))
    ratings = generic.GenericRelation(RatedItem)
    comments = generic.GenericRelation(get_model(), object_id_field='object_pk')
    comments_count = models.PositiveIntegerField(default=0, editable=False)
    created = models.DateTimeField(auto_now=True, verbose_name=u'Дата создания', db_index=True)
    modified = models.DateTimeField(auto_now=True, verbose_name=u'Дата редактирования')

    objects = TransformManager()

    search = SphinxSearch(
        index='posts delta',
        weights={
            'tags_as_str': 1,
            'content': 2,
            },
        mode='SPH_MATCH_ALL',
        rankmode='SPH_RANK_NONE',
    )

    def __unicode__(self):
        return ': '.join([smart_unicode(self.blog), str(self.pk)])

    class Meta:
        verbose_name = _(u'пост')
        verbose_name_plural = _(u'посты')

    @models.permalink
    def get_absolute_url(self):
        return 'blogs_post', [], dict(blog_slug=self.blog.slug, post_pk=self.id)

    @property
    def permissions(self):
        if not getattr(self, "_permissions_obj", None):
            self._permissions_obj = BlogPostPermissions(self)
        return self._permissions_obj

    #noinspection PyUnusedLocal
    @classmethod
    def on_comment_create(cls, instance, raw, created, using, **kwargs):
        if created and instance.content_object.__class__ == cls:
            cls.objects.filter(pk=instance.content_object.pk).update(comments_count=F('comments_count')+1)

    #noinspection PyUnusedLocal
    @classmethod
    def on_comment_delete(cls, instance, using, **kwargs):
        if instance.content_object.__class__ == cls:
            cls.objects.filter(pk=instance.content_object.pk).update(comments_count=F('comments_count')-1)

    @classmethod
    def on_comment_post(cls, comment, request, **kwargs):
        if comment.content_object.__class__ == cls:
            view_time, created = BlogPostView.objects.get_or_create(user=request.user, post=comment.content_object)
            view_time.timestamp = datetime.now()
            view_time.save()

    @classmethod
    def on_delete(cls, instance, using, **kwargs):
        now = datetime.now()
        DeletedPosts.objects.create(post_id=instance.id, deleted_ts=now)

    @classmethod
    def on_save(cls, instance, raw, created, using, **kwargs):
        if instance.__class__ == cls:
            instance.__class__.objects.filter(pk=instance.pk).update(tags_as_str=', '.join((t.name for t in instance.tags.all())))

    def last_view(self, user):
        views = self.last_view_objs.filter(user__id=user.id).order_by('-timestamp')
        if len(views) > 0:
            return views[0].timestamp
        else:
            return datetime.now()

post_save.connect(BlogPost.on_comment_create, sender=get_model())
pre_delete.connect(BlogPost.on_comment_delete, sender=get_model())
post_save.connect(BlogPost.on_save, sender=BlogPost)
pre_delete.connect(BlogPost.on_delete, sender=BlogPost)
comment_was_posted.connect(BlogPost.on_comment_post, sender=get_model())


class BlogSubscription(models.Model):
    user = models.ForeignKey(User)
    blog = models.ForeignKey(Blog)
    created = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return "{0}: {1}".format(self.blog, self.user.username)

    class Meta:
        verbose_name = _(u'подписка')
        verbose_name_plural = _(u'подписки')

        
class BlogPostView(models.Model):
    user = models.ForeignKey(User, db_index=True)
    post = models.ForeignKey(BlogPost, related_name='last_view_objs', db_index=True)
    timestamp = models.DateTimeField(default=datetime.now)

    def __unicode__(self):
        return u'{0} post={1} {2}'.format(smart_unicode(self.user), str(self.post_id), str(self.timestamp))
    
    class Meta:
        verbose_name = _(u'просмотр поста')
        verbose_name_plural = _(u'просмотры постов')

# Модели для SphinxSearch, используемы для дельта-индекса

class UpdatedPosts(models.Model):
    updated_ts = models.DateTimeField(db_index=True)

    class Meta:
        db_table = 'blogs_blogpost_updated'
    

class DeletedPosts(models.Model):
    post_id = models.IntegerField()
    deleted_ts = models.DateTimeField(db_index=True)

    class Meta:
        db_table = 'blogs_blogpost_deleted'

