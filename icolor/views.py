# -*- coding: utf-8 -*

import os
import logging

from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect
from django.template import Context, loader

import models

import sinat_helper
import request_helper
from request_helper import require_login


def index(request, page_index=None):
    if page_index is None:
        page_index = 0
    else:
        page_index = int(page_index)

    appconfig = models.AppConfig.get_default_appconfig()
    intro = appconfig.intro
    hotcolor_count_onepage = appconfig.hotcolor_count_onepage

    color_count = models.Color.all().count(limit=1000)
    page_count = color_count / hotcolor_count_onepage
    if int(color_count % hotcolor_count_onepage) is not 0:
        page_count += 1

    hotcolors = models.Color.all().order('-likecount')
    onepage_hotcolors = hotcolors.fetch(hotcolor_count_onepage,
            hotcolor_count_onepage * page_index)

    user_count = models.User.all().count(limit=1000)
    users = models.User.all().order('-like_color_count').fetch(limit=20)

    states = models.State.all().order('-creat_time') \
        .fetch(limit=hotcolor_count_onepage)

    alltags = models.Tag.all().fetch(limit=100)

    page_urls = ['/' + str(i) for i in range(page_count)]
    like_url = '/like'
    comment_url = '/detail'
    hint = request.GET.get('hint', '')

    template = loader.get_template('icolor/templates/index.html')
    context = Context({
        'intro': intro,
        'hint': hint,
        'hotcolor_count_onepage': hotcolor_count_onepage,
        'hotcolors': onepage_hotcolors,
        'like_url': like_url,
        'comment_url': comment_url,
        'page_urls': page_urls,
        'color_count': color_count,
        'users': users,
        'page_index': page_index,
        'user_count': user_count,
        'states': states,
        'alltags': alltags,
        'widget_recent_entries': True,
        'widget_users_wall': True,
        'widget_tag_cloud': True,
        })

    return HttpResponse(template.render(context))


@require_login
def pick(request):
    if request.POST:
        auth_client = request.auth_client
        sina_user = auth_client.get_user()
        value = request.POST.get('colorvalue', '')
        comment = request.POST.get('comment', '')
        is_success = models.UserLikeColor \
            .insert_or_like_color_by_username_and_colorvalue(
                    sina_user.screen_name, value)
        if not is_success:
            return HttpResponseRedirect(reverse('icolor.views.pick')
                    + u'?hint=你已经喜欢过')

        color = models.Color.get_color_by_value(value)
        color_id = color.key().id()
        host = 'http://' + request.META['HTTP_HOST']

        tags = request.POST.get('tags', '')

        url = host + ('/detail/%s' % str(color_id))
        content = u'我选择了一个我喜欢的颜色[%s]（%s），%s——%s这里支持或者评论我喜欢的颜色' % (value, tags, comment, url)
        auth_client.upload_color(content, color.value)

        models.State.add_state(sina_user.screen_name,
                color_id, '', comment, type='like')
        models.Comment.add_comment(sina_user.screen_name, color_id, comment)

        tags = tags.split(',')
        for tag_name in tags:
            models.Tag.add_tag(tag_name, color, models.User.get_user_by_name(sina_user.screen_name))

        return HttpResponseRedirect(reverse('icolor.views.pick'))
    else:
        hint = request.GET.get('hint', '')
        auth_client = request.auth_client
        sina_user = auth_client.get_user()
        mycolors = models.User.get_user_by_name(sina_user.screen_name).like_colors()
        mycomments = models.User.get_user_by_name(sina_user.screen_name).comment_set

        template = loader.get_template('icolor/templates/pick.html')
        context = Context({
            'hint': hint,
            'mycolors': mycolors,
            'mycomments': mycomments,
            'widget_mycolors': True,
            'widget_mycommets': True,
            })

        return HttpResponse(template.render(context))


def wall(request):
    colors = models.Color.all().order('-creat_time').fetch(limit=1000)

    template = loader.get_template('icolor/templates/wall.html')
    context = Context({
        'colors': colors,
        })

    return HttpResponse(template.render(context))


def detail(request, color_id):

    color = models.Color.get_by_id(int(color_id))
    like_url = '/like'
    hint = request.GET.get('hint', '')

    comments = []
    if color.comment_set is not None:
        comments = color.comment_set

    template = loader.get_template('icolor/templates/detail.html')
    context = Context({
        'color': color,
        'like_url': like_url,
        'hint': hint,
        'comments': comments,
        'widget_users_like_wall': True,
        })

    return HttpResponse(template.render(context))


