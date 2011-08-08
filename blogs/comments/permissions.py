#coding=utf-8
from blogs.permissions import Permissions


class CommentPermissions(Permissions):

    def __init__(self, comment):
        self.comment = comment

    def can_vote(self, user):
        if user == self.comment.user:
            return False
        return True