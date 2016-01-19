# -*- coding: utf-8 -*-
from django.shortcuts import render
from django.http import HttpResponse
from django.template import RequestContext
from django.db.models.query_utils import Q
from django.contrib.auth.decorators import login_required
from libs.sendmail import send_mail
from KPI.models import table,table_detail
import simplejson

import sys
reload(sys)
sys.setdefaultencoding('utf-8')

@login_required
def KPI_table(request):
    path = request.path.split('/')[1]
    return render(request, 'KPI/KPI_table.html',{'user':'%s%s' % (request.user.last_name,request.user.first_name),
                                                 'path1':'KPI',
                                                 'path2':path,
                                                 'page_name1':u'绩效管理',
                                                 'page_name2':u'绩效考评'},
                                                context_instance=RequestContext(request))

@login_required
def KPI_table_data(request):
    sEcho =  request.POST.get('sEcho') #标志，直接返回
    iDisplayStart = int(request.POST.get('iDisplayStart'))#第几行开始
    iDisplayLength = int(request.POST.get('iDisplayLength'))#显示多少行
    iSortCol_0 = int(request.POST.get("iSortCol_0"))#排序行号
    sSortDir_0 = request.POST.get('sSortDir_0')#asc/desc
    sSearch = request.POST.get('sSearch')#高级搜索

    aaData = []
    sort = ['KPI_name','final_score','supervisor_comment','status']

    if  sSortDir_0 == 'asc':
        if sSearch == '':
            result_data = table.objects.filter(name=request.user.first_name).order_by(sort[iSortCol_0])[iDisplayStart:iDisplayStart+iDisplayLength]
            iTotalRecords = table.objects.filter(name=request.user.first_name).count()
        else:
            result_data = table.objects.filter(name=request.user.first_name).filter(Q(KPI_name__contains=sSearch) | \
                                                    Q(final_score__contains=sSearch) | \
                                                    Q(status__contains=sSearch)) \
                                                    .order_by(sort[iSortCol_0])[iDisplayStart:iDisplayStart+iDisplayLength]
            iTotalRecords = table.objects.filter(name=request.user.first_name).filter(Q(KPI_name__contains=sSearch) | \
                                                    Q(final_score__contains=sSearch) | \
                                                    Q(status__contains=sSearch)).count()
    else:
        if sSearch == '':
            result_data = table.objects.filter(name=request.user.first_name).order_by(sort[iSortCol_0]).reverse()[iDisplayStart:iDisplayStart+iDisplayLength]
            iTotalRecords = table.objects.filter(name=request.user.first_name).count()
        else:
            result_data = table.objects.filter(name=request.user.first_name).filter(Q(KPI_name__contains=sSearch) | \
                                                    Q(final_score__contains=sSearch) | \
                                                    Q(status__contains=sSearch)) \
                                                    .order_by(sort[iSortCol_0]).reverse()[iDisplayStart:iDisplayStart+iDisplayLength]
            iTotalRecords = table.objects.filter(name=request.user.first_name).filter(Q(KPI_name__contains=sSearch) | \
                                                    Q(final_score__contains=sSearch) | \
                                                    Q(status__contains=sSearch)).count()

    for i in  result_data:
        aaData.append({
                       '0':i.KPI_name,
                       '1':i.final_score,
                       '2':i.supervisor_comment,
                       '3':i.status,
                       '4':i.name,
                       '5':i.id
                      })
    result = {'sEcho':sEcho,
               'iTotalRecords':iTotalRecords,
               'iTotalDisplayRecords':iTotalRecords,
               'aaData':aaData
    }
    return HttpResponse(simplejson.dumps(result),content_type="application/json")

@login_required
def KPI_set_session(request):
    KPI_name = request.POST.get('KPI_name')
    name = request.POST.get('name')
    request.session['KPI'] = KPI_name,name
    return HttpResponse(simplejson.dumps('OK'),content_type="application/json")

@login_required
def KPI_table_detail(request):
    KPI_name = request.session.get('KPI_name')
    name = request.session.get('name')
    orm = table.objects.filter(KPI_name=KPI_name).filter(name=name)
    for i in orm:
        print i.status
        status = i.status
    try:
        if status:pass
    except Exception:
        status = '员工设定目标'
    return render(request, 'KPI/KPI_table_detail.html',{'user':'%s%s' % (request.user.last_name,request.user.first_name),
                                                 'path1':'KPI',
                                                 'path2':'KPI_table',
                                                 'page_name1':u'绩效管理',
                                                 'page_name2':u'绩效考评',
                                                 'status':status},
                                                context_instance=RequestContext(request))

