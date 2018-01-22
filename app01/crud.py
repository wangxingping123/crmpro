import json

from django.shortcuts import HttpResponse,render,redirect
from django.utils.safestring import mark_safe
from django.conf.urls import url
from django.forms import Form
from django.forms import fields
from django.forms import widgets
from django.urls import reverse

from crud.service import throne
from app01 import models
from app01.configs.customerconfig import CustomerConfig
from app01.permission.base import BasePermission

class DeaprtmentConfig(BasePermission,throne.CrudConfig):
    list_display = ["title","code"]
    editor_link = ['title', ]
throne.site.register(models.Department,DeaprtmentConfig)

class UserInfoConfig(BasePermission,throne.CrudConfig):
    comb_filter=[throne.FilterOption('depart',text_func_name=lambda x: str(x),val_func_name=lambda x: str(x.code)),]
    list_display = ["name","username","password","email","depart"]
    editor_link = ['name',]
throne.site.register(models.UserInfo,UserInfoConfig)

class CourseConfig(BasePermission,throne.CrudConfig):
    list_display = ["name",]
    editor_link = ['name', ]
throne.site.register(models.Course,CourseConfig)

class SchoolConfig(BasePermission,throne.CrudConfig):

    list_display = ["title",]
    editor_link = ['title', ]
throne.site.register(models.School,SchoolConfig)

class ClassListConfig(BasePermission,throne.CrudConfig):

    def teachers(self,condition=None,obj=None,is_header=False):
        if is_header:
            return "讲师"
        teacher_list=[]
        for obj in obj.teachers.all():
            teacher_list.append(obj.name)
        return ",".join(teacher_list)
    def cls(self,condition=None,obj=None,is_header=False):
        if is_header:
            return "班级"
        return '%s(%s)'%(obj.course.name,obj.semester)
    def number(self,condition=None,obj=None,is_header=False):
        if is_header:
            return "人数"
        
        return models.Student.objects.filter(class_list=obj.id).count()
    list_display = ["school",cls,number,"price","start_date",
                    "graduate_date","memo",teachers,"tutor"]
    editor_link = ['school', ]
    comb_filter = [throne.FilterOption("school"),
                   throne.FilterOption("course"),
                   throne.FilterOption("tutor",condition={"depart":10002}),
                   throne.FilterOption("teachers",condition={"depart":10003}, is_multi=True)]

    show_search=True
    search_condition=["price__contains",]
throne.site.register(models.ClassList,ClassListConfig)




throne.site.register(models.Customer,CustomerConfig)



class ConsultRecordConfig(BasePermission,throne.CrudConfig):
    list_display = ['customer','consultant','date']

    comb_filter = [
        throne.FilterOption('customer')
    ]

    def changelist_view(self,request,*args,**kwargs):
        customer = request.GET.get('customer')
        # session中获取当前用户ID
        current_login_user_id = 6
        ct = models.Customer.objects.filter(consultant=current_login_user_id,id=customer).count()
        if not ct:
            return HttpResponse('别抢客户呀...')

        return super(ConsultRecordConfig,self).changelist_view(request)

throne.site.register(models.ConsultRecord,ConsultRecordConfig)


class ConsultRecordConfig(BasePermission,throne.CrudConfig):

    list_display = ["customer","consultant","date","note"]

throne.site.register(models.ConsultRecord,ConsultRecordConfig)

class StudentConfig(BasePermission,throne.CrudConfig):

    def socore_display(self,condition=None,obj=None,is_header=False):
        if is_header:
            return "作业成绩"

        return mark_safe('<a href="/crm/app01/student/score/%s/">查看成绩</a>'%obj.pk)
    list_display = ["username","emergency_contract",socore_display]

    def extra_url(self):
        app_model_name = self.model_class._meta.app_label, self.model_class._meta.model_name
        patterns = [
            url(r'^score/(\d+)/$', self.wrapper(self.score_view), name='%s_%s_score' % app_model_name),
            url(r'^chart/$', self.wrapper(self.chart_view), name='%s_%s_chart' % app_model_name),
        ]
        return patterns

    def chart_view(self,request):
        ret = {'status': False, 'data': None, 'msg': None}
        try:
            cid = request.GET.get('cid')
            sid = request.GET.get('sid')
            record_list = models.StudyRecord.objects.filter(student_id=sid, course_record__class_obj_id=cid).order_by(
                'course_record_id')
            data = [ ]
            for row in record_list:
                day = "day%s" % row.course_record.day_num
                data.append([day, row.score])
            ret['data'] = data

            ret['status'] = True
        except Exception as e:
            ret['msg'] = "获取失败"

        return HttpResponse(json.dumps(ret))

    def score_view(self,request,sid):
        class_list=models.Student.objects.filter(pk=sid).first().class_list.all()

        return render(request,"stu_score.html",{"class_list":class_list,"sid":sid})
