#coding: utf-8
import os
from django.contrib.auth.models import User
from django.db import models
from django.db.models import fields
from users.models import UserProfile

class Clips(models.Model):

    PREMIER_NO = 0
    PREMIER_YES = 1

    PREMIER = (
        (PREMIER_NO, 'No'),
        (PREMIER_YES, 'Yes'),
    )

    title = models.CharField(max_length=255, db_index=True)
    id_parsing = models.CharField(max_length=255, blank=True, null=True)
    thumb = models.CharField(max_length=255)
    link_youtube = models.CharField(max_length=255, blank=True, null=True)
    year = models.CharField(max_length=4, blank=True, null=True)
    date_create = models.DateTimeField(auto_now_add=True)
    date_update = models.DateTimeField(auto_now=True)
    likes = models.IntegerField(default=0)
    views = models.IntegerField(default=0)
    tags = models.CharField(max_length=255, blank=True, null=True)
    link_download = models.CharField(max_length=255)
    premier = models.IntegerField(choices=PREMIER, default=PREMIER_NO)
    count_comments = models.IntegerField(default=0)
    artist = models.CharField(max_length=255, blank=True, null=True)
    song = models.CharField(max_length=255, blank=True, null=True)
    moderated = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False)

    def __unicode__(self):
        return "%s - %s" % (self.id, self.title)

class UsersClips(models.Model):

    user = models.ForeignKey(User, blank=True, null=True)
    clip = models.ForeignKey(Clips)

class FavouritesClips(models.Model):

    user = models.IntegerField()
    clip = models.IntegerField()
    date_create = models.DateTimeField(auto_now_add=True)
    date_update = models.DateTimeField(auto_now=True)

class Premier(models.Model):

    title = models.CharField(max_length=255)
    id_parsing = models.CharField(max_length=255)
    thumb = models.CharField(max_length=255)
    link_youtube = models.CharField(max_length=255, blank=True, null=True)
    year = models.CharField(max_length=4, blank=True, null=True)
    date_create = models.DateTimeField(auto_now_add=True)
    date_update = models.DateTimeField(auto_now=True)
    likes = models.IntegerField(default=0)
    views = models.IntegerField(default=0)
    tags = models.CharField(max_length=255, blank=True, null=True)
    link_download = models.CharField(max_length=255)

class Comments(models.Model):

    clip = models.ForeignKey(Clips)
    author = models.ForeignKey(User)
    text = models.TextField(max_length=255)
    date_create = models.DateTimeField(auto_now_add=True)
    likes = models.IntegerField(default=0)
    is_deleted = models.BooleanField(default=False)

class LastItem(models.Model):

    last_page = models.IntegerField(max_length=50)
    last_clip = models.CharField(max_length=50)
    all_pages = models.IntegerField(max_length=50)

class CommentsLikes(models.Model):

    comment = models.ForeignKey(Comments)
    user = models.ForeignKey(User)
    like = models.IntegerField(default=1)

class ClipsLikes(models.Model):

    clip = models.ForeignKey(Clips)
    user = models.ForeignKey(User)
    like = models.IntegerField(default=1)

class PrivateMessages(models.Model):

    from_user = models.ForeignKey(UserProfile)
    to_user = models.ForeignKey(User)
    subject = models.CharField(max_length=255)
    message = models.CharField(max_length=255)
    date_create = models.DateTimeField(auto_now_add=True)
    is_deleted = models.BooleanField(default=False)
    unique = models.IntegerField()

class AnswerMessages(models.Model):

    message = models.ForeignKey(PrivateMessages)
    author = models.ForeignKey(User)
    date_create = models.DateTimeField(auto_now_add=True)
    text = models.CharField(max_length=255)
    is_deleted = models.BooleanField(default=False)

class Emails(models.Model):

    EMAIL_STATUS_NOT_SENT = 1
    EMAIL_STATUS_SENT = 2

    EMAILS_STATUSES = (
        (EMAIL_STATUS_NOT_SENT, 'Not sent'),
        (EMAIL_STATUS_SENT, 'Sent'),
        )

    email_to = fields.CharField(max_length=255, null=False)
    subject = fields.CharField(max_length=255, null=False)
    html = fields.TextField(null=False, blank=True)
    status = fields.IntegerField(default=EMAIL_STATUS_NOT_SENT, choices=EMAILS_STATUSES)
    date = fields.DateTimeField(auto_now=True)

    def __unicode__(self):
        return self.subject

    class Meta:
        db_table = "emails"

class EmailTemplate(models.Model):

    title = fields.CharField(max_length=255, null=False, unique=True)
    subject = fields.CharField(max_length=255, null=False)
    body = fields.TextField()

    def __unicode__(self):
        return self.title

    class Meta:
        db_table = 'email_templates'

class BrokenClips(models.Model):

    STATUS_BROKEN = 0
    STATUS_DELETE = 1
    STATUS_NORMAL = 2

    STATUSES = (
        (STATUS_BROKEN, 'Broken'),
        (STATUS_DELETE, 'Delete'),
        (STATUS_NORMAL, 'Back to normal'),
    )

    clip = models.ForeignKey(Clips)
    status = models.IntegerField(choices=STATUSES, default=STATUS_BROKEN)
    date_create = models.DateTimeField(auto_now_add=True)
    date_update = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'broken_clips'

class ModerateClips(models.Model):

    clip = models.ForeignKey(Clips)
    moderated = models.BooleanField(default=False)
    date_create = models.DateTimeField(auto_now_add=True)
    date_update = models.DateTimeField(auto_now=True)
    email = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False)

    class Meta:
        db_table = 'moderate_clips'

class Statistic(models.Model):

    user = models.ForeignKey(User, blank=True, null=True)
    HTTP_ACCEPT_LANGUAGE = models.CharField(max_length=255, null=True, blank=True)
    HTTP_HOST = models.CharField(max_length=255, null=True, blank=True)
    HTTP_REFERER = models.CharField(max_length=255, null=True, blank=True)
    HTTP_USER_AGENT = models.CharField(max_length=255, null=True, blank=True)
    REMOTE_ADDR = models.CharField(max_length=255, null=True, blank=True)
    date_create = models.DateTimeField(auto_now_add=True)
    date_update = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'statistic'