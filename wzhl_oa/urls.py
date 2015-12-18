from django.conf.urls import patterns, include, url
from main.views import *
from login.views import *
from order_form.views import *
from user_manage.views import *
from vacation.views import *
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
    url(r'^summary/', summary),
    url(r'^vacation_table/', vacation_table),
    url(r'^vacation_table_data/', vacation_table_data),
    url(r'^vacation_table_save/', vacation_table_save),
    url(r'^vacation_table_del/', vacation_table_del),
    url(r'^vacation_refresh/', vacation_refresh),
    url(r'^vacation_apply/', vacation_apply),
    url(r'^vacation_apply_data/', vacation_apply_data),
    url(r'^vacation_apply_save/', vacation_apply_save),
    url(r'^vacation_apply_del/', vacation_apply_del),
    url(r'^vacation_approve_alert/', vacation_approve_alert),
    url(r'^vacation_approve/', vacation_approve),
    url(r'^vacation_approve_data/', vacation_approve_data),
    url(r'^vacation_approve_process/', vacation_approve_process),
    url(r'^vacation_log/', vacation_log),
    url(r'^vacation_log_data/', vacation_log_data),
    url(r'^vacation_export_excel/', vacation_export_excel),
)
