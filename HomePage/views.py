# -*- coding:utf-8 -*-
'''
from __future__ import division使得
'/'只用于真除法，而'//'仅用于整除法的话
'''
from __future__ import division

from django.shortcuts import render_to_response
from django.http import HttpResponse,StreamingHttpResponse
from django.core.servers.basehttp import FileWrapper
import mimetypes
from HomePage.models import *
from django.db.models import Q,F

# from django.utils import simplejson
import simplejson
from django.contrib.auth.models import *
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.template import RequestContext
from jobwj import JobWJ
# 邮件相关
import os,time
# 导入Excel工具类
from ExcelUtil import Excel_2007_Engine

# job实例
job = JobWJ()

# 首页
@login_required(login_url='/login/')
def index(request):
    # 导航条上的信息
    nav_result = getCuruser_And_Events(request)
    return render_to_response(
        'index.html',nav_result
    )
# 自动化任务排期页
@login_required(login_url='/login/')
def task_page(request):
    # 导航条上的信息
    nav_result = getCuruser_And_Events(request)


    # 所有任务
    all_tasks = WJ_TeamTask.objects.all()
    # 各任务数
    pro_unstart_num = all_tasks.filter(t_task_status=1).count()
    pro_inprogress_num = all_tasks.filter(t_task_status=2).count()
    pro_end_num = all_tasks.filter(t_task_status=3).count()
    pro_cancel_num = all_tasks.filter(t_task_status=4).count()
    # 所有任务数
    all_task_num = all_tasks.count()

    # 每一种状态的任务
    unstart_t = WJ_TestTaskDetail.objects.filter(t_status=1).order_by('-t_test_time')
    unstart_d = WJ_DevTaskDetail.objects.filter(d_status=1).order_by('-d_start_time')
    inprogress_t = WJ_TestTaskDetail.objects.filter(t_status=2).order_by('-t_test_time')
    inprogress_d = WJ_DevTaskDetail.objects.filter(d_status=2).order_by('-d_start_time')
    end_t = WJ_TestTaskDetail.objects.filter(t_status=3).order_by('-t_test_time')
    end_d = WJ_DevTaskDetail.objects.filter(d_status=3).order_by('-d_start_time')
    cancel_t = WJ_TestTaskDetail.objects.filter(t_status=4).order_by('-t_test_time')
    cancel_d = WJ_DevTaskDetail.objects.filter(d_status=4).order_by('-d_start_time')

    # 所有任务
    all_task_test = WJ_TestTaskDetail.objects.all().order_by('-t_test_time')
    all_task_dev = WJ_DevTaskDetail.objects.all().order_by('d_start_time')

    return render_to_response(
        'Task.html',
        {
            'all_tasks':all_tasks,
            'pro_unstart_num':pro_unstart_num,
            'pro_inprogress_num':pro_inprogress_num,
            'pro_end_num':pro_end_num,
            'pro_cancel_num':pro_cancel_num,
            # 所有任务数
            'all_task_num':all_task_num,

            # 各个状态的任务
            'unstart_t':unstart_t[:3],
            'inprogress_t':inprogress_t[:3],
            'end_t':end_t[:3],
            'cancel_t':cancel_t[:3],
            'unstart_d':unstart_d[:3],
            'inprogress_d':inprogress_d[:3],
            'end_d':end_d[:3],
            'cancel_d':cancel_d[:3],
            # 所有任务
            'all_task_test':all_task_test,
            'all_task_dev':all_task_dev,



            'curuser':nav_result['curuser'],
            # events相关信息
            'Curuser_Events':nav_result['Curuser_Events'],
            'hasEvent':nav_result['hasEvent'],
            'myEventsNum':nav_result['myEventsNum'],
            'isAdmin':nav_result['isAdmin'],
        }
    )
# 自动化任务排期页动态结果
def ajax_get_task_info(request):
    '''status:1,2,3,4   12,13,14,23,24,34,123,124,134,234,1234'''
    task_status = request.POST['task_status']

    Test_TaskDetail = None
    Dev_TaskDetail = None

    if len(task_status) == 1:
        if int(task_status) == 0:
            Test_TaskDetail = WJ_TestTaskDetail.objects.all().order_by('-t_test_time')
            Dev_TaskDetail = WJ_DevTaskDetail.objects.all().order_by('-d_start_time')
        else:
            Test_TaskDetail = WJ_TestTaskDetail.objects.filter(t_status=task_status).order_by('-t_test_time')
            Dev_TaskDetail = WJ_DevTaskDetail.objects.filter(d_status=task_status).order_by('-d_start_time')
    elif len(task_status) == 2:
        Test_TaskDetail = WJ_TestTaskDetail.objects.filter(Q(t_status=task_status[0]) | Q(t_status=task_status[1])).order_by('-t_test_time')
        Dev_TaskDetail = WJ_DevTaskDetail.objects.filter(Q(d_status=task_status[0]) | Q(d_status=task_status[1])).order_by('-d_start_time')
    elif len(task_status) == 3:
        Test_TaskDetail = WJ_TestTaskDetail.objects.filter(Q(t_status=task_status[0]) | Q(t_status=task_status[1]) | Q(t_status=task_status[2])).order_by('-t_test_time')
        Dev_TaskDetail = WJ_DevTaskDetail.objects.filter(Q(d_status=task_status[0]) | Q(d_status=task_status[1]) | Q(d_status=task_status[2])).order_by('-d_start_time')
    elif len(task_status) == 4:
        Test_TaskDetail = WJ_TestTaskDetail.objects.all().order_by('-t_test_time')
        Dev_TaskDetail = WJ_DevTaskDetail.objects.all().order_by('-d_start_time')



    return render_to_response(
        'ajax_content_of_task_info.html',
        {
            'Test_TaskDetail':Test_TaskDetail,
            'Dev_TaskDetail':Dev_TaskDetail,
        }
    )


