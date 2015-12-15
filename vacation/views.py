# -*- coding: utf-8 -*-
from django.shortcuts import render
from django.http import HttpResponse
from vacation.models import user_table,operation_log,state
from django.db.models.query_utils import Q
from django.utils.log import logger
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from libs.sendmail import send_mail
import simplejson,datetime

import sys
reload(sys)
sys.setdefaultencoding('utf-8')

@login_required
def vacation_table(request):
    path = request.path.split('/')[1]
    return render(request, 'vacation/vacation_table.html',{'user':'%s%s' % (request.user.last_name,request.user.first_name),
                                                       'path1':'vacation',
                                                       'path2':path,
                                                       'page_name1':u'请假管理',
                                                       'page_name2':u'总览表'})

@login_required
def vacation_table_data(request):
    sEcho =  request.POST.get('sEcho') #标志，直接返回
    iDisplayStart = int(request.POST.get('iDisplayStart'))#第几行开始
    iDisplayLength = int(request.POST.get('iDisplayLength'))#显示多少行
    iSortCol_0 = int(request.POST.get("iSortCol_0"))#排序行号
    sSortDir_0 = request.POST.get('sSortDir_0')#asc/desc
    sSearch = request.POST.get('sSearch')#高级搜索

    aaData = []
    sort = ['name','department','supervisor','principal','join_date','graduate_year','statutory_annual_leave_available',
            'statutory_annual_leave_used','statutory_annual_leave_total','company_annual_leave_available',
            'company_annual_leave_used','company_annual_leave_total','seasons_leave_available','seasons_leave_used',
            'seasons_leave_total','email','id']

    if  sSortDir_0 == 'asc':
        if sSearch == '':
            result_data = user_table.objects.all().order_by(sort[iSortCol_0])[iDisplayStart:iDisplayStart+iDisplayLength]
            iTotalRecords = user_table.objects.all().count()
        else:
            result_data = user_table.objects.filter(Q(name__contains=sSearch) | \
                                                    Q(department__contains=sSearch) | \
                                                    Q(supervisor__contains=sSearch) | \
                                                    Q(principal__contains=sSearch)) \
                                                    .order_by(sort[iSortCol_0])[iDisplayStart:iDisplayStart+iDisplayLength]
            iTotalRecords = user_table.objects.filter(Q(name__contains=sSearch) | \
                                                    Q(department__contains=sSearch) | \
                                                    Q(supervisor__contains=sSearch) | \
                                                    Q(principal__contains=sSearch)).count()
    else:
        if sSearch == '':
            result_data = user_table.objects.all().order_by(sort[iSortCol_0]).reverse()[iDisplayStart:iDisplayStart+iDisplayLength]
            iTotalRecords = user_table.objects.all().count()
        else:
            result_data = user_table.objects.filter(Q(name__contains=sSearch) | \
                                                    Q(department__contains=sSearch) | \
                                                    Q(supervisor__contains=sSearch) | \
                                                    Q(principal__contains=sSearch)) \
                                                    .order_by(sort[iSortCol_0]).reverse()[iDisplayStart:iDisplayStart+iDisplayLength]
            iTotalRecords = user_table.objects.filter(Q(name__contains=sSearch) | \
                                                    Q(department__contains=sSearch) | \
                                                    Q(supervisor__contains=sSearch) | \
                                                    Q(principal__contains=sSearch)).count()

    for i in  result_data:
        aaData.append({
                       '0':i.name,
                       '1':i.department,
                       '2':i.supervisor,
                       '3':i.principal,
                       '4':str(i.join_date).split('+')[0],
                       '5':str(i.graduate_year).split('+')[0],
                       '6':i.statutory_annual_leave_available,
                       '7':i.statutory_annual_leave_used,
                       '8':i.statutory_annual_leave_total,
                       '9':i.company_annual_leave_available,
                       '10':i.company_annual_leave_used,
                       '11':i.company_annual_leave_total,
                       '12':i.seasons_leave_available,
                       '13':i.seasons_leave_used,
                       '14':i.seasons_leave_total,
                       '15':i.email,
                       '16':i.id
                      })
    result = {'sEcho':sEcho,
               'iTotalRecords':iTotalRecords,
               'iTotalDisplayRecords':iTotalRecords,
               'aaData':aaData
    }
    return HttpResponse(simplejson.dumps(result),content_type="application/json")

