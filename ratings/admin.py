#coding=utf-8
#--- Author: Dmitri Patrakov <traditio@gmail.com>
from django.contrib import admin

from ratings.models import RatedItem


class RatedItemAdmin(admin.ModelAdmin):
    pass

admin.site.register(RatedItem, RatedItemAdmin)