# 各任务详细页
@login_required(login_url='/login/')
def task_detail(request):
    # 导航条上的信息
    nav_result = getCuruser_And_Events(request)

    # 任务类型(1未开始、2进行中、3已结束、4已取消)
    # 获取任务类型代号
    task_status = request.GET['task_status']
    task_status = int(task_status)
    Test_TaskDetail = WJ_TestTaskDetail.objects.filter(t_status=task_status)
    Dev_TaskDetail = WJ_DevTaskDetail.objects.filter(d_status=task_status)
    # 换一种看得懂的语言
    for testtaskdetail in Test_TaskDetail:
        testtaskdetail.t_type = WJ_Change(testtaskdetail.t_type)
        testtaskdetail.t_status = WJ_Change(testtaskdetail.t_status)
    # 换一种看得懂的语言
    for devtaskdetail in Dev_TaskDetail:
        devtaskdetail.d_type = WJ_Change(devtaskdetail.d_type)
        devtaskdetail.d_status = WJ_Change(devtaskdetail.d_status)
    return render_to_response(
        'taskdetail.html',
        {
            'Test_TaskDetail':Test_TaskDetail,
            'Dev_TaskDetail':Dev_TaskDetail,
            'task_status_name':WJ_Change(task_status),
            'task_status':task_status,

            'curuser':nav_result['curuser'],
            # events相关信息
            'Curuser_Events':nav_result['Curuser_Events'],
            'hasEvent':nav_result['hasEvent'],
            'myEventsNum':nav_result['myEventsNum'],
            'isAdmin':nav_result['isAdmin'],
        }
    )

# 我的任务(一条)
@login_required(login_url='/login/')
def one_event_detail(request):
    # 导航条上的信息
    nav_result = getCuruser_And_Events(request)

    result_test = None
    result_dev = None
    event_name = None
    result = None

    # task_id
    task_id = request.GET['event_id']
    # 去WJ_TeamTask表里查找这条task
    team_task_result = WJ_TeamTask.objects.filter(t_task_id=task_id)
    # task的属性(1、测试  2、开发)
    for t in team_task_result:
        attribute = t.t_task_attribute

    # 去WJ_MyEvents表里查找当前用户的这条task,并设置m_events_is_new = 0
    my_event_result =  WJ_MyEvents.objects.get(m_events_id=task_id,m_user=nav_result['curuser'])
    if not my_event_result.m_events_is_new == 0:
        my_event_result.m_events_is_new = 0
        my_event_result.save()


    # 测试
    if attribute == 1:
        result_test = WJ_TestTaskDetail.objects.filter(t_id=task_id)
        # 换一种看得懂的语言
        for r in result_test:
            r.t_status = WJ_Change(r.t_status)
            r.t_type = WJ_Change(r.t_type)
        for r in result_test:
            event_name = r.t_name
    # 开发
    if attribute == 2:
        result_dev = WJ_DevTaskDetail.objects.filter(d_id=task_id)
        # 换一种看得懂的语言
        for r in result_dev:
            r.d_status = WJ_Change(r.d_status)
            r.d_type = WJ_Change(r.d_type)
        for r in result_dev:
            event_name = r.d_name

    if result_test:
        result = result_test
    else:
        result = result_dev

    return render_to_response(
        'eventdetail.html',{
            'attribute':attribute,
            'event_name':event_name,
            'result':result,

            'curuser':nav_result['curuser'],
            # events相关信息
            'Curuser_Events':nav_result['Curuser_Events'],
            'hasEvent':nav_result['hasEvent'],
            'myEventsNum':nav_result['myEventsNum'],
            'isAdmin':nav_result['isAdmin'],
        }
    )

# 获取登录用户所有events
def all_my_event_detail(request):
    # 导航条上的信息
    nav_result = getCuruser_And_Events(request)
    curuser = nav_result['curuser']

    events_result = WJ_MyEvents.objects.filter(m_user=curuser)

    # 去WJ_MyEvents表里查找当前用户的所有task,并设置m_events_is_new = 0
    my_event_result =  WJ_MyEvents.objects.filter(m_user=nav_result['curuser'])
    for r in my_event_result:
        if not r.m_events_is_new == 0:
            r.m_events_is_new = 0
            r.save()
    # my_event_result.update(m_events_is_new=0)

    test_events = []
    dev_events = []

    for r in events_result:
        task_id = r.m_events_id
        # 去WJ_TeamTask表里查找这条task
        team_task_result = WJ_TeamTask.objects.filter(t_task_id=task_id)
        # task的属性(1、测试  2、开发)
        for t in team_task_result:
            attribute = t.t_task_attribute

        # 测试
        if attribute == 1:
            result_test = WJ_TestTaskDetail.objects.filter(t_id=task_id)
            # 换一种看得懂的语言
            for r in result_test:
                r.t_status = WJ_Change(r.t_status)
                r.t_type = WJ_Change(r.t_type)

            test_events.append(result_test)
        # 开发
        if attribute == 2:
            result_dev = WJ_DevTaskDetail.objects.filter(d_id=task_id)
            # 换一种看得懂的语言
            for r in result_dev:
                r.d_status = WJ_Change(r.d_status)
                r.d_type = WJ_Change(r.d_type)
            dev_events.append(result_dev)


    return render_to_response(
        'allmyevents.html',{
            'test_events':test_events,
            'dev_events':dev_events,

            'curuser':curuser,
            # events相关信息
            'Curuser_Events':nav_result['Curuser_Events'],
            'hasEvent':nav_result['hasEvent'],
            'myEventsNum':nav_result['myEventsNum'],
            'isAdmin':nav_result['isAdmin'],
        }
    )

