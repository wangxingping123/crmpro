from django.db import models

# Create your models here.
class Menu(models.Model):
    title=models.CharField(verbose_name="菜单名",max_length=16)

    def __str__(self):
        return self.title

class Group(models.Model):
    name=models.CharField(verbose_name="组名",max_length=32)
    menu=models.ForeignKey(verbose_name="所属菜单",to="Menu",default=1)

    def __str__(self):
        return self.name

class Permission(models.Model):
    '''权限表'''
    title = models.CharField(verbose_name="标题", max_length=32)
    url=models.CharField(verbose_name="含正则表达式的url",max_length=64)
    code=models.CharField(verbose_name="代码",max_length=32)
    menu_gp=models.ForeignKey(verbose_name="组内菜单",null=True,blank=True,to="Permission")
    group=models.ForeignKey(to="Group")
    def __str__(self):
        return self.title

class Role(models.Model):
    '''角色表'''
    title=models.CharField(verbose_name="角色名",max_length=32)
    permissions=models.ManyToManyField(verbose_name="所拥有的权限",to="Permission")
    def __str__(self):
        return self.title

class User(models.Model):
    '''用户表'''
    username=models.CharField(verbose_name="用户名",max_length=32)
    password=models.CharField(verbose_name="密码",max_length=32)
    roles=models.ManyToManyField(verbose_name="所拥有的角色",to="Role",blank=True)

    def __str__(self):
        return self.username