#coding:utf8
import locale

#给数字添加千分符
def int_format(n):
    locale.setlocale(locale.LC_ALL, '')
    locale.format('%d', 1000000, 1)
    num = str(n).replace('-','')
    if '+' in num:
        return str(n)
    all = num.split('.')
    if len(all) > 1:
        left = all[0]
        right = all[1]
    else:
        left = all[0]
        right = ''
    left = locale.format('%d', int(left), 1)
    if n >= 0:
        if right:
            return left + '.' + right
        else:
            return left
    else:
        if right:
            return '-%s.%s' % (left,right)
        else:
            return '-%s' % left