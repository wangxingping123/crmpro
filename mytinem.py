# import datetime
#
# current_date = datetime.datetime.now().date()
# fifth_day = datetime.timedelta(days=15)  # 间隔时间
# three_day = datetime.timedelta(days=3)
#
# print(current_date-fifth_day)


import smtplib
from email.mime.text import MIMEText
from email.utils import formataddr



def send(subject,body,to,name):

    msg = MIMEText(body, 'plain', 'utf-8')  # 发送内容
    msg['From'] = formataddr(["王兴平","wxp_live@126.com"])  # 发件人
    msg['To'] = formataddr([name, to])  # 收件人
    msg['Subject'] = subject # 主题


    server = smtplib.SMTP("smtp.126.com", 25) # SMTP服务
    server.login("wxp_live@126.com", 'w934475989') # 邮箱用户名和密码
    server.sendmail("wxp_live@126.com", [to, ], msg.as_string()) # 发送者和接收者
    server.quit()

email_list=[
    {"email":'924519844@qq.com',"name":"张总"},
    {"email":'2359435197@qq.com',"name":"鹏哥哥"},
    {"email":'1013780045@qq.com',"name":"陈浩"},
    {"email":'1136341654@qq.com',"name":"阿星"},
    {"email":'1217885733@qq.com',"name":"小贱"},
    {"email":'1364873962@qq.com',"name":"国栋"},
    {"email":'414846066@qq.com',"name":"辉总"},
]
for dic in email_list:

    send("新年快乐","^o^蛋生鸡、鸡生蛋，管它还是先有鸡、还是先有蛋，送走圣诞迎元旦；圣诞圆、圆蛋圆，管它圣诞圆还是元旦圆，只愿家家户户都团圆；你蛋疼、他蛋疼，管你们谁的蛋最疼，元旦佳节大家快乐那就行。元旦快乐哈！",'%s'%dic["email"],"%s"%dic["name"])
    print("chegngogn")