# 项目管理页(开始、结束、取消、恢复、修改项目等)
def admin_project_management(request):
    # 导航条上的信息
    nav_result = getCuruser_And_Events(request)
    config_type = request.GET['type']

    unstart = []        # [{'id':'xxx','name':'xxx'},{'id':'xxx','name':'xxx'},...]
    inprogress = []
    end = []
    cancel = []

    # 所有任务
    all_tasks = WJ_TeamTask.objects.all()
    # 各任务数
    pro_unstart_num = all_tasks.filter(t_task_status=1).count()
    pro_inprogress_num = all_tasks.filter(t_task_status=2).count()
    pro_end_num = all_tasks.filter(t_task_status=3).count()
    pro_cancel_num = all_tasks.filter(t_task_status=4).count()


    # 每一种状态的任务
    unstart_t = WJ_TestTaskDetail.objects.filter(t_status=1).order_by('-t_test_time')
    for i in unstart_t:
        tmp = {}
        tmp['id'] = i.t_id
        tmp['name'] = i.t_name
        unstart.append(tmp)
    unstart_d = WJ_DevTaskDetail.objects.filter(d_status=1).order_by('-d_start_time')
    for i in unstart_d:
        tmp = {}
        tmp['id'] = i.d_id
        tmp['name'] = i.d_name
        unstart.append(tmp)

    inprogress_t = WJ_TestTaskDetail.objects.filter(t_status=2).order_by('-t_test_time')
    for i in inprogress_t:
        tmp = {}
        tmp['id'] = i.t_id
        tmp['name'] = i.t_name
        inprogress.append(tmp)
    inprogress_d = WJ_DevTaskDetail.objects.filter(d_status=2).order_by('-d_start_time')
    for i in inprogress_d:
        tmp = {}
        tmp['id'] = i.d_id
        tmp['name'] = i.d_name
        inprogress.append(tmp)

    end_t = WJ_TestTaskDetail.objects.filter(t_status=3).order_by('-t_test_time')
    for i in end_t:
        tmp = {}
        tmp['id'] = i.t_id
        tmp['name'] = i.t_name
        end.append(tmp)
    end_d = WJ_DevTaskDetail.objects.filter(d_status=3).order_by('-d_start_time')
    for i in end_d:
        tmp = {}
        tmp['id'] = i.d_id
        tmp['name'] = i.d_name
        end.append(tmp)


    cancel_t = WJ_TestTaskDetail.objects.filter(t_status=4).order_by('-t_test_time')
    for i in cancel_t:
        tmp = {}
        tmp['id'] = i.t_id
        tmp['name'] = i.t_name
        cancel.append(tmp)
    cancel_d = WJ_DevTaskDetail.objects.filter(d_status=4).order_by('-d_start_time')
    for i in cancel_d:
        tmp = {}
        tmp['id'] = i.d_id
        tmp['name'] = i.d_name
        cancel.append(tmp)


    # 各人员
    Project_Manager = WJ_Project_Manager.objects.all()
    Product_Manager = WJ_Product_Manager.objects.all()
    Devuser = WJ_Devuser.objects.all()
    Tester = WJ_Tester.objects.all()
    # 任务类型
    TaskType = WJ_TaskType.objects.all()
    # 任务当前状态
    TaskStatus = WJ_TaskStatus.objects.all()

    return render_to_response(
        'project_config.html',
        {
            'config_type':config_type,
            'pro_unstart_num':pro_unstart_num,
            'pro_inprogress_num':pro_inprogress_num,
            'pro_end_num':pro_end_num,
            'pro_cancel_num':pro_cancel_num,

            'unstart':unstart,
            'inprogress':inprogress,
            'end':end,
            'cancel':cancel,

            # 'unstart_t':unstart_t,
            # 'inprogress_t':inprogress_t,
            # 'end_t':end_t,
            # 'cancel_t':cancel_t,
            # 'unstart_d':unstart_d,
            # 'inprogress_d':inprogress_d,
            # 'end_d':end_d,
            # 'cancel_d':cancel_d,


            'Project_Manager':Project_Manager,
            'Product_Manager':Product_Manager,
            'Devuser':Devuser,
            'Tester':Tester,
            'TaskType':TaskType,
            'TaskStatus':TaskStatus,


            'curuser':nav_result['curuser'],
            # events相关信息
            'Curuser_Events':nav_result['Curuser_Events'],
            'hasEvent':nav_result['hasEvent'],
            'myEventsNum':nav_result['myEventsNum'],
            'isAdmin':nav_result['isAdmin'],
        },
        context_instance=RequestContext(request)
    )

