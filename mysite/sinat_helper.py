# -*- coding: utf-8 -*

from weibo import APIClient
import generate_image_helper
import logging

APP_KEY = "3150277999"
APP_SECRET = "dffd9932ff6f29f3b9e64174bd3493fb"


class WebOAuthHandler():
    """继承自OAuthHandler，提供Web应用方法。"""
    def __init__(self, callback_url, access_token=None, expires_in=None):
        self.client = APIClient(app_key=APP_KEY,
                app_secret=APP_SECRET, redirect_uri=callback_url)
        if access_token is not None:
            logging.info("access_token: %s, expire: %s" % (access_token,
                expires_in))
            self.client.set_access_token(str(access_token), str(expires_in))

    def get_authorize_url(self):
        return self.client.get_authorize_url()

    def update(self, message):
        """添加一条新微博信息"""
        message = message.encode("utf-8")
        self.client.post.statuses__update(status=message)

    def upload(self, filename, message):
        message = message.encode("utf-8")
        f = open(filename)
        self.client.upload.statuses__upload(status=message, pic=f)
        f.close()

    def upload_color(self, message, color_value):
        """上传颜色图片微博"""
        message = message.encode("utf-8")
        data = generate_image_helper.generate_image(color_value)
        logging.info('status: %s, data: %s' % (message, data))
        self.client.upload.statuses__upload(status=message, pic=data)

    def get_user(self, uid):
        user = self.client.get.users__show(uid=uid)
        return user


def get_oauth(callback_url='', access_token=None, expires_in=None):
    """获取oauth认证类"""
    logging.info("access_token: %s, expire: %s" % (access_token,
        expires_in))
    return WebOAuthHandler(callback_url, access_token=access_token,
            expires_in=expires_in)
