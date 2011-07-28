#coding=utf-8
#--- Author: Dmitri Patrakov <traditio@gmail.com>
from django.conf.urls.defaults import *

urlpatterns = patterns('ratings.views',
    url('^vote/$', 'vote', name='ratings_vote'),
)
