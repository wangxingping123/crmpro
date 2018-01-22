import redis

from app01 import models

POOL=redis.ConnectionPool(host="47.93.4.198",port="6379",password="")  #连接池
CONN=redis.Redis(connection_pool=POOL)

class Sell(object):

    @classmethod
    def fetch_users(cls):

        from django.db.models import Max
        sell_list_id=[]
        ret=models.SaleRank.objects.all().aggregate(Max('num'))  #取出所有销售能接受最大的人数量{'num__max': 10}
        max_num=ret.get("num__max")
        count=0
        sell_list = models.SaleRank.objects.all().order_by('weight')
        while count<max_num:
            for obj in sell_list:
                if obj.num>0:
                    sell_list_id.append(obj.user.id)
                    obj.num-=1
            count+=1
        if sell_list_id:
            CONN.lpush("sale_id_list_wxp",*sell_list_id)          #自动pop的数据
            CONN.rpush('sale_id_list_origin_wxp', *sell_list_id)  # 原来的数据
            return True
        return False

    @classmethod
    def get_sale_id(cls):
        # 查看原来数据是否存在
        sale_id_origin_count = CONN.llen('sale_id_list_origin_wxp')
        if not sale_id_origin_count:
            # 去数据库中获取数据，并赋值给： 原数据，pop数据
            status = cls.fetch_users()
            if not status:
                return None

        user_id = CONN.lpop('sale_id_list_wxp')
        if user_id:
            return user_id

        reset = CONN.get('sale_id_reset_wxp')
        # 要重置
        if reset:
            CONN.delete('sale_id_list_origin_wxp')
            status = cls.fetch_users()
            if not status:
                return None
            CONN.delete('sale_id_reset_wxp')
            return CONN.lpop('sale_id_list_wxp')
        else:
            ct = CONN.llen('sale_id_list_origin_wxp')
            for i in range(ct):
                v = CONN.lindex('sale_id_list_origin_wxp', i)
                CONN.rpush('sale_id_list_wxp', v)
            return CONN.lpop('sale_id_list_wxp')

    @classmethod
    def reset(cls):
        CONN.set('sale_id_reset_wxp', 1)

    @classmethod
    def rollback(cls, nid):
        CONN.lpush('sale_id_list_wxp', nid)

