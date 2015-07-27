from django.conf.urls import patterns, include, url
from order_form.views import order_form
# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'wzhl_oa.views.home', name='home'),
    # url(r'^wzhl_oa/', include('wzhl_oa.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # url(r'^admin/', include(admin.site.urls)),
    url(r'^$', order_form),
    url(r'^order_form/', order_form),
)
