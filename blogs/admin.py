#coding=utf-8
#--- Author: Dmitri Patrakov <traditio@gmail.com>
from django.contrib import admin

from blogs.models import Blog, BlogPost, BlogSubscription


class BlogAdmin(admin.ModelAdmin):
    raw_id_fields = ("author", "moderators")
    readonly_fields = ("slug",)
    
admin.site.register(Blog, BlogAdmin)


class BlogPostAdmin(admin.ModelAdmin):
    readonly_fields = ("slug",)

admin.site.register(BlogPost, BlogPostAdmin)


class BlogSubscriptionAdmin(admin.ModelAdmin):
    pass

admin.site.register(BlogSubscription, BlogSubscriptionAdmin)
