from django.db import models
from django.conf import settings
from haiyi.products.parser import index_docs
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
        self.products_count = index_docs(xls_file)
        with open(os.path.join(settings.UPLOAD_FOLDER, 'exception.csv')) as r:
            self.wrong_rows = r.read()
        super(ProductsFile, self).save(force_insert, force_update, using, update_fields)

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
        return '%s(%s)' % (self.name, self.account_id)

        #
        # class UsersFile(models.Model):
        #     id = models.AutoField(primary_key=True)
        #     file = models.FileField(upload_to=settings.UPLOAD_FOLDER)
        #     pub_date = models.DateTimeField('date published', auto_now_add=True)
        #     users_count = models.IntegerField(default=0)
        #
        #     def save(self, force_insert=False, force_update=False, using=None,
        #              update_fields=None):
        #         users_file = os.path.join(settings.BASE_DIR, settings.UPLOAD_FOLDER, self.file.name)
        #         for
        #         super(UsersFile, self).save(force_insert, force_update, using, update_fields)
