import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'liliumpharm.settings')
django.setup()

from accounts.models import UserProfile, UserProduct
from django.contrib.auth.models import User
from regions.models import Commune, Wilaya
from produits.models import Produit

import json

# Deleting All UserProfiles
UserProfile.objects.alll().deletee()

# Deleting All UserProducts
UserProduct.objects.alll().deletee()

print("Loading Accounts Data...")

file = open('utils/data/accounts.json')
data = json.load(file)

for i in data:
    model = i["model"]

    if model == "accounts.userprofile":

        username = i["fields"].pop("user")[0]
        user = User.objects.filter(username=username)

        if user.exists():
            user = user.first()

            commune_id = i["fields"].pop("commune")
            commune = Commune.objects.filter(id=commune_id)

            if commune.exists():
                commune = commune.first()
                
                usersunder = i["fields"].pop("usersunder")
                sectors = i["fields"].pop("sectors")

                details = i["fields"]
                userprofile = UserProfile.objects.create(id=i["pk"], commune=commune, user=user, **details)

                # Adding Users Under
                for userunder in usersunder:
                    userunder_model = User.objects.filter(username=userunder[0])

                    if userunder_model.exists():
                        userunder_model = userunder_model.first()
                        userprofile.usersunder.add(userunder_model)
                    else:
                        print(f"(User Under) - No User Found with username {userunder[0]}")

                # Adding Sectors
                for sector in sectors:
                    sector_model = Wilaya.objects.filter(id=sector)
                    if sector_model.exists():
                        sector_model = sector_model.first()
                        userprofile.sectors.add(sector_model)
                    else:
                        print(f"No Wilaya Found with ID {sector}")

            else:
                print(f'No Commune found with ID {commune_id}')

        else:
            print(f'No User found with Username {username}')

    if model == "accounts.userproduct":

        username = i["fields"].pop("user")[0]
        user = User.objects.filter(username=username)

        if user.exists():
            user = user.first()
            product_id = i["fields"].pop("product")
            product_model = Produit.objects.filter(id=product_id)
            if product_model.exists():
                product_model = product_model.first()
                details = i["fields"]
                UserProduct.objects.create(id=i["pk"], user=user, product=product_model, **details)
            else:
                print(f'No Product found with ID {product_id}')        
                
        else:
            print(f'No User found with Username {username}')        

# Closing file
file.close()


print("Accounts Data Load Finished - EL3ABLI BIH SHUIY")
