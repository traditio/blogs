#coding=utf-8
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseBadRequest
from django.utils.translation import ugettext as _
from django.views.decorators.http import require_http_methods

from ratings.models import RatedItem


@require_http_methods(["GET"])
@login_required
def vote(request):
  content_type = request.GET.get("content_type")
  obj_pk = long(request.GET.get("obj_pk"))
  direction = request.GET.get("direction")
  if direction not in ["up", "down"]:
      return HttpResponseBadRequest(_(u'Направление голосования может быть только "up" или "down".'))
  user = request.user
  app, model = content_type.rsplit('.', 1)
  obj_type = ContentType.objects.get(app_label=app, model=model)
  obj = obj_type.get_object_for_this_type(pk=obj_pk)
  RatedItem.objects.vote(user, obj, direction)
  score = RatedItem.objects.score_for_obj(obj)
  return HttpResponse(str(score))