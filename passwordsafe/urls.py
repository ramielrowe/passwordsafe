from django.conf.urls import patterns, include, url

import safe.urls


urlpatterns = patterns('',
    url(r'', include(safe.urls, app_name='safe', namespace='safe'))
)
