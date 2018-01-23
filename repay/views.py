# -*- coding: utf-8 -*-
from django.shortcuts import render
from django.http import HttpResponse
from django.template import RequestContext
from django.db.models.query_utils import Q
from repay.models import budget, log, repay
from vacation.models import user_table
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from libs.common import int_format
import json, re
from django.db import transaction
import datetime
from libs.common import Num2MoneyFormat


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




@login_required
def repay_apply(request):
    path = request.path.split('/')[1]
    return render(request, 'repay/repay_apply.html',{'user':'%s%s' % (request.user.last_name,request.user.first_name),
                                                       'path1':'repay',
                                                       'path2':path,
                                                       'page_name1':u'报销管理',
                                                       'page_name2':u'报销申请'},context_instance=RequestContext(request))



@login_required
def repay_apply_sub(request):
    path = request.path.split('/')[1]
    try:
        orm_user = user_table.objects.get(name=request.user.first_name)
        orm = budget.objects.filter(date=str(datetime.datetime.now().date())).filter(department=orm_user.department)
        if orm:
            budget_available = orm[0].budget_available
    except Exception:
        return render(request,'public/no_passing.html')
    return render(request, 'vacation/vacation_apply_sub.html',{'budget_available':budget_available},context_instance=RequestContext(request))




@login_required
def repay_apply_data(request):
    sEcho =  request.POST.get('sEcho') #标志，直接返回
    iDisplayStart = int(request.POST.get('iDisplayStart'))#第几行开始
    iDisplayLength = int(request.POST.get('iDisplayLength'))#显示多少行
    iSortCol_0 = int(request.POST.get("iSortCol_0"))#排序行号
    sSortDir_0 = request.POST.get('sSortDir_0')#asc/desc
    sSearch = request.POST.get('sSearch')#高级搜索

    aaData = []
    sort = ['name','apply_time','budget_class','budget_class_level2','department','description','amount','amount_words',
            'payment_class','beneficiary_name','beneficiary_account','beneficiary_bank','contract_uuid','final_payment_date',
            'state','approve_now']

    if  sSortDir_0 == 'asc':
        if sSearch == '':
            result_data = repay.objects.filter(name=request.user.first_name).order_by(sort[iSortCol_0])[iDisplayStart:iDisplayStart+iDisplayLength]
            iTotalRecords = repay.objects.filter(name=request.user.first_name).count()
        else:
            result_data = repay.objects.filter(name=request.user.first_name).filter(Q(name__contains=sSearch) | \
                                                    Q(budget_class__contains=sSearch) | \
                                                    Q(budget_class_level2__contains=sSearch) | \
                                                    Q(department__contains=sSearch) | \
                                                    Q(description__contains=sSearch) | \
                                                    Q(payment_class__contains=sSearch) | \
                                                    Q(beneficiary_name__contains=sSearch) | \
                                                    Q(beneficiary_account__contains=sSearch) | \
                                                    Q(beneficiary_bank__contains=sSearch) | \
                                                    Q(contract_uuid__contains=sSearch)) \
                                                    .order_by(sort[iSortCol_0])[iDisplayStart:iDisplayStart+iDisplayLength]
            iTotalRecords = repay.objects.filter(name=request.user.first_name).filter(Q(name__contains=sSearch) | \
                                                    Q(budget_class__contains=sSearch) | \
                                                    Q(budget_class_level2__contains=sSearch) | \
                                                    Q(department__contains=sSearch) | \
                                                    Q(description__contains=sSearch) | \
                                                    Q(payment_class__contains=sSearch) | \
                                                    Q(beneficiary_name__contains=sSearch) | \
                                                    Q(beneficiary_account__contains=sSearch) | \
                                                    Q(beneficiary_bank__contains=sSearch) | \
                                                    Q(contract_uuid__contains=sSearch)).count()
    else:
        if sSearch == '':
            result_data = repay.objects.filter(name=request.user.first_name).order_by(sort[iSortCol_0]).reverse()[iDisplayStart:iDisplayStart+iDisplayLength]
            iTotalRecords = repay.objects.filter(name=request.user.first_name).count()
        else:
            result_data = repay.objects.filter(name=request.user.first_name).filter(Q(name__contains=sSearch) | \
                                                    Q(budget_class__contains=sSearch) | \
                                                    Q(budget_class_level2__contains=sSearch) | \
                                                    Q(department__contains=sSearch) | \
                                                    Q(description__contains=sSearch) | \
                                                    Q(payment_class__contains=sSearch) | \
                                                    Q(beneficiary_name__contains=sSearch) | \
                                                    Q(beneficiary_account__contains=sSearch) | \
                                                    Q(beneficiary_bank__contains=sSearch) | \
                                                    Q(contract_uuid__contains=sSearch)) \
                                                    .order_by(sort[iSortCol_0]).reverse()[iDisplayStart:iDisplayStart+iDisplayLength]
            iTotalRecords = repay.objects.filter(name=request.user.first_name).filter(Q(name__contains=sSearch) | \
                                                    Q(budget_class__contains=sSearch) | \
                                                    Q(budget_class_level2__contains=sSearch) | \
                                                    Q(department__contains=sSearch) | \
                                                    Q(description__contains=sSearch) | \
                                                    Q(payment_class__contains=sSearch) | \
                                                    Q(beneficiary_name__contains=sSearch) | \
                                                    Q(beneficiary_account__contains=sSearch) | \
                                                    Q(beneficiary_bank__contains=sSearch) | \
                                                    Q(contract_uuid__contains=sSearch)).count()

    for i in  result_data:
        aaData.append({
                       '0':i.name,
                       '1':str(i.apply_time),
                       '2':i.budget_class,
                       '3':i.budget_class_level2,
                       '4':i.department,
                       '5':i.description,
                       '6':i.amount,
                       '7':i.amount_words,
                       '8':i.payment_class,
                       '9':i.beneficiary_name,
                       '10':i.beneficiary_account,
                       '11':i.beneficiary_bank,
                       '12':i.contract_uuid,
                       '13':i.final_payment_date,
                       '14':i.state,
                       '15':i.id,
                       '16':i.approve_now
                      })
    result = {'sEcho':sEcho,
               'iTotalRecords':iTotalRecords,
               'iTotalDisplayRecords':iTotalRecords,
               'aaData':aaData
    }
    return HttpResponse(json.dumps(result),content_type="application/json")



