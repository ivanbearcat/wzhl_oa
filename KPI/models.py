#coding:utf8
from django.db import models

class table(models.Model):
    KPI_name = models.CharField(verbose_name='绩效考评名称', max_length=30, blank=False)
    name = models.CharField(verbose_name='被考评人名称', max_length=30, blank=False)
    final_score = models.FloatField(verbose_name='最终分数', max_length=10, blank=True)
    supervisor_comment = models.CharField(verbose_name='主管评价', max_length=256, blank=True)
    status = models.CharField(verbose_name='状态', max_length=10, blank=False)

class table_detail(models.Model):
    KPI_name = models.CharField(verbose_name='绩效考评名称', max_length=30, blank=False)
    name = models.CharField(verbose_name='被考评人名称', max_length=30, blank=False)
    objective = models.CharField(verbose_name='绩效目标', max_length=30, blank=False)
    description = models.CharField(verbose_name='描述', max_length=128, blank=False)
    weight = models.IntegerField(verbose_name='权重', max_length=10, blank=False)
    self_report_value = models.FloatField(verbose_name='自评分值', max_length=10, blank=False)
    self_report_score = models.FloatField(verbose_name='自评分数', max_length=10, blank=False)
    supervisor_report_value = models.FloatField(verbose_name='上级主管所评分值', max_length=10, blank=False)
    supervisor_report_score = models.FloatField(verbose_name='上级主管所评分数', max_length=10, blank=False)
    principal_report_value = models.FloatField(verbose_name='部门负责人所评分值', max_length=10, blank=False)
    principal_report_score = models.FloatField(verbose_name='部门负责人所评分数', max_length=10, blank=False)
