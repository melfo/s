#coding: utf-8
# -*- encoding: UTF-8 -*-
import logging

import random
from BeautifulSoup import BeautifulSoup

from copy import copy
import urllib2
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.cache import cache
from django.core.mail import EmailMessage
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db.models import Q
from django.http import HttpResponseRedirect, HttpResponse, Http404
from django.utils import simplejson
from django.views.decorators.cache import cache_page
from clips.forms.search import SearchForm, RegistrationForm, Comment, LoginForm, AddClipForm, FavouritesClipsForm, ChangeImage, EditProfile, ChangePassword, SentPrivateMessages, AnswerMessageForm
from clips.inludes.email_helper import BaseUtils
from clips.inludes.rss import get_rss_news
from clips.inludes.statistic import static
import settings
from clips.models import Clips, UserProfile, Comments, CommentsLikes, ClipsLikes, UsersClips, FavouritesClips, PrivateMessages, AnswerMessages, EmailTemplate, Emails, BrokenClips, ModerateClips, Statistic
from decorators import render_to

@render_to('clips/index.html')
def index(request):

    request.session['premier'] = 1
    request.session['now_see'] = 0

    logger = logging.getLogger('log_to_file')

    statistic = {}
    for item in settings.META_INFO:
        statistic[item] = request.META.get(item, None)
    if request.user.is_anonymous():
        static(statistic)
    else:
        static(statistic, request.user)
    logger.info(statistic)

    clips = Clips.objects.filter(is_deleted=False, moderated=True).order_by('date_create', 'views', 'count_comments', 'year').reverse()

    if request.method == 'GET':
        search = SearchForm(request.GET)
        if search.is_valid():
            value = search.cleaned_data.get('search')
            if clips.filter(title__icontains=value).order_by('-title').count() > 0:
                clips = clips.filter(title__icontains=value).order_by('-title')

    paginator_clips = Paginator(clips, settings.PAGINATOR_PER_PAGE)

    if request.GET.get('page', None):
        current_page_clips = request.GET.get('page', 1)
        request.session['page'] = request.GET.get('page', 1)
    else:
        request.session['page'] = 1
        current_page_clips = request.session.get('page', 1)

    try:
        clip = paginator_clips.page(current_page_clips)
    except PageNotAnInteger:
        clip = paginator_clips.page(1)
    except EmptyPage:
        clip = paginator_clips.page(paginator_clips.num_pages)

    request_params = copy(request.GET)
    if request_params.get('page'):
        del request_params['page']

    return {
        'pager_clips':clip,
        'clips_items':clip.object_list,
        'request_params': "&%s" %
            request_params.urlencode() if request_params.urlencode() else "",
        }

@render_to('clips/clip.html')
def clip(request, clip):

    request.session['premier'] = 0
    request.session['now_see'] = 1

    logger = logging.getLogger('log_to_file')

    statistic = {}
    for item in settings.META_INFO:
        statistic[item] = request.META.get(item, None)
    if request.user.is_anonymous():
        static(statistic)
    else:
        static(statistic, request.user)
    logger.info(statistic)

    try:
        clip = Clips.objects.get(id=clip, is_deleted=False, moderated=True)
        clip.views += 1
        clip.save()
    except Exception, e:
        logger.info(e)
        return HttpResponseRedirect('/')

    if request.method == 'GET':
        search = SearchForm(request.GET)
        if search.is_valid():
            value = search.cleaned_data.get('search')
            return HttpResponseRedirect('/?search=%s' % value)

    form = Comment()
    if request.method == 'POST':
        form = Comment(request.POST)
        if form.is_valid():
            comment = Comments.objects.create(
                clip_id = clip.id,
                author_id = request.user.id,
                text = form.cleaned_data.get('text'),
            )
            comment.save()
            clip.count_comments += 1
            clip.save()
            return HttpResponseRedirect('/create/comment')

    comments = Comments.objects.filter(clip__id=clip.id)

    paginator = Paginator(comments, settings.PAGINATOR_PER_PAGE)
    current_page = request.GET.get('page', 1)

    try:
        comment = paginator.page(current_page)
    except PageNotAnInteger:
        comment = paginator.page(1)
    except EmptyPage:
        comment = paginator.page(paginator.num_pages)

    same_clips = []
    try:
        search = u'%s' % clip.title.encode('cp1251').decode('cp1251').split(' - ')[0]
        same_clips = Clips.objects.filter(artist__icontains=search, is_deleted=False, moderated=True).exclude(pk=clip.id).order_by('?')[:10]
    except Exception:
        pass

    return {
        'pager':comment,
        'comments_items':comment.object_list,
        'form':form,
        'clip':clip,
        'same_clips':same_clips,
    }

