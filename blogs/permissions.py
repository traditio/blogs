#coding=utf-8

class BlogPostPermissions(object):

    def __init__(self, post):
        self.post = post

    def can_delete(self, user):
        if user.is_superuser or self.post.blog.author == user:
            return True
        return False