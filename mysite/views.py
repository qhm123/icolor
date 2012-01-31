# -*- coding: utf-8 -*

import os
import logging

from django.core.urlresolvers import reverse
from django.core.paginator import Paginator, InvalidPage, EmptyPage
from django.core.context_processors import csrf
from django.http import HttpResponse, HttpResponseRedirect
from django.template import Context, loader
from django.shortcuts import render_to_response
from django.template import RequestContext

import models

import sinat_helper
import request_helper
from request_helper import require_login


def index(request, page_index=None):
    page_index = 0 if page_index is None else index(page_index)

    all_colors = models.Color.objects.order_by('-creat_time')
    paginator = Paginator(all_colors, 10)

    try:
        page = int(request.GET.get('page', '1'))
    except ValueError:
        page = 1

    try:
        colors = paginator.page(page)
    except (EmptyPage, InvalidPage):
        colors = paginator.page(paginator.num_pages)

    users = models.User.objects.order_by('-creat_time')[:20]
    alltags = models.Tag.objects.all()[:100]

    hint = request.GET.get('hint', '')

    template = loader.get_template('templates/index.html')
    context = Context({
        'hint': hint,
        'colors': colors,
        'users': users,
        'alltags': alltags,
        'widget_users_wall': True,
        'widget_tag_cloud': True,
        })
    context.update(RequestContext(request))
    return HttpResponse(template.render(context))


@require_login
def pick(request):
    if request.POST:
        auth_client = request.auth_client
        value = request.POST.get('colorvalue', '')
        try:
            color = models.Color.get(value)
        except:
            color = models.Color.add(value)
        host = 'http://' + request.META['HTTP_HOST']
        url = host + ('/detail/%d' % color.id)
        comment = request.POST.get('comment', '')
        tags = request.POST.get('tags', '')

        # maybe a async task
        content = u'我选择了一个我喜欢的颜色[%s]（%s），%s——%s这里支持或者评论我喜欢的颜色' % (value, tags, comment, url)
        auth_client.upload_color(content, color.value)

        models.UserLikeColor.like(request.user, color)
        models.Comment.add_comment(request.user, color, comment)

        tags = tags.split(',')
        for tag_name in tags:
            models.Tag.add_tag(tag_name, color, request.user)

        return HttpResponseRedirect('/pick')
    else:
        hint = request.GET.get('hint', '')
        auth_client = request.auth_client
        mycolors = request.user.like_colors()
        mycomments = request.user.comments()

        template = loader.get_template('templates/pick.html')
        context = Context({
            'hint': hint,
            'mycolors': mycolors,
            'mycomments': mycomments,
            'widget_mycolors': True,
            'widget_mycommets': True,
            })
        context.update(csrf(request))

        context.update(RequestContext(request))
        return HttpResponse(template.render(context))


def wall(request):
    colors = models.Color.objects.order_by('-creat_time')

    template = loader.get_template('templates/wall.html')
    context = Context({
        'colors': colors,
        })

    context.update(RequestContext(request))
    return HttpResponse(template.render(context))


def detail(request, color_id):
    color = models.Color.objects.get(id=int(color_id))
    hint = request.GET.get('hint', '')
    comments = models.Comment.objects.filter(color=color)

    template = loader.get_template('templates/detail.html')
    context = Context({
        'color': color,
        'hint': hint,
        'comments': comments,
        'widget_users_like_wall': True,
        })
    context.update(csrf(request))
    context.update(RequestContext(request))

    return HttpResponse(template.render(context))


def tag(request, tag_id):
    tag = models.Tag.objects.get(id=int(tag_id))
    colors = tag.colors()

    template = loader.get_template('templates/tag.html')
    context = Context({
        'colors': colors,
        })
    context.update(RequestContext(request))
    return HttpResponse(template.render(context))


@require_login
def guestbook(request):
    content = request.POST.get('comment', '')
    models.Idea.add_idea(request.user, content)

    url = request_helper.get_referer_url(request)

    return HttpResponseRedirect(url)


def about(request):
    ideas = models.Idea.get_all_idea_by_create_time()

    context = Context({
        'ideas': ideas,
        })
    return render_to_response('templates/about.html',
            context, context_instance=RequestContext(request))