@require_login
def addtag(request):
    tags = request.POST.get('tags', '')
    tags = tags.split(',')

    auth_client = request.auth_client
    sina_user = auth_client.get_user()
    user = models.User.get_user_by_name(sina_user.screen_name)

    color_id = request.POST.get('color_id', '')
    color = models.Color.get_by_id(int(color_id))

    for tag_name in tags:
        models.Tag.add_tag(tag_name, color, user)
    back_url = request_helper.get_referer_url(request)

    return HttpResponseRedirect(back_url)


def tag(request, tag_id):

    tag = models.Tag.get_by_id(int(tag_id))
    colors = tag.colors()
    users = tag.users()

    template = loader.get_template('icolor/templates/tag.html')
    context = Context({
        'colors': colors,
        'users': users,
        })
    return HttpResponse(template.render(context))


def about(request):
    ideas = models.Idea.get_all_idea_by_create_time()

    template = loader.get_template('icolor/templates/about.html')
    context = Context({
        'ideas': ideas,
        })

    return HttpResponse(template.render(context))


@require_login
def like(request, color_id):
    url = request_helper.get_referer_url(request)
    if color_id is not None:
        auth_client = request.auth_client
        sina_user = auth_client.get_user()

        color = models.Color.get_by_id(int(color_id))
        is_success = models.UserLikeColor.insert_or_like_color_by_username_and_colorvalue(sina_user.screen_name, color.value)
        if not is_success:
            return HttpResponseRedirect(url + u'?hint=你已经喜欢过')

        host = 'http://' + request.META['HTTP_HOST']
        color_url = host + '/detail/%s' % (str(color_id),)

        message = u'我喜欢了颜色：[%s]，%s这里支持或者评论我喜欢的颜色' % (color.value, color_url)
        #auth_client.update(content)
        auth_client.upload_color(message, color.value)

        models.State.add_state(sina_user.screen_name,
                color_id, '', '', type='like')

    return HttpResponseRedirect(url)


@require_login
def comment(request, color_id):
    if request.POST:
        auth_client = request.auth_client
        sina_user = auth_client.get_user()
        comment_text = request.POST.get('comment', '')

        models.Comment.add_comment(sina_user.screen_name,
                color_id, comment_text)
        color = models.Color.get_by_id(int(color_id))

        host = 'http://' + request.META['HTTP_HOST']
        color_url = host + '/detail/%s' % (str(color_id),)

        tags = request.POST.get('tags', '')
        message = u'我评论了颜色：[%s]（%s），评论：%s——%s这里评论或喜欢该颜色' % (color.value,
                tags, comment_text, color_url)

        auth_client.upload_color(message, color.value)

        models.State.add_state(sina_user.screen_name,
                color_id, '', comment_text, type='comment')
        tags = tags.split(',')
        for tag_name in tags:
            models.Tag.add_tag(tag_name, color,
                    models.User.get_user_by_name(sina_user.screen_name))

    return HttpResponseRedirect(reverse('icolor.views.detail',
        kwargs={'color_id': color_id, }))


@require_login
def share(request):
    """分享"""
    host = 'http://' + request.META['HTTP_HOST']
    content = u'爱颜色，一个新浪微博应用，推荐大家来看看' + host

    filename = os.path.join(os.path.dirname(__file__), "images/aicolor.png")
    request.auth_client.upload(filename, content)

    url = request_helper.get_referer_url(request)
    return HttpResponseRedirect(url)


@require_login
def guestbook(request):
    """留言板"""
    content = request.POST.get('comment', '')
    sina_user = request.auth_client.get_user()
    models.Idea.add_Idea(sina_user.screen_name, content)

    url = request_helper.get_referer_url(request)
    return HttpResponseRedirect(url)


def login(request):
    back_to_url = request_helper.get_referer_url(request)
    login_backurl = request.build_absolute_uri('/login_check')
    logging.debug(login_backurl)
    client = sinat_helper.get_oauth(login_backurl)
    if 'oauth_request_expires' not in request.session:
        request.session['login_back_to_url'] = back_to_url
        url = client.get_authorize_url()
        return HttpResponseRedirect(url)
    else:
        access_token = request.session['oauth_access_token']
        expires_in = request.session['oauth_request_expires']
        client.client.set_access_token(access_token, expires_in)
        return HttpResponseRedirect(back_to_url)


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
    sina_user = client.get_user()
    domain = 'http://weibo.com/%s' % (sina_user.id,)
    models.User.add_user(str(sina_user.id), sina_user.screen_name,
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