@cache_page(60*60)
@render_to('clips/premiers.html')
def premiers(request):

    return {
        'premier':Clips.objects.filter(premier=Clips.PREMIER_YES, is_deleted=False, moderated=True).order_by('-date_create', 'title')[:4],
    }

@render_to('clips/popular.html')
def popular(request):

    clips = []
    if request.session['now_see'] == 1:
        clips = Clips.objects.filter(is_deleted=False, moderated=True).order_by('?')[:5]
    else:
        clips = Clips.objects.filter(is_deleted=False, moderated=True).order_by('-views')[:5]

    if cache.get('rss', 0) == 0:
        rss = get_rss_news()
        cache.set('rss', rss, 3600)
    else:
        rss = cache.get('rss')

    return {
        'rss':rss,
        'last_added':clips,
        }

def add_comment(request):
    return HttpResponseRedirect('%s' % request.META.get('HTTP_REFERER', '/'))

@login_required(login_url='/login')
@render_to('clips/add-like.html')
def add_like(request):

    logger = logging.getLogger('log_to_file')

    item = ''
    comment = {}
    clip = {}
    if request.GET.get('comment', '') != '':
        comment_id = request.GET.get('comment')
        try:
            comment = Comments.objects.get(id=comment_id, is_deleted=False)
            try:
                all_comments = CommentsLikes.objects.get(comment=comment_id, user=request.user.id)
            except Exception, e:
                logger.info(e)
                if comment.author.id != request.user.id:
                    all_comments = CommentsLikes.objects.create(
                        comment_id=int(comment_id),
                        user_id=request.user.id,
                    )
                    all_comments.save()
                    comment.likes += 1
                    comment.save()
            item = 'comment'
        except Exception:
            item = ''

    if request.GET.get('clip', '') != '':
        clip_id = request.GET.get('clip')
        try:
            clip = Clips.objects.get(id=clip_id, is_deleted=False, moderated=True)
            try:
                all_clips = ClipsLikes.objects.get(clip=clip_id, user=request.user.id)
            except Exception, e:
                logger.info(e)
                all_clips = ClipsLikes.objects.create(
                    clip_id=int(clip_id),
                    user_id=request.user.id,
                )
                all_clips.save()

                clip.likes += 1
                clip.save()
            item = 'clip'
        except Exception:
            item = ''

    if request.GET.get('clip_index', '') != '':
        clip_id = request.GET.get('clip_index')
        try:
            clip = Clips.objects.get(id=clip_id, is_deleted=False, moderated=True)
            try:
                all_clips = ClipsLikes.objects.get(clip=clip_id, user=request.user.id)
            except Exception, e:
                logger.info(e)
                all_clips = ClipsLikes.objects.create(
                    clip_id=int(clip_id),
                    user_id=request.user.id,
                )
                all_clips.save()

                clip.likes += 1
                clip.save()
            item = 'clip_index'
        except Exception:
            item = ''

    return {
        'item':item,
        'comment':comment,
        'clip':clip,
    }

@render_to('clips/all_premiers.html')
def all_premiers(request):

    request.session['premier'] = 0
    request.session['now_see'] = 0

    clips = Clips.objects.filter(premier=Clips.PREMIER_YES, is_deleted=False, moderated=True).order_by('date_create').reverse()

    if request.method == 'GET':
        search = SearchForm(request.GET)
        if search.is_valid():
            value = search.cleaned_data.get('search')
            if clips.filter(title__icontains=value).order_by('-title').count() > 0:
                clips = clips.filter(title__icontains=value).order_by('-title')
            else:
                pass

    paginator_clips = Paginator(clips, settings.PAGINATOR_PER_PAGE)
    current_page_clips = request.GET.get('page', 1)

    try:
        clip = paginator_clips.page(current_page_clips)
    except PageNotAnInteger:
        clip = paginator_clips.page(1)
    except EmptyPage:
        clip = paginator_clips.page(paginator_clips.num_pages)

    request_params = copy(request.GET)
    if request_params.get('page'):
        del request_params['page']

    return {
        'pager_clips':clip,
        'clips_items':clip.object_list,
        'request_params': "&%s" %
                          request_params.urlencode() if request_params.urlencode() else "",
        }

