from blogs.comments.forms import ThreadedCommentForm
from blogs.comments.models import ThreadedCommentWithPermissions


def get_model():
    return ThreadedCommentWithPermissions


def get_form():
    return ThreadedCommentForm
