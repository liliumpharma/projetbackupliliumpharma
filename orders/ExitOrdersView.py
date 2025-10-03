from .serializers import ExitOrderSerializer

tokens=[]

for user in User.objects.filter(userprofile__usersunder=kwargs['instance'].user):
    tokens.append(user.userprofile.notification_token) if user.userprofile.notification_token else None


for user in User.objects.filter(is_superuser=True):
    tokens.append(user.userprofile.notification_token) if user.userprofile.notification_token else None

for user in User.objects.filter(username__in=["liliumdz","ibtissemdz"]):
    tokens.append(user.userprofile.notification_token) if user.userprofile.notification_token else None    


for user in User.objects.filter(userprofile__rolee="CountryManager"):
    tokens.append(user.userprofile.notification_token) if user.userprofile.notification_token else None    


instance=kwargs['instance']



notification=Notification.objects.create(
        title=f"Nouveau Bon de commande  {kwargs['instance'].user.username}",
        description=f"{str(instance.added)}",
        data={
                "name":"ExitOrders",
                "title":"Bon de commande",
                "message":f"Nouveau Bon de commande de {instance.user.username}",
                "confirm_text":"voir le bon",
                "cancel_text":"plus tard",
                "StackName":"ExitOrders",
                # "url":f"https://app.liliumpharma.com/exit_orders/front/?user={instance.user.username}&date={instance.added.date()}",
                "navigate_to":
                json.dumps({
                        "screen":"List",
                        "params":{
                                "user":instance.user.username,
                                "date":str(instance.added.date())
                        }

                    },ensure_ascii=False)
            },
    )
notification.users.set([usr for usr in instance.user.userprofile.get_users_to_notify()])
# notification.send()
# shot = WebShot()
create_jpg = thread(
    "generating_jpg_for_exit_order"+str(instance.id),
        instance.id+1000,
        'http://localhost:8001/exit_orders/'+str(instance.id),
        '/app/static/share/exit_orders/'+str(instance.id)+'.jpg'
        )

create_jpg.start()
