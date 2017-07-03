# -*- coding: utf-8 -*-
from django.shortcuts import render
from django.http import HttpResponse,HttpResponseRedirect
from django.template import RequestContext
from django.db.models.query_utils import Q
from django.contrib.auth.decorators import login_required
from libs.sendmail import send_mail
from business_trip.models import *
from vacation.models import user_table
import json
import datetime
from wzhl_oa.settings import administration


import sys
reload(sys)
sys.setdefaultencoding('utf-8')


@login_required
def business_trip_table(request):
    path = request.path.split('/')[1]

    return render(request, 'business_trip/business_trip_table.html',{'user':'%s%s' % (request.user.last_name,request.user.first_name),
                                                 'path1':'business_trip',
                                                 'path2':path,
                                                 'page_name1':u'出差管理',
                                                 'page_name2':u'出差申请',
                                                 'username':request.user.username},
                                                context_instance=RequestContext(request))



@login_required
def business_trip_table_data(request):
    sEcho =  request.POST.get('sEcho') #标志，直接返回
    iDisplayStart = int(request.POST.get('iDisplayStart'))#第几行开始
    iDisplayLength = int(request.POST.get('iDisplayLength'))#显示多少行
    iSortCol_0 = int(request.POST.get("iSortCol_0"))#排序行号
    sSortDir_0 = request.POST.get('sSortDir_0')#asc/desc
    sSearch = request.POST.get('sSearch')#高级搜索

    aaData = []
    sort = ['name', 'reason', 'destination', 'apply_time', None, None, 'vehicle', None, 'budget_sum', 'status', None, None, None, 'id']

    if  sSortDir_0 == 'asc':
        if sSearch == '':
            print iSortCol_0
            result_data = main.objects.filter(name=request.user.first_name).order_by(sort[iSortCol_0])[iDisplayStart:iDisplayStart+iDisplayLength]
            iTotalRecords = main.objects.filter(name=request.user.first_name).count()
        else:
            result_data = main.objects.filter(name=request.user.first_name).filter(Q(name__contains=sSearch) | \
                                                                                    Q(reason__contains=sSearch) | \
                                                                                    Q(vehicle__contains=sSearch) | \
                                                                                    Q(destination__contains=sSearch)) \
                                                                                .order_by(sort[iSortCol_0])[iDisplayStart:iDisplayStart+iDisplayLength]
            iTotalRecords = main.objects.filter(name=request.user.first_name).filter(Q(name__contains=sSearch) | \
                                                                                    Q(reason__contains=sSearch) | \
                                                                                    Q(vehicle__contains=sSearch) | \
                                                                                    Q(destination__contains=sSearch)).count()
    else:
        if sSearch == '':
            result_data = main.objects.filter(name=request.user.first_name).order_by(sort[iSortCol_0]).reverse()[iDisplayStart:iDisplayStart+iDisplayLength]
            iTotalRecords = main.objects.filter(name=request.user.first_name).count()
        else:
            result_data = main.objects.filter(name=request.user.first_name).filter(Q(name__contains=sSearch) | \
                                                                                    Q(reason__contains=sSearch) | \
                                                                                    Q(vehicle__contains=sSearch) | \
                                                                                    Q(destination__contains=sSearch)) \
                                                    .order_by(sort[iSortCol_0]).reverse()[iDisplayStart:iDisplayStart+iDisplayLength]
            iTotalRecords = main.objects.filter(name=request.user.first_name).filter(Q(name__contains=sSearch) | \
                                                                                    Q(reason__contains=sSearch) | \
                                                                                    Q(vehicle__contains=sSearch) | \
                                                                                    Q(destination__contains=sSearch)).count()



    for i in  result_data:
        budget_info = '''
                    <a class="btn btn-sm blue">
                        详细预算 <i class="fa"></i>
                    </a>
                '''.format(i.id)
        export = '''
                    <a class="btn btn-sm green">
                        生成Excel文件 <i class="fa fa-level-down"></i>
                    </a>
                '''.format(i.id)
        delete = '''
                    <a class="btn btn-sm red">
                        删除 <i class="fa"></i>
                    </a>
                 '''.format(i.id)
        if i.hotel_reservation == 1:
            hotel_reservation = u'是'
        else:
            hotel_reservation = u'否'
        aaData.append({
                       '0':i.name,
                       '1':i.reason,
                       '2':i.destination,
                       '3':str(i.apply_time),
                       '4':i.date,
                       '5':i.travel_partner,
                       '6':i.vehicle,
                       '7':hotel_reservation,
                       '8':i.budget_sum,
                       '9':i.status,
                       '10':budget_info,
                       '11':export,
                       '12':delete,
                       '13':i.id,
                       '14':i.approve_now
                      })
    result = {'sEcho':sEcho,
               'iTotalRecords':iTotalRecords,
               'iTotalDisplayRecords':iTotalRecords,
               'aaData':aaData
    }
    return HttpResponse(json.dumps(result),content_type="application/json")



