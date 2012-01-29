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

urlpatterns = patterns('',
)

urlpatterns += patterns('',
    (r'^$', 'icolor.views.index'),
    (r'^(?P<page_index>\d+)$', 'icolor.views.index'),
    (r'^pick', 'icolor.views.pick'),
    (r'^wall$', 'icolor.views.wall'),
    (r'^detail/(?P<color_id>\d+)$', 'icolor.views.detail'),
    (r'^about$', 'icolor.views.about'),
    (r'^like/(?P<color_id>\d+)$', 'icolor.views.like'),
    (r'^comment/(?P<color_id>\d+)$', 'icolor.views.comment'),
    (r'^share$', 'icolor.views.share'),
    (r'^addtag$', 'icolor.views.addtag'),
    (r'^tag/(?P<tag_id>\d+)$', 'icolor.views.tag'),
    (r'^guestbook$', 'icolor.views.guestbook'),
    (r'^login$', 'icolor.views.login'),
    (r'^logout$', 'icolor.views.logout'),
    (r'^login_check', 'icolor.views.login_check'),
)
