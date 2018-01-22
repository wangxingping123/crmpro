# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2018-01-02 08:25
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Group',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=32, verbose_name='组名')),
            ],
        ),
        migrations.CreateModel(
            name='Menu',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=16, verbose_name='菜单名')),
            ],
        ),
        migrations.CreateModel(
            name='Permission',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=32, verbose_name='标题')),
                ('url', models.CharField(max_length=64, verbose_name='含正则表达式的url')),
                ('code', models.CharField(max_length=32, verbose_name='代码')),
                ('group', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='rbac.Group')),
                ('menu_gp', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='rbac.Permission', verbose_name='组内菜单')),
            ],
        ),
        migrations.CreateModel(
            name='Role',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=32, verbose_name='角色名')),
                ('permissions', models.ManyToManyField(to='rbac.Permission', verbose_name='所拥有的权限')),
            ],
        ),
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('username', models.CharField(max_length=32, verbose_name='用户名')),
                ('password', models.CharField(max_length=32, verbose_name='密码')),
                ('roles', models.ManyToManyField(blank=True, to='rbac.Role', verbose_name='所拥有的角色')),
            ],
        ),
        migrations.AddField(
            model_name='group',
            name='menu',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='rbac.Menu', verbose_name='所属菜单'),
        ),
    ]