@render_to('clips/sort_clips.html')
def sort_clips(request, sort):

    request.session['premier'] = 0
    request.session['now_see'] = 1

    logger = logging.getLogger('log_to_file')

    statistic = {}
    for item in settings.META_INFO:
        statistic[item] = request.META.get(item, None)
    if request.user.is_anonymous():
        static(statistic)
    else:
        static(statistic, request.user)
    logger.info(statistic)

    SORT = {'new':0, 'comments':1, 'views':2, 'recommended':3}
    if SORT.get(sort, '') == '':
        return HttpResponseRedirect('/')

    if sort == 'new':
        clips = Clips.objects.filter(is_deleted=False, moderated=True).order_by('-date_create')[:50]

    if sort == 'comments':
        clips = Clips.objects.filter(is_deleted=False, moderated=True).order_by('-count_comments')[:50]

    if sort == 'views':
        clips = Clips.objects.filter(is_deleted=False, moderated=True).order_by('-views')[:50]

    if sort == 'recommended':
        clips = Clips.objects.filter(is_deleted=False, moderated=True).order_by('?')[:10]

    if request.method == 'GET':
        search = SearchForm(request.GET)
        if search.is_valid():
            value = search.cleaned_data.get('search')
            if clips.filter(title__icontains=value).order_by('-title').count() > 0:
                clips = clips.filter(title__icontains=value).order_by('-title')
            else:
                pass

    paginator_clips = Paginator(clips, settings.PAGINATOR_PER_PAGE)
    current_page_clips = request.GET.get('page', 1)

    try:
        clip = paginator_clips.page(current_page_clips)
    except PageNotAnInteger:
        clip = paginator_clips.page(1)
    except EmptyPage:
        clip = paginator_clips.page(paginator_clips.num_pages)

    request_params = copy(request.GET)
    if request_params.get('page'):
        del request_params['page']

    return {
        'sort':sort,
        'pager_clips':clip,
        'clips_items':clip.object_list,
        'request_params': "&%s" %
                          request_params.urlencode() if request_params.urlencode() else "",
        }

@login_required(login_url='/login')
@render_to('clips/add-clip.html')
def add_clip(request):

    request.session['premier'] = 0
    request.session['now_see'] = 0

    return {}

@render_to('clips/parsing_clip.html')
def parsing_clip(request):

    title = ''
    form = AddClipForm()
    error = 0
    clip = {}

    if request.method == 'GET':
        link = request.GET.get('link_youtube')
        try:
            r = urllib2.urlopen(link).read()
            soup = BeautifulSoup(''.join(r))
            table = soup.find('h1', id="watch-headline-title")
            if table:
                rows = table.findAll('span')
                for i in rows:
                    title = i['title']

                thumb = 'http://img.youtube.com/vi/%s/1.jpg' % str(link).split('?')[1].split('=')[1]

                tags = ''
                tag = title.split('-')[0]
                try:
                    tag_items = tag.split('feat.')[1]
                    tag_items = tag.split('&')[1]
                    tag_items = tag.split('feat')[1]
                    for i in tag.split('feat.'):
                        tags += i
                    for i in tag.split('&'):
                        tags += i
                    for i in tag.split('feat'):
                        tags += i
                except IndexError:
                    tags = tag

                artist = tag

                try:
                    song = title.split('-')[1]
                except IndexError:
                    song = ''

                link_youtube = 'http://www.youtube.com/embed/%s' % str(link).split('?')[1].split('=')[1]

                link_download = 'http://www.ssyoutube.com/watch?v=%s' % str(link).split('?')[1].split('=')[1]

                try:
                    clip = Clips.objects.get(link_youtube__contains=link_youtube)
                    error = 1
                except Clips.DoesNotExist:
                    clip = Clips.objects.create(
                        title = title,
                        thumb = thumb,
                        link_youtube = link_youtube,
                        tags = tags,
                        link_download = link_download,
                        artist = artist,
                        song = song,
                    )
                    mc = ModerateClips.objects.create(
                        clip = clip
                    )
                    uc = UsersClips.objects.create(
                        user_id = request.user.id,
                        clip_id = clip.id
                    )
                    error = 2
            else:
                error = 0
                clip = {}
        except urllib2.HTTPError, Exception:
            error = 0
            clip = {}

    return {
        'error':error,
        'clip':clip,
        }

