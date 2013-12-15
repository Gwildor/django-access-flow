from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.db import models


class SecuredModel(models.Model):

    class Meta:
        abstract = True

    def check_access(self, actions, user, **kwargs):
        """Execute methods based on iterable of actions.

        Return a list of actions which methods didn't return True, or raise an
        ImproperlyConfigured exception when the required method does not exist.
        """

        if not isinstance(actions, (list, tuple)):
            actions = [actions]

        denied = []
        for action in actions:
            try:
                fn = getattr(self, 'can_{}'.format(action))
            except AttributeError:
                raise ImproperlyConfigured
            else:
                if not fn(user, **kwargs):
                    denied.append(action)

        return denied


class Staff(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL)
    author = models.BooleanField(default=False)
    editor = models.BooleanField(default=False)
    moderator = models.BooleanField(default=False)


class Article(SecuredModel):
    author = models.ForeignKey(settings.AUTH_USER_MODEL)
    title = models.CharField(max_length=255)
    text = models.TextField()
    registered_only = models.BooleanField(default=False)

    @staticmethod
    def can_create(user, **kwargs):
        return user.staff.author

    def can_read(self, user, **kwargs):
        return not self.registered_only or user.is_authenticated()

    def can_edit(self, user, **kwargs):
        return user == self.author or user.staff.editor

    def can_delete(self, user, **kwargs):
        return user == self.author and not self.comments


class Comment(SecuredModel):
    article = models.ForeignKey(Article, related_name='comments')
    author = models.ForeignKey(settings.AUTH_USER_MODEL)
    text = models.TextField()

    @staticmethod
    def can_create(user, **kwargs):
        return user.is_authenticated()

    def can_read(self, user, **kwargs):
        return True

    def can_edit(self, user, **kwargs):
        return user == self.user or user.staff.moderator

    def can_delete(self, user, **kwargs):
        return self.staff.moderator
