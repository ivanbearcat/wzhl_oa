# -*- coding: utf-8 -*-
from django.shortcuts import render
from django.http import HttpResponse
from django.template import RequestContext
from vacation.models import user_table,operation_log,state
from django.db.models.query_utils import Q
from django.utils.log import logger
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from libs.sendmail import send_mail
from wzhl_oa.settings import HR,BASE_DIR
import simplejson,datetime,xlsxwriter
from threading import Thread

import sys
reload(sys)
sys.setdefaultencoding('utf-8')

@login_required
def vacation_table(request):
    path = request.path.split('/')[1]
    if not request.user.has_perm('vacation.can_view'):
        return render(request,'public/no_passing.html')
    return render(request, 'vacation/vacation_table.html',{'user':'%s%s' % (request.user.last_name,request.user.first_name),
                                                       'path1':'vacation',
                                                       'path2':path,
                                                       'page_name1':u'请假管理',
                                                       'page_name2':u'总览表'},context_instance=RequestContext(request))

@login_required
def vacation_table_data(request):
    sEcho =  request.POST.get('sEcho') #标志，直接返回
    iDisplayStart = int(request.POST.get('iDisplayStart'))#第几行开始
    iDisplayLength = int(request.POST.get('iDisplayLength'))#显示多少行
    iSortCol_0 = int(request.POST.get("iSortCol_0"))#排序行号
    sSortDir_0 = request.POST.get('sSortDir_0')#asc/desc
    sSearch = request.POST.get('sSearch')#高级搜索

    aaData = []
    sort = ['name','department','supervisor','principal','join_date','graduate_year','sick_leave_num','statutory_annual_leave_available',
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
                       '6':i.sick_leave_num,
                       '7':i.statutory_annual_leave_available,
                       '8':i.statutory_annual_leave_used,
                       '9':i.statutory_annual_leave_total,
                       '10':i.company_annual_leave_available,
                       '11':i.company_annual_leave_used,
                       '12':i.company_annual_leave_total,
                       '13':i.seasons_leave_available,
                       '14':i.seasons_leave_used,
                       '15':i.seasons_leave_total,
                       '16':i.leave_in_lieu,
                       '17':i.email,
                       '18':i.id
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

        if today < join_date_datetime:
            company_annual_leave_total = 0
            company_annual_leave_available = 0
        else:
            company_annual_leave_total = (today - join_date_datetime).days / 365
            company_annual_leave_available = company_annual_leave_total


        orm = user_table(name=name,department=department,supervisor=supervisor,principal=principal,join_date=join_date,graduate_year=graduate_year,
                         email=email,sick_leave_num=0,statutory_annual_leave_available=statutory_annual_leave_available,statutory_annual_leave_used=0,
                         statutory_annual_leave_total=statutory_annual_leave_total,company_annual_leave_available=company_annual_leave_available,
                         company_annual_leave_used=0,company_annual_leave_total=company_annual_leave_total,seasons_leave_available=1,
                         seasons_leave_used=0,seasons_leave_total=1,leave_in_lieu=0,has_approve=0,approved_id='',has_KPI_commit=0,KPI_commit_id='')

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
    #每天0点5分刷新每个人各种假的天数，以及申请过期检查
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
        if today.month == 1 and today.day == 1 or today.month == 4 and today.day == 1 or \
                                today.month == 7 and today.day == 1 or today.month == 10 and today.day == 1:
            i.seasons_leave_used = 0
            i.seasons_leave_available = 1

        i.company_annual_leave_total = company_annual_leave_total
        i.company_annual_leave_available = company_annual_leave_total - i.company_annual_leave_used
        i.statutory_annual_leave_total = statutory_annual_leave_total
        i.statutory_annual_leave_available = statutory_annual_leave_total - i.statutory_annual_leave_used

        orm_state = state.objects.filter(name=i.name)
        for j in orm_state:
            if j.state not in [0,8,9]:
                if 6 < (datetime.datetime.now() - j.apply_time).days and (j.state == 1 or j.state == 2 or j.state == 3):
                    orm_fetch_email = user_table.objects.get(name=j.approve_now)
                    Thread(target=send_mail,args=(orm_fetch_email.email,'请假审批过期提醒','<h3>有一个请假事件等待您的审批，还有1天就将过期，请在尽快在OA系统中审批。</h3><br>OA链接：http://oa.xiaoquan.com/vacation_approve/</br><br>此邮件为自动发送的提醒邮件，请勿回复。')).start()
                    # send_mail(to_addr='%s' % orm_fetch_email.email,subject='请假审批过期提醒',
                    #           body='<h3>有一个请假事件等待您的审批，还有1天就将过期，请在尽快在OA系统中审批。</h3><br>OA链接：http://oa.xiaoquan.com/vacation_approve/</br><br>此邮件为自动发送的提醒邮件，请勿回复。')

                if (datetime.datetime.now() - j.apply_time).days > 7 and (j.state == 1 or j.state == 2 or j.state == 3):
                    j.state = 9
                    j.state_interface = '已过期'
                    orm_fetch_approve_now = user_table.objects.get(name=j.approve_now)
                    orm_fetch_approve_now.has_approve -= 1
                    j.approve_now = ''

                    if j.type == '法定年假':
                        i.statutory_annual_leave_available += j.days
                        i.statutory_annual_leave_used -= j.days
                    elif j.type == '公司年假':
                        i.company_annual_leave_available += j.days
                        i.company_annual_leave_used -= j.days
                    elif j.type == '季度假':
                        i.seasons_leave_available += j.days
                        i.seasons_leave_used -= j.days
                    elif j.type == '调休假':
                        i.leave_in_lieu += j.days

                    try:
                        orm_fetch_approve_now.save()
                        j.save()
                    except Exception,e:
                        print e
                        return HttpResponse('ERROR')

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
                                                       'seasons_leave_available':orm.seasons_leave_available,
                                                       'leave_in_lieu':orm.leave_in_lieu},context_instance=RequestContext(request))

