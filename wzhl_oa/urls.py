from django.conf.urls import patterns, include, url
from main.views import *
from login.views import *
from order_form.views import *
from user_manage.views import *
# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'wzhl_oa.views.home', name='home'),
    # url(r'^wzhl_oa/', include('wzhl_oa.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
    url(r'^$', login),
    url(r'^login_auth/', login_auth),
    url(r'^logout/', logout),
    url(r'^accounts/login/$',not_login),
    url(r'^main/', main),
    url(r'^chpasswd/', chpasswd),
    url(r'^post_chpasswd/', post_chpasswd),
    url(r'^order_form/', order_form),
    url(r'^order_form_data/', order_form_data),
    url(r'^order_form_dropdown/', order_form_dropdown),
    url(r'^order_form_save/', order_form_save),
    url(r'^order_form_del/', order_form_del),
)