@login_required
def vacation_table_save(request):
    name = request.POST.get('name')
    department = request.POST.get('department')
    supervisor = request.POST.get('supervisor')
    principal = request.POST.get('principal')
    join_date = request.POST.get('join_date')
    graduate_year = request.POST.get('graduate_year')
    email = request.POST.get('email')
    _id = request.POST.get('id')

    if not _id:
        today = datetime.datetime.now().date()

        #判断法定年假天数
        graduate_year_date_list = graduate_year.split('-')
        graduate_year_datetime = datetime.date(int(graduate_year_date_list[0]),int(graduate_year_date_list[1]),int(graduate_year_date_list[2]))

        if today < graduate_year_datetime+datetime.timedelta(+365):
            statutory_annual_leave_total = 0
        if graduate_year_datetime+datetime.timedelta(+365) < today <= graduate_year_datetime+datetime.timedelta(+3650):
            statutory_annual_leave_total = 5
        if graduate_year_datetime+datetime.timedelta(+3650) < today <= graduate_year_datetime+datetime.timedelta(+7300):
            statutory_annual_leave_total = 10
        if today > graduate_year_datetime+datetime.timedelta(+7300):
            statutory_annual_leave_total = 15

        statutory_annual_leave_available = statutory_annual_leave_total

        #判断公司年假天数
        join_date_list = join_date.split('-')
        join_date_datetime = datetime.date(int(join_date_list[0]),int(join_date_list[1]),int(join_date_list[2]))

        company_annual_leave_total = (today - join_date_datetime).days / 365
        company_annual_leave_available = company_annual_leave_total


        orm = user_table(name=name,department=department,supervisor=supervisor,principal=principal,join_date=join_date,graduate_year=graduate_year,
                         email=email,statutory_annual_leave_available=statutory_annual_leave_available,statutory_annual_leave_used=0,
                         statutory_annual_leave_total=statutory_annual_leave_total,company_annual_leave_available=company_annual_leave_available,
                         company_annual_leave_used=0,company_annual_leave_total=company_annual_leave_total,seasons_leave_available=1,
                         seasons_leave_used=0,seasons_leave_total=1,has_approve=0)

        try:
            orm.save()
            return HttpResponse(simplejson.dumps({'code':0,'msg':u'保存成功'}),content_type="application/json")
        except Exception,e:
            logger.error(e)
            return HttpResponse(simplejson.dumps({'code':1,'msg':str(e)}),content_type="application/json")
    else:
        orm = user_table.objects.get(id=_id)
        orm.name = name
        orm.department = department
        orm.supervisor = supervisor
        orm.principal = principal
        orm.join_date = join_date
        orm.graduate_year = graduate_year
        orm.email = email
        try:
            orm.save()
            return HttpResponse(simplejson.dumps({'code':0,'msg':u'保存成功'}),content_type="application/json")
        except Exception,e:
            logger.error(e)
            return HttpResponse(simplejson.dumps({'code':1,'msg':str(e)}),content_type="application/json")

@login_required
def vacation_table_del(request):
    _id = request.POST.get('id')
    orm = user_table.objects.get(id=_id)
    try:
        orm.delete()
        return HttpResponse(simplejson.dumps({'code':0,'msg':u'删除成功'}),content_type="application/json")
    except Exception,e:
        logger.error(e)
        return HttpResponse(simplejson.dumps({'code':1,'msg':str(e)}),content_type="application/json")

@login_required
def vacation_refresh(request):
    #每天0点5分刷新每个人各种假的天数
    today = datetime.datetime.now().date()

    orm = user_table.objects.all()
    for i in orm:
        graduate_year = i.graduate_year
        join_date = i.join_date

        #判断法定年假天数
        if today < graduate_year+datetime.timedelta(+365):
            statutory_annual_leave_total = 0
        if graduate_year+datetime.timedelta(+365) < today <= graduate_year+datetime.timedelta(+3650):
            statutory_annual_leave_total = 5
        if graduate_year+datetime.timedelta(+3650) < today <= graduate_year+datetime.timedelta(+7300):
            statutory_annual_leave_total = 10
        if today > graduate_year+datetime.timedelta(+7300):
            statutory_annual_leave_total = 15

        #判断公司年假天数
        company_annual_leave_total = (today - join_date).days / 365

        #刷新季度假
        if today.month == 1 or today.month == 4 or today.month == 7 or today.month == 10 and today.day == 1:
            i.seasons_leave_used = 0
            i.seasons_leave_available = 1

        i.company_annual_leave_total = company_annual_leave_total
        i.company_annual_leave_available = company_annual_leave_total - i.company_annual_leave_used
        i.statutory_annual_leave_total = statutory_annual_leave_total
        i.statutory_annual_leave_available = statutory_annual_leave_total - i.statutory_annual_leave_used

        try:
            i.save()
        except Exception,e:
            print e
            return HttpResponse('ERROR')
    return HttpResponse('OK')

