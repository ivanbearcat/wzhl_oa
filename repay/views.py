# -*- coding: utf-8 -*-
from django.shortcuts import render
from django.http import HttpResponse
from django.template import RequestContext
from django.db.models.query_utils import Q
from repay.models import budget, log
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from libs.common import int_format
import json, re
from django.db import transaction

@login_required
def budget_table(request):
    path = request.path.split('/')[1]
    if not request.user.has_perm('repay.can_view'):
        return render(request,'public/no_passing.html')
    return render(request, 'repay/budget_table.html',{'user':'%s%s' % (request.user.last_name,request.user.first_name),
                                                       'path1':'repay',
                                                       'path2':path,
                                                       'page_name1':u'报销管理',
                                                       'page_name2':u'预算表'},context_instance=RequestContext(request))



@login_required
def budget_table_data(request):
    sEcho =  request.POST.get('sEcho') #标志，直接返回
    iDisplayStart = int(request.POST.get('iDisplayStart'))#第几行开始
    iDisplayLength = int(request.POST.get('iDisplayLength'))#显示多少行
    iSortCol_0 = int(request.POST.get("iSortCol_0"))#排序行号
    sSortDir_0 = request.POST.get('sSortDir_0')#asc/desc
    sSearch = request.POST.get('sSearch')#高级搜索

    aaData = []
    sort = ['date','department','budget_class','budget_summary','budget_used','budget_available','budget_added']

    if  sSortDir_0 == 'asc':
        if sSearch == '':
            result_data = budget.objects.all().order_by(sort[iSortCol_0])[iDisplayStart:iDisplayStart+iDisplayLength]
            iTotalRecords = budget.objects.all().count()
        else:
            result_data = budget.objects.filter(Q(date__contains=sSearch) | \
                                                    Q(department__contains=sSearch) | \
                                                    Q(budget_class__contains=sSearch)) \
                                                    .order_by(sort[iSortCol_0])[iDisplayStart:iDisplayStart+iDisplayLength]
            iTotalRecords = budget.objects.filter(Q(date__contains=sSearch) | \
                                                    Q(department__contains=sSearch) | \
                                                    Q(budget_class__contains=sSearch)).count()
    else:
        if sSearch == '':
            result_data = budget.objects.all().order_by(sort[iSortCol_0]).reverse()[iDisplayStart:iDisplayStart+iDisplayLength]
            iTotalRecords = budget.objects.all().count()
        else:
            result_data = budget.objects.filter(Q(date__contains=sSearch) | \
                                                    Q(department__contains=sSearch) | \
                                                    Q(budget_class__contains=sSearch)) \
                                                    .order_by(sort[iSortCol_0]).reverse()[iDisplayStart:iDisplayStart+iDisplayLength]
            iTotalRecords = budget.objects.filter(Q(date__contains=sSearch) | \
                                                    Q(department__contains=sSearch) | \
                                                    Q(budget_class__contains=sSearch)).count()

    for i in  result_data:
        i_dict = {}
        i_dict['budget_summary'] = int_format(float('%.2f' % i.budget_summary))
        i_dict['budget_used'] = int_format(float('%.2f' % i.budget_used))
        i_dict['budget_available'] = int_format(float('%.2f' % i.budget_available))
        i_dict['budget_added'] = int_format(float('%.2f' % i.budget_added))
        for j in i_dict.keys():
            i_dict[j] = re.sub(r'\.(?P<d>\d)$','.\g<d>0',i_dict[j])


        aaData.append({
                       '0':str(i.date),
                       '1':i.department,
                       '2':i.budget_class,
                       '3':i_dict['budget_summary'],
                       '4':i_dict['budget_used'],
                       '5':i_dict['budget_available'],
                       '6':i_dict['budget_added'],
                       '7':i.id
                      })
    result = {'sEcho':sEcho,
               'iTotalRecords':iTotalRecords,
               'iTotalDisplayRecords':iTotalRecords,
               'aaData':aaData
    }
    return HttpResponse(json.dumps(result),content_type="application/json")




