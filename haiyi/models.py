from django.db import models
from django.conf import settings
from haiyi.products.parser import index_docs
from haiyi.crm.cold_call.dialog import init
import os


class ProductsFile(models.Model):
    id = models.AutoField(primary_key=True)
    file = models.FileField('批量文件', upload_to=settings.UPLOAD_FOLDER)
    pub_date = models.DateTimeField('上传时间', auto_now_add=True)
    products_count = models.IntegerField('商品总数', default=0)
    wrong_rows = models.TextField(default='', null=True, blank=True)

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        super(ProductsFile, self).save(force_insert, force_update, using, update_fields)
        xls_file = self.file.name
        self.products_count = index_docs(xls_file, type=settings.PRODUCT_SCHEMA_TYPE)
        with open(os.path.join(settings.UPLOAD_FOLDER, 'exception.csv')) as r:
            self.wrong_rows = r.read()
        super(ProductsFile, self).save(force_insert, force_update, using, update_fields)

    def __str__(self):
        return '%s' % self.file.name


class HaiyiProduct(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.TextField('商品名称', null=True, blank=False)
    uploader = models.IntegerField('管理员', null=False, default='管理员')

    def __str__(self):
        return '%s(%s)' % (self.name, self.id)


class ColdDialogFile(models.Model):
    id = models.AutoField(primary_key=True)
    file = models.FileField('话术文件', upload_to=settings.UPLOAD_FOLDER)
    pub_date = models.DateTimeField('上传时间', auto_now_add=True)
    dialog_count = models.IntegerField('话术总条数', default=0)
    error = models.TextField(default='', null=True, blank=True)

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        super(ColdDialogFile, self).save(force_insert, force_update, using, update_fields)
        xls_file = self.file.name
        # self.dialog_count = index_docs(xls_file)
        # with open(os.path.join(settings.UPLOAD_FOLDER, 'exception.csv')) as r:
        #     self.wrong_rows = r.read()
        super(ColdDialogFile, self).save(force_insert, force_update, using, update_fields)

    def __str__(self):
        return '%s' % self.file.name


class HaiyiUser(models.Model):
    id = models.AutoField(primary_key=True)
    pub_date = models.DateTimeField('加入日期', auto_now_add=True)
    end_date = models.DateTimeField('会员截止', null=False)
    active = models.BooleanField('激活', default=False)
    open_id = models.TextField('Open Id', null=False, blank=False)
    name = models.TextField('名字', null=False, blank=False)
    account_id = models.TextField('微信号', null=True, blank=True)

    indexes = [
        models.Index(fields=['open_id', ]),
    ]

    def __str__(self):
        return '%s(%s)  激活 = %s' % (self.name, self.account_id, self.active)
