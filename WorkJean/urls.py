from django.conf.urls import patterns, include, url
from HomePage import views
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'WorkJean.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^admin/', include(admin.site.urls)),
    # url(r'^',views.index,name='index'),
    url(r'^index/$',views.index,name='index'),
    url(r'^myadmin/$',views.myadmin),
    url(r'^task/$',views.task_page),
    url(r'^task/taskdetail/',views.task_detail),
    # url(r'^allevent/$',views.event_detail),
    url(r'^eventdetail/',views.one_event_detail),
    url(r'^addtask/$',views.add_task),
    url(r'^login/$',views.login),
    url(r'^logout/$',views.logout),
    url(r'^ajaxlogin/$',views.ajaxlogin),
    url(r'^allevent/$',views.all_my_event_detail),
    url(r'^ajaxadduser/$',views.ajax_add_user),
    url(r'^ajaxdeluser/$',views.ajax_del_user),
    url(r'^ajaxdealproject/$',views.ajax_deal_project),
    url(r'^lookproject/',views.look_project),
    url(r'^modifyproject/',views.modify_project),
    url(r'^ajaxmodifyproject/$',views.ajax_modify_project),
    url(r'^interface_config/addinterfaceinfo/',views.add_interface_info_page),
    url(r'^ajaxaddinterfaceinfo/$',views.ajax_add_interface_info),
    url(r'^ajaxgetinterfaceinfo/$',views.ajax_get_interface_info),
    url(r'^ajaxgettaskinfo/$',views.ajax_get_task_info),

    url(r'^user_config/',views.users_configuration_management),
    url(r'^module_config/',views.modules_configuration_management),
    url(r'^interface_config/',views.interface_configuration_management),
    url(r'^project_config/',views.admin_project_management),
    url(r'^backup_mysql/',views.backup_mysql),

    url(r'^generate_excel/',views.generate_excel_test_report),
    url(r'^download/(?P<path>.*)$', 'django.views.static.serve', {'document_root': 'Download/', 'show_indexes':True}),
)
