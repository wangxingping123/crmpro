from django.conf import settings
def init_permission(request,user):

    '''获取权限并放置到session中'''
    permissionlist = user.roles.values(
                                        "permissions__id",
                                        "permissions__menu_gp_id",
                                        "permissions__title",
                                       "permissions__url",
                                       "permissions__code",
                                       "permissions__group_id",
                                       "permissions__group__menu_id",
                                       "permissions__group__menu__title",

                                       ).distinct()
    '''
    menu_list = [
    {'id': 1, 'title': '用户列表', 'url': '/userinfo/', 'menu_gp_id': None, 'menu_id': 1, 'menu_title': '菜单管理'},
    {'id': 2, 'title': '添加用户', 'url': '/userinfo/add/', 'menu_gp_id': 1, 'menu_id': 1, 'menu_title': '菜单管理'},
    {'id': 3, 'title': '删除用户', 'url': '/userinfo/del/(\\d+)/', 'menu_gp_id': 1, 'menu_id': 1, 'menu_title': '菜单管理'},
    {'id': 4, 'title': '修改用户', 'url': '/userinfo/edit/(\\d+)/', 'menu_gp_id': 1, 'menu_id': 1, 'menu_title': '菜单管理'},
    {'id': 5, 'title': '订单列表', 'url': '/order/', 'menu_gp_id': None, 'menu_id': 2, 'menu_title': '菜单2'},
    {'id': 6, 'title': '添加订单', 'url': '/order/add/', 'menu_gp_id': 5, 'menu_id': 2, 'menu_title': '菜单2'},
    {'id': 7, 'title': '删除订单', 'url': '/order/del/(\\d+)/', 'menu_gp_id': 5, 'menu_id': 2, 'menu_title': '菜单2'},
    {'id': 8, 'title': '修改订单', 'url': '/order/edit/(\\d+)/', 'menu_gp_id': 5, 'menu_id': 2, 'menu_title': '菜单2'}
]
    '''
    menu_list = []
    for item in permissionlist:
        dic={"id":item["permissions__id"],"title":item["permissions__title"],
             "url":item["permissions__url"],"menu_gp_id":item["permissions__menu_gp_id"],
            "menu_id":item["permissions__group__menu_id"],
             "menu_title":item["permissions__group__menu__title"]}
        menu_list.append(dic)
    request.session[settings.PERMISSION_MENU_KEY] = menu_list
#权限相关
    permission_url_dic ={}
    for item in permissionlist:
        code=item["permissions__code"]
        url=item["permissions__url"]
        group_id=item["permissions__group_id"]
        if group_id in permission_url_dic:
            permission_url_dic[group_id]["codes"].append(code)
            permission_url_dic[group_id]["urls"].append(url)
        else:
            permission_url_dic[group_id]={"codes":[code,],
                                            "urls":[url,]
             }
    request.session[settings.PERMISSIONS_URL_DIC] = permission_url_dic
