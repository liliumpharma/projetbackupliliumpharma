import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'liliumpharm.settings')
django.setup()



from datetime import datetime
from django.utils import timezone
from orders.models import Order  # adapte selon ton projet
from accounts.models import User

def delete_2024_order_photos():
    # Filtrer les commandes de 2024
    orders = Order.objects.filter(
        added__year=2021
    )

    total = 0

    for order in orders:
        if order.image:  # adapte le champ (image, file, etc.)
            file_path = order.image.path

            if os.path.exists(file_path):
                os.remove(file_path)
                print(f"Supprimé: {file_path}")
                total += 1

            # Optionnel : vider le champ en base
            #order.image = None
            order.save()

    print(f"Total supprimé: {total}")


delete_2024_order_photos()