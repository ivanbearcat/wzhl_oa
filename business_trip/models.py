#coding:utf8
from django.db import models

class main(models.Model):
    reason = models.CharField(verbose_name='事由', max_length=256, blank=True, unique=True)
    destination = models.CharField(verbose_name='目的地', max_length=64, blank=True)
    apply_time = models.DateTimeField(verbose_name='申请时间', auto_now_add=True)
    date = models.CharField(verbose_name='日期', max_length=64, blank=False)
    budget_sum = models.FloatField(verbose_name='总预算', max_length=10, blank=True)
    status = models.IntegerField(verbose_name='状态', max_length=2, blank=False)
    approve_now = models.CharField(verbose_name='当前审批人', max_length=30, blank=True)
    commit_time = models.DateTimeField(verbose_name='提交时间', blank=True)


class base_info(models.Model):
    reason = models.CharField(verbose_name='事由', max_length=256, blank=False, unique=True)
    destination = models.CharField(verbose_name='目的地', max_length=64, blank=False)
    date = models.CharField(verbose_name='日期', max_length=64, blank=False)
    travel_partner = models.CharField(verbose_name='同行人', max_length=64, blank=False)
    vehicle = models.CharField(verbose_name='交通工具', max_length=8, blank=False)
    hotel_reservation = models.IntegerField(verbose_name='订酒店', max_length=2, blank=False)
    parent_id = models.IntegerField(verbose_name='父id', max_length=8, blank=False)


class budget(models.Model):
    travelling_expenses = models.CharField(verbose_name='交通费', max_length=10, blank=False)
    board_expenses = models.CharField(verbose_name='膳食费', max_length=10, blank=False)
    hotel_expenses = models.CharField(verbose_name='招待费', max_length=10, blank=False)
    other_expenses = models.CharField(verbose_name='其他费用', max_length=10, blank=False)
    budget_sum = models.FloatField(verbose_name='总预算', max_length=10, blank=True)
    parent_id = models.IntegerField(verbose_name='父id', max_length=8, blank=False)
