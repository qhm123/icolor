# -*- coding: utf-8 -*

import logging

from functools import wraps

from django.http import HttpResponseRedirect

from models import User

import sinat_helper


def get_referer_url(request):
    """获得请求页的url"""
    referer_url = request.META.get('HTTP_REFERER', '/')
    host = request.META['HTTP_HOST']
    if referer_url.startswith('http') and host not in referer_url:
        referer_url = '/'  # 避免外站直接跳到登录页而发生跳转错误
    return referer_url


def require_login(method):
    @wraps(method)
    def wrapper(self, *args, **kwargs):
        if 'oauth_access_token' not in self.session:
            return HttpResponseRedirect('/login')
        else:
            access_token = self.session['oauth_access_token']
            expires_in = self.session['oauth_request_expires']
            uid = self.session['oauth_uid']
            logging.info('access_token: %s, expires_in: %s' % (access_token,
                expires_in))
            logging.debug('access_token: %s, expires_in: %s' % (access_token,
                expires_in))
            login_backurl = self.build_absolute_uri('/login_check')
            self.auth_client = sinat_helper.get_oauth(login_backurl,
                    access_token, expires_in)
            self.uid = uid
            self.user = User.get_user_by_id(uid)
            return method(self, *args, **kwargs)
    return wrapper
