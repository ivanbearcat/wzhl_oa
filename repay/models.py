#coding:utf8
from django.db import models

class budget(models.Model):
    class Meta:
        permissions = (
            ("can_view", "Can view the page"),
        )
    date = models.CharField(verbose_name='日期', max_length=8, blank=False)
    department = models.CharField(verbose_name='所属中心', max_length=32, blank=False)
    budget_class = models.CharField(verbose_name='预算类型', max_length=64, blank=False)
    budget_summary = models.FloatField(verbose_name='总预算', max_length=12, blank=False)
    budget_used = models.FloatField(verbose_name='已用预算', max_length=12, blank=False)
    budget_available = models.FloatField(verbose_name='剩余预算', max_length=12, blank=False)
    budget_added = models.FloatField(verbose_name='附加预算', max_length=12, blank=False)



class log(models.Model):
    apply_time = models.DateTimeField(verbose_name='提交时间', auto_now_add=True)
    name = models.CharField(verbose_name='提交人', max_length=8, blank=False)
    comment = models.CharField(verbose_name='内容', max_length=512, blank=True)
