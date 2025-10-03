import os
import django
import subprocess 


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'liliumpharm.settings')
django.setup()


import calendar

from django.core.mail import send_mail
from django.core.mail import EmailMessage
from django.contrib.auth.models import User
from rapports.models import Rapport
from plans.models import * 
from datetime import date, timedelta
from django.template.loader import render_to_string 




# ####   DATABASE BACKUP 



os.system("./utils/dump_all.sh")

os.system("bash -c  'zip -r data.zip utils/data' ")


body="website database"
# # # body+=f" link: https://liliumpharma.com/admin/recrutement/candidaturespantane/{cv.id}/change/"
# # # send_mail('New CV From Website',body,'webmaster@liliumpharma.com',["contact.liliumpharma@gmail.com","fatah.ramoul@liliumpharma.com"])


email = EmailMessage(
    'Website Database in server', 
    body, 'server.lilium@gmail.com', 
    ["contact.liliumpharma@gmail.com","fatah.ramoul@liliumpharma.com"]
    )

for f in os.listdir("utils/data"):
    open("utils/data/{f}","wb").write(open("utils/data/{f}").read().decode("unicode_escape").encode("utf8"))
    #_file=open(f"utils/data/{f}",encoding="utf8")
    #email.attach(f, _file.read())
    #_file.close()

os.system("zip  utils/db/lldb.zip utils/db/lldb.sql")
#_file=open(f"utils/db/lldb.zip","rb")
#_file.read()
#email.attach("lldb.zip", _file.read())
email.send()



print("email sent")






# GENERATING RAPPORTS 
    



# for p in  Plan.objects.filter(plantask__isnull=False,day__lte=datetime.datetime.today()):
#     try:
#         Rapport.objects.create(user=p.user,added=p.day,image="rapports/rapport.jpeg")
#     except:
#         # print("alreday exists ")
#         pass   



# SENDING MAILS FOR MISSING RAPPORTS 

# yesturday = date.today() -timedelta(days=1)
# yesturday = date.today() -timedelta(days=1)

 

# if calendar.day_name[yesturday.weekday()] not in ["Friday", "Saturday"]:

#     for usr in User.objects.filter(userprofile__recive_mail=True):
#         try:
#             r=Rapport.objects.get(user=usr,added=yesturday)

#             if len(r.visites_list) == 0 and len(PlanTask.objects.filter(plan__day=r.added,plan__user=usr)) == 0 :
#                 print(r.user,"has empty rapport",r.added)
#                 subject="Rapport Quotidien Lilium Pharma"
#                 body=render_to_string("rapports/empty_email.html",{"usr":usr,"yesturday":yesturday})
#                 email = EmailMessage(subject, body, 'server.lilium@gmail.com', [usr.email,"contact.liliumpharma@gmail.com","n.bouriah@gmail.com","boughezala.aimen@gmail.com"])
#                 email.content_subtype = 'html'
#                 email.send()
#                 print("email sent to ",usr)


#         except Exception as e:
#             print(e)
#             print(usr.username,"has no rapport", yesturday)

#             # Create Absences


#             Absence.objects.create(user=usr, reason=f'Rapport du {yesturday} Manquant', date=yesturday)

#             if usr.email:
#                 subject="Rapport Quotidien LiliumPharma"
#                 body=render_to_string("rapports/email.html",{"usr":usr,"yesturday":yesturday})
#                 email = EmailMessage(subject, body, 'server.lilium@gmail.com', [usr.email,"contact.liliumpharma@gmail.com","n.bouriah@gmail.com","boughezala.aimen@gmail.com"])
#                 email.content_subtype = 'html'
#                 email.send()
#                 print("email sent to ",usr)

