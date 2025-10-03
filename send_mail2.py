import os
import django
import subprocess 


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'liliumpharm.settings')
django.setup()



from django.core.mail import send_mail
from django.core.mail import EmailMessage


# os.system("./utils/dump_all.sh")

# os.system("bash -c  'zip -r data.zip utils/data' ")





print("sending mail .......")

body="website database"
# body+=f" link: https://liliumpharma.com/admin/recrutement/candidaturespantane/{cv.id}/change/"
# send_mail('New CV From Website',body,'webmaster@liliumpharma.com',["contact.liliumpharma@gmail.com","boughezala.aimen@gmail.com"])


email = EmailMessage('Website Database', body, 'server.lilium@gmail.com', ["contact.liliumpharma@gmail.com","ramoul.fatah.rf@gmail.com"])

# for f in os.listdir("utils/data"):
#     _file=open(f"utils/data/{f}")
#     email.attach(f, _file.read())
#     _file.close()


email.send()



print("email sent")