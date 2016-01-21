# -*- coding: utf-8 -*-
from django.shortcuts import render
from django.http import HttpResponse
from django.template import RequestContext
from django.db.models.query_utils import Q
from django.contrib.auth.decorators import login_required
from libs.sendmail import send_mail
from KPI.models import table,table_detail
from vacation.models import user_table
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
                                                 'page_name2':u'绩效考评',},
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
    sort = ['KPI_name','final_score','supervisor_comment','status','name','id']

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
        export = '''
                <a id="export" value="%s" class="btn btn-sm green">
                    生成Excel文件 <i class="fa fa-level-down"></i>
                </a>
            ''' % i.id
        aaData.append({
                       '0':i.KPI_name,
                       '1':i.final_score,
                       '2':i.status,
                       '3':export,
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
    status = request.POST.get('status')
    request.session['KPI'] = KPI_name,name
    if status == '员工设定目标':
        request.session['status'] = 1
    if status == '等待主管确认目标':
        request.session['status'] = 2
    if status == '员工自我评分':
        request.session['status'] = 3
    if status == '等待直属主管评分':
        request.session['status'] = 4
    if status == '等待部门负责人评分':
        request.session['status'] = 5
    return HttpResponse(simplejson.dumps('OK'),content_type="application/json")

@login_required
def KPI_table_detail(request):
    KPI_name = request.session.get('KPI')[0]
    name = request.session.get('KPI')[1]
    orm = table.objects.filter(KPI_name=KPI_name).filter(name=name)

    if len(orm):
        for i in orm:
            self_comment = i.self_comment.replace('\n','\\n')
            supervisor_comment = i.supervisor_comment.replace('\n','\\n')
            principal_comment = i.principal_comment.replace('\n','\\n')
    else:
        self_comment = ''
        supervisor_comment = ''
        principal_comment = ''
    # try:
    #     if status:pass
    # except Exception:
    #     status = '员工设定目标'
    return render(request, 'KPI/KPI_table_detail.html',{'user':'%s%s' % (request.user.last_name,request.user.first_name),
                                                 'path1':'KPI',
                                                 'path2':'KPI_table',
                                                 'page_name1':u'绩效管理',
                                                 'page_name2':u'绩效考评',
                                                 'self_comment':self_comment,
                                                 'supervisor_comment':supervisor_comment,
                                                 'principal_comment':principal_comment,
                                                 'KPI_name':KPI_name,
                                                 'name':name},
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

@login_required
def KPI_table_detail_save(request):
    KPI_name = request.session.get('KPI')[0]
    name = request.session.get('KPI')[1]
    objective = request.POST.get('objective')
    description = request.POST.get ('description')
    weight = request.POST.get('weight')
    self_report_value = request.POST.get('self_report_value')
    supervisor_report_value = request.POST.get('self_report_value')
    principal_report_value = request.POST.get('self_report_value')
    _id = request.POST.get('id')

    if not _id:
        orm = table_detail(KPI_name=KPI_name,name=name,objective=objective,description=description,weight=weight,
                           self_report_value=0,self_report_score=0,supervisor_report_value=0,supervisor_report_score=0,
                           principal_report_value=0,principal_report_score=0)
        try:
            orm.save()
            return HttpResponse(simplejson.dumps({'code':0,'msg':u'保存成功'}),content_type="application/json")
        except Exception,e:
            print e
            return HttpResponse(simplejson.dumps({'code':1,'msg':str(e)}),content_type="application/json")
    else:
        orm = table_detail.objects.get(id=_id)
        if self_report_value:
            orm.self_report_value = self_report_value
            orm.self_report_score = self_report_value / 100 * orm.weight
        if supervisor_report_value:
            orm.supervisor_report_value = supervisor_report_value
            orm.supervisor_report_score = supervisor_report_value / 100 * orm.weight
        if principal_report_value:
            orm.principal_report_value = principal_report_value
            orm.principal_report_score = principal_report_value / 100 * orm.weight
        orm.objective = objective
        orm.description = description
        orm.weight = weight
        try:
            orm.save()
            return HttpResponse(simplejson.dumps({'code':0,'msg':u'保存成功'}),content_type="application/json")
        except Exception,e:
            print e
            return HttpResponse(simplejson.dumps({'code':1,'msg':str(e)}),content_type="application/json")

@login_required
def KPI_table_detail_del(request):
    _id = request.POST.get('id')
    orm = table_detail.objects.get(id=_id)
    try:
        orm.delete()
        return HttpResponse(simplejson.dumps({'code':0,'msg':u'删除成功'}),content_type="application/json")
    except Exception,e:
        print e
        return HttpResponse(simplejson.dumps({'code':1,'msg':str(e)}),content_type="application/json")

@login_required
def KPI_table_detail_comment_save(request):
    self_comment = request.POST.get('self_comment')
    supervisor_comment = request.POST.get('supervisor_comment')
    principal_comment = request.POST.get('principal_comment')

    KPI_name = request.session.get('KPI')[0]
    name = request.session.get('KPI')[1]
    orm = table.objects.filter(KPI_name=KPI_name).filter(name=name)

    if len(orm):
        for i in orm:
            if self_comment:
                i.self_comment = self_comment
            if supervisor_comment:
                i.supervisor_comment = supervisor_comment
            if principal_comment:
                i.principal_comment = principal_comment
            try:
                i.save()
                return HttpResponse(simplejson.dumps({'code':0,'msg':u'保存成功'}),content_type="application/json")
            except Exception,e:
                print e
                return HttpResponse(simplejson.dumps({'code':1,'msg':str(e)}),content_type="application/json")
    else:
        return HttpResponse(simplejson.dumps({'code':1,'msg':u'保存失败'}),content_type="application/json")

@login_required
def KPI_table_detail_commit(request):
    KPI_name = request.POST.get('KPI_name')
    name = request.POST.get('name')
    status = request.POST.get('status')

    orm = table.objects.filter(KPI_name=KPI_name).filter(name=name)
    if len(orm):
        for i in orm:
            if status == '1':
                i.status = '等待主管确认目标'
                vacation_user_table_orm = user_table.objects.get(name=name)
                i.commit_now = vacation_user_table_orm.supervisor
                vacation_user_table_orm = user_table.objects.get(name=i.commit_now)
                vacation_user_table_orm.has_KPI_commit += 1
                if vacation_user_table_orm.KPI_commit_id:
                    vacation_user_table_orm.KPI_commit_id += ',' + str(i.id)
                else:
                    vacation_user_table_orm.KPI_commit_id = str(i.id)
                try:
                    vacation_user_table_orm.save()
                    i.save()
                    return HttpResponse(simplejson.dumps({'code':0,'msg':u'提交成功'}),content_type="application/json")
                except Exception,e:
                    print e
                    return HttpResponse(simplejson.dumps({'code':0,'msg':str(e)}),content_type="application/json")