@login_required
def KPI_table_detail_data(request):
    sEcho =  request.POST.get('sEcho') #标志，直接返回
    iDisplayStart = int(request.POST.get('iDisplayStart'))#第几行开始
    iDisplayLength = int(request.POST.get('iDisplayLength'))#显示多少行
    iSortCol_0 = int(request.POST.get("iSortCol_0"))#排序行号
    sSortDir_0 = request.POST.get('sSortDir_0')#asc/desc
    sSearch = request.POST.get('sSearch')#高级搜索

    if request.session.get('KPI'):
        KPI_name = request.session.get('KPI')[0]
        name = request.session.get('KPI')[1]
    else:
        result = {'sEcho':sEcho,
               'iTotalRecords':0,
               'iTotalDisplayRecords':0,
               'aaData':[]
        }
        return HttpResponse(simplejson.dumps(result),content_type="application/json")

    aaData = []
    sort = ['KPI_name','final_score','objective','description','weight','self_report_value','self_report_score',
            'supervisor_report_value','supervisor_report_score','principal_report_value','principal_report_score']

    if  sSortDir_0 == 'asc':
        if sSearch == '':
            result_data = table_detail.objects.filter(KPI_name=KPI_name).filter(name=name).order_by(sort[iSortCol_0])[iDisplayStart:iDisplayStart+iDisplayLength]
            iTotalRecords = table_detail.objects.filter(KPI_name=KPI_name).filter(name=name).count()
        else:
            result_data = table_detail.objects.filter(KPI_name=KPI_name).filter(name=name).filter(Q(KPI_name__contains=sSearch) | \
                                                    Q(final_score__contains=sSearch) | \
                                                    Q(objective__contains=sSearch) | \
                                                    Q(description__contains=sSearch) | \
                                                    Q(weight__contains=sSearch) | \
                                                    Q(self_report_value__contains=sSearch) | \
                                                    Q(self_report_score__contains=sSearch) | \
                                                    Q(supervisor_report_value__contains=sSearch) | \
                                                    Q(supervisor_report_score__contains=sSearch) | \
                                                    Q(principal_report_value__contains=sSearch) | \
                                                    Q(principal_report_score__contains=sSearch)) \
                                                    .order_by(sort[iSortCol_0])[iDisplayStart:iDisplayStart+iDisplayLength]
            iTotalRecords = table_detail.objects.filter(KPI_name=KPI_name).filter(name=name).filter(Q(KPI_name__contains=sSearch) | \
                                                    Q(final_score__contains=sSearch) | \
                                                    Q(objective__contains=sSearch) | \
                                                    Q(description__contains=sSearch) | \
                                                    Q(weight__contains=sSearch) | \
                                                    Q(self_report_value__contains=sSearch) | \
                                                    Q(self_report_score__contains=sSearch) | \
                                                    Q(supervisor_report_value__contains=sSearch) | \
                                                    Q(supervisor_report_score__contains=sSearch) | \
                                                    Q(principal_report_value__contains=sSearch) | \
                                                    Q(principal_report_score__contains=sSearch)).count()
    else:
        if sSearch == '':
            result_data = table_detail.objects.filter(KPI_name=KPI_name).filter(name=name).order_by(sort[iSortCol_0]).reverse()[iDisplayStart:iDisplayStart+iDisplayLength]
            iTotalRecords = table_detail.objects.filter(KPI_name=KPI_name).filter(name=name).count()
        else:
            result_data = table_detail.objects.filter(KPI_name=KPI_name).filter(name=name).filter(Q(KPI_name__contains=sSearch) | \
                                                    Q(final_score__contains=sSearch) | \
                                                    Q(objective__contains=sSearch) | \
                                                    Q(description__contains=sSearch) | \
                                                    Q(weight__contains=sSearch) | \
                                                    Q(self_report_value__contains=sSearch) | \
                                                    Q(self_report_score__contains=sSearch) | \
                                                    Q(supervisor_report_value__contains=sSearch) | \
                                                    Q(supervisor_report_score__contains=sSearch) | \
                                                    Q(principal_report_value__contains=sSearch) | \
                                                    Q(principal_report_score__contains=sSearch)) \
                                                    .order_by(sort[iSortCol_0]).reverse()[iDisplayStart:iDisplayStart+iDisplayLength]
            iTotalRecords = table_detail.objects.filter(KPI_name=KPI_name).filter(name=name).filter(Q(KPI_name__contains=sSearch) | \
                                                    Q(final_score__contains=sSearch) | \
                                                    Q(objective__contains=sSearch) | \
                                                    Q(description__contains=sSearch) | \
                                                    Q(weight__contains=sSearch) | \
                                                    Q(self_report_value__contains=sSearch) | \
                                                    Q(self_report_score__contains=sSearch) | \
                                                    Q(supervisor_report_value__contains=sSearch) | \
                                                    Q(supervisor_report_score__contains=sSearch) | \
                                                    Q(principal_report_value__contains=sSearch) | \
                                                    Q(principal_report_score__contains=sSearch)).count()

    for i in  result_data:
        aaData.append({
                       '0':i.objective,
                       '1':i.description,
                       '2':i.weight,
                       '3':i.self_report_value,
                       '4':i.self_report_score,
                       '5':i.supervisor_report_value,
                       '6':i.supervisor_report_score,
                       '7':i.principal_report_value,
                       '8':i.principal_report_score,
                       '9':i.KPI_name,
                       '10':i.name,
                       '11':i.id
                      })
    result = {'sEcho':sEcho,
               'iTotalRecords':iTotalRecords,
               'iTotalDisplayRecords':iTotalRecords,
               'aaData':aaData
    }
    return HttpResponse(simplejson.dumps(result),content_type="application/json")