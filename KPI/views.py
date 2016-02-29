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
                       '2':i.status_interface,
                       '3':export,
                       '4':i.name,
                       '5':i.status,
                       '6':i.id
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
    if int(status) == 1:
        request.session['status'] = 1
    if int(status) == 2:
        request.session['status'] = 2
    if int(status) == 3:
        request.session['status'] = 3
    if int(status) == 4:
        request.session['status'] = 4
    if int(status) == 5:
        request.session['status'] = 5
    if int(status) == 6:
        request.session['status'] = 6
    return HttpResponse(simplejson.dumps('OK'),content_type="application/json")

@login_required
def KPI_table_detail(request):
    if request.session.get('KPI'):
        KPI_name = request.session.get('KPI')[0]
        name = request.session.get('KPI')[1]
    else:
        KPI_name = ''
        name = ''
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
                                                 'path2':'',
                                                 'page_name1':u'绩效管理',
                                                 'page_name2':u'绩效考评详情',
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
    status = request.POST.get('status')
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
        if int(status) == 3:
            self_report_value = int(request.POST.get('grade'))
            orm.self_report_value = self_report_value
            orm.self_report_score = float(self_report_value) / 100 * orm.weight
        if int(status) == 4:
            supervisor_report_value = int(request.POST.get('grade'))
            orm.supervisor_report_value = supervisor_report_value
            orm.supervisor_report_score = float(supervisor_report_value) / 100 * orm.weight
        if int(status) == 5:
            principal_report_value = int(request.POST.get('grade'))
            orm.principal_report_value = principal_report_value
            orm.principal_report_score = float(principal_report_value) / 100 * orm.weight
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
    flag = request.POST.get('flag')

    orm = table.objects.filter(KPI_name=KPI_name).filter(name=name)
    if len(orm):
        for i in orm:
            if flag == '0':
                i.status = 2
                vacation_user_table_orm = user_table.objects.get(name=name)
                i.commit_now = vacation_user_table_orm.supervisor
                i.status_interface = '等待 %s 确认目标' % vacation_user_table_orm.supervisor

                vacation_user_table_orm = user_table.objects.get(name=i.commit_now)
                supervisor_email = vacation_user_table_orm.email
                vacation_user_table_orm.has_KPI_commit += 1
                if vacation_user_table_orm.KPI_commit_id:
                    vacation_user_table_orm.KPI_commit_id += ',' + str(i.id)
                else:
                    vacation_user_table_orm.KPI_commit_id = str(i.id)
                try:
                    i.save()
                    vacation_user_table_orm.save()
                    send_mail(to_addr=supervisor_email,subject='绩效审核提醒',body='<h3>有一个绩效事件等待您的处理，请在OA系统中查看。</h3><br>OA链接：http://oa.xiaoquan.com/PKI_table_approve/</br><br>此邮件为自动发送的提醒邮件，请勿回复。')
                    return HttpResponse(simplejson.dumps({'code':0,'msg':u'提交成功'}),content_type="application/json")
                except Exception,e:
                    print e
                    return HttpResponse(simplejson.dumps({'code':0,'msg':str(e)}),content_type="application/json")
            else:

                vacation_user_table_orm = user_table.objects.get(name=name)
                if vacation_user_table_orm.supervisor == vacation_user_table_orm.principal:
                    i.status = 5
                else:
                    i.status = 4
                i.commit_now = vacation_user_table_orm.supervisor
                i.status_interface = '等待 %s 评分' % vacation_user_table_orm.supervisor

                vacation_user_table_orm = user_table.objects.get(name=i.commit_now)
                supervisor_email = vacation_user_table_orm.email
                vacation_user_table_orm.has_KPI_commit += 1

                try:
                    i.save()
                    vacation_user_table_orm.save()
                    send_mail(to_addr=supervisor_email,subject='绩效审核提醒',body='<h3>有一个绩效事件等待您的处理，请在OA系统中查看。</h3><br>OA链接：http://oa.xiaoquan.com/PKI_table_approve/</br><br>此邮件为自动发送的提醒邮件，请勿回复。')
                    return HttpResponse(simplejson.dumps({'code':0,'msg':u'提交成功'}),content_type="application/json")
                except Exception,e:
                    print e
                    return HttpResponse(simplejson.dumps({'code':0,'msg':str(e)}),content_type="application/json")


@login_required
def KPI_approve_alert(request):
    orm = user_table.objects.get(name=request.user.first_name)
    PKI_alert_num = orm.has_KPI_commit
    if PKI_alert_num > 0:
        msg = '有%s个绩效事件等待您的审核' % PKI_alert_num
        return HttpResponse(simplejson.dumps({'code':0,'msg':msg}),content_type="application/json")
    else:
        return HttpResponse(simplejson.dumps({'code':1}),content_type="application/json")

