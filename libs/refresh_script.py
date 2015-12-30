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
    r = s.post('http://192.168.100.251/login_auth/',data=payload,headers=headers)
    cookies = r.cookies
    s.post('http://192.168.100.251:8000/%s/' % path,cookies=cookies)

refresh(path)