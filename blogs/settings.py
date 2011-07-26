from django.conf import settings

POSTS_PER_PAGE = getattr(settings, 'POSTS_PER_PAGE', 10)
  