@login_required
def vacation_apply_sub(request):
    path = request.path.split('/')[1]
    try:
        orm = user_table.objects.get(name=request.user.first_name)
    except Exception:
        return render(request,'public/no_passing.html')
    return render(request, 'vacation/vacation_apply_sub.html',{'statutory_annual_leave_available':orm.statutory_annual_leave_available,
                                                       'company_annual_leave_available':orm.company_annual_leave_available,
                                                       'seasons_leave_available':orm.seasons_leave_available,
                                                       'leave_in_lieu':orm.leave_in_lieu},context_instance=RequestContext(request))

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

    # try:
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

    orm_fetch_supervisor = user_table.objects.get(name=request.user.first_name)

    if orm_fetch_supervisor.supervisor == '/':
        return HttpResponse(simplejson.dumps({'code':0,'msg':u'您是部门负责人无需申请'}),content_type="application/json")

    if type == '法定年假':
        if days > orm_fetch_supervisor.statutory_annual_leave_available:
            return HttpResponse(simplejson.dumps({'code':1,'msg':u'您的法定年假剩余不足'}),content_type="application/json")
        orm_fetch_supervisor.statutory_annual_leave_available -= days
        orm_fetch_supervisor.statutory_annual_leave_used += days
    if type == '公司年假':
        if days > orm_fetch_supervisor.company_annual_leave_available:
            return HttpResponse(simplejson.dumps({'code':1,'msg':u'您的公司年假剩余不足'}),content_type="application/json")
        orm_fetch_supervisor.company_annual_leave_available -= days
        orm_fetch_supervisor.company_annual_leave_used += days
    if type == '季度假':
        if days > orm_fetch_supervisor.seasons_leave_available:
            return HttpResponse(simplejson.dumps({'code':1,'msg':u'您的季度假剩余不足'}),content_type="application/json")
        orm_fetch_supervisor.seasons_leave_available -= days
        orm_fetch_supervisor.seasons_leave_used += days
    if type == '调休':
        if days > orm_fetch_supervisor.leave_in_lieu:
            return HttpResponse(simplejson.dumps({'code':1,'msg':u'您的调休剩余不足'}),content_type="application/json")
        orm_fetch_supervisor.leave_in_lieu -= days

    orm_fetch_supervisor.save()

    approve_now = orm_fetch_supervisor.supervisor
    state_interface = u'等待 ' + orm_fetch_supervisor.supervisor + u' 审批'
    orm_supervisor = user_table.objects.get(name=approve_now)
    supervisor_email = orm_supervisor.email

    orm = state(name=request.user.first_name,type=type,reason=reason,vacation_date=vacation_date,days=days,
                state_interface=state_interface,state=1,approve_now=approve_now,real_days=0)

    log_info = '<b>%s</b> 申请了 <b>%s</b>，日期为 <b>%s</b>，当前状态为 <b>%s</b>' % (request.user.first_name,type,vacation_date,state_interface)
    orm_log = operation_log(name=request.user.first_name,operation=log_info)

    orm_alert = user_table.objects.get(name=approve_now)
    orm_alert.has_approve += 1

    orm_log.save()
    orm_alert.save()
    orm.save()

    all_entry_dict = {}
    def add_entry_group_reduce_func(front_time,back_time):
        #将刚才的结构进一步处理成为,以自己的datetime为key，[[所有组成员的datetime列表],所有组成员的id以逗号隔开,请假天数,自己的id]为value

        if all_entry_dict[back_time][2] == 0.5:
            all_entry_dict[back_time][2] = 1
        if ((back_time + datetime.timedelta(all_entry_dict[back_time][2] - 1)) - front_time).days < 2:
            all_entry_dict[front_time][0] += all_entry_dict[back_time][0]
            all_entry_dict[back_time][0] = all_entry_dict[front_time][0]
            all_entry_dict[back_time][1] += ',' + all_entry_dict[front_time][1]
            for i in all_entry_dict[front_time][0]:
                all_entry_dict[i][1] = all_entry_dict[back_time][1]
        return back_time

    def thread_run():
        #以自己的datetime为key，[[自己的datetime],自己的id,请假天数,自己的id]为value，这样的结构存入字典，交给reduce处理
        state_orm = state.objects.filter(name=request.user.first_name).exclude(type='加班')

        for entry in state_orm:
            date = entry.vacation_date.split('&nbsp')[0].split()
            date_list = date[0].split('-')
            if len(date) > 1:
                if date[1] == '10:00-15:00':
                    date_datetime = datetime.datetime(int(date_list[0]),int(date_list[1]),int(date_list[2]),1)
                if date[1] == '15:00-19:00':
                    date_datetime = datetime.datetime(int(date_list[0]),int(date_list[1]),int(date_list[2]),2)
            else:
                date_datetime = datetime.datetime(int(date_list[0]),int(date_list[1]),int(date_list[2]),0)
            all_entry_dict[date_datetime] = [[date_datetime],str(entry.id),entry.days,str(entry.id)]
        reduce(add_entry_group_reduce_func,sorted(all_entry_dict.keys()))
        #根据刚才的数据结构，计算出每个id的real_days
        for entry in all_entry_dict.values():
            orm_iter = state.objects.filter(id__in=entry[1].split(','))
            real_days = 0
            for orm in orm_iter:
                real_days += orm.days

            orm = state.objects.get(id=entry[3])
            orm.real_days = real_days
            orm.save()
    Thread(target=thread_run).start()
    Thread(target=send_mail,args=(supervisor_email,'请假审批提醒','<h3>有一个请假事件等待您的审批，请在OA系统中查看。</h3><br>OA链接：http://oa.xiaoquan.com/vacation_approve/</br><br>此邮件为自动发送的提醒邮件，请勿回复。')).start()
    # send_mail(to_addr=supervisor_email,subject='请假审批提醒',body='<h3>有一个请假事件等待您的审批，请在OA系统中查看。</h3><br>OA链接：http://oa.xiaoquan.com/vacation_approve/</br><br>此邮件为自动发送的提醒邮件，请勿回复。')
    return HttpResponse(simplejson.dumps({'code':0,'msg':u'保存成功'}),content_type="application/json")
    # except Exception,e:
    #     print e
    #     return HttpResponse(simplejson.dumps({'code':1,'msg':str(e)}),content_type="application/json")

