from django.contrib import admin
from django.contrib.auth.models import User
from clips.models import Emails, Clips, EmailTemplate, BrokenClips, UserProfile, FavouritesClips, Comments, ModerateClips, Statistic

class EmailsAdmin(admin.ModelAdmin):
    list_display = ('email_to', 'format_date', 'subject', 'status')
    list_filter = ('status',)
    search_fields = ('email_to', 'subject')
    date_hierarchy = 'date'

    def format_date(self, obj):
        return obj.date.strftime('%Y-%m-%d %H:%M')
    format_date.short_description = 'Date'
    format_date.allow_tags = True

class ClipsAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'artist', 'song', 'link_youtube', 'format_date', 'likes', 'views', 'tags', 'premier', 'moderated')
    list_filter = ('premier',)
    search_fields = ('id', 'title')
    date_hierarchy = 'date_create'

    def format_date(self, obj):
        return obj.date_create.strftime('%Y-%m-%d %H:%M')
    format_date.short_description = 'Date Create'
    format_date.allow_tags = True

class EmailTemplateAdmin(admin.ModelAdmin):
    list_display = ('title', 'subject')
    search_fields = ('title', 'subject')

class BrokenClipsAdmin(admin.ModelAdmin):
    list_display = ('clip', 'clip_details', 'check', 'status')
    search_fields = ('clip__title', 'clip__artist', 'clip__song', 'clip__tags')
    list_filter = ('status',)

    def check(self, obj):
        return '<a href="/clip/%s" target="_blank">check clip</a>' % obj.clip.id
    check.short_description = 'Check clip'
    check.allow_tags = True

    def clip_details(self, obj):
        return '<strong><a href="/admin/clips/clips/%s/" target="_blank">%s</a></strong>' % (obj.clip.id, obj.clip.title)
    clip_details.short_description = 'Clip details'
    clip_details.allow_tags = True

class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'email', 'gender', 'subscribe', 'is_active')
    list_filter = ('user__is_active', 'user__is_superuser', 'gender', 'subscribe')
    search_fields = ('user__first_name', 'user__email')

    def first_name(self, obj):
        return obj.user.first_name
    def is_active(self, obj):
        return obj.user.is_active
    def email(self, obj):
        return obj.user.email

class FavouritesClipsAdmin(admin.ModelAdmin):
    list_display = ('user', 'username', 'clip', 'clip_title', 'check', 'format_date')
    search_fields = ('clip__title', 'clip__artist', 'clip__song', 'clip__tags', 'user__first_name', 'user__email')

    def username(self, obj):
        user = User.objects.get(pk=obj.user)
        return user.username

    def clip_title(self, obj):
        clip = Clips.objects.get(pk=obj.clip)
        return clip.title

    def check(self, obj):
        return '<a href="/clip/%s" target="_blank">check clip</a>' % obj.clip
    check.short_description = 'Check clip'
    check.allow_tags = True

    def format_date(self, obj):
        return obj.date_create.strftime('%Y-%m-%d %H:%M')
    format_date.short_description = 'Date Create'
    format_date.allow_tags = True

class CommentsAdmin(admin.ModelAdmin):
    list_display = ('author_id', 'author', 'comment_id', 'comment_text', 'clip_details', 'format_date')

    def clip_details(self, obj):
        return '<strong><a href="/clip/%s" target="_blank">%s</a></strong>' % (obj.clip.id, obj.clip.title)
    clip_details.short_description = 'Clip'
    clip_details.allow_tags = True

    def author_id(self, obj):
        return '<strong><a href="/admin/auth/user/%s/" target="_blank">%s</a></strong>' % (obj.author.id, obj.author.id)
    author_id.allow_tags = True

    def format_date(self, obj):
        return obj.date_create.strftime('%Y-%m-%d %H:%M')
    format_date.short_description = 'Date Create'
    format_date.allow_tags = True

    def comment_id(self, obj):
        return '<strong><a href="/admin/clips/comments/%s/" target="_blank">%s</a></strong>' % (obj.id, obj.id)
    comment_id.short_description = 'Comment id'
    comment_id.allow_tags = True

    def comment_text(self, obj):
        return '<strong><a href="/admin/clips/comments/%s/" target="_blank">%s</a></strong>' % (obj.id, obj.text)
    comment_text.short_description = 'Comment text'
    comment_text.allow_tags = True

class ModerateClipsAdmin(admin.ModelAdmin):
    list_display = ('clip', 'check', 'clip_details', 'moderated', 'email', 'is_deleted')
    search_fields = ('clip__title', 'clip__artist', 'clip__song', 'clip__tags', 'user__first_name', 'user__email')

    def check(self, obj):
        return '<a href="/clip/%s" target="_blank">check clip</a>' % obj.clip.id
    check.short_description = 'Check clip'
    check.allow_tags = True

    def clip_details(self, obj):
        return '<strong><a href="/admin/clips/clips/%s/" target="_blank">%s</a></strong>' % (obj.clip.id, obj.clip.title)
    clip_details.short_description = 'Clip details'
    clip_details.allow_tags = True

class StatisticAdmin(admin.ModelAdmin):
    list_display = ('user', 'format_date', 'HTTP_USER_AGENT', 'HTTP_HOST', 'HTTP_REFERER')
    search_fields = ('HTTP_ACCEPT_LANGUAGE', 'HTTP_HOST', 'HTTP_REFERER', 'HTTP_USER_AGENT', 'REMOTE_ADDR')

    def format_date(self, obj):
        return obj.date_create.strftime('%Y-%m-%d %H:%M')
    format_date.short_description = 'Date Create'
    format_date.allow_tags = True

admin.site.register(Emails, EmailsAdmin)
admin.site.register(Clips, ClipsAdmin)
admin.site.register(EmailTemplate, EmailTemplateAdmin)
admin.site.register(BrokenClips, BrokenClipsAdmin)
admin.site.register(UserProfile, UserProfileAdmin)
admin.site.register(FavouritesClips, FavouritesClipsAdmin)
admin.site.register(Comments, CommentsAdmin)
admin.site.register(ModerateClips, ModerateClipsAdmin)
admin.site.register(Statistic, StatisticAdmin)