#coding=utf-8
#Author: Dmitri Patrakov <traditio@gmail.com>
#Created at 08.08.11
from threadedcomments.models import ThreadedComment
from blogs.comments.permissions import CommentPermissions


class ThreadedCommentWithPermissions(ThreadedComment):

    @property
    def permissions(self):
        if not getattr(self, "_permissions_obj", None):
            self._permissions_obj = CommentPermissions(self)
        return self._permissions_obj