@login_required(login_url='/login')
@render_to('clips/favourites.html')
def favourites(request):

    logger = logging.getLogger('log_to_file')

    statistic = {}
    for item in settings.META_INFO:
        statistic[item] = request.META.get(item, None)
    if request.user.is_anonymous():
        static(statistic)
    else:
        static(statistic, request.user)
    logger.info(statistic)

    request.session['premier'] = 0
    request.session['now_see'] = 0

    favourite_clips = FavouritesClips.objects.filter(user=request.user.id).order_by('-id', 'date_create')

    clips = []
    for i in favourite_clips:
        clip = Clips.objects.get(id=i.clip)
        if clip.is_deleted == False:
            clips.append(clip)

    paginator_clips = Paginator(clips, settings.PAGINATOR_PER_PAGE)
    current_page_clips = request.GET.get('page', 1)

    try:
        clip = paginator_clips.page(current_page_clips)
    except PageNotAnInteger:
        clip = paginator_clips.page(1)
    except EmptyPage:
        clip = paginator_clips.page(paginator_clips.num_pages)

    request_params = copy(request.GET)
    if request_params.get('page'):
        del request_params['page']

    return {
        'pager_clips':clip,
        'clips_items':clip.object_list,
    }

@login_required(login_url='/login')
@render_to('clips/favourites.html')
def add_favourite(request, clip):

    code = 0

    data = {}
    data['user'] = request.user.id
    data['clip'] = clip

    form = FavouritesClipsForm(data)
    if form.is_valid():
        try:
            info = FavouritesClips.objects.get(user=form.cleaned_data.get('user'), clip=form.cleaned_data.get('clip'))
            code = 1
        except FavouritesClips.DoesNotExist, e:
            info = FavouritesClips.objects.create(
                user = form.cleaned_data.get('user'),
                clip = form.cleaned_data.get('clip')
            )
            code = 2

    json = simplejson.dumps(code)
    return HttpResponse(json, mimetype='application/json')

def clip_delete(request, clip):

    code = 0

    try:
        favourite_clip = FavouritesClips.objects.get(user=request.user.id, clip=clip)
        favourite_clip.delete()
        code = 1
    except FavouritesClips.DoesNotExist:
        code = 2

    json = simplejson.dumps(code)
    return HttpResponse(json, mimetype='application/json')

@login_required(login_url='/login')
@render_to('clips/clips_user.html')
def clips_user(request):

    request.session['premier'] = 0
    request.session['now_see'] = 0

    try:
        clips_user = UsersClips.objects.filter(user=request.user.id)
    except Exception:
        return HttpResponseRedirect('/')

    clips = []
    for i in clips_user:
        clip = Clips.objects.get(id=i.clip.id, is_deleted=False, moderated=True)
        clips.append(clip)

    paginator_clips = Paginator(clips, settings.PAGINATOR_PER_PAGE)
    current_page_clips = request.GET.get('page', 1)

    try:
        clip = paginator_clips.page(current_page_clips)
    except PageNotAnInteger:
        clip = paginator_clips.page(1)
    except EmptyPage:
        clip = paginator_clips.page(paginator_clips.num_pages)

    request_params = copy(request.GET)
    if request_params.get('page'):
        del request_params['page']

    return {
        'pager_clips':clip,
        'clips_items':clip.object_list,
        'request_params': "&%s" %
                          request_params.urlencode() if request_params.urlencode() else "",
        }

def refresh(request):

    return  HttpResponseRedirect('%s' % request.META.get('HTTP_REFERER'))

def search_clips(request):

    results = []
    model_results = []
    if request.method == "GET":
        if request.GET.has_key(u'query'):
            value = request.GET[u'query']
            if len(value) > 0:
                model_results = Clips.objects.filter(title__icontains=value, is_deleted=False, moderated=True).order_by('title')[:15]
            results = [ x.title for x in model_results ]
    json = simplejson.dumps(results)
    return HttpResponse(json, mimetype='application/json')

def broken_clip(request, clip):

    logger = logging.getLogger('log_to_file')

    clip = Clips.objects.get(pk=clip)

    try:
        broken = BrokenClips.objects.get(clip=clip)
        broken.status = BrokenClips.STATUS_BROKEN
        broken.save()
    except Exception, e:
        logger.info(e)
        broken = BrokenClips.objects.create(
            clip=clip
        )
        broken.save()

    results = []

    clip_id = broken.clip.id
    results.append(clip_id)

    json = simplejson.dumps(results)
    return HttpResponse(json, mimetype='application/json')