# 选中项目后点击查看页面
def look_project(request):
    pro_data = request.GET['pro_data']
    task_id = pro_data.split('|')[0]
    # 获取该项目信息
    result = WJ_TeamTask.objects.get(t_task_id=task_id)
    task_attribute = result.t_task_attribute
    if task_attribute == 1:
        pro_info = WJ_TestTaskDetail.objects.get(t_id=task_id)
    else:
        pro_info = WJ_DevTaskDetail.objects.get(d_id=task_id)
    return render_to_response(
        'look_project.html',
        {
            'pro_info':pro_info,
        }
    )
# 选中项目后点击修改页面
def modify_project(request):
    pro_data = request.GET['pro_data']
    task_id = pro_data.split('|')[0]
    # 获取该项目信息
    result = WJ_TeamTask.objects.get(t_task_id=task_id)
    task_attribute = result.t_task_attribute
    if task_attribute == 1:
        pro_info = WJ_TestTaskDetail.objects.get(t_id=task_id)
    else:
        pro_info = WJ_DevTaskDetail.objects.get(d_id=task_id)
    return render_to_response(
        'modify_project.html',
        {
            'pro_info':pro_info,
        }
    )
# 修改项目后提交
def ajax_modify_project(request):
    data = {}
    # 获取ajax发送过来的键、值
    for key in request.POST:
        value = request.POST.get(key)
        data[key] = value
    # 属性和编号
    attribute = data['attribute']
    task_id = data['task_id']
    # 删除两个键值对
    del data['attribute']   # 也可以用pop方法，data.pop('attribute')
    del data['task_id']     # 也可以用pop方法，data.pop('task_id')
    # data = {键值对}
    if attribute == '1':
        r = WJ_TestTaskDetail.objects.get(t_id=task_id)
        for d in data:
            if d == 't_name':
                r.t_name = data[d]
            if d == 't_is_performance':
                r.t_is_performance = data[d]
            if d == 't_type':
                r.t_type = data[d]
            if d == 't_manager':
                r.t_manager = data[d]
            if d == 't_s_tester':
                r.t_s_tester = data[d]
            if d == 't_pre_start_time':
                r.t_pre_start_time = data[d]
            if d == 't_test_time':
                r.t_test_time = data[d]
            if d == 't_pre_end_time':
                r.t_pre_end_time = data[d]
            if d == 't_re_start_time':
                r.t_re_start_time = data[d]
            if d == 't_re_end_time':
                r.t_re_end_time = data[d]
            if d == 't_pro_release_time':
                r.t_pro_release_time = data[d]
            if d == 't_phase':
                r.t_phase = data[d]
            if d == 't_target':
                r.t_target = data[d]
        # 保存更新
        r.save()
        return HttpResponse(1)
    elif attribute == '2':
        r = WJ_DevTaskDetail.objects.get(d_id=task_id)
        for d in data:
            if d == 'd_name':
                r.d_name = data[d]
            if d == 'd_is_performance':
                r.d_is_performance = data[d]
            if d == 'd_type':
                r.d_type = data[d]
            if d == 'd_product_manager':
                r.d_product_manager = data[d]
            if d == 'd_project_manager':
                r.d_project_manager = data[d]
            if d == 'd_dever':
                r.d_dever = data[d]
            if d == 'd_start_time':
                r.d_start_time = data[d]
            if d == 'd_dev_time':
                r.d_dev_time = data[d]
            if d == 'd_test_time':
                r.d_test_time = data[d]
            if d == 'd_use_time':
                r.d_use_time = data[d]
            if d == 'd_release_time':
                r.d_release_time = data[d]
            if d == 'd_end_time':
                r.d_end_time = data[d]
            if d == 'd_phase':
                r.d_phase = data[d]
            if d == 'd_target':
                r.d_target = data[d]
        # 保存更新
        r.save()
        return HttpResponse(1)
    else:
        return HttpResponse(0)


# 人员信息管理
def users_configuration_management(request):
    # 导航条上的信息
    nav_result = getCuruser_And_Events(request)
    config_type = request.GET['type']

    testers = WJ_Tester.objects.all()
    devers = WJ_Devuser.objects.all()
    project_managers = WJ_Project_Manager.objects.all()
    product_managers = WJ_Product_Manager.objects.all()

    return render_to_response(
        'user_config.html',
        {
            'config_type':config_type,

            'testers':testers,
            'devers':devers,
            'project_managers':project_managers,
            'product_managers':product_managers,

            'curuser':nav_result['curuser'],
            # events相关信息
            'Curuser_Events':nav_result['Curuser_Events'],
            'hasEvent':nav_result['hasEvent'],
            'myEventsNum':nav_result['myEventsNum'],
            'isAdmin':nav_result['isAdmin'],
        }
        )
# 模块服务管理
def modules_configuration_management(request):
    # 导航条上的信息
    nav_result = getCuruser_And_Events(request)
    config_type = request.GET['type']

    return render_to_response(
        'module_config.html',
        {
            'config_type':config_type,

            'curuser':nav_result['curuser'],
            # events相关信息
            'Curuser_Events':nav_result['Curuser_Events'],
            'hasEvent':nav_result['hasEvent'],
            'myEventsNum':nav_result['myEventsNum'],
            'isAdmin':nav_result['isAdmin'],
        }
        )