@login_required
def vacation_apply_del(request):
    try:
        _id = request.POST.get('id')
        orm = state.objects.get(id=_id)
        if orm.state_interface == '已批准' or orm.state_interface == '不批准':
            return HttpResponse(simplejson.dumps({'code':1,'msg':u'已审批完成无法删除'}),content_type="application/json")
        orm_user = user_table.objects.get(name=request.user.first_name)

        if orm.type == '法定年假':
            orm_user.statutory_annual_leave_available += orm.days
            orm_user.statutory_annual_leave_used -= orm.days
        if orm.type == '公司年假':
            orm_user.company_annual_leave_available += orm.days
            orm_user.company_annual_leave_used -= orm.days
        if orm.type == '季度假':
            orm_user.seasons_leave_available += orm.days
            orm_user.seasons_leave_used -= orm.days
        if orm.type == '调休':
            orm_user.leave_in_lieu += orm.days
        orm_user.save()

        approve_now = orm.approve_now
        orm_supervisor = user_table.objects.get(name=approve_now)
        orm_supervisor.has_approve -= 1
        orm_supervisor.save()

        log_info = '<b>%s</b> 取消了 <b>%s</b> 的申请，日期为 <b>%s</b>' % (request.user.first_name,orm.type,orm.vacation_date)
        orm_log = operation_log(name=request.user.first_name,operation=log_info)

        orm_log.save()
        orm.delete()
        return HttpResponse(simplejson.dumps({'code':0,'msg':u'删除成功'}),content_type="application/json")
    except Exception,e:
        print e
        return HttpResponse(simplejson.dumps({'code':1,'msg':str(e)}),content_type="application/json")

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
                                                       'page_name2':u'请假申请',},context_instance=RequestContext(request))

