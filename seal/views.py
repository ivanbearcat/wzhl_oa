# -*- coding: utf-8 -*-
from django.shortcuts import render
from django.http import HttpResponse
from django.template import RequestContext
from django.db.models.query_utils import Q
from django.contrib.auth.decorators import login_required
from seal.models import table, detail
from vacation.models import user_table
from wzhl_oa.settings import BASE_DIR
import json
import datetime
import os
from libs.common import Num2MoneyFormat
from django import forms
from openpyxl import load_workbook


@login_required
def seal_apply(request):
    path = request.path.split('/')[1]
    return render(request, 'seal/seal_table.html',{'user':'%s%s' % (request.user.last_name,request.user.first_name),
                                                 'path1':'seal',
                                                 'path2':path,
                                                 'page_name1':u'印章管理',
                                                 'page_name2':u'印章申请',},
                                                context_instance=RequestContext(request))



@login_required
def seal_apply_data(request):
    sEcho =  request.POST.get('sEcho') #标志，直接返回
    iDisplayStart = int(request.POST.get('iDisplayStart'))#第几行开始
    iDisplayLength = int(request.POST.get('iDisplayLength'))#显示多少行
    iSortCol_0 = int(request.POST.get("iSortCol_0"))#排序行号
    sSortDir_0 = request.POST.get('sSortDir_0')#asc/desc
    sSearch = request.POST.get('sSearch')#高级搜索

    aaData = []
    sort = ['uuid','name','department','seal_class','usage','status','id']

    if  sSortDir_0 == 'asc':
        if sSearch == '':
            result_data = table.objects.filter(name=request.user.first_name).order_by(sort[iSortCol_0])[iDisplayStart:iDisplayStart+iDisplayLength]
            iTotalRecords = table.objects.filter(name=request.user.first_name).count()
        else:
            result_data = table.objects.filter(name=request.user.first_name)
            sSearch_list = sSearch.split()
            for i in range(len(sSearch_list)):
                result_data = result_data.filter(Q(uuid__contains=sSearch_list[i]) | \
                                                Q(name__contains=sSearch_list[i]))

                iTotalRecords = result_data.filter(Q(uuid__contains=sSearch_list[i]) | \
                                                Q(name__contains=sSearch_list[i])).count()
            result_data = result_data.order_by(sort[iSortCol_0]).reverse()[iDisplayStart:iDisplayStart+iDisplayLength]
    else:
        if sSearch == '':
            result_data = table.objects.filter(name=request.user.first_name).order_by(sort[iSortCol_0]).reverse()[iDisplayStart:iDisplayStart+iDisplayLength]
            iTotalRecords = table.objects.filter(name=request.user.first_name).count()
        else:
            result_data = table.objects.filter(name=request.user.first_name)
            sSearch_list = sSearch.split()
            for i in range(len(sSearch_list)):
                result_data = result_data.filter(Q(uuid__contains=sSearch_list[i]) | \
                                                Q(name__contains=sSearch_list[i]))

                iTotalRecords = result_data.filter(Q(uuid__contains=sSearch_list[i]) | \
                                                Q(name__contains=sSearch_list[i])).count()
            result_data = result_data.order_by(sort[iSortCol_0]).reverse()[iDisplayStart:iDisplayStart+iDisplayLength]


    for i in  result_data:
        aaData.append({
                       '0':i.uuid,
                       '1':i.name,
                       '2':i.department,
                       '3':i.seal_class,
                       '4':i.usage,
                       '5':i.status,
                       '6':i.id,
                       '7':i.approve_now
                      })
    result = {'sEcho':sEcho,
               'iTotalRecords':iTotalRecords,
               'iTotalDisplayRecords':iTotalRecords,
               'aaData':aaData
    }
    return HttpResponse(json.dumps(result),content_type="application/json")




@login_required
def seal_set_session(request):
    _id = request.POST.get('id')
    commit = request.POST.get('commit')
    if _id == '0':
        try:
            request.session.pop('seal_id')
        except KeyError:
            pass
    elif _id:
        request.session['seal_id'] = int(_id)
    if commit:
        request.session['seal_commit'] = commit
    return HttpResponse(json.dumps('OK'),content_type="application/json")




