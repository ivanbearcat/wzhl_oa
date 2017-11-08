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