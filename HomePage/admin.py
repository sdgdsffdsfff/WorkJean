from django.contrib import admin
from HomePage import models
# Register your models here.
admin.site.register(models.WJ_User)
admin.site.register(models.WJ_Modules)
admin.site.register(models.WJ_list)
admin.site.register(models.WJ_Devuser)
admin.site.register(models.WJ_Tester)
admin.site.register(models.WJ_Project_Manager)
admin.site.register(models.WJ_Product_Manager)
admin.site.register(models.WJ_TaskType)
admin.site.register(models.WJ_TaskStatus)
admin.site.register(models.WJ_Interface)
admin.site.register(models.WJ_WorkReport)
admin.site.register(models.WJ_TestTaskDetail)
admin.site.register(models.WJ_DevTaskDetail)
admin.site.register(models.WJ_TeamTask)