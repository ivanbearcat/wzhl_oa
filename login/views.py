# -*- coding: utf-8 -*-
from django.shortcuts import render_to_response
from django.http import HttpResponseRedirect,HttpResponse
from django.utils.log import logger
from django.contrib import auth
from django.contrib.auth.decorators import login_required


def login(request):
    return render_to_response('login/login.html')

def login_auth(request):
    user_auth = request.POST.get('username')
    passwd_auth = request.POST.get('password')
    authed = auth.authenticate(username=user_auth,password=passwd_auth)
    if authed and authed.is_active:
        auth.login(request,authed)

        for perm in ['vacation.can_view','assets.can_view','KPI.can_view','personal_information.can_view','contract.can_view_all']:
            if request.user.has_perm(perm):
                request.session['_'.join(perm.split('.'))] = 1
            else:
                request.session['_'.join(perm.split('.'))] = 0

        # if globals().has_key('next_next') and not next_next == None:
        #     logger.info('<%s> login in sucess.' % user_auth)
        #     return HttpResponseRedirect(next_next)
        # else:
        #     logger.info('<%s> login in sucess.' % user_auth)
        #     return HttpResponseRedirect('/main/')
        next_page = request.session.get('next')
        if next_page:
            request.session.pop('next')
            return HttpResponseRedirect(next_page)
        else:
            return HttpResponseRedirect('/main/')
    else:
        logger.warn('<%s> login in fail.' % user_auth)
        return render_to_response('login/login.html',{'msg':u'账号或密码错误'})

def logout(request):
    auth.logout(request)
    return render_to_response('login/login.html')

def not_login(request):
    next_next = request.GET.get('next')
    # print next_next
    # global next_next
    request.session['next'] = next_next
    return render_to_response('login/login.html',{'msg':u'您还没有登录'})

def test_notify(request):
    offline = request.POST.get('mod_offline_post')
    to = request.POST.get('to')
    test_from = request.POST.get('from')
    body = request.POST.get('body')
    access_token = request.POST.get('access_token')
    print offline,to,test_from,body,access_token
    return HttpResponse('ok')
