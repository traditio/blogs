#coding=utf-8
#Author: Dmitri Patrakov <traditio@gmail.com>
#Created at 11.08.11
from django.conf.urls.defaults import *
from django.views.generic.simple import direct_to_template


urlpatterns = patterns('test_jsmvc.views',
    url(r'^$', direct_to_template, dict(template='test_jsmvc/index.html')),
    url(r'^ajax/$', 'num_gen'),
)
