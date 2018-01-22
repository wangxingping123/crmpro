from django.shortcuts import render,redirect
from django.forms import Form,fields,widgets,ValidationError

from rbac import models
from rbac.service import init_permission

class UserLoginForm(Form):

    username=fields.CharField(error_messages={"required":"用户名不能为空"})
    password=fields.CharField(error_messages={"required":"密码不能为空"})


def user_login(request):
    '''用户登录页面'''
    if request.method=="GET":
        form=UserLoginForm()
    else:
        form=UserLoginForm(request.POST)
        if form.is_valid():
            obj=models.User.objects.filter(**form.cleaned_data).first()
            if obj:
                request.session["user_info"]={"status":True,"user_id":obj.id}
                init_permission.init_permission(request=request, user=obj)
                return redirect("/index/")
            else:
                errors="用户名或密码错误"
                return render(request, "user_login.html", {"errors": errors})
    return render(request, "user_login.html",{"form":form})


def index(request):

    return render(request,"index.html")