# -*- coding:utf-8 -*-
from django.db import models
import datetime

class WJ_User(models.Model):
    u_name = models.CharField(max_length=10)         # 用户名
    u_pwd = models.CharField(max_length=100)          # 密码
    u_real_name = models.CharField(max_length=10)    # 真实名称

# 模块类别(支付,收银,结算等)
class WJ_Modules(models.Model):
    m_name = models.CharField(max_length=10)          # 模块名称

# 每个大类模块下的小类
class WJ_list(models.Model):
    l_name = models.CharField(max_length=10)          # 小类名称
    l_father_name = models.IntegerField()             # 所属大类

# 开发人员名单
class WJ_Devuser(models.Model):
    d_name = models.CharField(max_length=5)           # 开发人员姓名

# 测试人员名单
class WJ_Tester(models.Model):
    t_name = models.CharField(max_length=5)           # 测试人员姓名

# 项目经理名单
class WJ_Project_Manager(models.Model):
    m_name = models.CharField(max_length=5)           # 项目经理姓名

# 产品经理名单
class WJ_Product_Manager(models.Model):
    m_name = models.CharField(max_length=5)           # 项目经理姓名


# 任务类型(X、新项目  G、改造类项目  N、内部项目)
class WJ_TaskType(models.Model):
    t_type = models.CharField(max_length=1)            # 项目代码
    t_name = models.CharField(max_length=10)           # 项目类型名称

# 任务状态(1、未开始 2、进行中 3、已结束 4、已取消)
class WJ_TaskStatus(models.Model):
    t_id = models.IntegerField()                       # 任务状态对应id
    t_name = models.CharField(max_length=10)           # 任务状态名称


# 任务接口信息
class WJ_Interface(models.Model):
    i_task_id = models.CharField(max_length=10)                                 # 接口所属任务的编号
    i_name = models.CharField(max_length=100)                                   # 接口名称
    i_case_num = models.IntegerField()                                          # 接口case数量
    i_case_pass_num = models.IntegerField()                                     # 通过的case数量
    i_case_upass_num = models.IntegerField()                                    # 不通过的case数量
    i_case_check_num = models.IntegerField()                                    # 接口检查点数量
    i_case_bug_find_num = models.IntegerField()                                 # 发现BUG数
    i_case_bug_ufind_num = models.IntegerField(blank=True,null=True)            # 遗漏BUG数
    i_case_pass_rate = models.CharField(max_length=10,blank=True,null=True)     # case通过率,存储字符串
    i_case_upass_rate = models.CharField(max_length=10,blank=True,null=True)    # case遗漏率
    i_dev_name = models.CharField(max_length=10,blank=True,null=True)           # 接口所属开发
    i_test_name = models.CharField(max_length=10,blank=True,null=True)          # 接口测试负责人
    i_text = models.CharField(max_length=10,blank=True,null=True)               # 备注(已完成、废弃等)
    i_info = models.TextField(max_length=500,blank=True,null=True)              # 接口有用信息

# 日报和周报
class WJ_WorkReport(models.Model):
    # 待完善
    pass


# 测试任务详细
class WJ_TestTaskDetail(models.Model):
    t_id = models.CharField(max_length=10)                                  # 任务编号
    t_name = models.CharField(max_length=100)                               # task名称
    t_is_performance = models.IntegerField()                                # 是否性能项目(1是0否)
    t_type = models.CharField(max_length=5)                                 # 项目类型(X、新项目  G、技术改造  N、内部项目)
    t_manager = models.CharField(max_length=50)                             # 项目经理
    t_tester = models.CharField(max_length=50)                              # 负责测试人员
    t_s_tester = models.CharField(max_length=50)                            # 实施测试人员
    t_pre_start_time = models.DateTimeField(blank=True,null=True)           # 前置开始时间
    t_test_time = models.DateTimeField(blank=True,null=True)                # 提测时间
    t_pre_end_time = models.DateTimeField(blank = True,null=True)           # 前置结束时间
    t_re_start_time = models.DateTimeField(blank=True,null=True)            # 回归开始时间
    t_re_end_time = models.DateTimeField(blank=True,null=True)              # 回归结束时间
    t_pro_release_time = models.DateTimeField(blank=True,null=True)         # 项目发布时间
    t_status = models.IntegerField()                                        # 项目当前状态(1未开始、2进行中、3已结束、4已取消)
    t_phase = models.CharField(max_length=10,blank=True,null=True)          # 项目当前阶段(需求评审、架构评审、脚本开发、测试、回归、上线)
    t_target = models.CharField(max_length=100,blank=True,null=True)        # 目标


# 开发任务详细
class WJ_DevTaskDetail(models.Model):
    d_id = models.CharField(max_length=10)                                  # 任务编号
    d_name = models.CharField(max_length=100)                               # task名称
    d_is_performance = models.IntegerField()                                # 是否性能项目(1是0否)
    d_type = models.CharField(max_length=5)                                 # 项目类型(X、新项目  G、技术改造  N、内部项目)
    d_product_manager = models.CharField(max_length=50)                     # 产品经理
    d_project_manager = models.CharField(max_length=50)                     # 项目经理
    d_dever = models.CharField(max_length=50)                               # 开发人员
    d_start_time = models.DateTimeField(blank=True,null=True)               # 开始时间
    d_dev_time = models.DateTimeField(blank=True,null=True)                 # 开发时间
    d_test_time = models.DateTimeField(blank = True,null=True)              # 测试时间
    d_use_time = models.DateTimeField(blank=True,null=True)                 # 试用时间
    d_release_time = models.DateTimeField(blank=True,null=True)             # 发布时间
    d_end_time = models.DateTimeField(blank=True,null=True)                 # 结束时间
    d_status = models.IntegerField()                                        # 当前状态(1未开始、2进行中、3已结束、4已取消)
    d_phase = models.CharField(max_length=10,blank=True,null=True)          # 当前阶段(需求评审、架构评审、开发、测试、试用、维护、版本迭代)
    d_target = models.CharField(max_length=100,blank=True,null=True)        # 备注


# 自动化任务排期
class WJ_TeamTask(models.Model):
    t_task_attribute = models.IntegerField()            # 任务属性(1、测试  2、开发)
    t_task_id = models.CharField(max_length=10)         # 任务编号(X001   G002等,对应任务详细中的编号)
    t_task_type = models.CharField(max_length=5)        # 任务类型(X、新项目  G、技术改造  N、内部项目)
    t_task_status = models.IntegerField()               # 任务状态(1、未开始 2、进行中 3、已结束 4、已取消)


# 用户events
class WJ_MyEvents(models.Model):
    m_user = models.CharField(max_length=10)            # 登录用户
    m_events_id = models.CharField(max_length=10)       # events的编号(对应自动化任务排期中的t_task_id)
    m_events_name = models.CharField(max_length=100)    # 前端显示events的名字
    m_is_send_email = models.IntegerField()             # 是否已经发送邮件通知(0、否  1、是)
    m_events_status = models.IntegerField()             # events的状态(1、未开始  2、进行中)
    m_events_is_new = models.IntegerField()             # events是否是新的(1是  0否)

# 项目编号
class WJ_TaskNum(models.Model):
    t_id = models.IntegerField()                        # 项目编号