@login_required
def vacation_approve_data(request):
    sEcho =  request.POST.get('sEcho') #标志，直接返回
    iDisplayStart = int(request.POST.get('iDisplayStart'))#第几行开始
    iDisplayLength = int(request.POST.get('iDisplayLength'))#显示多少行
    iSortCol_0 = int(request.POST.get("iSortCol_0"))#排序行号
    sSortDir_0 = request.POST.get('sSortDir_0')#asc/desc
    sSearch = request.POST.get('sSearch')#高级搜索

    aaData = []
    sort = ['name','type','reason','apply_time','vacation_date','days',None,'state_interface']

    if request.user.has_perm('vacation.can_view_all'):
        if  sSortDir_0 == 'asc':
            if sSearch == '':
                result_data = state.objects.all().order_by(sort[iSortCol_0])[iDisplayStart:iDisplayStart+iDisplayLength]
                iTotalRecords = state.objects.all().count()
            else:
                result_data = state.objects.filter(Q(name__contains=sSearch) | \
                                                        Q(type__contains=sSearch) | \
                                                        Q(vacation_date__contains=sSearch) | \
                                                        Q(days__contains=sSearch) | \
                                                        Q(state_interface__contains=sSearch)) \
                                                        .order_by(sort[iSortCol_0])[iDisplayStart:iDisplayStart+iDisplayLength]
                iTotalRecords = state.objects.filter(Q(name__contains=sSearch) | \
                                                        Q(type__contains=sSearch) | \
                                                        Q(vacation_date__contains=sSearch) | \
                                                        Q(days__contains=sSearch) | \
                                                        Q(state_interface__contains=sSearch)).count()
        else:
            if sSearch == '':
                result_data = state.objects.all().order_by(sort[iSortCol_0]).reverse()[iDisplayStart:iDisplayStart+iDisplayLength]
                iTotalRecords = state.objects.all().count()
            else:
                result_data = state.objects.filter(Q(name__contains=sSearch) | \
                                                        Q(type__contains=sSearch) | \
                                                        Q(vacation_date__contains=sSearch) | \
                                                        Q(days__contains=sSearch) | \
                                                        Q(state_interface__contains=sSearch)) \
                                                        .order_by(sort[iSortCol_0]).reverse()[iDisplayStart:iDisplayStart+iDisplayLength]
                iTotalRecords = state.objects.filter(Q(name__contains=sSearch) | \
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

    else:
        orm_approved_id = user_table.objects.get(name=request.user.first_name)
        approved_id_list = orm_approved_id.approved_id.split(',')
        if approved_id_list != [u'']:
            approved_id_list = map(lambda x:int(x), approved_id_list)
        else:
            approved_id_list = []

        if  orm_approved_id.subordinate:
            subordinate_list = orm_approved_id.subordinate.split(',')
        else:
            subordinate_list = []

        if  sSortDir_0 == 'asc':
            if sSearch == '':
                result_data = state.objects.filter(Q(approve_now=request.user.first_name) | Q(id__in=approved_id_list) | Q(name__in=subordinate_list)).order_by(sort[iSortCol_0])[iDisplayStart:iDisplayStart+iDisplayLength]
                iTotalRecords = state.objects.filter(Q(approve_now=request.user.first_name) | Q(id__in=approved_id_list) | Q(name__in=subordinate_list)).count()
            else:
                result_data = state.objects.filter(Q(approve_now=request.user.first_name) | Q(id__in=approved_id_list) | Q(name__in=subordinate_list)).filter(Q(name__contains=sSearch) | \
                                                        Q(type__contains=sSearch) | \
                                                        Q(vacation_date__contains=sSearch) | \
                                                        Q(days__contains=sSearch) | \
                                                        Q(state_interface__contains=sSearch)) \
                                                        .order_by(sort[iSortCol_0])[iDisplayStart:iDisplayStart+iDisplayLength]
                iTotalRecords = state.objects.filter(Q(approve_now=request.user.first_name) | Q(id__in=approved_id_list) | Q(name__in=subordinate_list)).filter(Q(name__contains=sSearch) | \
                                                        Q(type__contains=sSearch) | \
                                                        Q(vacation_date__contains=sSearch) | \
                                                        Q(days__contains=sSearch) | \
                                                        Q(state_interface__contains=sSearch)).count()
        else:
            if sSearch == '':
                result_data = state.objects.filter(Q(approve_now=request.user.first_name) | Q(id__in=approved_id_list) | Q(name__in=subordinate_list)).order_by(sort[iSortCol_0]).reverse()[iDisplayStart:iDisplayStart+iDisplayLength]
                iTotalRecords = state.objects.filter(Q(approve_now=request.user.first_name) | Q(id__in=approved_id_list) | Q(name__in=subordinate_list)).count()
            else:
                result_data = state.objects.filter(Q(approve_now=request.user.first_name) | Q(id__in=approved_id_list) | Q(name__in=subordinate_list)).filter(Q(name__contains=sSearch) | \
                                                        Q(type__contains=sSearch) | \
                                                        Q(vacation_date__contains=sSearch) | \
                                                        Q(days__contains=sSearch) | \
                                                        Q(state_interface__contains=sSearch)) \
                                                        .order_by(sort[iSortCol_0]).reverse()[iDisplayStart:iDisplayStart+iDisplayLength]
                iTotalRecords = state.objects.filter(Q(approve_now=request.user.first_name) | Q(id__in=approved_id_list) | Q(name__in=subordinate_list)).filter(Q(name__contains=sSearch) | \
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
    disagree_reason = request.POST.get('disagree_reason')

    orm = state.objects.get(id=dst_id)

    if orm.approve_now != request.user.first_name:
        return HttpResponse(simplejson.dumps({'code':1,'msg':u'这条申请的审批人不是您'}),content_type="application/json")

    if int(flag) == 1:
        if orm.state == 1:
            orm_fetch_principal = user_table.objects.get(name=orm.name)
            if orm_fetch_principal.supervisor != orm_fetch_principal.principal and orm.real_days >= 2:
                approve_now = orm_fetch_principal.principal
                state_interface = u'等待 ' + orm_fetch_principal.principal + u' 审批'
                orm_principal = user_table.objects.get(name=approve_now)
                principal_email = orm_principal.email

                orm.state_interface = state_interface
                orm.approve_now = approve_now
                orm.state = 2

                log_info = '<b>%s</b> 批准了 <b>%s</b> 申请的 <b>%s</b>，日期为 <b>%s</b>，当前状态为 <b>%s</b>' % (request.user.first_name,orm.name,orm.type,orm.vacation_date,state_interface)
                orm_log = operation_log(name=request.user.first_name,operation=log_info)

                orm_alert = user_table.objects.get(name=approve_now)
                orm_alert.has_approve += 1

                orm_alert_my = user_table.objects.get(name=request.user.first_name)
                orm_alert_my.has_approve -= 1
                if orm_alert_my.approved_id:
                    orm_alert_my.approved_id += ',' + str(orm.id)
                else:
                    orm_alert_my.approved_id = str(orm.id)

                try:
                    if orm.type == u'病假':
                        orm_fetch_principal.sick_leave_num += orm.days
                    orm_fetch_principal.save()
                    orm_log.save()
                    orm_alert.save()
                    orm_alert_my.save()
                    orm.save()
                    Thread(target=send_mail,args=(principal_email,'请假审批提醒','<h3>有一个请假事件等待您的审批，请在OA系统中查看。</h3><br>OA链接：http://oa.xiaoquan.com/vacation_approve/</br><br>此邮件为自动发送的提醒邮件，请勿回复。')).start()
                    # send_mail(to_addr=principal_email,subject='请假审批提醒',body='<h3>有一个请假事件等待您的审批，请在OA系统中查看。</h3><br>OA链接：http://oa.xiaoquan.com/vacation_approve/</br><br>此邮件为自动发送的提醒邮件，请勿回复。')
                    return HttpResponse(simplejson.dumps({'code':0,'msg':u'审批成功'}),content_type="application/json")
                except Exception,e:
                    print e
                    return HttpResponse(simplejson.dumps({'code':1,'msg':str(e)}),content_type="application/json")
            else:
                if orm.type == '病假' and orm.real_days >= 2 or orm.type == '产假' or orm.type == '婚假' or orm.type == '陪产假' or orm.type == '丧假' or orm.type == '事假' or orm.type == u'加班':
                    state_interface = u'等待 ' + HR['name'] + u' 审批'
                    HR_email = HR['email']

                    orm.state_interface = state_interface
                    orm.approve_now = HR['name']
                    orm.state = 3

                    log_info = '<b>%s</b> 批准了 <b>%s</b> 申请的 <b>%s</b>，日期为 <b>%s</b>，当前状态为 <b>%s</b>' % (request.user.first_name,orm.name,orm.type,orm.vacation_date,state_interface)
                    orm_log = operation_log(name=request.user.first_name,operation=log_info)

                    orm_alert = user_table.objects.get(name=HR['name'])
                    orm_alert.has_approve += 1

                    orm_alert_my = user_table.objects.get(name=request.user.first_name)
                    orm_alert_my.has_approve -= 1
                    if orm_alert_my.approved_id:
                        orm_alert_my.approved_id += ',' + str(orm.id)
                    else:
                        orm_alert_my.approved_id = str(orm.id)

                    try:
                        orm_log.save()
                        orm_alert.save()
                        orm_alert_my.save()
                        orm.save()
                        Thread(target=send_mail,args=(HR_email,'请假审批提醒','<h3>有一个请假事件等待您的审批，请在OA系统中查看。</h3><br>OA链接：http://oa.xiaoquan.com/vacation_approve/</br><br>此邮件为自动发送的提醒邮件，请勿回复。')).start()
                        # send_mail(to_addr=HR_email,subject='请假审批提醒',body='<h3>有一个请假事件等待您的审批，请在OA系统中查看。</h3><br>OA链接：http://oa.xiaoquan.com/vacation_approve/</br><br>此邮件为自动发送的提醒邮件，请勿回复。')
                        return HttpResponse(simplejson.dumps({'code':0,'msg':u'审批成功'}),content_type="application/json")
                    except Exception,e:
                        print e
                        return HttpResponse(simplejson.dumps({'code':1,'msg':str(e)}),content_type="application/json")

                apply_email = orm_fetch_principal.email
                orm.state_interface = '已批准'
                orm.state = 8
                orm.approve_now = ''

                log_info = '<b>%s</b> 批准了 <b>%s</b> 申请的 <b>%s</b>，日期为 <b>%s</b>，当前状态为 <b>%s</b>' % (request.user.first_name,orm.name,orm.type,orm.vacation_date,orm.state_interface)
                orm_log = operation_log(name=request.user.first_name,operation=log_info)

                if orm.type == u'病假':
                    orm_fetch_principal.sick_leave_num += orm.days

                if orm.type == u'加班':
                    orm_fetch_principal.leave_in_lieu += orm.days
                # if orm.type == u'法定年假':
                #     orm_fetch_principal.statutory_annual_leave_used += orm.days
                #     orm_fetch_principal.statutory_annual_leave_available -= orm.days
                # if orm.type == u'公司年假':
                #     orm_fetch_principal.company_annual_leave_used += orm.days
                #     orm_fetch_principal.company_annual_leave_available -= orm.days
                # if orm.type == u'季度假':
                #     orm_fetch_principal.seasons_leave_used += orm.days
                #     orm_fetch_principal.seasons_leave_available -= orm.days

                try:
                    orm_log.save()
                    orm_fetch_principal.save()
                    orm_alert_my = user_table.objects.get(name=request.user.first_name)
                    orm_alert_my.has_approve -= 1
                    if orm_alert_my.approved_id:
                        orm_alert_my.approved_id += ',' + str(orm.id)
                    else:
                        orm_alert_my.approved_id = str(orm.id)
                    orm_alert_my.save()
                    orm.save()
                    Thread(target=send_mail,args=(apply_email,'请假申请已批准','<h3>您的请假申请已被批准，请在OA系统中查看。</h3><br>OA链接：http://oa.xiaoquan.com/vacation_approve/</br><br>此邮件为自动发送的提醒邮件，请勿回复。')).start()
                    # send_mail(to_addr=apply_email,subject='请假申请已批准',body='<h3>您的请假申请已被批准，请在OA系统中查看。</h3><br>OA链接：http://oa.xiaoquan.com/vacation_approve/</br><br>此邮件为自动发送的提醒邮件，请勿回复。')

                    return HttpResponse(simplejson.dumps({'code':0,'msg':u'审批成功'}),content_type="application/json")
                except Exception,e:
                    print e
                    return HttpResponse(simplejson.dumps({'code':1,'msg':str(e)}),content_type="application/json")
        if orm.state == 2:
            if orm.type == '病假' and orm.real_days >= 2 or orm.type == '产假' or orm.type == '婚假' or orm.type == '陪产假' or orm.type == '丧假' or orm.type == u'加班':
                state_interface = u'等待 ' + HR['name'] + u' 审批'
                HR_email = HR['email']

                orm.state_interface = state_interface
                orm.approve_now = HR['name']
                orm.state = 3

                log_info = '<b>%s</b> 批准了 <b>%s</b> 申请的 <b>%s</b>，日期为 <b>%s</b>，当前状态为 <b>%s</b>' % (request.user.first_name,orm.name,orm.type,orm.vacation_date,state_interface)
                orm_log = operation_log(name=request.user.first_name,operation=log_info)

                orm_alert = user_table.objects.get(name=HR['name'])
                orm_alert.has_approve += 1

                orm_alert_my = user_table.objects.get(name=request.user.first_name)
                orm_alert_my.has_approve -= 1
                if orm_alert_my.approved_id:
                    orm_alert_my.approved_id += ',' + str(orm.id)
                else:
                    orm_alert_my.approved_id = str(orm.id)

                try:
                    orm_log.save()
                    orm_alert.save()
                    orm_alert_my.save()
                    orm.save()
                    Thread(target=send_mail,args=(HR_email,'请假审批提醒','<h3>有一个请假事件等待您的审批，请在OA系统中查看。</h3><br>OA链接：http://oa.xiaoquan.com/vacation_approve/</br><br>此邮件为自动发送的提醒邮件，请勿回复。')).start()
                    # send_mail(to_addr=HR_email,subject='请假审批提醒',body='<h3>有一个请假事件等待您的审批，请在OA系统中查看。</h3><br>OA链接：http://oa.xiaoquan.com/vacation_approve/</br><br>此邮件为自动发送的提醒邮件，请勿回复。')
                    return HttpResponse(simplejson.dumps({'code':0,'msg':u'审批成功'}),content_type="application/json")
                except Exception,e:
                    print e
                    return HttpResponse(simplejson.dumps({'code':1,'msg':str(e)}),content_type="application/json")
            orm.state_interface = '已批准'
            orm.state = 8
            orm.approve_now = ''

            log_info = '<b>%s</b> 批准了 <b>%s</b> 申请的 <b>%s</b>，日期为 <b>%s</b>，当前状态为 <b>%s</b>' % (request.user.first_name,orm.name,orm.type,orm.vacation_date,orm.state_interface)
            orm_log = operation_log(name=request.user.first_name,operation=log_info)

            orm_fetch_principal = user_table.objects.get(name=orm.name)
            apply_email = orm_fetch_principal.email

            if orm.type == u'病假':
                orm_fetch_principal.sick_leave_num += orm.days

            if orm.type == u'加班':
                orm_fetch_principal.leave_in_lieu += orm.days
            # if orm.type == '法定年假':
            #     orm_fetch_principal.statutory_annual_leave_used += orm.days
            #     orm_fetch_principal.statutory_annual_leave_available -= orm.days
            # if orm.type == '公司年假':
            #     orm_fetch_principal.company_annual_leave_used += orm.days
            #     orm_fetch_principal.company_annual_leave_available -= orm.days
            # if orm.type == '季度假':
            #     orm_fetch_principal.seasons_leave_used += orm.days
            #     orm_fetch_principal.seasons_leave_available -= orm.days

            try:
                orm_log.save()
                orm_fetch_principal.save()
                orm_alert_my = user_table.objects.get(name=request.user.first_name)
                orm_alert_my.has_approve -= 1
                if orm_alert_my.approved_id:
                    orm_alert_my.approved_id += ',' + str(orm.id)
                else:
                    orm_alert_my.approved_id = str(orm.id)
                orm_alert_my.save()
                orm.save()
                Thread(target=send_mail,args=(apply_email,'请假申请已批准','<h3>您的请假申请已被批准，请在OA系统中查看。</h3><br>OA链接：http://oa.xiaoquan.com/vacation_approve/</br><br>此邮件为自动发送的提醒邮件，请勿回复。')).start()
                # send_mail(to_addr=apply_email,subject='请假申请已批准',body='<h3>您的请假申请已被批准，请在OA系统中查看。</h3><br>OA链接：http://oa.xiaoquan.com/vacation_approve/</br><br>此邮件为自动发送的提醒邮件，请勿回复。')

                return HttpResponse(simplejson.dumps({'code':0,'msg':u'审批成功'}),content_type="application/json")
            except Exception,e:
                print e
                return HttpResponse(simplejson.dumps({'code':1,'msg':str(e)}),content_type="application/json")
        if orm.state == 3:
            orm.state_interface = '已批准'
            orm.state = 8
            orm.approve_now = ''

            log_info = '<b>%s</b> 批准了 <b>%s</b> 申请的 <b>%s</b>，日期为 <b>%s</b>，当前状态为 <b>%s</b>' % (request.user.first_name,orm.name,orm.type,orm.vacation_date,orm.state_interface)
            orm_log = operation_log(name=request.user.first_name,operation=log_info)

            orm_fetch_principal = user_table.objects.get(name=orm.name)
            apply_email = orm_fetch_principal.email

            if orm.type == u'病假':
                orm_fetch_principal.sick_leave_num += orm.days

            if orm.type == u'加班':
                    orm_fetch_principal.leave_in_lieu += orm.days
            # if orm.type == '法定年假':
            #     orm_fetch_principal.statutory_annual_leave_used += orm.days
            #     orm_fetch_principal.statutory_annual_leave_available -= orm.days
            # if orm.type == '公司年假':
            #     orm_fetch_principal.company_annual_leave_used += orm.days
            #     orm_fetch_principal.company_annual_leave_available -= orm.days
            # if orm.type == '季度假':
            #     orm_fetch_principal.seasons_leave_used += orm.days
            #     orm_fetch_principal.seasons_leave_available -= orm.days

            try:
                orm_log.save()
                orm_fetch_principal.save()
                orm_alert_my = user_table.objects.get(name=request.user.first_name)
                orm_alert_my.has_approve -= 1
                if orm_alert_my.approved_id:
                    orm_alert_my.approved_id += ',' + str(orm.id)
                else:
                    orm_alert_my.approved_id = str(orm.id)
                orm_alert_my.save()
                orm.save()
                Thread(target=send_mail,args=(apply_email,'请假申请已批准','<h3>您的请假申请已被批准，请在OA系统中查看。</h3><br>OA链接：http://oa.xiaoquan.com/vacation_approve/</br><br>此邮件为自动发送的提醒邮件，请勿回复。')).start()
                # send_mail(to_addr=apply_email,subject='请假申请已批准',body='<h3>您的请假申请已被批准，请在OA系统中查看。</h3><br>OA链接：http://oa.xiaoquan.com/vacation_approve/</br><br>此邮件为自动发送的提醒邮件，请勿回复。')

                return HttpResponse(simplejson.dumps({'code':0,'msg':u'审批成功'}),content_type="application/json")
            except Exception,e:
                print e
                return HttpResponse(simplejson.dumps({'code':1,'msg':str(e)}),content_type="application/json")
    if int(flag) == 0:
        try:
            orm.state_interface = '不批准'
            orm.state = 0
            orm.approve_now = ''

            log_info = '<b>%s</b> 没有批准 <b>%s</b> 申请的 <b>%s</b>，日期为 <b>%s</b>，当前状态为 <b>%s</b>' % (request.user.first_name,orm.name,orm.type,orm.vacation_date,orm.state_interface)
            orm_log = operation_log(name=request.user.first_name,operation=log_info)

            fetch_email = user_table.objects.get(name=orm.name)
            email = fetch_email.email

            if orm.type == '法定年假':
                fetch_email.statutory_annual_leave_available += orm.days
                fetch_email.statutory_annual_leave_used -= orm.days
            if orm.type == '公司年假':
                fetch_email.company_annual_leave_available += orm.days
                fetch_email.company_annual_leave_used -= orm.days
            if orm.type == '季度假':
                fetch_email.seasons_leave_available += orm.days
                fetch_email.seasons_leave_used -= orm.days
            if orm.type == '调休':
                fetch_email.leave_in_lieu += orm.days
            fetch_email.save()
            Thread(target=send_mail,args=(email,'请假申请被拒绝','<h3>您的请假申请被拒绝，请在OA系统中查看。</h3><br>拒绝理由：<font color="red">%s</font><br>OA链接：http://oa.xiaoquan.com/vacation_approve/</br><br>此邮件为自动发送的提醒邮件，请勿回复。' % disagree_reason)).start()
            # send_mail(to_addr=email,subject='请假申请被拒绝',body='<h3>您的请假申请被拒绝，请在OA系统中查看。</h3><br>拒绝理由：<font color="red">%s</font><br>OA链接：http://oa.xiaoquan.com/vacation_approve/</br><br>此邮件为自动发送的提醒邮件，请勿回复。' % disagree_reason)
            orm_alert = user_table.objects.get(name=request.user.first_name)
            orm_alert.has_approve -= 1
            if orm_alert.approved_id:
                orm_alert.approved_id += ',' + str(orm.id)
            else:
                orm_alert.approved_id = str(orm.id)

            orm_log.save()
            orm_alert.save()
            orm.save()

            return HttpResponse(simplejson.dumps({'code':0,'msg':u'审批成功'}),content_type="application/json")
        except Exception,e:
            print e
            return HttpResponse(simplejson.dumps({'code':1,'msg':str(e)}),content_type="application/json")

@login_required
def vacation_log(request):
    path = request.path.split('/')[1]
    if not request.user.has_perm('vacation.can_view'):
        return render(request,'public/no_passing.html')
    return render(request, 'vacation/vacation_log.html',{'user':'%s%s' % (request.user.last_name,request.user.first_name),
                                                       'path1':'vacation',
                                                       'path2':path,
                                                       'page_name1':u'请假管理',
                                                       'page_name2':u'日志记录'},context_instance=RequestContext(request))

@login_required
def vacation_log_data(request):
    sEcho =  request.POST.get('sEcho') #标志，直接返回
    iDisplayStart = int(request.POST.get('iDisplayStart'))#第几行开始
    iDisplayLength = int(request.POST.get('iDisplayLength'))#显示多少行
    iSortCol_0 = int(request.POST.get("iSortCol_0"))#排序行号
    sSortDir_0 = request.POST.get('sSortDir_0')#asc/desc
    sSearch = request.POST.get('sSearch')#高级搜索

    type = request.POST.get('type')
    begin = request.POST.get('begin')
    end = request.POST.get('end')

    if not begin:
        aaData = []
        sort = ['name','operation','operation_time']

        if  sSortDir_0 == 'asc':
            if sSearch == '':
                result_data = operation_log.objects.all().order_by(sort[iSortCol_0])[iDisplayStart:iDisplayStart+iDisplayLength]
                iTotalRecords = operation_log.objects.all().count()
            else:
                result_data = operation_log.objects.filter(Q(name__contains=sSearch) | \
                                                        Q(operation__contains=sSearch)) \
                                                        .order_by(sort[iSortCol_0])[iDisplayStart:iDisplayStart+iDisplayLength]
                iTotalRecords = operation_log.objects.filter(Q(name__contains=sSearch) | \
                                                        Q(operation__contains=sSearch)).count()
        else:
            if sSearch == '':
                result_data = operation_log.objects.all().order_by(sort[iSortCol_0]).reverse()[iDisplayStart:iDisplayStart+iDisplayLength]
                iTotalRecords = operation_log.objects.all().count()
            else:
                result_data = operation_log.objects.filter(Q(name__contains=sSearch) | \
                                                        Q(operation__contains=sSearch)) \
                                                        .order_by(sort[iSortCol_0]).reverse()[iDisplayStart:iDisplayStart+iDisplayLength]
                iTotalRecords = operation_log.objects.filter(Q(name__contains=sSearch) | \
                                                        Q(operation__contains=sSearch)).count()

        for i in  result_data:
            aaData.append({
                           '0':i.name,
                           '1':i.operation,
                           '2':str(i.operation_time).split('+')[0],
                           '3':i.id
                          })
        result = {'sEcho':sEcho,
                   'iTotalRecords':iTotalRecords,
                   'iTotalDisplayRecords':iTotalRecords,
                   'aaData':aaData
        }
        return HttpResponse(simplejson.dumps(result),content_type="application/json")

    else:
        begin = begin.split('-')
        end = end.split('-')

        begin = datetime.datetime(int(begin[0]),int(begin[1]),int(begin[2]))
        try:
            end = datetime.datetime(int(end[0]),int(end[1]),int(end[2])+1)
        except ValueError:
            end = datetime.datetime(int(end[0]),int(end[1]),int(end[2]),23,59)

        aaData = []
        sort = ['name','operation','operation_time']

        if  sSortDir_0 == 'asc':
            if sSearch == '':
                result_data = operation_log.objects.filter(operation_time__range=(begin,end)) \
                                                    .order_by(sort[iSortCol_0])[iDisplayStart:iDisplayStart+iDisplayLength]
                iTotalRecords = operation_log.objects.filter(operation_time__range=(begin,end)).count()
            else:
                result_data = operation_log.objects.filter(operation_time__range=(begin,end)).filter( \
                                                        Q(name__contains=sSearch) | \
                                                        Q(operation__contains=sSearch)) \
                                                .order_by(sort[iSortCol_0])[iDisplayStart:iDisplayStart+iDisplayLength]
                iTotalRecords = operation_log.objects.filter(operation_time__range=(begin,end)).filter( \
                                                        Q(name__contains=sSearch) | \
                                                        Q(operation__contains=sSearch)).count()
        else:
            if sSearch == '':
                result_data = operation_log.objects.filter(operation_time__range=(begin,end)).order_by(sort[iSortCol_0]).reverse()[iDisplayStart:iDisplayStart+iDisplayLength]
                iTotalRecords = operation_log.objects.filter(operation_time__range=(begin,end)).count()
            else:
                result_data = operation_log.objects.filter(operation_time__range=(begin,end)).filter( \
                                                        Q(name__contains=sSearch) | \
                                                        Q(operation__contains=sSearch)) \
                                                .order_by(sort[iSortCol_0]).reverse()[iDisplayStart:iDisplayStart+iDisplayLength]
                iTotalRecords = operation_log.objects.filter(operation_time__range=(begin,end)).filter( \
                                                        Q(name__contains=sSearch) | \
                                                        Q(operation__contains=sSearch)).count()
        for i in  result_data:
            aaData.append({
                           '0':i.name,
                           '1':i.operation,
                           '2':str(i.operation_time).split('+')[0],
                           '3':i.id
                          })
        result = {'sEcho':sEcho,
                   'iTotalRecords':iTotalRecords,
                   'iTotalDisplayRecords':iTotalRecords,
                   'aaData':aaData
        }
        return HttpResponse(simplejson.dumps(result),content_type="application/json")

@login_required
def vacation_export_excel(request):
    try:
        workbook = xlsxwriter.Workbook(BASE_DIR + '/static/files/fixed_assets.xlsx')
        worksheet = workbook.add_worksheet()

        title = [u'姓名',u'操作',u'操作时间']

        worksheet.write_row('B2',title)

        orm = operation_log.objects.all()
        count = 3
        for i in orm:
            operation = i.operation.replace('<b>','').replace('</b>','').replace('&nbsp',' ')
            worksheet.write_row('B%s' % count, [i.name,operation,str(i.operation_time).split('+')[0]])
            count += 1
        workbook.close()
        return HttpResponse(simplejson.dumps({'code':0,'msg':u'生成Excel文件成功'}),content_type="application/json")
    except Exception,e:
        print e
        return HttpResponse(simplejson.dumps({'code':1,'msg':u'生成Excel文件失败'}),content_type="application/json")

@login_required
def refresh_subordinate(request):
    for i in user_table.objects.all():
        i.subordinate = ''
        i.save()
    for i in user_table.objects.all():
        if i.name != i.principal:
            principal_orm = user_table.objects.get(name=i.principal)
            if principal_orm.subordinate:
                if i.name not in principal_orm.subordinate.split(','):
                    principal_orm.subordinate += ',' + i.name
            else:
                principal_orm.subordinate = i.name
            try:
                principal_orm.save()
            except Exception,e:
                print e
    return HttpResponse(simplejson.dumps('finish'),content_type="application/json")