# 接口信息管理页
def interface_configuration_management(request):
    # 导航条上的信息
    nav_result = getCuruser_And_Events(request)
    config_type = request.GET['type']

    return render_to_response(
        'interface_config.html',
        {
            'config_type':config_type,

            'curuser':nav_result['curuser'],
            # events相关信息
            'Curuser_Events':nav_result['Curuser_Events'],
            'hasEvent':nav_result['hasEvent'],
            'myEventsNum':nav_result['myEventsNum'],
            'isAdmin':nav_result['isAdmin'],
        },
        context_instance=RequestContext(request)
    )

# ajax获取接口信息
def ajax_get_interface_info(request):
    what_task = request.POST['what_task']

    if what_task == 'All':
        # 所有已完结项目
        t_end_projects = WJ_TestTaskDetail.objects.filter(t_status = 3)
    else:
        t_end_projects = WJ_TestTaskDetail.objects.filter(t_status = 3,t_name__icontains = what_task) # 模糊查询

    # 完结项目的接口数据（管理页只列出部分统计数据）
    interface_info = []
    for res in t_end_projects:
        tmp = {
            'task_id':None,
            'task_name':None,
            'task_interface_num':0,
            'task_case_num':0,
            'task_check_num':0,
            'task_find_bug':0,
            'task_unfind_bug':0,
        }
        task_id = res.t_id
        # 项目编号和项目名称
        tmp['task_id'] = task_id
        tmp['task_name'] = res.t_name
        # 查询该项目编号下的所有接口信息
        interface_results = WJ_Interface.objects.filter(i_task_id=task_id)
        # 项目接口数
        tmp['task_interface_num'] = interface_results.count()
        if interface_results:
            for rs in interface_results:
                tmp['task_case_num'] += rs.i_case_num
                tmp['task_check_num'] += rs.i_case_check_num
                tmp['task_find_bug'] += rs.i_case_bug_find_num
                tmp['task_unfind_bug'] += rs.i_case_bug_ufind_num
        interface_info.append(tmp)

    return render_to_response(
        "ajax_content_of_interface_info.html",
        {
            "interface_info":interface_info,
        },
        context_instance=RequestContext(request)
    )

# 增加接口信息页
def add_interface_info_page(request):
    # 导航条上的信息
    nav_result = getCuruser_And_Events(request)
    task_id = request.GET['task_id']
    task_name = WJ_TestTaskDetail.objects.get(t_id=task_id).t_name

    # 根据任务编号筛选出所有属于该任务的接口信息
    interface_info = WJ_Interface.objects.filter(i_task_id=task_id)
    # 总计信息
    all_info = {
        "case_num":0,
        "pass_num":0,
        "upass_num":0,
        "check_num":0,
        "bug_find_num":0,
        "bug_ufind_num":0,
        "pass_rate":'%.2f'%0,
    }
    # 如果有结果则进行计算
    if interface_info:
        for res in interface_info:
            all_info['case_num'] += res.i_case_num
            all_info['pass_num'] += res.i_case_pass_num
            all_info['upass_num'] += res.i_case_upass_num
            all_info['check_num'] += res.i_case_check_num
            all_info['bug_find_num'] += res.i_case_bug_find_num
            all_info['bug_ufind_num'] += res.i_case_bug_ufind_num

        all_info['pass_rate'] = '%.2f'%(all_info["pass_num"]/all_info["case_num"]*100)

    return render_to_response(
        'add_interface_info.html',
        {
            'task_id':task_id,
            'task_name':task_name,
            'interface_info':interface_info,
            'all_info':all_info,

            'curuser':nav_result['curuser'],
            # events相关信息
            'Curuser_Events':nav_result['Curuser_Events'],
            'hasEvent':nav_result['hasEvent'],
            'myEventsNum':nav_result['myEventsNum'],
            'isAdmin':nav_result['isAdmin'],
        }
    )

def ajax_add_interface_info(request):
    if request.method == "POST":
        name = request.POST['name']
        case_num = request.POST['case_num']
        pass_num = request.POST['pass_num']
        upass_num = request.POST['upass_num']
        check_num = request.POST['check_num']
        pass_rate = request.POST['pass_rate']
        bug_find_num = request.POST['bug_find_num']
        bug_ufind_num = request.POST['bug_ufind_num']
        task_id = request.POST['task_id']

        interface_obj = WJ_Interface(
            i_task_id = task_id,
            i_name = name,
            i_case_num = case_num,
            i_case_pass_num = pass_num,
            i_case_upass_num = upass_num,
            i_case_check_num = check_num,
            i_case_bug_find_num = bug_find_num,
            i_case_bug_ufind_num = bug_ufind_num,
            i_case_pass_rate = pass_rate,
        )
        interface_obj.save()
        return HttpResponse('添加成功!')
    return HttpResponse('添加失败!')


# 导航条上所有信息
def getCuruser_And_Events(request):
    # 当前登录用户
    loginuser = request.user
    result = WJ_User.objects.filter(u_name=loginuser)
    for r in result:
        curuser = r.u_real_name
    hasEvent = False
    isAdmin = False

    # 所有任务分类
    result_status = get_task_info(1)
    result_type = get_task_info(2)

    # 查找当前登录用户的events
    Curuser_Events = WJ_MyEvents.objects.filter(m_user=curuser)
    # 我的events总数
    myEventsNum = Curuser_Events.count()

    # 管理员(auth_user表中的超级管理员)
    admins = User.objects.filter(is_superuser=1)
    for a in admins:
        AdminUser = a.username

    # 判断是否超级管理员
    if str(loginuser) == str(AdminUser):
        isAdmin = True
    else:
        isAdmin = False



    if myEventsNum == 0:
        hasEvent = True
    result = {
        'result_status':result_status,
        'result_type':result_type,


        'curuser':curuser,
        # events相关信息
        'Curuser_Events':Curuser_Events[::-1][:5],      # 首先反转序列,随后取前5个
        'hasEvent':hasEvent,
        'myEventsNum':myEventsNum,
        'isAdmin':isAdmin,
    }
    return result