@login_required
def seal_apply_detail(request):
    path = request.path.split('/')[1]
    # uuid = request.POST.get('uuid')
    # name = request.POST.get('name')
    # department = request.POST.get('department')
    seal_from = request.POST.get('seal_from')
    seal_class = request.POST.get('seal_class')
    usage = request.POST.get('usage')
    reason = request.POST.get('reason')
    borrow_begin_time = request.POST.get('borrow_begin_time')
    borrow_end_time = request.POST.get('borrow_end_time')
    comment = request.POST.get('comment')
    _id = request.POST.get('id')
    commit = request.POST.get('commit')

    user_info_orm = user_table.objects.get(name=request.user.first_name)

    name = user_info_orm.name
    department = user_info_orm.department

    status = 0


    try:
        request.session.pop('seal_result')
    except KeyError:
        pass

    table_id =  request.session.get('seal_id')
    if not table_id:
        if seal_from:
            try:
                year = datetime.datetime.now().year
                if len(table.objects.filter(uuid__contains=year)) == 0:
                    uuid = str(datetime.datetime.now().year) + '-0001'
                else:
                    uuid_orm = table.objects.filter(contract_uuid__contains=year).order_by('id').reverse()[0]
                    uuid = str(datetime.datetime.now().year) + '-' + str(int(uuid_orm.uuid.split('-')[1]) + 1)


                status = 1
                approve_now = user_info_orm.principal

                try:
                    archive_path = request.session['seal_upload_file']
                    request.session['seal_upload_file'] = ''
                except KeyError:
                    archive_path = ''


                orm = table(uuid=uuid,name=name,department=department,seal_from=seal_from,seal_class=seal_class,\
                            usage=usage,reason=reason,archive_path=archive_path,borrow_begin_time=borrow_begin_time,\
                            borrow_end_time=borrow_end_time,comment=comment,status=status,approve_now=approve_now)

                orm.save()


                orm_last_id = table.objects.all().order_by('id').reverse()[0]

                orm2 = detail(name=request.user.first_name,operation=9,comment='',parent_id=orm_last_id.id)
                orm2.save()

                request.session['seal_result'] = u'保存成功'
            except Exception,e:
                print e
                request.session['seal_result'] = e
        else:
            if commit == '1':
                request.session['seal_result'] = u'星号为必填项'
    else:
        try:
            orm = table.objects.get(id=table_id)
            commit = request.session.get('seal_commit')

            if commit != '0':
                try:
                    archive_path = request.session['seal_upload_file']
                    request.session['seal_upload_file'] = ''
                except KeyError:
                    archive_path = ''

                orm.seal_from = seal_from
                orm.seal_class = seal_class
                orm.usage = usage
                orm.reason = reason
                orm.archive_path = archive_path
                orm.borrow_begin_time = borrow_begin_time
                orm.borrow_end_time = borrow_end_time
                orm.comment = comment

                # if orm.status == 0:
                #     if user_info_orm.principal == u'曹津' and process_type == 'l':
                #         print user_info_orm.principal
                #         orm.status = 2
                #         orm.approve_now = u'龚晓芸'
                #     else:
                #         orm.status = 1
                #         orm.approve_now = user_info_orm.principal

                orm.save()
                # request.session['contract_result'] = u'保存成功'
            # try:
            #     request.session.pop('contract_commit')
            # except KeyError:
            #     pass
            return render(request, 'seal/seal_table_detail.html',{'user':'%s%s' % (request.user.last_name,request.user.first_name),
                                                     'path1':'seal',
                                                     'path2':path,
                                                     'page_name1':u'印章管理',
                                                     'page_name2':u'印章信息',
                                                     'name':orm.name,
                                                     'department':orm.department,
                                                     'uuid':orm.uuid,
                                                     'seal_from':orm.seal_from,
                                                     'seal_class':orm.seal_class,
                                                     'usage':orm.usage,
                                                     'reason':orm.reason,
                                                     'archive_path':orm.archive_path,
                                                     'borrow_begin_time':orm.borrow_begin_time,
                                                     'borrow_end_time':orm.borrow_end_time,
                                                     'comment':orm.comment,
                                                     'status':orm.status,
                                                     'id':orm.id
                                                     },
                                                    context_instance=RequestContext(request))
        except Exception,e:
            print e
            request.session['contract_result'] = e
    return render(request, 'seal/seal_table_detail.html',{'user':'%s%s' % (request.user.last_name,request.user.first_name),
                                                     'path1':'seal',
                                                     'path2':path,
                                                     'page_name1':u'印章管理',
                                                     'page_name2':u'印章信息',
                                                     'name':name,
                                                     'department':department,
                                                     'status':status,
                                                     },
                                                    context_instance=RequestContext(request))




