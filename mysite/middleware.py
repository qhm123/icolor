# coding: utf-8


class UserMiddleware(object):
    def process_request(self, request):
        if 'oauth_access_token' in request.session:
            request.__class__.logined = True
        else:
            request.__class__.logined = False
