from threadedcomments.models import ThreadedComment
from blogs.comments.forms import ThreadedCommentForm


def get_model():
    return ThreadedComment


def get_form():
    return ThreadedCommentForm
