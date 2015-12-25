# -*- coding: utf-8 -*-
from django.shortcuts import render
from django.http import HttpResponse
from django.template import RequestContext
from django.db.models.query_utils import Q
from assets.models import table
from libs.common import int_format
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from wzhl_oa.settings import description,model,category,department
import simplejson,datetime,xlsxwriter,re

@login_required
def assets_table(request):
    path = request.path.split('/')[1]
    if not request.user.has_perm('assets.can_view'):
        return render(request,'public/no_passing.html')
    return render(request, 'assets/assets_table.html',{'user':'%s%s' % (request.user.last_name,request.user.first_name),
                                                       'path1':'assets',
                                                       'path2':path,
                                                       'page_name1':u'资产管理',
                                                       'page_name2':u'资产表'},context_instance=RequestContext(request))

@login_required
def assets_table_data(request):
    sEcho =  request.POST.get('sEcho') #标志，直接返回
    iDisplayStart = int(request.POST.get('iDisplayStart'))#第几行开始
    iDisplayLength = int(request.POST.get('iDisplayLength'))#显示多少行
    iSortCol_0 = int(request.POST.get("iSortCol_0"))#排序行号
    sSortDir_0 = request.POST.get('sSortDir_0')#asc/desc
    sSearch = request.POST.get('sSearch')#高级搜索

    aaData = []
    sort = ['FANO','description','model','category','department','employee','purchase_date','payment','cost',
            'residual_life','residual_value','depreciation','total_depreciation','netbook_value','comment']

    if  sSortDir_0 == 'asc':
        if sSearch == '':
            result_data = table.objects.all().order_by(sort[iSortCol_0])[iDisplayStart:iDisplayStart+iDisplayLength]
            iTotalRecords = table.objects.all().count()
        else:
            result_data = table.objects.filter(Q(FANO__contains=sSearch) | \
                                                    Q(description__contains=sSearch) | \
                                                    Q(model__contains=sSearch) | \
                                                    Q(category__contains=sSearch) | \
                                                    Q(department__contains=sSearch) | \
                                                    Q(employee__contains=sSearch) | \
                                                    Q(comment__contains=sSearch)) \
                                                    .order_by(sort[iSortCol_0])[iDisplayStart:iDisplayStart+iDisplayLength]
            iTotalRecords = table.objects.filter(Q(FANO__contains=sSearch) | \
                                                    Q(description__contains=sSearch) | \
                                                    Q(model__contains=sSearch) | \
                                                    Q(category__contains=sSearch) | \
                                                    Q(department__contains=sSearch) | \
                                                    Q(employee__contains=sSearch) | \
                                                    Q(comment__contains=sSearch)).count()
    else:
        if sSearch == '':
            result_data = table.objects.all().order_by(sort[iSortCol_0]).reverse()[iDisplayStart:iDisplayStart+iDisplayLength]
            iTotalRecords = table.objects.all().count()
        else:
            result_data = table.objects.filter(Q(FANO__contains=sSearch) | \
                                                    Q(description__contains=sSearch) | \
                                                    Q(model__contains=sSearch) | \
                                                    Q(category__contains=sSearch) | \
                                                    Q(department__contains=sSearch) | \
                                                    Q(employee__contains=sSearch) | \
                                                    Q(comment__contains=sSearch)) \
                                                    .order_by(sort[iSortCol_0]).reverse()[iDisplayStart:iDisplayStart+iDisplayLength]
            iTotalRecords = table.objects.filter(Q(FANO__contains=sSearch) | \
                                                    Q(description__contains=sSearch) | \
                                                    Q(model__contains=sSearch) | \
                                                    Q(category__contains=sSearch) | \
                                                    Q(department__contains=sSearch) | \
                                                    Q(employee__contains=sSearch) | \
                                                    Q(comment__contains=sSearch)).count()

    for i in  result_data:
        i_dict = {}
        i_dict['payment'] = int_format(float('%.2f' % i.payment))
        i_dict['cost'] = int_format(float('%.2f' % i.cost))
        i_dict['residual_value'] = int_format(float('%.2f' % i.residual_value))
        i_dict['depreciation'] = int_format(float('%.2f' % i.depreciation))
        i_dict['total_depreciation'] = int_format(float('%.2f' % i.total_depreciation))
        i_dict['netbook_value'] = int_format(float('%.2f' % i.netbook_value))
        for j in i_dict.keys():
            i_dict[j] = re.sub(r'\.0$','.00',i_dict[j])

        aaData.append({
                       '0':i.FANO,
                       '1':i.description,
                       '2':i.model,
                       '3':i.category,
                       '4':i.residual_life,
                       '5':i.department,
                       '6':i.employee,
                       '7':str(i.purchase_date).split('+')[0],
                       '8':i_dict['payment'],
                       '9':i_dict['cost'],
                       '10':i_dict['residual_value'],
                       '11':i_dict['depreciation'],
                       '12':i_dict['total_depreciation'],
                       '13':i_dict['netbook_value'],
                       '14':i.comment,
                       '15':i.id
                      })
    result = {'sEcho':sEcho,
               'iTotalRecords':iTotalRecords,
               'iTotalDisplayRecords':iTotalRecords,
               'aaData':aaData
    }
    return HttpResponse(simplejson.dumps(result),content_type="application/json")

