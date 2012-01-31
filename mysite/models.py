# -*- coding: utf-8 -*

from django.db import models


class Color(models.Model):
    """颜色"""
    value = models.CharField(max_length=32, unique=True)
    creat_time = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = 'mysite'

    @classmethod
    def add(self, value):
        color = Color()
        color.value = value
        color.save()
        return color

    @classmethod
    def get(cls, value):
        return Color.objects.get(value=value)

    def like_users(self):
        return (ulc.user for ulc in UserLikeColor.objects.filter(color=self))

    def like_count(self):
        return UserLikeColor.objects.filter(color=self).count()

    def tags(self):
        return Tag.objects.filter(color=self)


class User(models.Model):
    """用户"""
    uid = models.CharField(max_length=128, unique=True)
    name = models.CharField(max_length=512)
    domain = models.CharField(max_length=512)
    profile_image_url = models.CharField(max_length=512)
    creat_time = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = 'mysite'

    def like_colors(self):
        return (ulc.color for ulc in UserLikeColor.objects.filter(user=self))

    def like_color_count(self):
        return UserLikeColor.objects.filter(user=self).count()

    def comments(self):
        return Comment.objects.filter(user=self)

    @classmethod
    def exists(cls, uid):
        try:
            User.objects.get(uid=uid)
            return True
        except:
            return False

    @classmethod
    def add_user(cls, uid, name, domain, profile_image_url):
        user = User()
        user.uid = uid
        user.name = name
        user.domain = domain
        user.profile_image_url = profile_image_url
        user.save()

    @classmethod
    def update(cls, uid, name, domain, profile_image_url):
        user = User.objects.get(uid=uid)
        user.name = name
        user.domain = domain
        user.profile_image_url = profile_image_url
        user.save()

    @classmethod
    def get_user_by_id(cls, uid):
        return User.objects.filter(uid=uid).get()

    @classmethod
    def get_user_by_name(cls, name):
        """如果不存在则创建"""
        selected_users = User.objects.filter(name=name)
        user = None
        if selected_users.count() is not 0:
            user = selected_users[0]

        return user


class Comment(models.Model):
    """用户对于颜色的评论"""
    text = models.CharField(max_length=2048)
    creat_time = models.DateTimeField(auto_now=True)
    user = models.ForeignKey(User)
    color = models.ForeignKey(Color)

    class Meta:
        app_label = 'mysite'

    @classmethod
    def add_comment(cls, user, color, comment_text):
        comment = Comment()
        comment.user = user
        comment.text = comment_text
        comment.color = color
        comment.save()


class Tag(models.Model):
    """标签"""
    name = models.CharField(max_length=512)
    color = models.ForeignKey(Color)
    user = models.ForeignKey(User)

    class Meta:
        app_label = 'mysite'

    def colors(self):
        return (tag.color for tag in Tag.objects.filter(name=self.name))

    def users(self):
        return (tag.user for tag in Tag.objects.filter(name=self.name))

    @classmethod
    def add_tag(cls, name, color, user):
        try:
            tag = Tag.objects.get(name=name, color=color, user=user).get()
        except:
            tag = Tag()
            tag.name = name
            tag.color = color
            tag.user = user
            tag.save()


class Idea(models.Model):
    """意见建议"""
    user = models.ForeignKey(User)
    content = models.TextField()
    create_time = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = 'mysite'

    @classmethod
    def add_idea(cls, user, content):
        idea = Idea()
        idea.content = content
        idea.user = user
        idea.save()

    @classmethod
    def get_all_idea_by_create_time(cls):
        return Idea.objects.order_by('-create_time').all()


class UserLikeColor(models.Model):
    user = models.ForeignKey(User)
    color = models.ForeignKey(Color)

    class Meta:
        app_label = 'mysite'

    @classmethod
    def like(cls, user, color):
        userlikecolor = UserLikeColor()
        userlikecolor.user = user
        userlikecolor.color = color
        userlikecolor.save()