class UploadFileForm(forms.Form):
    title = forms.CharField(max_length=50)
    file = forms.FileField()

@login_required
def handle_uploaded_file(request,f):
    file_name = ''
    try:
        path = 'media/'
        # file_name = path + f.name
        today = datetime.datetime.now()
        os.system('mkdir -p {0}{1}/{2}/{3}/'.format(path, today.year, today.month, today.day))
        full_name = '{0}{1}/{2}/{3}/{4}'.format(path, today.year, today.month, today.day, f.name)
        if os.path.isfile(full_name):
            time = datetime.datetime.now().strftime('%H%M%S')
            full_name =  '{0}{1}/{2}/{3}/{4}_{5}'.format(path, today.year, today.month, today.day, time, f.name)
            # orm = upload_files.objects.get(file_name=f.name)
            # orm.file_name = f.name + '_' + time
            # orm.save()
        file = open(full_name, 'wb+')
        for chunk in f.chunks():
            file.write(chunk)
        file.close()
        file_size = os.path.getsize(full_name)
        # upload_files.objects.create(file_name=f.name,file_size=file_size,upload_user=request.user.username)

        request.session['seal_upload_file'] = full_name
        result_code = 0
    except Exception, e:
        import traceback
        print traceback.format_exc()
        # logger.error(e)
        result_code = 1
    return result_code



@login_required
def seal_approve(request):
    path = request.path.split('/')[1]
    return render(request, 'seal/seal_approve.html',{'user':'%s%s' % (request.user.last_name,request.user.first_name),
                                                 'path1':'seal',
                                                 'path2':path,
                                                 'page_name1':u'印章管理',
                                                 'page_name2':u'全部印章',},
                                                context_instance=RequestContext(request))




