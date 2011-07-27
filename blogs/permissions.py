#coding=utf-8

class BlogPostPermissions(object):

    def __init__(self, post):
        self.post = post

    def can_delete(self, user):
        if user.is_superuser or self.post.blog.author == user:
            return True
        return False

    def can_delete_comments(self, user):
        return self.can_delete(user)
    
    def can_edit(self, user):
        return self.can_delete(user)