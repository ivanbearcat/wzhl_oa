# -*- coding: utf-8 -*-
from django.shortcuts import render
from django.http import HttpResponse
from vacation.models import user_table,operation_log
from django.db.models.query_utils import Q
from django.utils.log import logger
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
import simplejson,datetime

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
            'seasons_leave_total','id']

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
                       '15':i.id
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
                     statutory_annual_leave_available=statutory_annual_leave_available,statutory_annual_leave_used=0,
                     statutory_annual_leave_total=statutory_annual_leave_total,company_annual_leave_available=company_annual_leave_available,
                     company_annual_leave_used=0,company_annual_leave_total=company_annual_leave_total,seasons_leave_available=1,
                     seasons_leave_used=0,seasons_leave_total=1,has_approve=0)

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
    orm = user_table.objects.get(name=request.user.first_name)
    return render(request, 'vacation/vacation_apply.html',{'user':'%s%s' % (request.user.last_name,request.user.first_name),
                                                       'path1':'vacation',
                                                       'path2':path,
                                                       'page_name1':u'请假管理',
                                                       'page_name2':u'请假申请',
                                                       'statutory_annual_leave_available':orm.statutory_annual_leave_available,
                                                       'company_annual_leave_available':orm.company_annual_leave_available,
                                                       'seasons_leave_available':orm.seasons_leave_available})