@require_login
def like(request, color_id):
    url = request_helper.get_referer_url(request)
    if color_id is not None:
        auth_client = request.auth_client
        color = models.Color.objects.get(id=int(color_id))
        models.UserLikeColor.like(request.user, color)

        host = 'http://' + request.META['HTTP_HOST']
        color_url = host + ('/detail/%s' % str(color_id))

        message = u'我喜欢了颜色：[%s]，%s这里支持或者评论我喜欢的颜色' % (color.value, color_url)
        auth_client.upload_color(message, color.value)

    return HttpResponseRedirect(url)


@require_login
def comment(request, color_id):
    if request.POST:
        auth_client = request.auth_client
        comment_text = request.POST.get('comment', '')

        color = models.Color.objects.get(id=int(color_id))
        models.Comment.add_comment(request.user, color, comment_text)

        host = 'http://' + request.META['HTTP_HOST']
        color_url = host + '/detail/%s' % (str(color_id),)

        tags = request.POST.get('tags', '')
        message = u'我评论了颜色：[%s]（%s），评论：%s——%s这里评论或喜欢该颜色' % (color.value,
                tags, comment_text, color_url)
        auth_client.upload_color(message, color.value)

        tags = tags.split(',')
        for tag_name in tags:
            models.Tag.add_tag(tag_name, color, request.user)

    return HttpResponseRedirect('/detail/%s' % color_id)


@require_login
def share(request):
    """分享"""
    host = 'http://' + request.META['HTTP_HOST']
    content = u'爱颜色，一个新浪微博应用，推荐大家来看看' + host

    filename = os.path.join(os.path.dirname(__file__), "images/aicolor.png")
    request.auth_client.upload(filename, content)

    url = request_helper.get_referer_url(request)
    return HttpResponseRedirect(url)


def login(request):
    back_to_url = request_helper.get_referer_url(request)
    login_backurl = request.build_absolute_uri('/login_check')
    logging.debug(login_backurl)
    client = sinat_helper.get_oauth(login_backurl)
    if 'oauth_request_expires' not in request.session:
        request.session['login_back_to_url'] = back_to_url
        return HttpResponseRedirect('/weibo_login')
    else:
        access_token = request.session['oauth_access_token']
        expires_in = request.session['oauth_request_expires']
        client.client.set_access_token(access_token, expires_in)
        return HttpResponseRedirect(back_to_url)

def weibo_login(request):
    login_backurl = request.build_absolute_uri('/login_check')
    client = sinat_helper.get_oauth(login_backurl)
    url = client.get_authorize_url()
    template = loader.get_template('templates/weibo_login.html')
    context = Context({
        'url': url,
        })

    context.update(RequestContext(request))
    return HttpResponse(template.render(context))


def login_check(request):
    """用户成功登录授权后，会回调此方法，获取access_token，完成授权"""
    code = request.GET.get('code')
    login_backurl = request.build_absolute_uri('/login_check')
    client = sinat_helper.get_oauth(login_backurl)
    logging.info('code: %s' % code)
    r = client.client.request_access_token(code)
    access_token = r.access_token
    expires_in = r.expires_in
    logging.info("r: %s" % r)
    # save access_token
    request.session['oauth_access_token'] = access_token
    request.session['oauth_request_expires'] = expires_in
    request.session['oauth_uid'] = r.uid
    client.client.set_access_token(access_token, expires_in)

    # 添加用户
    sina_user = client.get_user(r.uid)
    domain = 'http://weibo.com/%s' % (sina_user.id,)
    if not models.User.exists(str(sina_user.id)):
        models.User.add_user(str(sina_user.id), sina_user.screen_name,
                domain, sina_user.profile_image_url)
    else:
        models.User.update(str(sina_user.id), sina_user.screen_name,
                domain, sina_user.profile_image_url)

    back_to_url = request.session.get('login_back_to_url', '/')
    return HttpResponseRedirect(back_to_url)


def logout(request):
    """用户登出，直接删除access_token"""
    del request.session['oauth_access_token']
    del request.session['oauth_request_expires']
    del request.session['oauth_uid']
    back_to_url = request_helper.get_referer_url(request)
    return HttpResponseRedirect(back_to_url)