@login_required
def KPI_table_approve(request):
    path = request.path.split('/')[1]
    return render(request, 'KPI/KPI_table_approve.html',{'user':'%s%s' % (request.user.last_name,request.user.first_name),
                                                 'path1':'KPI',
                                                 'path2':path,
                                                 'page_name1':u'绩效管理',
                                                 'page_name2':u'绩效考评',},
                                                context_instance=RequestContext(request))

@login_required
def KPI_table_approve_data(request):
    sEcho =  request.POST.get('sEcho') #标志，直接返回
    iDisplayStart = int(request.POST.get('iDisplayStart'))#第几行开始
    iDisplayLength = int(request.POST.get('iDisplayLength'))#显示多少行
    iSortCol_0 = int(request.POST.get("iSortCol_0"))#排序行号
    sSortDir_0 = request.POST.get('sSortDir_0')#asc/desc
    sSearch = request.POST.get('sSearch')#高级搜索

    aaData = []
    sort = ['KPI_name','final_score','supervisor_comment','status','name','id']

    orm_KPI_commit_id = user_table.objects.get(name=request.user.first_name)
    KPI_commit_id_list = orm_KPI_commit_id.KPI_commit_id.split(',')
    if KPI_commit_id_list != [u'']:
        KPI_commit_id_list = map(lambda x:int(x), KPI_commit_id_list)
    else:
        KPI_commit_id_list = []

    if  sSortDir_0 == 'asc':
        if sSearch == '':
            result_data = table.objects.filter(Q(commit_now=request.user.first_name) | Q(id__in=KPI_commit_id_list)).order_by(sort[iSortCol_0])[iDisplayStart:iDisplayStart+iDisplayLength]
            iTotalRecords = table.objects.filter(Q(commit_now=request.user.first_name) | Q(id__in=KPI_commit_id_list)).count()
        else:
            result_data = table.objects.filter(Q(commit_now=request.user.first_name) | Q(id__in=KPI_commit_id_list)).filter(Q(KPI_name__contains=sSearch) | \
                                                    Q(final_score__contains=sSearch) | \
                                                    Q(status__contains=sSearch)) \
                                                    .order_by(sort[iSortCol_0])[iDisplayStart:iDisplayStart+iDisplayLength]
            iTotalRecords = table.objects.filter(Q(commit_now=request.user.first_name) | Q(id__in=KPI_commit_id_list)).filter(Q(KPI_name__contains=sSearch) | \
                                                    Q(final_score__contains=sSearch) | \
                                                    Q(status__contains=sSearch)).count()
    else:
        if sSearch == '':
            result_data = table.objects.filter(Q(commit_now=request.user.first_name) | Q(id__in=KPI_commit_id_list)).order_by(sort[iSortCol_0]).reverse()[iDisplayStart:iDisplayStart+iDisplayLength]
            iTotalRecords = table.objects.filter(Q(commit_now=request.user.first_name) | Q(id__in=KPI_commit_id_list)).count()
        else:
            result_data = table.objects.filter(Q(commit_now=request.user.first_name) | Q(id__in=KPI_commit_id_list)).filter(Q(KPI_name__contains=sSearch) | \
                                                    Q(final_score__contains=sSearch) | \
                                                    Q(status__contains=sSearch)) \
                                                    .order_by(sort[iSortCol_0]).reverse()[iDisplayStart:iDisplayStart+iDisplayLength]
            iTotalRecords = table.objects.filter(Q(commit_now=request.user.first_name) | Q(id__in=KPI_commit_id_list)).filter(Q(KPI_name__contains=sSearch) | \
                                                    Q(final_score__contains=sSearch) | \
                                                    Q(status__contains=sSearch)).count()



    for i in  result_data:
        export = '''
                <a id="export" value="%s" class="btn btn-sm green">
                    生成Excel文件 <i class="fa fa-level-down"></i>
                </a>
            ''' % i.id
        aaData.append({
                       '0':i.name,
                       '1':i.KPI_name,
                       '2':i.final_score,
                       '3':i.status_interface,
                       '4':export,
                       '5':i.status,
                       '6':i.id
                      })
    result = {'sEcho':sEcho,
               'iTotalRecords':iTotalRecords,
               'iTotalDisplayRecords':iTotalRecords,
               'aaData':aaData
    }
    return HttpResponse(simplejson.dumps(result),content_type="application/json")

@login_required
def KPI_table_detail_approve(request):
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
    return render(request, 'KPI/KPI_table_detail_approve.html',{'user':'%s%s' % (request.user.last_name,request.user.first_name),
                                                 'path1':'KPI',
                                                 'path2':'',
                                                 'page_name1':u'绩效管理',
                                                 'page_name2':u'绩效考评详情',
                                                 'self_comment':self_comment,
                                                 'supervisor_comment':supervisor_comment,
                                                 'principal_comment':principal_comment,
                                                 'KPI_name':KPI_name,
                                                 'name':name},
                                                context_instance=RequestContext(request))

