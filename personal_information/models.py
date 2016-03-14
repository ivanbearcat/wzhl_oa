#coding:utf8
from django.db import models

class table(models.Model):
    class Meta:
        permissions = (
            ("can_view", "Can view the page."),
        )
    name = models.CharField(verbose_name='姓名', max_length=10, blank=False)
    phone = models.CharField(verbose_name='电话', max_length=11, blank=False)
    email = models.CharField(verbose_name='email', max_length=30, blank=False)
    keywords = models.CharField(verbose_name='关键词', max_length=30, blank=False)
    sex = models.CharField(verbose_name='性别', max_length=4, blank=False)
    date_of_entry = models.DateField(verbose_name='入库日期', auto_now_add=True, blank=True)
    birthday = models.DateTimeField(verbose_name='出生日期', auto_now_add=False, blank=True)
    graduate_date = models.DateField(verbose_name='毕业日期', auto_now_add=False, blank=False)
    first_education = models.CharField(verbose_name='第一学历', max_length=10, blank=False)
    education = models.CharField(verbose_name='学历', max_length=10, blank=False)
    specialty = models.CharField(verbose_name='专业', max_length=30, blank=False)
    graduate_school = models.CharField(verbose_name='毕业学校', max_length=30, blank=False)
    last_company = models.CharField(verbose_name='曾入职公司', max_length=30, blank=False)
    channel = models.CharField(verbose_name='渠道', max_length=8, blank=False)
    referrer = models.CharField(verbose_name='推荐人', max_length=10, blank=True)
    salary = models.CharField(verbose_name='薪资状况', max_length=8, blank=True)
    job_level = models.CharField(verbose_name='职级', max_length=20, blank=True)
    job_title = models.CharField(verbose_name='职位', max_length=20, blank=True)
    job_type = models.CharField(verbose_name='岗位类别', max_length=10, blank=False)
    resumes = models.FileField(verbose_name='简历',upload_to='media/%Y/%m/%d', blank=False)
    direction = models.CharField(verbose_name='方向', max_length=30, blank=True)
    resource_state = models.CharField(verbose_name='资源状态', max_length=10, blank=False)
    comment = models.CharField(verbose_name='备注', max_length=128, blank=True)
    state_change_time = models.DateTimeField(verbose_name='状态变更时间', auto_now_add=False, blank=True)
    executor = models.CharField(verbose_name='执行人', max_length=10, blank=False)
    update_time = models.DateTimeField(verbose_name='更新日期', auto_now=True, blank=False)