@login_required
def seal_approve_data(request):
    sEcho =  request.POST.get('sEcho') #标志，直接返回
    iDisplayStart = int(request.POST.get('iDisplayStart'))#第几行开始
    iDisplayLength = int(request.POST.get('iDisplayLength'))#显示多少行
    iSortCol_0 = int(request.POST.get("iSortCol_0"))#排序行号
    sSortDir_0 = request.POST.get('sSortDir_0')#asc/desc
    sSearch = request.POST.get('sSearch')#高级搜索

    aaData = []
    sort = ['uuid','name','department','seal_class','usage','status','id']

    subordinate = []
    subordinate_orm = user_table.objects.filter(principal=request.user.first_name)
    for i in subordinate_orm:
        subordinate.append(i.name)

    # if request.user.has_perm('contract.can_view_all'):
    #     if  sSortDir_0 == 'asc':
    #         if sSearch == '':
    #             result_data = table.objects.all().order_by(sort[iSortCol_0])[iDisplayStart:iDisplayStart+iDisplayLength]
    #             iTotalRecords = table.objects.all().count()
    #         else:
    #             result_data = table.objects.all()
    #             sSearch_list = sSearch.split()
    #             for i in range(len(sSearch_list)):
    #                 result_data = result_data.all().filter(Q(contract_uuid__contains=sSearch_list[i]) | \
    #                                                 Q(party_b__contains=sSearch_list[i]) | \
    #                                                 Q(contract_name__contains=sSearch_list[i]))
    #
    #                 iTotalRecords = result_data.all().filter(Q(contract_uuid__contains=sSearch_list[i]) | \
    #                                                 Q(party_b__contains=sSearch_list[i]) | \
    #                                                 Q(contract_name__contains=sSearch_list[i])).count()
    #             result_data = result_data.order_by(sort[iSortCol_0]).reverse()[iDisplayStart:iDisplayStart+iDisplayLength]
    #     else:
    #         if sSearch == '':
    #             result_data = table.objects.all().order_by(sort[iSortCol_0]).reverse()[iDisplayStart:iDisplayStart+iDisplayLength]
    #             iTotalRecords = table.objects.all().count()
    #         else:
    #             result_data = table.objects.all()
    #             sSearch_list = sSearch.split()
    #             for i in range(len(sSearch_list)):
    #                 result_data = result_data.all().filter(Q(contract_uuid__contains=sSearch_list[i]) | \
    #                                                 Q(party_b__contains=sSearch_list[i]) | \
    #                                                 Q(contract_name__contains=sSearch_list[i]))
    #
    #                 iTotalRecords = result_data.all().filter(Q(contract_uuid__contains=sSearch_list[i]) | \
    #                                                 Q(party_b__contains=sSearch_list[i]) | \
    #                                                 Q(contract_name__contains=sSearch_list[i])).count()
    #             result_data = result_data.order_by(sort[iSortCol_0]).reverse()[iDisplayStart:iDisplayStart+iDisplayLength]
    # else:
    if  sSortDir_0 == 'asc':
        if sSearch == '':
            result_data = table.objects.filter(approve_now=request.user.first_name).order_by(sort[iSortCol_0])[iDisplayStart:iDisplayStart+iDisplayLength]
            iTotalRecords = table.objects.filter(approve_now=request.user.first_name).count()
        else:
            result_data = table.objects.all()
            sSearch_list = sSearch.split()
            for i in range(len(sSearch_list)):
                result_data = result_data.filter(approve_now=request.user.first_name).filter(Q(contract_uuid__contains=sSearch_list[i]) | \
                                                Q(party_b__contains=sSearch_list[i]) | \
                                                Q(contract_name__contains=sSearch_list[i]))

                iTotalRecords = result_data.filter(approve_now=request.user.first_name).filter(Q(contract_uuid__contains=sSearch_list[i]) | \
                                                Q(party_b__contains=sSearch_list[i]) | \
                                                Q(contract_name__contains=sSearch_list[i])).count()
            result_data = result_data.order_by(sort[iSortCol_0]).reverse()[iDisplayStart:iDisplayStart+iDisplayLength]
    else:
        if sSearch == '':
            result_data = table.objects.filter(approve_now=request.user.first_name).order_by(sort[iSortCol_0]).reverse()[iDisplayStart:iDisplayStart+iDisplayLength]
            iTotalRecords = table.objects.filter(approve_now=request.user.first_name).count()
        else:
            result_data = table.objects.all()
            sSearch_list = sSearch.split()
            for i in range(len(sSearch_list)):
                result_data = result_data.filter(approve_now=request.user.first_name).filter(Q(contract_uuid__contains=sSearch_list[i]) | \
                                                Q(party_b__contains=sSearch_list[i]) | \
                                                Q(contract_name__contains=sSearch_list[i]))

                iTotalRecords = result_data.filter(approve_now=request.user.first_name).filter(Q(contract_uuid__contains=sSearch_list[i]) | \
                                                Q(party_b__contains=sSearch_list[i]) | \
                                                Q(contract_name__contains=sSearch_list[i])).count()
            result_data = result_data.order_by(sort[iSortCol_0]).reverse()[iDisplayStart:iDisplayStart+iDisplayLength]


    for i in  result_data:
        export = '''
                    <a class="btn btn-sm green">
                        生成Excel文件 <i class="fa fa-level-down"></i>
                    </a>
                '''
        approve = '''
                    <a class="btn btn-sm blue">
                        审批 <i class="fa"></i>
                    </a>
                 '''
        aaData.append({
                       '0':i.contract_uuid,
                       '1':str(i.apply_time),
                       '2':i.name,
                       '3':i.contract_class,
                       '4':i.party_b,
                       '5':i.contract_name,
                       '6':i.contract_amount_figures,
                       '7':i.status,
                       '8':export,
                       '9':approve,
                       '10':i.id,
                       '11':i.process_type,
                       '12':i.approve_now
                      })
    result = {'sEcho':sEcho,
               'iTotalRecords':iTotalRecords,
               'iTotalDisplayRecords':iTotalRecords,
               'aaData':aaData
    }
    return HttpResponse(json.dumps(result),content_type="application/json")



@login_required
def seal_get_upload(request):
    file = request.FILES.get('file')
    if not file == None:
        result_code = handle_uploaded_file(request,file)
        if result_code == 0:
            return HttpResponse(json.dumps({'msg': "上传成功", "code": 0}),content_type="application/json")
        else:
            return HttpResponse(json.dumps({'msg': "上传失败", "code": 1}),content_type="application/json")
    else:
        return HttpResponse(json.dumps({'msg': "上传失败", "code": 1}),content_type="application/json")