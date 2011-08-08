#coding=utf-8
#--- Author: Dmitri Patrakov <traditio@gmail.com>
from django.contrib import admin
from django.contrib.contenttypes.generic import GenericStackedInline, GenericTabularInline
from django.contrib.contenttypes.models import ContentType
from django.utils.translation import ugettext_lazy as _


from blogs.models import Blog, BlogPost, BlogSubscription
from blogs.comments import get_model


class PostsInline(admin.TabularInline):
    model = BlogPost
    extra = 0
    max_num = 20
    verbose_name = _(u'пост')
    verbose_name_plural = _(u'посты')


class BlogAdmin(admin.ModelAdmin):
    inlines = (PostsInline,)
    list_display = ('pk', 'title', 'author', 'created',)
    list_display_links = ('pk', 'title',)
    raw_id_fields = ('author', 'moderators')
    readonly_fields = ('slug',)

admin.site.register(Blog, BlogAdmin)


class CommentInline(GenericTabularInline):
    model = get_model()
    ct_fk_field = 'object_pk'
    extra = 0
    max_num = 20
    can_delete = False
    fields = ('user', 'comment', 'is_removed',)
    verbose_name = _(u'комментарий')
    verbose_name_plural = _(u'комментарии')


class BlogPostAdmin(admin.ModelAdmin):
    inlines = (CommentInline,)
    date_hierarchy = 'modified'
    search_fields = ('blog',)
    list_display = ('pk', 'blog', 'author', 'modified', 'comments_num',)
    list_display_links = ('pk',)

admin.site.register(BlogPost, BlogPostAdmin)


class BlogSubscriptionAdmin(admin.ModelAdmin):
    pass

admin.site.register(BlogSubscription, BlogSubscriptionAdmin)
