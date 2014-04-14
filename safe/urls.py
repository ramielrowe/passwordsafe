from django.conf.urls import patterns, url

urlpatterns = patterns('',
    url(r'^$', 'safe.views.index', name='index'),
    url(r'^register/$', 'safe.views.register', name='register'),
    url(r'^login/$', 'safe.views.login', name='login'),
    url(r'^logout/$', 'safe.views.logout', name='logout'),
    url(r'^create_password/$', 'safe.views.create_password', name='create_password'),
    url(r'^show_password/$', 'safe.views.show_password', name='show_password'),
    url(r'^delete_password/$', 'safe.views.delete_password', name='delete_password'),
)
