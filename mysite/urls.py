# Copyright 2008 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from django.conf.urls.defaults import *

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^admin/', include(admin.site.urls)),
)

urlpatterns += patterns('',
    (r'^$', 'mysite.views.index'),
    (r'^(?P<page_index>\d+)$', 'mysite.views.index'),
    (r'^pick', 'mysite.views.pick'),
    (r'^wall$', 'mysite.views.wall'),
    (r'^detail/(?P<color_id>\d+)$', 'mysite.views.detail'),
    (r'^about$', 'mysite.views.about'),
    (r'^like/(?P<color_id>\d+)$', 'mysite.views.like'),
    (r'^comment/(?P<color_id>\d+)$', 'mysite.views.comment'),
    (r'^share$', 'mysite.views.share'),
    (r'^addtag$', 'mysite.views.addtag'),
    (r'^tag/(?P<tag_id>\d+)$', 'mysite.views.tag'),
    (r'^guestbook$', 'mysite.views.guestbook'),
    (r'^login$', 'mysite.views.login'),
    (r'^logout$', 'mysite.views.logout'),
    (r'^login_check', 'mysite.views.login_check'),
    (r'^weibo_login', 'mysite.views.weibo_login'),
)