@login_required
@transaction.commit_on_success()
def budget_table_save(request):
    date = request.POST.get('date')
    department = request.POST.get('department')
    budget_class = request.POST.get('budget_class')
    budget_summary = request.POST.get('budget_summary')
    budget_added = request.POST.get('budget_added')
    _id = request.POST.get('id')
    print budget_added

    try:
        if not _id:
            orm = budget(date=date,department=department,budget_class=budget_class,budget_summary=float(budget_summary),\
                         budget_used=0.0,budget_available=float(budget_summary),budget_added=0.0)
            orm.save()

            comment = '给 <b>{0}</b> 设置了 <b>{1}</b> 额度的 <b>{2}</b>'.format(department, budget_summary, budget_class)
            orm_log = log(name=request.user.first_name,comment=comment)
            orm_log.save()

        else:
            orm = budget.objects.get(id=_id)
            orm.budget_added = orm.budget_added + float(budget_added)
            orm.save()

            comment = '给 <b>{0}</b> 追加了 <b>{1}</b> 额度的 <b>{2}</b>'.format(orm.department, budget_added, orm.budget_class)
            orm_log = log(name=request.user.first_name,comment=comment)
            orm_log.save()

        return HttpResponse(json.dumps({'code':0,'msg':u'保存成功'}),content_type="application/json")
    except Exception,e:
        print e
        return HttpResponse(json.dumps({'code':1,'msg':str(e)}),content_type="application/json")



@login_required
def repay_log(request):
    path = request.path.split('/')[1]
    if not request.user.has_perm('repay.can_view'):
        return render(request,'public/no_passing.html')
    return render(request,'repay/repay_log.html',{'user':request.user.username,
                                                   'path1':'repay',
                                                   'path2':path,
                                                   'page_name1':u'报销管理',
                                                   'page_name2':u'操作日志'},context_instance=RequestContext(request))



@login_required
def repay_log_data(request):
    sEcho =  request.POST.get('sEcho') #标志，直接返回
    iDisplayStart = int(request.POST.get('iDisplayStart'))#第几行开始
    iDisplayLength = int(request.POST.get('iDisplayLength'))#显示多少行
    iSortCol_0 = int(request.POST.get("iSortCol_0"))#排序行号
    sSortDir_0 = request.POST.get('sSortDir_0')#asc/desc
    sSearch = request.POST.get('sSearch')#高级搜索

    aaData = []
    sort = ['name','comment','apply_time','id']

    if  sSortDir_0 == 'asc':
        if sSearch == '':
            result_data = log.objects.all().order_by(sort[iSortCol_0])[iDisplayStart:iDisplayStart+iDisplayLength]
            iTotalRecords = log.objects.all().count()
        else:
            result_data = log.objects.filter(Q(name__contains=sSearch) | \
                                                Q(comment__contains=sSearch) | \
                                               Q(id__contains=sSearch)) \
                                            .order_by(sort[iSortCol_0])[iDisplayStart:iDisplayStart+iDisplayLength]
            iTotalRecords = log.objects.filter(Q(name__contains=sSearch) | \
                                                Q(comment__contains=sSearch) | \
                                               Q(id__contains=sSearch)).count()
    else:
        if sSearch == '':
            result_data = log.objects.all().order_by(sort[iSortCol_0]).reverse()[iDisplayStart:iDisplayStart+iDisplayLength]
            iTotalRecords = log.objects.all().count()
        else:
            result_data = log.objects.filter(Q(name__contains=sSearch) | \
                                                Q(comment__contains=sSearch) | \
                                               Q(id__contains=sSearch)) \
                                            .order_by(sort[iSortCol_0]).reverse()[iDisplayStart:iDisplayStart+iDisplayLength]
            iTotalRecords = log.objects.filter(Q(name__contains=sSearch) | \
                                                Q(comment__contains=sSearch) | \
                                               Q(id__contains=sSearch)).count()
    for i in  result_data:
        aaData.append({
                       '0':i.name,
                       '1':i.comment,
                       '2':str(i.apply_time),
                       '3':i.id
                      })
    result = {'sEcho':sEcho,
               'iTotalRecords':iTotalRecords,
               'iTotalDisplayRecords':iTotalRecords,
               'aaData':aaData
    }
    return HttpResponse(json.dumps(result),content_type="application/json")