# 登录页
def login(request):
    return render_to_response(
        'login.html',
    )
# 登出页
def logout(request):
    auth.logout(request)
    return render_to_response(
        'login.html',
    )

# 添加人员
def ajax_add_user(request):
    name = request.POST['name']
    to = request.POST['to']

    result = {"status":False,"data":""}

    print 'add  ' + to
    if to == 'producter':
        n = WJ_Product_Manager.objects.filter(m_name=name).count()
        if n <= 0:
            m = WJ_Product_Manager(
                m_name = name
            )
            m.save()
            result = {"status":True,"data":"添加成功!"}
        else:
            result = {"status":False,"data":"用户已经存在!"}
    elif to == 'projecter':
        n = WJ_Project_Manager.objects.filter(m_name=name).count()
        if n <= 0:
            m = WJ_Project_Manager(
                m_name = name
            )
            m.save()
            result = {"status":True,"data":"添加成功!"}
        else:
            result = {"status":False,"data":"用户已经存在!"}
    elif to == 'dever':
        n = WJ_Devuser.objects.filter(d_name=name).count()
        if n <= 0:
            m = WJ_Devuser(
                d_name = name
            )
            m.save()
            result = {"status":True,"data":"添加成功!"}
        else:
            result = {"status":False,"data":"用户已经存在!"}
    if to == 'tester':
        n = WJ_Tester.objects.filter(t_name=name).count()
        if n <= 0:
            m = WJ_Tester(
                t_name = name
            )
            m.save()
            result = {"status":True,"data":"添加成功!"}
        else:
            result = {"status":False,"data":"用户已经存在!"}

    print result
    return HttpResponse(simplejson.dumps(result,ensure_ascii=False),content_type='application/json')

# 删除人员
def ajax_del_user(request):
    to = request.POST['to']
    name = request.POST['name']

    n = None
    if to == 'producter':
        n = WJ_Product_Manager.objects.get(m_name=name)
    elif to == 'projecter':
        n = WJ_Project_Manager.objects.get(m_name=name)
    elif to == 'dever':
        n = WJ_Devuser.objects.get(d_name=name)
    elif to == 'tester':
        n = WJ_Tester.objects.get(t_name=name)

    n.delete()
    result = {"status":True,"data":"删除成功!"}
    print result
    return HttpResponse(simplejson.dumps(result,ensure_ascii=False),content_type='application/json')


# 处理项目(开始、结束、取消)
def ajax_deal_project(request):
    myaction = request.POST['myaction']
    data = request.POST['data']
    task_id = data.split('|')[0].strip()    # 取得项目编号(传送过来的数据类似   N17  |  测试项目)
    # print task_id

    # 根据编号取得相关task信息
    result = WJ_TeamTask.objects.get(t_task_id=task_id)
    task_attribute = result.t_task_attribute
    # 判断是哪个表
    if task_attribute == 1:
        task_detail = WJ_TestTaskDetail.objects.get(t_id=task_id)
        # 什么操作
        if myaction == 'start':
            result.t_task_status = 2
            task_detail.t_status = 2
            result.save()
            task_detail.save()
        elif myaction == 'cancel':
            result.t_task_status = 4
            task_detail.t_status = 4
            result.save()
            task_detail.save()
        elif myaction == 'end':
            result.t_task_status = 3
            task_detail.t_status = 3
            result.save()
            task_detail.save()
        elif myaction == 'restart':
            result.t_task_status = 1
            task_detail.t_status = 1
            result.save()
            task_detail.save()
    elif task_attribute == 2:
        task_detail = WJ_DevTaskDetail.objects.get(d_id=task_id)
        # 什么操作
        if myaction == 'start':
            result.t_task_status = 2
            task_detail.d_status = 2
            result.save()
            task_detail.save()
        elif myaction == 'cancel':
            result.t_task_status = 4
            task_detail.d_status = 4
            result.save()
            task_detail.save()
        elif myaction == 'end':
            result.t_task_status = 3
            task_detail.d_status = 3
            result.save()
            task_detail.save()
        elif myaction == 'restart':
            result.t_task_status = 1
            task_detail.d_status = 1
            result.save()
            task_detail.save()
    # 调用一次job生成events
    job.eventsMain()
    # 每次改变项目状态,进行一次events探测
    results = job.change_events()
    for r in results:
        print r

    result = {"status":True,"data":"success!"}
    return HttpResponse(simplejson.dumps(result,ensure_ascii=False),content_type='application/json')