@login_required
def business_trip_table_save(request):
    reason = request.POST.get('reason')
    destination = request.POST.get('destination')
    begin = request.POST.get('begin')
    end = request.POST.get('end')
    travel_partner = request.POST.get('travel_partner')
    vehicle = request.POST.get('vehicle')
    hotel_reservation = request.POST.get('hotel_reservation')
    _id = request.POST.get('id')

    if begin == end:
        date = begin
    else:
        date = begin + '&nbsp->&nbsp' + end

    if not _id:
        orm_fetch_supervisor = user_table.objects.get(name=request.user.first_name)

        approve_now = orm_fetch_supervisor.supervisor

        orm = main(name=request.user.first_name, reason=reason, destination=destination, date=date, travel_partner=travel_partner,
             vehicle=vehicle, hotel_reservation=hotel_reservation, budget_sum=0, status=1, approve_now=approve_now,
             commit_time=datetime.datetime.now())
        orm.save()
    else:
        orm = main.objects.get(id=_id)
        orm.reason = reason
        orm.destination = destination
        orm.date = date
        orm.travel_partner = travel_partner
        orm.vehicle = vehicle
        orm.hotel_reservation = hotel_reservation
        orm.save()

    return HttpResponse(json.dumps({'code':0,'msg':u'保存成功'}),content_type="application/json")



@login_required
def business_trip_table_del(request):
    _id = request.POST.get('id')
    orm = main.objects.get(id=_id)
    if orm.status == 5 or orm.status == 6 or orm.status == 7 or orm.status == 8:
        return HttpResponse(json.dumps({'code':1,'msg':u'无法删除'}),content_type="application/json")
    else:
        orm.delete()
        return HttpResponse(json.dumps({'code':0,'msg':u'删除成功'}),content_type="application/json")





@login_required
def business_trip_set_session(request):
    parent_id = request.POST.get('parent_id')
    request.session['parent_id'] = parent_id
    return HttpResponse(json.dumps('OK'),content_type="application/json")





@login_required
def business_trip_budget(request):
    path = request.path.split('/')[1]
    return render(request, 'business_trip/business_trip_budget.html',{'user':'%s%s' % (request.user.last_name,request.user.first_name),
                                                 'path1':'business_trip',
                                                 'path2':path,
                                                 'page_name1':u'出差管理',
                                                 'page_name2':u'出差申请',
                                                 'username':request.user.username},
                                                context_instance=RequestContext(request))




@login_required
def business_trip_budget_data(request):
    sEcho =  request.POST.get('sEcho') #标志，直接返回
    iDisplayStart = int(request.POST.get('iDisplayStart'))#第几行开始
    iDisplayLength = int(request.POST.get('iDisplayLength'))#显示多少行
    iSortCol_0 = int(request.POST.get("iSortCol_0"))#排序行号
    sSortDir_0 = request.POST.get('sSortDir_0')#asc/desc
    sSearch = request.POST.get('sSearch')#高级搜索

    parent_id = request.session.get('parent_id')

    aaData = []
    sort = ['budget_type', 'budget', 'id']

    if  sSortDir_0 == 'asc':
        if sSearch == '':
            print iSortCol_0
            result_data = budget.objects.filter(parent_id=parent_id).order_by(sort[iSortCol_0])[iDisplayStart:iDisplayStart+iDisplayLength]
            iTotalRecords = budget.objects.filter(parent_id=parent_id).count()
        else:
            result_data = budget.objects.filter(parent_id=parent_id).filter(Q(budget_type__contains=sSearch) | \
                                                                                    Q(budget__contains=sSearch)) \
                                                                                .order_by(sort[iSortCol_0])[iDisplayStart:iDisplayStart+iDisplayLength]
            iTotalRecords = budget.objects.filter(parent_id=parent_id).filter(Q(budget_type__contains=sSearch) | \
                                                                                    Q(budget__contains=sSearch)).count()
    else:
        if sSearch == '':
            result_data = budget.objects.filter(parent_id=parent_id).order_by(sort[iSortCol_0]).reverse()[iDisplayStart:iDisplayStart+iDisplayLength]
            iTotalRecords = budget.objects.filter(parent_id=parent_id).count()
        else:
            result_data = budget.objects.filter(parent_id=parent_id).filter(Q(budget_type__contains=sSearch) | \
                                                                                    Q(budget__contains=sSearch)) \
                                                    .order_by(sort[iSortCol_0]).reverse()[iDisplayStart:iDisplayStart+iDisplayLength]
            iTotalRecords = budget.objects.filter(parent_id=parent_id).filter(Q(budget_type__contains=sSearch) | \
                                                                                    Q(budget__contains=sSearch)).count()



    for i in  result_data:
        aaData.append({
                       '0':i.budget_type,
                       '1':i.budget,
                       '2':i.id,
                      })
    result = {'sEcho':sEcho,
               'iTotalRecords':iTotalRecords,
               'iTotalDisplayRecords':iTotalRecords,
               'aaData':aaData
    }
    return HttpResponse(json.dumps(result),content_type="application/json")



