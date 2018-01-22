import re
from django.template import Library
from django.conf import settings
register = Library()

@register.inclusion_tag("rbac_menu.html")
def menu_html(request):
    '''去Session中获取菜单相关信息，匹配当前URL，生成菜单'''
    menu_list = request.session[settings.PERMISSION_MENU_KEY]
    current_url = request.path_info
    menu_dic = {}
    for item in menu_list:
        if not item["menu_gp_id"]:
            menu_dic[item["id"]] = item
    for item in menu_list:
        url = item["url"]
        db_url = "^{0}$".format(url)
        if re.match(db_url, current_url):
            if not item["menu_gp_id"]:
                menu_dic[item["id"]]["active"] = True
            else:
                menu_dic[item["menu_gp_id"]]["active"] = True

    result = {}
    ''' {
    1: {'id': 1, 'title': '用户列表', 'url': '/userinfo/', 
'menu_gp_id': None, 'menu_id': 1, 'menu_title': '菜单管理'},
    5: {'id': 5, 'title': '订单列表', 'url': '/order/',
  'menu_gp_id': None, 'menu_id': 2, 'menu_title': '菜单2', 'active': True}}
    '''
    for item in menu_dic.values():
        active = item.get('active')
        menu_id = item['menu_id']
        if menu_id in result:
            result[menu_id]['children'].append({'title': item['title'], 'url': item['url'], 'active': active})
            if active:
                result[menu_id]['active'] = True
        else:
            result[menu_id] = {
                'menu_id': item['menu_id'],
                'menu_title': item['menu_title'],
                'active': active,
                'children': [
                    {'title': item['title'], 'url': item['url'], 'active': active}
                ]
            }

    return {'menu_dict':result}