@login_required
def KPI_table_detail_approve_commit(request):
    KPI_name = request.POST.get('KPI_name')
    name = request.POST.get('name')
    flag = request.POST.get('flag')
    commit = request.POST.get('commit')

    orm = table.objects.filter(KPI_name=KPI_name).filter(name=name)
    if len(orm):
        for i in orm:
            if not int(flag):
                if int(commit):
                    i.status = 3
                    i.commit_now = ''
                    i.status_interface = '员工自我评分'

                    vacation_user_table_orm = user_table.objects.get(name=name)
                    email = vacation_user_table_orm.email

                    vacation_user_table_orm = user_table.objects.get(name=request.user.first_name)
                    vacation_user_table_orm.has_KPI_commit -= 1
                    try:
                        i.save()
                        vacation_user_table_orm.save()
                        send_mail(to_addr=email,subject='绩效审核提醒',body='<h3>%s 通过了您设定的绩效目标，请在OA系统中查看。</h3><br>OA链接：http://oa.xiaoquan.com/PKI_table_approve/</br><br>此邮件为自动发送的提醒邮件，请勿回复。' % request.user.first_name)
                        return HttpResponse(simplejson.dumps({'code':0,'msg':u'提交成功'}),content_type="application/json")
                    except Exception,e:
                        print e
                        return HttpResponse(simplejson.dumps({'code':0,'msg':str(e)}),content_type="application/json")
                else:
                    i.status = 1
                    i.commit_now = ''
                    i.status_interface = '员工设定目标'

                    vacation_user_table_orm = user_table.objects.get(name=name)
                    email = vacation_user_table_orm.email

                    vacation_user_table_orm = user_table.objects.get(name=request.user.first_name)
                    vacation_user_table_orm.has_KPI_commit -= 1

                    reason = request.POST.get('reason')
                    try:
                        i.save()
                        vacation_user_table_orm.save()
                        send_mail(to_addr=email,subject='绩效审核提醒',body='<h3>%s 不通过您设定的绩效目标，请在OA系统中查看。</h3><br>拒绝理由：<font color="red">%s</font><br><br>OA链接：http://oa.xiaoquan.com/PKI_table_approve/</br><br>此邮件为自动发送的提醒邮件，请勿回复。' % (request.user.first_name,reason))
                        return HttpResponse(simplejson.dumps({'code':0,'msg':u'提交成功'}),content_type="application/json")
                    except Exception,e:
                        print e
                        return HttpResponse(simplejson.dumps({'code':0,'msg':str(e)}),content_type="application/json")
            else:
                if i.status == 4:
                    i.status = 5
                    vacation_user_table_orm = user_table.objects.get(name=name)
                    i.commit_now = vacation_user_table_orm.principal
                    i.status_interface = '等待 %s 评分' % vacation_user_table_orm.principal

                    vacation_user_table_orm = user_table.objects.get(name=i.commit_now)
                    principal_email = vacation_user_table_orm.email
                    vacation_user_table_orm.has_KPI_commit += 1

                    try:
                        i.save()
                        vacation_user_table_orm.save()
                        vacation_user_table_orm = user_table.objects.get(name=request.user.first_name)
                        vacation_user_table_orm.has_KPI_commit -= 1
                        vacation_user_table_orm.save()
                        send_mail(to_addr=principal_email,subject='绩效审核提醒',body='<h3>有一个绩效事件等待您的处理，请在OA系统中查看。</h3><br>OA链接：http://oa.xiaoquan.com/PKI_table_approve/</br><br>此邮件为自动发送的提醒邮件，请勿回复。')
                        return HttpResponse(simplejson.dumps({'code':0,'msg':u'提交成功'}),content_type="application/json")
                    except Exception,e:
                        print e
                        return HttpResponse(simplejson.dumps({'code':0,'msg':str(e)}),content_type="application/json")
                if i.status == 5:
                    if i.commit_now == request.user.first_name:
                        i.status = 6
                        i.commit_now = ''
                        i.status_interface = '已完成'

                        vacation_user_table_orm = user_table.objects.get(name=name)
                        email = vacation_user_table_orm.email

                        vacation_user_table_orm = user_table.objects.get(name=request.user.first_name)
                        vacation_user_table_orm.has_KPI_commit -= 1

                        final_score = request.POST.get('sum')
                        i.final_score = float(final_score)

                        try:
                            i.save()
                            vacation_user_table_orm.save()
                            send_mail(to_addr=email,subject='绩效审核提醒',body='<h3>您的绩效考评已完成，请在OA系统中查看。</h3><br>OA链接：http://oa.xiaoquan.com/PKI_table_approve/</br><br>此邮件为自动发送的提醒邮件，请勿回复。')
                            return HttpResponse(simplejson.dumps({'code':0,'msg':u'提交成功'}),content_type="application/json")
                        except Exception,e:
                            print e
                            return HttpResponse(simplejson.dumps({'code':0,'msg':str(e)}),content_type="application/json")
                    else:
                        return HttpResponse(simplejson.dumps({'code':0,'msg':'当前审核人不是您'}),content_type="application/json")