@login_required
def business_trip_budget_save(request):
    budget_type = request.POST.get('budget_type')
    _budget = request.POST.get('budget')
    parent_id = request.POST.get('parent_id')
    _id = request.POST.get('id')

    if not _id:
        orm = budget(budget_type=budget_type, budget=_budget, parent_id=int(parent_id))
        orm.save()
        budget_sum = 0
        orm2 = budget.objects.filter(parent_id=parent_id)
        for i in orm2:
            budget_sum += i.budget
        orm3 = main.objects.get(id=parent_id)
        orm3.budget_sum = budget_sum
        orm3.save()
    else:
        orm = budget.objects.get(id=_id)
        orm.budget_type = budget_type
        orm.budget = int(_budget)
        orm.save()
        budget_sum = 0
        orm2 = budget.objects.filter(parent_id=parent_id)
        for i in orm2:
            budget_sum += i.budget
        orm3 = main.objects.get(id=parent_id)
        orm3.budget_sum = budget_sum
        orm3.save()

    return HttpResponse(json.dumps({'code':0,'msg':u'保存成功'}),content_type="application/json")




@login_required
def business_trip_budget_del(request):
    _id = request.POST.get('id')
    orm = budget.objects.get(id=_id)
    orm.delete()
    return HttpResponse(json.dumps({'code':0,'msg':u'删除成功'}),content_type="application/json")




@login_required
def business_trip_approve(request):
    path = request.path.split('/')[1]
    return render(request, 'business_trip/business_trip_approve.html',{'user':'%s%s' % (request.user.last_name,request.user.first_name),
                                                 'path1':'business_trip',
                                                 'path2':path,
                                                 'page_name1':u'出差管理',
                                                 'page_name2':u'出差审批',
                                                 'username':request.user.username},
                                                context_instance=RequestContext(request))





