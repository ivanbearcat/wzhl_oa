#coding:utf-8
import requests,sys

username = 'refresh_user'
password = 'MTFkNzJkYjkyM2Ji'

path = sys.argv[1]

def refresh(path):
    s = requests.session()
    payload = {'username':username,'password':password}
    #print payload
    headers = {'content-type':'application/json'}
    r = s.post('http://oa.xiaoquan.com/login_auth/',data=payload,headers=headers)
    cookies = r.cookies
    s.post('http://oa.xiaoquan.com/%s/' % path,cookies=cookies)

refresh(path)