# login check
@require_POST
def ajaxlogin(request):
    username = request.POST['login_name']
    passwd = request.POST['login_pass']
    # 返回json数据
    result = {"status":False,"data":""}
    if username == '' or username.isspace():
        result = {"status":False,"data":"用户名不能为空"}
        return HttpResponse(simplejson.dumps(result,ensure_ascii=False),content_type='application/json')
    if passwd == '' or passwd.isspace():
        result = {"status":False,"data":"密码不能为空"}
        return HttpResponse(simplejson.dumps(result,ensure_ascii=False),content_type='application/json')
    user = auth.authenticate(username=username, password=passwd)
    if user is not None:
        if user.is_active:
            auth.login(request, user)
            result = {"status": True, "data":"OK"}
            # return HttpResponseRedirect('/index/')
            # return render_to_response('index.html')
            return HttpResponse(simplejson.dumps(result, ensure_ascii = False), content_type="application/json")
        else:
            result = {"status": False, "data":"["+username+"]已被暂时禁用"}
            return HttpResponse(simplejson.dumps(result, ensure_ascii = False), content_type="application/json")
    else:
        result = {"status": False, "data":"用户名或密码不正确，请重试"}
        return HttpResponse(simplejson.dumps(result, ensure_ascii = False), mimetype="application/json")





# 所有任务
def get_task_info(type):
    result = {}
    all_task = WJ_TeamTask.objects.all()
    if type == 1:
        result[u'未开始'] = all_task.filter(t_task_status = 1).count()
        result[u'进行中'] = all_task.filter(t_task_status = 2).count()
        result[u'已结束'] = all_task.filter(t_task_status = 3).count()
        result[u'已取消'] = all_task.filter(t_task_status = 4).count()
    if type == 2:
        result[u'新项目'] = all_task.filter(t_task_type = 'X').count()
        result[u'改造类项目'] = all_task.filter(t_task_type = 'G').count()
        result[u'内部项目'] = all_task.filter(t_task_type = 'N').count()
    return result



# 换一种看得懂的语言
def WJ_Change(code):
    task_change = {
        'X':u'新项目',
        'G':u'改造类项目',
        'N':u'内部项目',
        1:u'未开始',
        2:u'进行中',
        3:u'已结束',
        4:u'已取消',
        u'新项目':'X',
        u'改造类项目':'G',
        u'内部项目':'N',
        u'未开始':1,
        u'进行中':2,
        u'已结束':3,
        u'已取消':4,
    }
    return task_change[code]


# ajax增加任务
def add_task(request):

    if request.method == 'POST':
        # 获取id
        task_id = getTaskDetailId()
        attribute = request.POST['attribute']

        if attribute == '1':
            # 落地数据库
            # 任务类型(新项目   改造类项目   内部项目)
            type = request.POST['t_type']
            # 任务状态
            status = request.POST['t_status']


            TaskDetail = WJ_TestTaskDetail(
                t_id = WJ_Change(type) + str(task_id),
                t_name = request.POST['t_name'],
                t_is_performance = request.POST['t_is_performance'],
                t_type = WJ_Change(type),
                t_manager = request.POST['t_manager'],
                t_tester = request.POST['t_tester'],
                t_s_tester = request.POST['t_s_tester'],
                t_pre_start_time = None if not request.POST['t_pre_start_time'] else request.POST['t_pre_start_time'],
                t_test_time = None if not request.POST['t_test_time'] else request.POST['t_test_time'],
                t_pre_end_time = None if not request.POST['t_pre_end_time'] else request.POST['t_pre_end_time'],
                t_re_start_time = None if not request.POST['t_re_start_time'] else request.POST['t_re_start_time'],
                t_re_end_time = None if not request.POST['t_re_end_time'] else request.POST['t_re_end_time'],
                t_pro_release_time = None if not request.POST['t_pro_release_time'] else request.POST['t_pro_release_time'],
                t_status = WJ_Change(status),
                t_phase = request.POST['t_phase'],
                t_target = request.POST['t_target'],
            )
            TeamTask = WJ_TeamTask(
                t_task_attribute = attribute,
                t_task_id = WJ_Change(type) + str(task_id),
                t_task_type = WJ_Change(type),
                t_task_status = WJ_Change(status),
            )
            TaskDetail.save()
            TeamTask.save()

        elif attribute == '2':
            # 任务类型(X   G   N)
            type = request.POST['d_type']
            # 任务状态
            status = request.POST['d_status']

            TaskDetail = WJ_DevTaskDetail(
                d_id = WJ_Change(type) + str(task_id),
                d_name = request.POST['d_name'],
                d_is_performance = request.POST['d_is_performance'],
                d_type = WJ_Change(type),
                d_product_manager = request.POST['d_product_manager'],
                d_project_manager = request.POST['d_project_manager'],
                d_dever = request.POST['d_dever'],
                d_start_time = None if not request.POST['d_start_time'] else request.POST['d_start_time'] ,
                d_dev_time = None if not request.POST['d_dev_time'] else request.POST['d_dev_time'],
                d_test_time = None if not request.POST['d_test_time'] else request.POST['d_test_time'],
                d_use_time = None if not request.POST['d_use_time'] else request.POST['d_use_time'],
                d_release_time = None if not request.POST['d_release_time'] else request.POST['d_release_time'],
                d_end_time = None if not request.POST['d_end_time'] else request.POST['d_end_time'],
                d_status = WJ_Change(status),
                d_phase = request.POST['d_phase'],
                d_target = request.POST['d_target'],
            )
            TeamTask = WJ_TeamTask(
                t_task_attribute = attribute,
                t_task_id = WJ_Change(type) + str(task_id),
                t_task_type = WJ_Change(type),
                t_task_status = WJ_Change(status),
            )
            TaskDetail.save()
            TeamTask.save()
        ''''''
        # 增加完任务后调用一次job
        job = JobWJ()
        # 生成events
        job.eventsMain()
        # job完成
        ''''''
        return HttpResponse(1)  # success
    else:
        return HttpResponse(0)  # fail


