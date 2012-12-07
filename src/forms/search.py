#coding: utf-8

from django import forms
from django.contrib.auth.models import User
from clips.models import Comments, Clips, FavouritesClips, PrivateMessages, AnswerMessages
from users.models import UserProfile

class SearchForm(forms.Form):

    search = forms.CharField(max_length=255)

class RegistrationForm(forms.ModelForm):

    username = forms.CharField(max_length=255, required=True)
    email = forms.EmailField(max_length=255, required=True)
    first_name = forms.CharField(max_length=255, required=True)
    last_name = forms.CharField(max_length=255, required=False)
    password = forms.CharField(max_length=255, min_length=5)
    password_c = forms.CharField(max_length=255, min_length=5)

    def clean_username(self):
        login = self.cleaned_data.get('username')

        if User.objects.filter(username=login).count() > 0:
            raise forms.ValidationError(u'Этот логин уже используется')

        return login

    def clean_email(self):
        email = self.cleaned_data.get('email')

        if User.objects.filter(email=email).count():
            raise forms.ValidationError(u'Этот email уже используется')

        return email

    class Meta:
        model = UserProfile
        fields = (
            'gender',
        )


class Comment(forms.ModelForm):

    class Meta:
        model = Comments
        fields = (
            'text',
        )

class LoginForm(forms.Form):

    username = forms.CharField(max_length=255, required=True)
    password = forms.CharField(max_length=255, min_length=5)

class AddClipForm(forms.ModelForm):

    class Meta:
        model = Clips
        fields = (
            'link_youtube',
        )

class FavouritesClipsForm(forms.ModelForm):

    class Meta:
        model = FavouritesClips

class ChangeImage(forms.ModelForm):

    class Meta:
        model = UserProfile
        fields = (
            'image',
        )

class EditProfile(forms.ModelForm):

    username = forms.CharField(max_length=255, required=True)
    email = forms.EmailField(max_length=255, required=True)
    first_name = forms.CharField(max_length=255, required=True)
    last_name = forms.CharField(max_length=255, required=False)

    class Meta:
        model = UserProfile
        fields = (
            'gender',
        )

class ChangePassword(forms.Form):

    password_old = forms.CharField(max_length=255, required=True, min_length=5)
    password_c = forms.CharField(max_length=255, required=True, min_length=5)
    password_new = forms.CharField(max_length=255, required=True, min_length=5)

class RestorePassword(forms.Form):

    password_new = forms.CharField(max_length=255, required=True, min_length=5)
    password_copy = forms.CharField(max_length=255, required=True, min_length=5)

    def clean(self):
        data = self.cleaned_data
        if data.get('password_new') != data.get('password_copy'):
            raise forms.ValidationError(u'Пароли не совпадают')
        return  data

class SentPrivateMessages(forms.ModelForm):

    for_user = forms.CharField(max_length=255, required=True)

    class Meta:
        model = PrivateMessages
        fields = (
            'subject',
            'message',
        )

class AnswerMessageForm(forms.ModelForm):

    class Meta:
        model = AnswerMessages
        fields = (
            'text',
        )

class RequestEmail(forms.Form):

    email = forms.EmailField(max_length=255, required=True)

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if not User.objects.filter(email=email).count():
            raise forms.ValidationError('Такого почтового адреса не существует в базе')
        return email