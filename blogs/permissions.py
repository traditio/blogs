#coding=utf-8

class Permissions(object):
    """Абстрактный класс прав для моделей"""
    

class BlogPostPermissions(Permissions):

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

    def can_vote(self, user):
        if user == self.post.author:
            return False
        return True

    
class BlogPermissions(Permissions):

    def __init__(self, blog):
        self.blog = blog

    def can_post(self, user):
        """
        Может ли постить в блог пользователь :user ?
        """
        return self.blog.author == None or self.blog.author == user