# 获取任务详细id(不重复)
def getTaskDetailId():
    result = WJ_TaskNum.objects.get()
    # task_id
    task_id = result.t_id
    # 每次调用该方法后,将task_id加1
    result.t_id += 1
    result.save()

    return task_id

# 发送邮件
# def send_email(request):
#     app = 'outlook'
#     outlook = win32.gencache.EnsureDispatch("%s.Application"%app)
#     mail = outlook.CreateItem(win32.constants.olMailItem)
#     # 收件人
#     mail.Recipients.Add('shen_jl@Ctrip.com')
#     # 设置邮件标题
#     subj = mail.Subject = u'只是测试'
#     # 邮件正文
#     body = ["Test"]
#     # 加上签名
#     body.append(u"\r\n金融测试组  沈佳龙")
#     # join到mail.Body
#     mail.Body = '\r\n'.join(body)
#     # send
#     mail.Send()
#     print "send '%s' email ok"%subj

# # 邮件发送接口
# def send_email(request):
#     if request.method=="POST" and request.POST['mailContent']:
#
#         mail_contents = request.POST['mailContent']
#         sudsclient_email=sudsclient("http://192.168.81.123/SendMail/SendMail.asmx?wsdl")
#         try:
#             sudsclient_email.service.SendMailWithHtml2("shen_jl@ctrip.com",u"项目测试数据统计",mail_contents,"shen_jl@ctrip.com")
#         except:
#             return HttpResponse(u"发送失败!")
#         return HttpResponse(u'发送成功!')

# 生成excel并返回文件名称
def generate_excel(task_id):
    result = WJ_TestTaskDetail.objects.get(t_id = task_id)
    task_name = result.t_name
    # 先去判断是否有文件
    EXCEL_PATH = 'Download/'
    if EXCEL_PATH is None:
        raise Exception(EXCEL_PATH + "not found")
    f_name = EXCEL_PATH + task_name + u'测试报告.xlsx'
    if os.path.exists(f_name):
        os.remove(f_name)
    try:
        # 实例化对象,传入报告名称(即项目名称)
        excel = Excel_2007_Engine(excel_name = task_name)
        result = get_interface_info(task_id)
        all_case_num = all_pass_case_num = all_check_num = 0
        for r in result:
            all_case_num += r['case_num']
            all_pass_case_num += r['pass_case_num']
            all_check_num += r['check_num']
        # 生成excel
        excel.create_excel(title = task_name,interface_info=result,all_case_num=all_case_num,all_pass_case_num=all_pass_case_num,all_check_num=all_check_num)

        return True
    except Exception as e:
        print e
        return False

# 获取接口信息
def get_interface_info(task_id):
    interface_info = []
    interface_results = WJ_Interface.objects.filter(i_task_id=task_id)
    for r in interface_results:
        tmp = {}
        tmp['name'] = r.i_name
        tmp['owner'] = r.i_test_name
        tmp['contract_is_provide'] = u'是'
        tmp['is_confirm'] = u'是'
        tmp['soa_is_provide'] = u'是'
        tmp['case_num'] = r.i_case_num
        tmp['pass_case_num'] = r.i_case_pass_num
        tmp['unpass_case_num'] = r.i_case_upass_num
        tmp['check_num'] = r.i_case_check_num
        tmp['pass_rate'] = r.i_case_pass_rate
        interface_info.append(tmp)
    return interface_info

# 生成基础excel格式的测试报告
def generate_excel_test_report(request):
    '''每个项目保存最新的一份测试报告'''
    '''首先根据task_id找到项目,并生成一份Excel测试报告'''
    if request.method == 'POST':
        task_id = request.POST['task_id']
    else:
        task_id = request.GET['task_id']
    if generate_excel(task_id=task_id):
        return HttpResponse('成功')
    else:
        return HttpResponse('失败')



# 备份数据库
def backup_mysql(request):
        # web请求过来时的目录是处于项目根目录的,所以mysqldump.exe放在根目录
        # 备份目录
        backup_dir = "mysqlback"
        if not(os.path.exists((backup_dir))):
            os.mkdir(backup_dir)
        # 当前时间
        now_time = time.strftime('%Y%m%d%H%M%S',time.localtime(time.time()))
        try:
            if os.system(r'mysqldump.exe -P3306 -u root -padmin workjean > ' + backup_dir + '\\' + now_time + '.sql') == 0:
                print 'backup success'
                result = {"status":True,"data":"备份成功!"}
                return HttpResponse(simplejson.dumps(result,ensure_ascii=False),content_type='application/json')
            else:
                print 'backup fail'
                result = {"status":False,"data":"备份失败!"}
                return HttpResponse(simplejson.dumps(result,ensure_ascii=False),content_type='application/json')
        except Exception as e:
            print e
            result = {"status":False,"data":"备份失败!"}
            return HttpResponse(simplejson.dumps(result,ensure_ascii=False),content_type='application/json')


def pro_interface_manage(request):
    pass


# check field
def check_task_field(task_field):
    if not task_field.strip():
        return 0     # null
    else:
        return 1     # ok


# 管理页
def myadmin(request):
    return render_to_response('myadmin.html')