@login_required
def vacation_apply(request):
    path = request.path.split('/')[1]
    try:
        orm = user_table.objects.get(name=request.user.first_name)
    except Exception:
        return render(request,'public/no_passing.html')
    return render(request, 'vacation/vacation_apply.html',{'user':'%s%s' % (request.user.last_name,request.user.first_name),
                                                       'path1':'vacation',
                                                       'path2':path,
                                                       'page_name1':u'请假管理',
                                                       'page_name2':u'请假申请',
                                                       'statutory_annual_leave_available':orm.statutory_annual_leave_available,
                                                       'company_annual_leave_available':orm.company_annual_leave_available,
                                                       'seasons_leave_available':orm.seasons_leave_available})

@login_required
def vacation_apply_data(request):
    sEcho =  request.POST.get('sEcho') #标志，直接返回
    iDisplayStart = int(request.POST.get('iDisplayStart'))#第几行开始
    iDisplayLength = int(request.POST.get('iDisplayLength'))#显示多少行
    iSortCol_0 = int(request.POST.get("iSortCol_0"))#排序行号
    sSortDir_0 = request.POST.get('sSortDir_0')#asc/desc
    sSearch = request.POST.get('sSearch')#高级搜索

    aaData = []
    sort = ['name','type','reason','apply_time','vacation_date','days','state_interface']

    if  sSortDir_0 == 'asc':
        if sSearch == '':
            result_data = state.objects.filter(name=request.user.first_name).order_by(sort[iSortCol_0])[iDisplayStart:iDisplayStart+iDisplayLength]
            iTotalRecords = state.objects.filter(name=request.user.first_name).count()
        else:
            result_data = state.objects.filter(name=request.user.first_name).filter(Q(name__contains=sSearch) | \
                                                    Q(type__contains=sSearch) | \
                                                    Q(vacation_date__contains=sSearch) | \
                                                    Q(days__contains=sSearch) | \
                                                    Q(state_interface__contains=sSearch)) \
                                                    .order_by(sort[iSortCol_0])[iDisplayStart:iDisplayStart+iDisplayLength]
            iTotalRecords = state.objects.filter(name=request.user.first_name).filter(Q(name__contains=sSearch) | \
                                                    Q(type__contains=sSearch) | \
                                                    Q(vacation_date__contains=sSearch) | \
                                                    Q(days__contains=sSearch) | \
                                                    Q(state_interface__contains=sSearch)).count()
    else:
        if sSearch == '':
            result_data = state.objects.filter(name=request.user.first_name).order_by(sort[iSortCol_0]).reverse()[iDisplayStart:iDisplayStart+iDisplayLength]
            iTotalRecords = state.objects.filter(name=request.user.first_name).count()
        else:
            result_data = state.objects.filter(name=request.user.first_name).filter(Q(name__contains=sSearch) | \
                                                    Q(type__contains=sSearch) | \
                                                    Q(vacation_date__contains=sSearch) | \
                                                    Q(days__contains=sSearch) | \
                                                    Q(state_interface__contains=sSearch)) \
                                                    .order_by(sort[iSortCol_0]).reverse()[iDisplayStart:iDisplayStart+iDisplayLength]
            iTotalRecords = state.objects.filter(name=request.user.first_name).filter(Q(name__contains=sSearch) | \
                                                    Q(type__contains=sSearch) | \
                                                    Q(vacation_date__contains=sSearch) | \
                                                    Q(days__contains=sSearch) | \
                                                    Q(state_interface__contains=sSearch)).count()

    for i in  result_data:
        aaData.append({
                       '0':i.name,
                       '1':i.type,
                       '2':i.reason,
                       '3':str(i.apply_time).split('+')[0],
                       '4':i.vacation_date,
                       '5':i.days,
                       '6':i.state,
                       '7':i.state_interface,
                       '8':i.id
                      })
    result = {'sEcho':sEcho,
               'iTotalRecords':iTotalRecords,
               'iTotalDisplayRecords':iTotalRecords,
               'aaData':aaData
    }
    return HttpResponse(simplejson.dumps(result),content_type="application/json")

