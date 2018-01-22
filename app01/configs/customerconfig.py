import json
import datetime
from django.shortcuts import HttpResponse,render,redirect
from django.utils.safestring import mark_safe
from django.conf.urls import url
from django.db import transaction
from django.db.models import Q
from django.forms import ModelForm

from crud.service import throne
from app01 import models
from utils.get_sell import Sell
from app01.permission.base import BasePermission

class SingleModelForm(ModelForm):
    class Meta:
        model = models.Customer
        exclude = ['consultant','status','recv_date','last_consult_date']


class CustomerConfig(BasePermission,throne.CrudConfig):

    editor_link = ["name"]
    def display_gender(self,condition=None,obj=None,is_header=False):
        if is_header:
            return '性别'
        return obj.get_gender_display()

    def display_education(self,condition=None,obj=None,is_header=False):
        if is_header:
            return '学历'
        return obj.get_education_display()

    def display_course(self,condition=None,obj=None,is_header=False):
        if is_header:
            return '咨询课程'
        course_list = obj.course.all()
        html = []
        # self.request.GET
        # self._query_param_key
        # 构造QueryDict
        # urlencode()
        for item in course_list:
            temp = "<a style='display:inline-block;padding:3px 5px;border:1px solid blue;margin:2px;' href='/crm/app01/customer/%s/%s/dc/'>%s X</a>" %(obj.pk,item.pk,item.name)
            html.append(temp)

        return mark_safe("".join(html))

    def display_status(self,condition=None,obj=None,is_header=False):
        if is_header:
            return '状态'
        return obj.get_status_display()

    def record(self,condition=None,obj=None,is_header=False):
        if is_header:
            return '跟进记录'
        # /stark/crm/consultrecord/?customer=11
        return mark_safe("<a href='/crm/app01/consultrecord/?customer=%s'>查看跟进记录</a>" %(obj.pk,))



    list_display = ['qq','name',display_gender,display_education,display_course,display_status,record]
    edit_link = ['name']
    order_by = ["-status"]


    def delete_course(self,request,customer_id,course_id):
        """
        删除当前用户感兴趣的课程
        :param request:
        :param customer_id:
        :param course_id:
        :return:
        """
        customer_obj = self.model_class.objects.filter(pk=customer_id).first()
        customer_obj.course.remove(course_id)
        # 跳转回去时，要保留原来的搜索条件
        return redirect(self.get_changelist_url())

    def extra_url(self):
        app_model_name = (self.model_class._meta.app_label, self.model_class._meta.model_name,)
        patterns = [
            url(r'^(\d+)/(\d+)/dc/$', self.wrapper(self.delete_course), name="%s_%s_dc" %app_model_name),
            url(r'^public/$', self.wrapper(self.public_view), name="%s_%s_public" % app_model_name),
            url(r'^(\d+)/competition/$', self.wrapper(self.competition_view), name="%s_%s_competition" % app_model_name),
            url(r'^userlist/$', self.wrapper(self.userlist_view), name="%s_%s_userlist" % app_model_name),
            url(r'^single/$', self.wrapper(self.single_view), name="%s_%s_single" % app_model_name),
            url(r'^multi/$', self.wrapper(self.multi_view), name="%s_%s_multi" % app_model_name),
            url(r'^file_download/$', self.wrapper(self.file_download_view), name="%s_%s_file_download" % app_model_name),

        ]
        return patterns

    def public_view(self,request):
        '''公共资源'''

        current_user_id=request.session["user_info"].get("user_id")  #当前登录用户的id
        current_date=datetime.datetime.now().date()
        fifth_day=datetime.timedelta(days=15)  #间隔时间
        three_day=datetime.timedelta(days=3)
        public_coustomer_list=models.Customer.objects.filter(Q(status=2)&Q(last_consult_date__lt=current_date-three_day)|Q(recv_date__lt=current_date-fifth_day))
        return render(request,"public_customer.html",{"public_coustomer_list":public_coustomer_list,'current_user_id':current_user_id})

    def competition_view(self,request,cid):
        '''进行抢单'''
        current_user_id=request.session["user_info"].get("user_id")    #当前登录的用户id

        current_date = datetime.datetime.now().date()
        fifth_day = datetime.timedelta(days=15)  # 间隔时间
        three_day = datetime.timedelta(days=3)
        # q=Q()
        # q.connector="or"
        # q.children.append("last_consult_date__lt",current_date - three_day)
        # q.children.append("recv_date__lt",current_date - fifth_day)
        #
        ret = models.Customer.objects.filter(
            Q(status=2) & Q(last_consult_date__lt=current_date - three_day) | Q(recv_date__lt=current_date - fifth_day),id=cid).exclude(consultant_id=current_user_id).update(recv_date=current_date,last_consult_date=current_date,consultant_id=current_user_id)
        if not ret:
            return HttpResponse("你不能抢这个单或已被抢走")
        models.CustomerDistribution.objects.create(user_id=current_user_id,customer_id=cid,ctime=current_date)
        return HttpResponse("你已成功抢单！")

    def userlist_view(self,request):
        '''查看个人的客户列表'''

        current_user_id=request.session["user_info"].get("user_id") #当前登录用户的id
        customer_list=models.CustomerDistribution.objects.filter(user_id=current_user_id).order_by("status")
        return render(request,"userlist.html",{"customer_list":customer_list})

    def single_view(self,request):
        '''给所有销售分配客户'''
        if request.method=="GET":
            form=SingleModelForm()

        else:
            form=SingleModelForm(request.POST)
            if form.is_valid():
                """客户表新增数据：
                - 获取该分配的课程顾问id
                - 当前时间
                客户分配表中新增数据
                - 获取新创建的客户ID
                - 顾问ID
            """
                sale_id=Sell.get_sale_id()
                if not sale_id:
                    return HttpResponse("没有销售顾问，无法进行自动分配")
                now_date=datetime.datetime.now().date()

                ret=form.cleaned_data.pop("course")   #取出多对多字段
                form.cleaned_data["consultant_id"]=sale_id
                form.cleaned_data["recv_date"]=now_date

                try:
                    with transaction.atomic():
                        obj=models.Customer.objects.create(**form.cleaned_data)
                        obj.course.add(*ret)
                        models.CustomerDistribution.objects.create(user_id=sale_id,customer_id=obj.id,ctime=now_date)
                        #发消息
                        from utils import message
                        message.send_message("HELLO_WORLD","元旦快乐","1217885733@qq.com","小贱")

                except Exception as e:
                    print(e)
                    Sell.rollback(sale_id)
                    return HttpResponse("录入异常")
                return HttpResponse("录入成功")
        return render(request, "single_view.html", {"form": form})

    def multi_view(self,request):

        if request.method=="GET":
            return render(request,"multi_view.html")
        else:
            import xlrd
            from xlrd.sheet import Cell
            from django.core.files.uploadedfile import InMemoryUploadedFile
            file_obj=request.FILES.get("exfile")
            file_name=file_obj.name
            _,ty=file_name.rsplit(".",1)
            if ty != "xlsx":
                return HttpResponse("暂不支持此文件")

            maps={
                0:"name",
                1:"qq",
                2:"gender",

            }

            work_book=xlrd.open_workbook(file_contents=list(file_obj.chunks())[0])
            sheet=work_book.sheet_by_index(0)
            customer_list=[]
            for index in range(1, sheet.nrows):
                row = sheet.row(index)
                customer_dic={}
                for i in range(len(maps)):
                    k=maps[i]
                    v=str(row[i].value)
                    if '.' in v:
                        v,_=v.rsplit(".",1)
                        v=int(v)
                    customer_dic[k]=v
                # sale_id=int(Sell.get_sale_id().decode("utf-8"))
                sale_id=8
                customer_dic["consultant_id"]=sale_id
                customer_dic["recv_date"]=datetime.datetime.now().date()
                obj=models.Customer(**customer_dic)
                customer_list.append(obj)

            # models.Customer.objects.bulk_create(customer_list)


            return HttpResponse("上传成功")

    def file_download_view(self,request):
        '''文件的下载'''
        from django.http import StreamingHttpResponse
        def file_iterator(file_name, chunk_size=512):
            with open(file_name) as f:
                while True:
                    c = f.read(chunk_size)
                    if c:
                        yield c
                    else:
                        break

        the_file_name = "customerinfo.xlsx"
        response = StreamingHttpResponse(file_iterator(the_file_name))
        response['Content-Type'] = 'application/vnd.ms-excel'
        response['Content-Disposition'] = 'attachment;filename="{0}"'.format(the_file_name)

        return response

