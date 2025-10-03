from django.contrib.auth.models import User
from medecins.models import Medecin

souha=User.objects.get(username="souhadz")
constantine_medecin=Medecin.objects.filter(commune__wilaya__id=25)

for medecin in constantine_medecin:
    print(medecin.nom)
    medecin.users.add(souha)



#test