@login_required
def vacation_apply_save(request):
    type = request.POST.get('type')
    reason = request.POST.get('reason')
    begin = request.POST.get('begin')
    end = request.POST.get('end')
    half_day = request.POST.get('half_day')

    if begin == end:
        days = 1
        vacation_date = begin
        if half_day:
            days = 0.5
            vacation_date = '%s %s' % (vacation_date,half_day)
    else:
        begin_list = begin.split('-')
        begin_datetime = datetime.date(int(begin_list[0]),int(begin_list[1]),int(begin_list[2]))
        end_list = end.split('-')
        end_datetime = datetime.date(int(end_list[0]),int(end_list[1]),int(end_list[2]))
        days = (end_datetime - begin_datetime).days + 1
        vacation_date = begin + '&nbsp->&nbsp' + end

    orm_fetch_supervisor = user_table.objects.filter(name=request.user.first_name)
    for i in orm_fetch_supervisor:
        approve_now = i.supervisor
        state_interface = u'等待 ' + i.supervisor + u' 审批'
        orm_supervisor = user_table.objects.get(name=approve_now)
        supervisor_email = orm_supervisor.email

    orm = state(name=request.user.first_name,type=type,reason=reason,vacation_date=vacation_date,days=days,
                state_interface=state_interface,state=1,approve_now=approve_now)

    log_info = '%s 申请了 %s，日期为 %s，%s' % (request.user.first_name,type,vacation_date,state_interface)
    orm_log = operation_log(name=request.user.first_name,operation=log_info)

    orm_alert = user_table.objects.get(name=approve_now)
    orm_alert.has_approve += 1

    try:
        orm_log.save()
        orm_alert.save()
        orm.save()

        send_mail(to_addr=supervisor_email,subject='请假审批提醒',body='<h3>有一个请假事件等待您的审批，请在OA系统中查看。</h3><br>此邮件为自动发送的提醒邮件，请勿回复。')
        return HttpResponse(simplejson.dumps({'code':0,'msg':u'保存成功'}),content_type="application/json")
    except Exception,e:
        print e
        return HttpResponse(simplejson.dumps({'code':1,'msg':str(e)}),content_type="application/json")

@login_required
def vacation_apply_del(request):
    _id = request.POST.get('id')
    orm = state.objects.get(id=_id)
    log_info = '%s 取消了 %s 的申请，日期为 %s' % (request.user.first_name,orm.type,orm.vacation_date)
    orm_log = operation_log(name=request.user.first_name,operation=log_info)
    try:
        orm_log.save()
        orm.delete()
        return HttpResponse(simplejson.dumps({'code':0,'msg':u'删除成功'}),content_type="application/json")
    except Exception,e:
        print e
        return HttpResponse(simplejson.dumps({'code':0,'msg':str(e)}),content_type="application/json")

@login_required
def vacation_approve_alert(request):
    orm = user_table.objects.get(name=request.user.first_name)
    approve_alert_num = orm.has_approve
    if approve_alert_num > 0:
        msg = '有%s个请假事件等待您的审批' % approve_alert_num
        return HttpResponse(simplejson.dumps({'code':0,'msg':msg}),content_type="application/json")
    else:
        return HttpResponse(simplejson.dumps({'code':1}),content_type="application/json")

@login_required
def vacation_approve(request):
    path = request.path.split('/')[1]
    try:
        orm = user_table.objects.get(name=request.user.first_name)
    except Exception:
        return render(request,'public/no_passing.html')
    return render(request, 'vacation/vacation_approve.html',{'user':'%s%s' % (request.user.last_name,request.user.first_name),
                                                       'path1':'vacation',
                                                       'path2':path,
                                                       'page_name1':u'请假管理',
                                                       'page_name2':u'请假申请',})