@login_required
def assets_table_dropdown(request):
    _id = request.POST.get('id')
    _description = request.POST.get('description')
    _model = request.POST.get('model')
    _category = request.POST.get('category')
    _department = request.POST.get('department')

    result = {}
    result['description'] = []
    result['model'] = []
    result['category'] = []
    result['department'] = []

    if not _id == None:
        result['description_edit'] = []
        result['model_edit'] = []
        result['category_edit'] = []
        result['department_edit'] = []

        for i in range(len(description)):
            if description[i] == _description:
                result['description_edit'].append({'text':description[i],'id':i})
        for i in range(len(model)):
            if model[i] == _model:
                result['model_edit'].append({'text':model[i],'id':i})
        for i in range(len(category.keys())):
            if category.keys()[i] == _category:
                result['category_edit'].append({'text':category.keys()[i],'id':i})
        for i in range(len(department)):
            if department[i] == _department:
                result['department_edit'].append({'text':department[i],'id':i})
    else:
        for i in range(len(description)):
            result['description'].append({'text':description[i],'id':i})
        for i in range(len(model)):
            result['model'].append({'text':model[i],'id':i})
        for i in range(len(category.keys())):
            result['category'].append({'text':category.keys()[i],'id':i})
        for i in range(len(department)):
            result['department'].append({'text':department[i],'id':i})

    return HttpResponse(simplejson.dumps(result),content_type="application/json")

@login_required
def assets_table_save(request):
    FANO = request.POST.get('FANO')
    _description = request.POST.get('description')
    _model = request.POST.get('model')
    _category = request.POST.get('category')
    _department = request.POST.get('department')
    employee = request.POST.get('employee')
    purchase_date = request.POST.get('purchase_date')
    payment = request.POST.get('payment')
    cost = request.POST.get('cost')
    comment = request.POST.get('comment')
    _id = request.POST.get('id')

    try:
        if _id =='':
            residual_value = float(cost) * 0.05
            depreciation = (float(cost) - residual_value) / category[str(_category)]

            orm = table(FANO=FANO,description=_description,model=_model,category=_category,department=_department,
                        employee=employee,purchase_date=purchase_date,payment=payment,cost=cost,residual_life=category[str(_category)],
                        residual_value=residual_value,depreciation=depreciation,total_depreciation=0,
                        netbook_value=float(cost),comment=comment)
            orm.save()
        else:
            orm = table.objects.get(id=_id)
            orm.department = _department
            orm.employee = employee
            orm.comment = comment
            orm.save()

        return HttpResponse(simplejson.dumps({'code':0,'msg':u'保存成功'}),content_type="application/json")
    except Exception,e:
        print e
        return HttpResponse(simplejson.dumps({'code':1,'msg':str(e)}),content_type="application/json")

@login_required
def assets_export_excel(request):
    try:
        workbook = xlsxwriter.Workbook('static/files/fixed_assets.xlsx')
        worksheet = workbook.add_worksheet()

        title = ['编号','描述','型号','类别','剩余月','部门','员工','购买日期','含税价','原价','残值','折旧价','累计折旧价','剩余价值','备注']

        worksheet.write_row('B2',title)

        orm = table.objects.all()
        count = 3
        for i in orm:
            worksheet.write_row('B%s' % count, [i.FANO,i.description,i.model,i.category,i.residual_life,i.department,
                                                i.employee,str(i.purchase_date).split('+')[0],'%.2f' % i.payment,
                                                '%.2f' % i.cost,'%.2f' % i.residual_value,'%.2f' % i.depreciation,
                                                '%.2f' % i.total_depreciation,'%.2f' % i.netbook_value,i.comment,])
            count += 1
        workbook.close()
        return HttpResponse(simplejson.dumps({'code':0,'msg':u'生成Excel文件成功'}),content_type="application/json")
    except Exception,e:
        print e
        return HttpResponse(simplejson.dumps({'code':1,'msg':u'生成Excel文件失败'}),content_type="application/json")

@login_required
def assets_refresh(request):
    try:
        today = datetime.datetime.now().date()
        orm = table.objects.all()
        for i in orm:
            i.residual_life = category[str(i.category)] - (today - i.purchase_date).days // 30.5
            i.total_depreciation = i.depreciation * ((today - i.purchase_date).days // 30.5)
            i.netbook_value = i.cost - i.total_depreciation
            i.save()
        return HttpResponse('OK',content_type="application/json")
    except Exception,e:
        print e
        return HttpResponse('ERROR',content_type="application/json")