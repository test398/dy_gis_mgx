from os import path

urlpatterns = [
    path('get_mgx_rating_list', views.get_mgx_rating_list),                                 # 美观性评分规则
    path('save_mgx_rating_config', views.save_mgx_rating_config),                           # 美观性评分规则
    path('get_mgx_rating_config_by_id', views.get_mgx_rating_config_by_id),                 # 美观性评分规则
    path('save_max_rating_result', views.save_max_rating_result),                           # 美观性评分规则
    path('get_max_rating_result_list', views.get_max_rating_result_list),                   # 美观性评分规则
]