throne.site.register(models.Student,StudentConfig)


class CourseRecordConfig(BasePermission,throne.CrudConfig):

    def student_display(self,condition=None,obj=None,is_header=False):
        if is_header:
            return "考勤管理"
        return mark_safe('<a href="/crm/app01/studyrecord/?course_record=%s">点击进入</a>'%obj.pk)

    def homework_display(self,condition=None,obj=None,is_header=False):
        if is_header:
            return "作业管理"
        return mark_safe('<a href="/crm/app01/courserecord/score_list/%s/">录入成绩</a>'%obj.pk)
    list_display = ["class_obj","day_num","teacher","date",student_display,homework_display]
    show_actions=True

    def extra_url(self):
        app_model_name = self.model_class._meta.app_label, self.model_class._meta.model_name
        patterns = [

            url(r'^score_list/(\d+)/$', self.wrapper(self.score_list_view), name='%s_%s_score_list' % app_model_name),
        ]
        return patterns
    def score_list_view(self,request,course_id):
        '''录入学生成绩的函数'''
        if request.method=="GET":
            data=[]
            stu_record_list=models.StudyRecord.objects.filter(course_record_id=course_id)
            for stu_record in stu_record_list:
                form=type("TempForm",(Form,),{
                    'score_%s' % stu_record.pk: fields.ChoiceField(choices=models.StudyRecord.score_choices),
                    'homework_note_%s' % stu_record.pk: fields.CharField(widget=widgets.Textarea(attrs={"cols":25,"rows":1}))
                })

                data.append({'obj': stu_record, 'form': form(
                    initial={'score_%s' % stu_record.pk: stu_record.score, 'homework_note_%s' % stu_record.pk: stu_record.homework_note})})

            return render(request,"score_list.html",{"datalist":data})
        else:
            score_dic={}

            for k,v in request.POST.items():
                if k =="csrfmiddlewaretoken":
                    continue
                name,id=k.rsplit("_",1)
                if id not in score_dic:
                    score_dic[id]={name:v}
                else:
                    score_dic[id][name]=v
            for id,dic in score_dic.items():

                models.StudyRecord.objects.filter(pk=id).update(**dic)

            return redirect(self.get_changelist_url())

    def stu_init(self,request):
        pk_list=request.POST.getlist("pk")
        for pk in pk_list:
            course_record_obj=models.CourseRecord.objects.filter(pk=pk).first()
            if not course_record_obj:
                continue
            if models.StudyRecord.objects.filter(course_record_id=pk).exists():
                continue
            student_list=[]
            for student in course_record_obj.class_obj.student_set.all():
                obj=models.StudyRecord(course_record_id=pk,student=student)
                student_list.append(obj)
            models.StudyRecord.objects.bulk_create(student_list)

        return redirect(self.get_changelist_url())
    stu_init.short_desc="学生初始化"
    actions=[stu_init]

throne.site.register(models.CourseRecord,CourseRecordConfig)


class StudyRecordConfig(BasePermission,throne.CrudConfig):

    def record_display(self,condition=None,obj=None,is_header=False):
        if is_header:
            return "出勤"
        return obj.get_record_display()
    list_display = ["student","course_record",record_display]
    show_add_btn = False
    show_actions = True

    def checked_action(self,request):
        pklist = request.POST.getlist("pk")
        models.StudyRecord.objects.filter(pk__in=pklist).update(record="已签到")

    checked_action.short_desc ="已签到"
    def vacate_action(self,request):
        pklist=request.POST.getlist("pk")
        models.StudyRecord.objects.filter(pk__in=pklist).update(record="请假")
    vacate_action.short_desc ="请假"
    def late_action(self,request):
        pklist = request.POST.getlist("pk")
        models.StudyRecord.objects.filter(pk__in=pklist).update(record="迟到")

    late_action.short_desc ="迟到"
    def noshow_action(self,request):
        pklist = request.POST.getlist("pk")
        models.StudyRecord.objects.filter(pk__in=pklist).update(record="缺勤")

    noshow_action.short_desc ="缺勤"
    def leave_early_action(self,request):
        pklist = request.POST.getlist("pk")
        models.StudyRecord.objects.filter(pk__in=pklist).update(record="早退")

    leave_early_action.short_desc ="早退"

    actions = [checked_action,vacate_action,late_action,noshow_action,leave_early_action]

    comb_filter=[throne.FilterOption("course_record"),]
throne.site.register(models.StudyRecord,StudyRecordConfig)


throne.site.register(models.SaleRank)