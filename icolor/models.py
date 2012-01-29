# -*- coding: utf-8 -*

from appengine_django.models import BaseModel
from google.appengine.ext import db

# 以下的Users,LikeColors,UserLikeColor是为了实现
# “喜欢颜色”和“用户”的多对多关系
# 参考链接：http://blog.arbingersys.com/2008/04/google-app-engine-better-many-to-many.html

class Users(BaseModel):
    """用户集合"""
    notes = db.StringProperty()
    
    @classmethod
    def get_default_Users(cls):
        """获取用户集合"""
        default_users = Users.all().get()
        if default_users is None:
            default_users = Users()
            default_users.put()

        return default_users
    
class LikeColors(BaseModel):
    """喜欢的颜色集合"""
    notes = db.StringProperty()
    
    @classmethod
    def get_default_LikeColors(cls):
        """获取喜欢的颜色集合"""
        default_likecolors = LikeColors.all().get()
        if default_likecolors is None:
            default_likecolors = LikeColors()
            default_likecolors.put()

        return default_likecolors

class Color(BaseModel):
    """颜色"""
    value = db.StringProperty(required=True)
    creat_time = db.DateTimeProperty(auto_now_add=True)
    likecolors_col = db.ReferenceProperty(LikeColors, collection_name='likecolors_col')
    likecount = db.IntegerProperty(default=1)
    
    def like_users(self):
        return (x.user for x in self.userlikecolor_set)
    
    def tags(self):
        return (x.tag for x in self.colortag_set)
    
    # TODO: 方法语义上不是很明确，待改进。（该方法对于不存在的值会创建相应的值存入数据库）
    @classmethod
    def get_color_by_value(cls, value):
        """如果不存在则创建"""
        selected_color_values = Color.all().filter('value =', value)
        if selected_color_values.count() is 0:
            color = Color(value=value)
            color.likecolors_col = LikeColors.get_default_LikeColors()
            color.put()
        else:
            color = selected_color_values[0]
            
        return color

class User(BaseModel):
    """用户"""
    uid = db.StringProperty()
    name = db.StringProperty()
    domain = db.StringProperty()
    profile_image_url = db.StringProperty()
    like_color_count = db.IntegerProperty(default=0)
    users_col = db.ReferenceProperty(Users, collection_name='users_col')
    
    def like_colors(self):
        return (x.likecolor for x in self.userlikecolor_set)
    
    def tags(self):
        return (x.tag for x in self.usertag_set)
    
    @classmethod
    def add_user(cls, uid, name, domain, profile_image_url):
        """添加一名用户"""
        _user = User.get_user_by_id(uid)
        if _user is None:
            user = User()
            user.uid = uid
            user.name = name
            user.domain = domain
            user.profile_image_url = profile_image_url
            user.users_col = Users.get_default_Users()
            user.put()
        else:
            user = _user
            user.uid = uid
            user.name = name
            user.domain = domain
            user.profile_image_url = profile_image_url
            user.users_col = Users.get_default_Users()
            user.put() 
            
    @classmethod
    def get_user_by_id(cls, uid):
        return User.all().filter('uid =', uid).get()
    
    @classmethod
    def get_user_by_name(cls, name):
        """如果不存在则创建"""
        selected_users = User.all().filter('name =', name)
        user = None
        if selected_users.count() is not 0:
            user = selected_users[0]
        
        return user
    
class Comment(BaseModel):
    """用户对于颜色的评论"""
    text = db.StringProperty(multiline=True)
    creat_time = db.DateTimeProperty(auto_now_add=True)
    user = db.ReferenceProperty(User)
    color = db.ReferenceProperty(Color)
    
    @classmethod
    def add_comment(cls, user_name, color_id, comment_text):
        user = User.get_user_by_name(user_name)
        color = Color.get_by_id(int(color_id))
        comment = Comment()
        comment.user = user
        comment.text = comment_text
        comment.color = color
        comment.put()
        
