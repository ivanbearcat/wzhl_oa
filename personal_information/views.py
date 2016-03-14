# -*- coding: utf-8 -*-
from django.shortcuts import render
from django.http import HttpResponse
from django.template import RequestContext
from django.db.models.query_utils import Q
from django.contrib.auth.decorators import login_required
from personal_information.models import table
from wzhl_oa.settings import BASE_DIR
import json
import datetime

@login_required
def personal_information_table(request):
    path = request.path.split('/')[1]
    return render(request, 'personal_information/personal_information_table.html',{'user':'%s%s' % (request.user.last_name,request.user.first_name),
                                                 'path1':'personal_information',
                                                 'path2':path,
                                                 'page_name1':u'人员信息',
                                                 'page_name2':u'人员基本信息表',},
                                                context_instance=RequestContext(request))

@login_required
def personal_information_table_data(request):
    sEcho =  request.POST.get('sEcho') #标志，直接返回
    iDisplayStart = int(request.POST.get('iDisplayStart'))#第几行开始
    iDisplayLength = int(request.POST.get('iDisplayLength'))#显示多少行
    iSortCol_0 = int(request.POST.get("iSortCol_0"))#排序行号
    sSortDir_0 = request.POST.get('sSortDir_0')#asc/desc
    sSearch = request.POST.get('sSearch')#高级搜索

    aaData = []
    sort = ['name','phone','email','keywords']

    if  sSortDir_0 == 'asc':
        if sSearch == '':
            result_data = table.objects.all().order_by(sort[iSortCol_0])[iDisplayStart:iDisplayStart+iDisplayLength]
            iTotalRecords = table.objects.all().count()
        else:
            result_data = table.objects.all()
            sSearch_list = sSearch.split()
            for i in range(len(sSearch_list)):
                result_data = result_data.filter(Q(name__contains=sSearch_list[i]) | \
                                                        Q(phone__contains=sSearch_list[i]) | \
                                                        Q(email__contains=sSearch_list[i]) | \
                                                        Q(keywords__contains=sSearch_list[i]))

                iTotalRecords = result_data.filter(Q(name__contains=sSearch_list[i]) | \
                                                        Q(phone__contains=sSearch_list[i]) | \
                                                        Q(email__contains=sSearch_list[i]) | \
                                                        Q(keywords__contains=sSearch_list[i])).count()
            result_data = result_data.order_by(sort[iSortCol_0]).reverse()[iDisplayStart:iDisplayStart+iDisplayLength]
    else:
        if sSearch == '':
            result_data = table.objects.all().order_by(sort[iSortCol_0]).reverse()[iDisplayStart:iDisplayStart+iDisplayLength]
            iTotalRecords = table.objects.all().count()
        else:
            result_data = table.objects.all()
            sSearch_list = sSearch.split()
            for i in range(len(sSearch_list)):
                result_data = result_data.filter(Q(name__contains=sSearch_list[i]) | \
                                                        Q(phone__contains=sSearch_list[i]) | \
                                                        Q(email__contains=sSearch_list[i]) | \
                                                        Q(keywords__contains=sSearch_list[i]))

                iTotalRecords = result_data.filter(Q(name__contains=sSearch_list[i]) | \
                                                        Q(phone__contains=sSearch_list[i]) | \
                                                        Q(email__contains=sSearch_list[i]) | \
                                                        Q(keywords__contains=sSearch_list[i])).count()
            result_data = result_data.order_by(sort[iSortCol_0]).reverse()[iDisplayStart:iDisplayStart+iDisplayLength]


    for i in  result_data:
        aaData.append({
                       '0':i.name,
                       '1':i.phone,
                       '2':i.email,
                       '3':i.keywords,
                       '4':i.id
                      })
    result = {'sEcho':sEcho,
               'iTotalRecords':iTotalRecords,
               'iTotalDisplayRecords':iTotalRecords,
               'aaData':aaData
    }
    return HttpResponse(json.dumps(result),content_type="application/json")

@login_required
def personal_information_table_detail(request):
    path = request.path.split('/')[1]
    name = request.POST.get('name')
    email = request.POST.get('email')
    phone = request.POST.get('phone')
    keywords = request.POST.get('keywords')
    sex = request.POST.get('sex')
    birthday = request.POST.get('birthday')
    graduate_date = request.POST.get('graduate_date')
    first_education = request.POST.get('first_education')
    education = request.POST.get('education')
    specialty = request.POST.get('specialty')
    graduate_school = request.POST.get('graduate_school')
    last_company = request.POST.get('last_company')
    channel = request.POST.get('channel')
    referrer = request.POST.get('referrer')
    salary = request.POST.get('salary')
    job_level = request.POST.get('job_level')
    job_title = request.POST.get('job_title')
    job_type = request.POST.get('job_type')
    resumes = request.FILES.get('resumes')
    direction = request.POST.get('direction')
    resource_state = request.POST.get('resource_state')
    comment = request.POST.get('comment')
    executor = request.POST.get('executor')
    _id = request.POST.get('id')

    if _id:
        orm = table.objects.get(id=_id)
        if orm.resource_state != resource_state:
            orm.state_change_time = datetime.datetime.now()
        orm.name = name
        orm.email = email
        orm.phone = phone
        orm.keywords = keywords
        orm.sex = sex
        orm.birthday = birthday
        orm.graduate_date = graduate_date
        orm.first_education = first_education
        orm.education = education
        orm.specialty = specialty
        orm.graduate_school = graduate_school
        orm.last_company = last_company
        orm.channel = channel
        orm.referrer = referrer
        orm.salary = salary
        orm.job_level = job_level
        orm.job_title = job_title
        orm.job_type = job_type
        orm.resumes = resumes
        orm.direction = direction
        orm.resource_state = resource_state
        orm.comment = comment
        orm.executor = executor
    else:
        orm.object




    return render(request, 'personal_information/personal_information_table_detail.html',{'user':'%s%s' % (request.user.last_name,request.user.first_name),
                                                 'path1':'personal_information',
                                                 'path2':path,
                                                 'page_name1':u'人员信息',
                                                 'page_name2':u'人员基本信息表',},
                                                context_instance=RequestContext(request))

