# -*- coding:utf-8 -*-
from MySQLUtil import Connection
import config
import datetime,time
from time import timezone

__author__ = 'kiven'

'''job服务'''
class JobWJ(object):
    def __init__(self):
        self.conn = Connection(host=config._HOST, database=config._DB, user=config._USER, password=config._PASS, port=config._PORT)

    # 所有task
    def getAllTask(self,sql = 'select * from homepage_wj_teamtask'):
        result = self.conn.query(sql)
        self.conn.close()
        return result

    # 获取项目的详细信息
    def getTaskDetail(self,db_name,id_name,task_id):
        sql = 'select * from %s where %s = "%s"' % (db_name,id_name,task_id)
        # print sql
        result = self.conn.query(sql)
        self.conn.close()
        # print result
        return result

    # 生成events
    def generateEvents(self,events,attribute):
        '''result = [{},{},{}]'''
        result = []
        if attribute == 1:
            m_user = 't_s_tester'
            m_events_id = 't_id'
            m_events_name = 't_name'
            m_events_status = 't_status'
        elif attribute == 2:
            m_user = 'd_dever'
            m_events_id = 'd_id'
            m_events_name = 'd_name'
            m_events_status = 'd_status'
        for event in events:
            temp = {
                'm_user':'',
                'm_events_id':0,
                'm_events_name':'',
                'm_events_status':-1
            }
            temp['m_user'] = event[0][m_user]
            temp['m_events_id'] = event[0][m_events_id]
            temp['m_events_name'] = self.generateEventsName(event[0][m_events_name],event[0][m_events_status])
            temp['m_events_status'] = event[0][m_events_status]
            result.append(temp)

        return result

    # 解析需要通知的用户(数据库中存储方式为:沈佳龙戴马陈佳珠李娜娜),需要分离
    def parseUsers(self,userString):
        myUserSet = []
        userSet = []
        '''所有用户'''
        sql = 'select * from homepage_wj_tester'
        result = self.conn.query(sql)      # result = [{},{},{}]
        # 放到list中
        for p in result:
            userSet.append(p['t_name'])

        # 2014/11/4 21:40 得如下算法:
        step = 3
        while True:
            if len(userString) < 2:
                break
            temp = userString[:step]
            if temp in userSet:
                myUserSet.append(temp)
                userString = userString[step:]
            else:
                if step == 2:
                    step = 3
                else:
                    step = 2
        return myUserSet


    # 生成的events落地
    def putEvents(self,user_name,task_id,events_name,events_status):
        result = '已存在'
        # 首先判断表中是否存在这些数据
        sql_test = 'select * from homepage_wj_myevents where m_events_id = "%s" and m_user = "%s"'%(task_id,user_name)
        result_test = self.conn.query(sql_test)
        if not result_test:
            result = '落地成功!'
            sql = 'insert into homepage_wj_myevents(m_user,m_events_id,m_events_name,m_is_send_email,m_events_status,m_events_is_new) values("%s","%s",\'%s\',%d,%d,%d)'%(user_name,task_id,events_name,0,events_status,1)
            # print sql
            self.conn.execute(sql)
        self.conn.close()
        return result

    # 生成events的m_events_name
    def generateEventsName(self,task_name,task_status):
        str = {
            1:u'未开始',
            2:u'进行中',
        }
        content = u'您有<%s>新项目——"%s",请关注' % (str[task_status],task_name)
        return content

    # 更新任务表,如果任务状态不为1或2,则删除event
    # events探测
    def change_events(self):
        result = []
        # 获得所有event
        query_sql_event = "select * from homepage_wj_myevents"
        # result = [{任务1},{任务2},...]
        events = self.conn.query(query_sql_event)
        for e in events:
            # event_id
            event_id = e['m_events_id']
            # 根据event_id找出对应task_id的状态
            query_sql_task = "select t_task_status from homepage_wj_teamtask where t_task_id = '%s'"%(event_id)
            r = self.conn.query(query_sql_task)
            # 得到状态
            task_status = r[0]['t_task_status']
            # 如果task中taks的状态不为1或2,则从homepage_wj_myevents表中删除对应的event
            if not task_status == 1 and not task_status == 2:
                sql = "delete from homepage_wj_myevents where m_events_id = '%s'"%(event_id)
                self.conn.execute(sql)
                result.append(event_id + u'  已删除')
            else:
                result.append(event_id + u'  无变化')
        self.conn.close()
        return result


    # 生成events入口方法
    def eventsMain(self):
        '''results = {   'T':[[{}],[[{}]]],'D':[[{}]]     }'''
        results = {
            'T':[],
            'D':[],
        }
        # 收集events
        events_info = []

        alltasks = self.getAllTask()
        for task in alltasks:
            '''datetime.date()  取得年月日'''
            # print task['t_task_status']
            # 如果task的状态为1(未开始)或2(进行中)
            # print task
            if task['t_task_status'] == 1 or task['t_task_status'] == 2:
                # task的id和属性
                task_id = task['t_task_id']
                task_attribute = task['t_task_attribute']
                if task_attribute == 1:
                    db_name = 'homepage_wj_testtaskdetail'
                    id_name = 't_id'
                    results['T'].append(self.getTaskDetail(db_name,id_name,task_id))
                elif task_attribute == 2:
                    db_name = 'homepage_wj_devtaskdetail'
                    id_name = 'd_id'
                    results['D'].append(self.getTaskDetail(db_name,id_name,task_id))
        # print results
        '''t_tasks = [[{},{},{},... ]]'''
        t_tasks = results['T']
        d_tasks = results['D']
        events_info.append(self.generateEvents(t_tasks,1))
        events_info.append(self.generateEvents(d_tasks,2))
        '''
        events_info = [[{},{},{}],[{},{},{}]]
        '''
        # print events_info
        # for e in events_info[0]:
        #     print e
        # 落地WJ_MyEvents数据库
        for event in events_info:
            for e in event:
                users = e['m_user']
                # 解析出每个人
                users = self.parseUsers(users)
                for user in users:
                    print self.putEvents(user,e['m_events_id'],e['m_events_name'],e['m_events_status'])


    # 配置用户信息
    def userConfig(self,username,u_real_name):
        result = u'记录已存在'
        '''查出auth_user中用户相关信息'''
        sql = 'select * from auth_user where username = "%s"'%(username)
        userinfo = self.conn.query(sql)
        '''homepage_wj_user表中是否存在该记录'''
        querySQL = "select * from homepage_wj_user where u_name = '%s'"%(username)
        u_info = self.conn.query(querySQL)
        if not u_info:
            # 插入到homepage_wj_user表的信息
            u_name = userinfo[0]['username']
            u_pwd = userinfo[0]['password']
            insertSQL = "insert into homepage_wj_user(u_name,u_pwd,u_real_name) values ('%s','%s','%s')"%(u_name,u_pwd,u_real_name)
            self.conn.execute(insertSQL)
            result = u'用户信息保存成功!'
        # 关闭数据库连接
        self.conn.close()
        return result


    # 昨天现在
    def todayTime(self):
        now = datetime.datetime.now()
        start = now - datetime.timedelta(hours=23, minutes=59, seconds=59)
        return start

    # 当天日期(str类型)
    def nowTime_str(self):
        return time.strftime('%Y-%m-%d',time.localtime(time.time()))

    # 当天日期(datetime.date类型)
    def nowTime_date(self):
        return time.strftime('%Y-%m-%d',time.localtime(time.time()))

    '''获取过去任意一天日期
    @:param int类型,距今天相差的天数
    '''
    def anyDay(self,delta):
        today = datetime.date.today()
        anyday = today - datetime.timedelta(days=delta)
        return anyday


if __name__ == '__main__':
    job = JobWJ()

    # 生成Events
    job.eventsMain()

    # 用户配置
    # print job.userConfig('cjz',u'陈佳珠')
    # print job.userConfig('cmy',u'陈梦云')
    # print job.userConfig('dm',u'戴马')
    # print job.userConfig('gmx',u'高明霞')
    # print job.userConfig('lyq',u'李艳秋')
    # print job.userConfig('vgmg',u'高明国')
    # print job.userConfig('vsmx',u'孙明星')
    # print job.userConfig('xh',u'许惠')
    # print job.userConfig('lnn',u'李娜娜')
    # print job.userConfig('cl',u'陈亮')
    # print job.userConfig('sgx',u'石广学')

    # 探测event的状态
    # results = job.change_events()
    # for r in results:
    #     print r

