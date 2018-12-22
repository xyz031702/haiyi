from django.contrib import admin
from haiyi.models import ProductsFile, HaiyiUser
admin.site.site_title = "海蚁管理"
admin.site.site_header = "海蚁管理"
admin.site.index_title = "海蚁"


#
# class ProductsAdmin(admin.ModelAdmin):
#     actions = ['make_published']
#
#     def make_published(self, request, queryset):
#         queryset.update(status='p')
#
#     make_published.short_description = "Mark selected stories as published"

admin.site.register(ProductsFile)
admin.site.register(HaiyiUser)