class State(BaseModel):
    """状态"""
    content = db.StringProperty(multiline=True)
    creat_time = db.DateTimeProperty(auto_now_add=True)
    user = db.ReferenceProperty(User)
    color = db.ReferenceProperty(Color)
    comment = db.StringProperty(multiline=True)
    type = db.StringProperty(choices=set(["comment", "like"]))
    
    @classmethod
    def add_state(cls, user_name, color_id, content, comment, type):
        user = User.get_user_by_name(user_name)
        color = Color.get_by_id(int(color_id))
        state = State()
        state.content = content
        state.user = user
        state.color = color
        state.comment = comment
        state.type = type
        state.put()
        
class Tag(BaseModel):
    """标签"""
    name = db.StringProperty()
    count = db.IntegerProperty(default=0)
    
    def colors(self):
        return (x.color for x in self.colortag_set)
    
    def users(self):
        return (x.user for x in self.usertag_set)
    
    @classmethod
    def add_tag(cls, name, color, user):
        tag = Tag.all().filter("name =", name).get()
        if tag is None:
            tag = Tag()
            tag.name = name;
            tag.put()
            ColorTag.add_color_tag(color, tag)
            UserTag.add_user_tag(user, tag)
        tag.count += 1
        tag.put()
        
class ColorTag(BaseModel):
    """颜色，标签多对多关系"""
    color = db.ReferenceProperty(Color)
    tag = db.ReferenceProperty(Tag)
    
    @classmethod
    def add_color_tag(cls, color, tag):
        color_tag = ColorTag()
        color_tag.color = color
        color_tag.tag = tag;
        color_tag.put()
    
class UserTag(BaseModel):
    """用户，标签多对多关系"""
    user = db.ReferenceProperty(User)
    tag = db.ReferenceProperty(Tag)
    
    @classmethod
    def add_user_tag(cls, user, tag):
        user_tag = UserTag()
        user_tag.user = user
        user_tag.tag = tag
        user_tag.put()
        
class Idea(BaseModel):
    """意见建议"""
    user = db.ReferenceProperty(User)
    content = db.StringProperty(multiline=True)
    create_time = db.DateTimeProperty(auto_now_add=True)
    
    @classmethod
    def add_Idea(cls, user_name, content):
        user = User.get_user_by_name(user_name)
        idea = Idea()
        idea.content = content
        idea.user = user
        idea.put()
        
    @classmethod
    def get_all_idea_by_create_time(cls):
        return Idea.all().order('-create_time').fetch(limit=1000)

class UserLikeColor(BaseModel):
    """用户，喜欢的颜色之间多对多的关系"""
    user = db.ReferenceProperty(User)
    likecolor = db.ReferenceProperty(Color)
    
    @classmethod
    def insert_or_like_color_by_username_and_colorvalue(cls, name, value):
        user = User.get_user_by_name(name)
        values = [color for color in user.like_colors() if color.value == value]
        if len(values) > 0:
            return False
        
        selected_color_values = Color.all().filter('value =', value)
        if selected_color_values.count() is 0:
            color = Color(value=value)
            color.likecolors_col = LikeColors.get_default_LikeColors()
            color.put()
        else:
            color = selected_color_values[0]
            color.likecount += 1
            color.put()
            
        user.like_color_count += 1
        user.put()
        
        userlikecolor = UserLikeColor()
        userlikecolor.user = user
        userlikecolor.likecolor = color
        userlikecolor.put()
            
        return True
    
class AppConfig(BaseModel):
    """应用配置项"""
    intro = db.StringProperty(default="ai-color")
    hotcolor_count_onepage = db.IntegerProperty(default=6)
    
    @classmethod
    def get_default_appconfig(cls):
        """获取默认应用配置"""
        default_appconfig = AppConfig.all().get()
        if default_appconfig is None:
            default_appconfig = AppConfig()
            default_appconfig.put()

        return default_appconfig