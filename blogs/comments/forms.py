#coding=utf-8
import datetime

from django.contrib.comments.forms import   CommentDetailsForm
from django.contrib.contenttypes.models import ContentType
from django.forms.widgets import PasswordInput
from django.utils.encoding import force_unicode
from django import forms
from django.conf import settings
from django.utils.translation import ugettext_lazy as _

from blogs.comments.models import ThreadedCommentWithPermissions


class ShortCommentDetailsForm(CommentDetailsForm):
    """
    Handles the specific details of the comment (name, comment, etc.).
    """

    def get_comment_create_data(self):
        """
        Returns the dict of data to be used to create a comment. Subclasses in
        custom comment apps that override get_comment_model can override this
        method to add extra fields onto a custom comment model.
        """
        return dict(
            content_type=ContentType.objects.get_for_model(self.target_object),
            object_pk=force_unicode(self.target_object._get_pk_val()),
            user_name='',
            comment=self.cleaned_data["comment"],
            submit_date=datetime.datetime.now(),
            site_id=settings.SITE_ID,
            is_public=True,
            is_removed=False,
            )


    def check_for_duplicate_comment(self, new):
        """
        Check that a submitted comment isn't a duplicate. This might be caused
        by someone posting a comment twice. If it is a dup, silently return the *previous* comment.
        """
        possible_duplicates = self.get_comment_model()._default_manager.using(
            self.target_object._state.db
        ).filter(
            content_type=new.content_type,
            object_pk=new.object_pk,
            user_name=new.user_name,
            )
        for old in possible_duplicates:
            if old.submit_date.date() == new.submit_date.date() and old.comment == new.comment:
                return old

        return new


class HiddenCharField(forms.CharField):


    display_none = True

    def __init__(self, max_length=None, min_length=None, *args, **kwargs):
        super(HiddenCharField, self).__init__(max_length, min_length, *args, **kwargs)
        self.display_none = True



    def widget_attrs(self, widget):
        attrs = {'style': 'display: none;'}
        if self.max_length is not None and isinstance(widget, (forms.TextInput, forms.PasswordInput)):
            # The HTML attribute is maxlength, not max_length.
            attrs.update({'maxlength': str(self.max_length)})
        return attrs


class ShortCommentForm(ShortCommentDetailsForm):

    honeypot = HiddenCharField(required=False,
                               label=_('If you enter anything in this field '\
                                       'your comment will be treated as spam'))

    def clean_honeypot(self):
        """Check that nothing's been entered into the honeypot."""
        value = self.cleaned_data["honeypot"]
        if value:
            raise forms.ValidationError(self.fields["honeypot"].label)
        return value


class ThreadedCommentForm(ShortCommentForm):
    parent = forms.IntegerField(required=False, widget=forms.HiddenInput)

    def __init__(self, target_object, parent=None, data=None, initial=None):
        for f in ['email', 'url', 'name']:
            self.base_fields.pop(f, None)
        self.parent = parent
        if initial is None:
            initial = {}
        initial.update({'parent': self.parent})
        super(ThreadedCommentForm, self).__init__(target_object, data=data,
                                                  initial=initial)

    def get_comment_model(self):
        return ThreadedCommentWithPermissions

    def get_comment_create_data(self):
        d = super(ThreadedCommentForm, self).get_comment_create_data()
        d['parent_id'] = self.cleaned_data['parent']
        return d

