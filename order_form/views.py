# -*- coding: utf-8 -*-
from django.shortcuts import render_to_response
from django.http import HttpResponseRedirect,HttpResponse
from django.utils.log import logger
from django.contrib import auth
from django.contrib.auth.decorators import login_required


def login(request):
    return render_to_response('order_form/order_form.html')