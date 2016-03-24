from django.conf.urls import patterns, include, url
from wzhl_oa import settings
from main.views import *
from login.views import *
from order_form.views import *
from user_manage.views import *
from vacation.views import *
from assets.views import *
from KPI.views import *
from personal_information.views import *
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
    url(r'^media/(?P<path>.*)$', 'django.views.static.serve',{'document_root': settings.MEDIA_ROOT}),
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
    url(r'^order_form_star_save/', order_form_star_save),
    url(r'^order_form_del/', order_form_del),
    url(r'^summary/', summary),
    url(r'^vacation_table/', vacation_table),
    url(r'^vacation_table_data/', vacation_table_data),
    url(r'^vacation_table_save/', vacation_table_save),
    url(r'^vacation_table_del/', vacation_table_del),
    url(r'^vacation_refresh/', vacation_refresh),
    url(r'^vacation_apply/', vacation_apply),
    url(r'^vacation_apply_sub/', vacation_apply_sub),
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
    url(r'^refresh_subordinate/', refresh_subordinate),
    url(r'^assets_table/', assets_table),
    url(r'^assets_table_data/', assets_table_data),
    url(r'^assets_table_dropdown/', assets_table_dropdown),
    url(r'^assets_table_save/', assets_table_save),
    url(r'^assets_export_excel/', assets_export_excel),
    url(r'^assets_refresh/', assets_refresh),
    url(r'^assets_log/', assets_log),
    url(r'^assets_log_data/', assets_log_data),
    url(r'^KPI_table/', KPI_table),
    url(r'^KPI_table_data/', KPI_table_data),
    url(r'^KPI_table_export_all/', KPI_table_export_all),
    url(r'^KPI_set_session/', KPI_set_session),
    url(r'^KPI_table_detail/', KPI_table_detail),
    url(r'^KPI_table_detail_data/', KPI_table_detail_data),
    url(r'^KPI_table_detail_save/', KPI_table_detail_save),
    url(r'^KPI_table_detail_del/', KPI_table_detail_del),
    url(r'^KPI_table_detail_comment_save/', KPI_table_detail_comment_save),
    url(r'^KPI_table_detail_commit/', KPI_table_detail_commit),
    url(r'^KPI_approve_alert/', KPI_approve_alert),
    url(r'^KPI_table_approve/', KPI_table_approve),
    url(r'^KPI_table_approve_data/', KPI_table_approve_data),
    url(r'^KPI_table_detail_approve/', KPI_table_detail_approve),
    url(r'^KPI_table_detail_approve_commit/', KPI_table_detail_approve_commit),
    url(r'^KPI_upload_conf/',KPI_upload_conf),
    url(r'^create_excel/', create_excel),
    url(r'^personal_information_table/', personal_information_table),
    url(r'^personal_information_table_data/', personal_information_table_data),
    url(r'^personal_information_table_detail/', personal_information_table_detail),
    url(r'^personal_information_set_session/', personal_information_set_session),
    url(r'^personal_information_interview_data/', personal_information_interview_data),
    url(r'^personal_information_interview_set_session/', personal_information_interview_set_session),
)