@login_required
def business_trip_approve_data(request):
    sEcho =  request.POST.get('sEcho') #标志，直接返回
    iDisplayStart = int(request.POST.get('iDisplayStart'))#第几行开始
    iDisplayLength = int(request.POST.get('iDisplayLength'))#显示多少行
    iSortCol_0 = int(request.POST.get("iSortCol_0"))#排序行号
    sSortDir_0 = request.POST.get('sSortDir_0')#asc/desc
    sSearch = request.POST.get('sSearch')#高级搜索

    aaData = []
    sort = ['name', 'reason', 'destination', 'apply_time', None, None, 'vehicle', None, 'budget_sum', 'status', None, None, None, 'id']

    if request.user.has_perm('business_trip.can_view_all'):
        if  sSortDir_0 == 'asc':
            if sSearch == '':
                print iSortCol_0
                result_data = main.objects.filter(name=request.user.first_name).order_by(sort[iSortCol_0])[iDisplayStart:iDisplayStart+iDisplayLength]
                iTotalRecords = main.objects.filter(name=request.user.first_name).count()
            else:
                result_data = main.objects.filter(name=request.user.first_name).filter(Q(name__contains=sSearch) | \
                                                                                        Q(reason__contains=sSearch) | \
                                                                                        Q(vehicle__contains=sSearch) | \
                                                                                        Q(destination__contains=sSearch)) \
                                                                                    .order_by(sort[iSortCol_0])[iDisplayStart:iDisplayStart+iDisplayLength]
                iTotalRecords = main.objects.filter(name=request.user.first_name).filter(Q(name__contains=sSearch) | \
                                                                                        Q(reason__contains=sSearch) | \
                                                                                        Q(vehicle__contains=sSearch) | \
                                                                                        Q(destination__contains=sSearch)).count()
        else:
            if sSearch == '':
                result_data = main.objects.filter(name=request.user.first_name).order_by(sort[iSortCol_0]).reverse()[iDisplayStart:iDisplayStart+iDisplayLength]
                iTotalRecords = main.objects.filter(name=request.user.first_name).count()
            else:
                result_data = main.objects.filter(name=request.user.first_name).filter(Q(name__contains=sSearch) | \
                                                                                        Q(reason__contains=sSearch) | \
                                                                                        Q(vehicle__contains=sSearch) | \
                                                                                        Q(destination__contains=sSearch)) \
                                                        .order_by(sort[iSortCol_0]).reverse()[iDisplayStart:iDisplayStart+iDisplayLength]
                iTotalRecords = main.objects.filter(name=request.user.first_name).filter(Q(name__contains=sSearch) | \
                                                                                        Q(reason__contains=sSearch) | \
                                                                                        Q(vehicle__contains=sSearch) | \
                                                                                        Q(destination__contains=sSearch)).count()
    else:
        if  sSortDir_0 == 'asc':
            if sSearch == '':
                print iSortCol_0
                result_data = main.objects.filter(approve_now=request.user.first_name).order_by(sort[iSortCol_0])[iDisplayStart:iDisplayStart+iDisplayLength]
                iTotalRecords = main.objects.filter(approve_now=request.user.first_name).count()
            else:
                result_data = main.objects.filter(approve_now=request.user.first_name).filter(Q(name__contains=sSearch) | \
                                                                                        Q(reason__contains=sSearch) | \
                                                                                        Q(vehicle__contains=sSearch) | \
                                                                                        Q(destination__contains=sSearch)) \
                                                                                    .order_by(sort[iSortCol_0])[iDisplayStart:iDisplayStart+iDisplayLength]
                iTotalRecords = main.objects.filter(approve_now=request.user.first_name).filter(Q(name__contains=sSearch) | \
                                                                                        Q(reason__contains=sSearch) | \
                                                                                        Q(vehicle__contains=sSearch) | \
                                                                                        Q(destination__contains=sSearch)).count()
        else:
            if sSearch == '':
                result_data = main.objects.filter(approve_now=request.user.first_name).order_by(sort[iSortCol_0]).reverse()[iDisplayStart:iDisplayStart+iDisplayLength]
                iTotalRecords = main.objects.filter(approve_now=request.user.first_name).count()
            else:
                result_data = main.objects.filter(approve_now=request.user.first_name).filter(Q(name__contains=sSearch) | \
                                                                                        Q(reason__contains=sSearch) | \
                                                                                        Q(vehicle__contains=sSearch) | \
                                                                                        Q(destination__contains=sSearch)) \
                                                        .order_by(sort[iSortCol_0]).reverse()[iDisplayStart:iDisplayStart+iDisplayLength]
                iTotalRecords = main.objects.filter(approve_now=request.user.first_name).filter(Q(name__contains=sSearch) | \
                                                                                        Q(reason__contains=sSearch) | \
                                                                                        Q(vehicle__contains=sSearch) | \
                                                                                        Q(destination__contains=sSearch)).count()


    for i in  result_data:
        budget_info = '''
                    <a class="btn btn-sm blue">
                        详细预算 <i class="fa"></i>
                    </a>
                '''
        export = '''
                    <a class="btn btn-sm green">
                        生成Excel文件 <i class="fa fa-level-down"></i>
                    </a>
                '''
        approve = '''
                    <a class="btn btn-sm green">
                        审批通过 <i class="fa"></i>
                    </a>
                 '''
        not_approve = '''
                    <a class="btn btn-sm red">
                        审批不通过 <i class="fa"></i>
                    </a>
                 '''
        if i.hotel_reservation == 1:
            hotel_reservation = u'是'
        else:
            hotel_reservation = u'否'
        aaData.append({
                       '0':i.name,
                       '1':i.reason,
                       '2':i.destination,
                       '3':str(i.apply_time),
                       '4':i.date,
                       '5':i.travel_partner,
                       '6':i.vehicle,
                       '7':hotel_reservation,
                       '8':i.budget_sum,
                       '9':i.status,
                       '10':budget_info,
                       '11':export,
                       '12':approve,
                       '13':not_approve,
                       '14':i.id,
                       '15':i.approve_now
                      })
    result = {'sEcho':sEcho,
               'iTotalRecords':iTotalRecords,
               'iTotalDisplayRecords':iTotalRecords,
               'aaData':aaData
    }
    return HttpResponse(json.dumps(result),content_type="application/json")



@login_required
def business_trip_approve_process(request):
    flag = request.POST.get('flag')
    _id = request.POST.get('id')
    status = request.POST.get('status')

    orm = main.objects.get(id=_id)
    if flag == '1':
        if status == '1':
            orm.status = 2
            orm2 = user_table.objects.get(name=request.user.first_name)
            orm.approve_now = orm2.principal
            orm.apply_time = datetime.datetime.now()
        elif status == '2':
            orm.status = 3
            orm.approve_now = administration['name']
            orm.apply_time = datetime.datetime.now()
        elif status == '3':
            orm.status = 4
            orm.approve_now = administration['name']
            orm.apply_time = datetime.datetime.now()
        elif status == '4':
            orm.status = 5
            orm.approve_now = ''
    else:
        if status == '4':
            orm.status = 6
            orm.approve_now = ''
        else:
            orm.status = 7
            orm.approve_now = ''

    orm.save()
    return HttpResponse(json.dumps({'code':0,'msg':u'审批成功'}),content_type="application/json")