@login_required
def repay_apply_save(request):
    budget_class = request.POST.get('budget_class')
    budget_class_level2 = request.POST.get('budget_class_level2')
    department = request.POST.get('department')
    description = request.POST.get('description')
    amount = request.POST.get('amount')
    payment_class = request.POST.get('payment_class')
    beneficiary_name = request.POST.get('beneficiary_name')
    beneficiary_account = request.POST.get('beneficiary_account')
    beneficiary_bank = request.POST.get('beneficiary_bank')
    contract_uuid = request.POST.get('contract_uuid')
    final_payment_date = request.POST.get('final_payment_date')

    name = request.user.first_name
    amount_words = Num2MoneyFormat(float(amount))

    approve_now = ''


    orm = repay(name=name,budget_class=budget_class,budget_class_level2=budget_class_level2,department=department,
                description=description,amount=amount,payment_class=payment_class,beneficiary_name=beneficiary_name,
                beneficiary_account=beneficiary_account,beneficiary_bank=beneficiary_bank,contract_uuid=contract_uuid,
                final_payment_date=final_payment_date,state=1,approve_now=approve_now)

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
    Thread(target=send_mail,args=(supervisor_email,'请假审批提醒','<h3>有一个请假事件等待您的审批，请在OA系统中查看。</h3><br>OA链接：http://oa.xiaoquan.com:10000/vacation_approve/</br><br>此邮件为自动发送的提醒邮件，请勿回复。')).start()
    # send_mail(to_addr=supervisor_email,subject='请假审批提醒',body='<h3>有一个请假事件等待您的审批，请在OA系统中查看。</h3><br>OA链接：http://oa.xiaoquan.com:10000/vacation_approve/</br><br>此邮件为自动发送的提醒邮件，请勿回复。')
    return HttpResponse(simplejson.dumps({'code':0,'msg':u'保存成功'}),content_type="application/json")