@login_required
def vacation_approve_data(request):
    sEcho =  request.POST.get('sEcho') #标志，直接返回
    iDisplayStart = int(request.POST.get('iDisplayStart'))#第几行开始
    iDisplayLength = int(request.POST.get('iDisplayLength'))#显示多少行
    iSortCol_0 = int(request.POST.get("iSortCol_0"))#排序行号
    sSortDir_0 = request.POST.get('sSortDir_0')#asc/desc
    sSearch = request.POST.get('sSearch')#高级搜索

    aaData = []
    sort = ['name','type','reason','apply_time','vacation_date','days','state_interface']

    if  sSortDir_0 == 'asc':
        if sSearch == '':
            result_data = state.objects.filter(approve_now=request.user.first_name).order_by(sort[iSortCol_0])[iDisplayStart:iDisplayStart+iDisplayLength]
            iTotalRecords = state.objects.filter(approve_now=request.user.first_name).count()
        else:
            result_data = state.objects.filter(approve_now=request.user.first_name).filter(Q(name__contains=sSearch) | \
                                                    Q(type__contains=sSearch) | \
                                                    Q(vacation_date__contains=sSearch) | \
                                                    Q(days__contains=sSearch) | \
                                                    Q(state_interface__contains=sSearch)) \
                                                    .order_by(sort[iSortCol_0])[iDisplayStart:iDisplayStart+iDisplayLength]
            iTotalRecords = state.objects.filter(approve_now=request.user.first_name).filter(Q(name__contains=sSearch) | \
                                                    Q(type__contains=sSearch) | \
                                                    Q(vacation_date__contains=sSearch) | \
                                                    Q(days__contains=sSearch) | \
                                                    Q(state_interface__contains=sSearch)).count()
    else:
        if sSearch == '':
            result_data = state.objects.filter(approve_now=request.user.first_name).order_by(sort[iSortCol_0]).reverse()[iDisplayStart:iDisplayStart+iDisplayLength]
            iTotalRecords = state.objects.filter(approve_now=request.user.first_name).count()
        else:
            result_data = state.objects.filter(approve_now=request.user.first_name).filter(Q(name__contains=sSearch) | \
                                                    Q(type__contains=sSearch) | \
                                                    Q(vacation_date__contains=sSearch) | \
                                                    Q(days__contains=sSearch) | \
                                                    Q(state_interface__contains=sSearch)) \
                                                    .order_by(sort[iSortCol_0]).reverse()[iDisplayStart:iDisplayStart+iDisplayLength]
            iTotalRecords = state.objects.filter(approve_now=request.user.first_name).filter(Q(name__contains=sSearch) | \
                                                    Q(type__contains=sSearch) | \
                                                    Q(vacation_date__contains=sSearch) | \
                                                    Q(days__contains=sSearch) | \
                                                    Q(state_interface__contains=sSearch)).count()

    for i in  result_data:
        aaData.append({
                       '0':i.name,
                       '1':i.type,
                       '2':i.reason,
                       '3':str(i.apply_time).split('+')[0],
                       '4':i.vacation_date,
                       '5':i.days,
                       '6':i.state,
                       '7':i.state_interface,
                       '8':i.id
                      })
    result = {'sEcho':sEcho,
               'iTotalRecords':iTotalRecords,
               'iTotalDisplayRecords':iTotalRecords,
               'aaData':aaData
    }
    return HttpResponse(simplejson.dumps(result),content_type="application/json")

@login_required
def vacation_approve_process(request):
    flag = request.POST.get('flag')
    dst_id = request.POST.get('dst_id')
    orm = state.objects.get(id=dst_id)
    if flag:
        if orm.state == 1:
            orm_fetch_principal = user_table.objects.get(name=orm.name)
            if orm_fetch_principal.supervisor != orm_fetch_principal.principal:
                approve_now = orm_fetch_principal.principal
                state_interface = u'等待 ' + orm_fetch_principal.principal + u' 审批'
                orm_principal = user_table.objects.get(name=approve_now)
                principal_email = orm_principal.email

                orm.state_interface = state_interface
                orm.approve_now = approve_now
                orm.state = 2

                log_info = '%s 批准了 %s 申请的 %s，日期为 %s，%s' % (request.user.first_name,orm.name,orm.type,orm.vacation_date,state_interface)
                orm_log = operation_log(name=request.user.first_name,operation=log_info)

                orm_alert = user_table.objects.get(name=approve_now)
                orm_alert.has_approve += 1

                orm_alert_2 = user_table.objects.get(name=request.user.first_name)
                orm_alert_2.has_approve -= 1

                try:
                    orm_log.save()
                    orm_alert.save()
                    orm_alert_2.save()
                    orm.save()

                    send_mail(to_addr=principal_email,subject='请假审批提醒',body='<h3>有一个请假事件等待您的审批，请在OA系统中查看。</h3><br>此邮件为自动发送的提醒邮件，请勿回复。')
                    return HttpResponse(simplejson.dumps({'code':0,'msg':u'保存成功'}),content_type="application/json")
                except Exception,e:
                    print e
                    return HttpResponse(simplejson.dumps({'code':1,'msg':str(e)}),content_type="application/json")