from django import template
register = template.Library()

from rapports.models import Visite

from django.utils.safestring import mark_safe


@register.filter
def add_class(field, class_name):
    return field.as_widget(attrs={
        "class": " ".join((field.css_classes(), class_name))
    })





def htmlattributes(value, arg):
    attrs = value.field.widget.attrs


    data = arg.replace(' ', ' ')

    kvs = data.split(',')

    for string in kvs:
        kv = string.split(':')
        attrs[kv[0]] = kv[1]

    rendered = str(value)

    return rendered

register.filter('htmlattributes', htmlattributes)


@register.filter
def get_at_index(list, index):
    return list[index]

@register.filter
def split(string):
    return string.split(',')

@register.filter
def get_user(user_id):
    return User.objects.get(id=user_id)


@register.simple_tag
def get_visites(medecin,mindate,maxdate):
   return  mark_safe("<br>".join( ["<span style='font-size:12px'>"+str(v.rapport.added)+"</span>" for v in Visite.objects.filter(rapport__added__gte=mindate,rapport__added__lte=maxdate,medecin=medecin)] ) )


@register.simple_tag
def medecin_list_commune(commune, user):
    return commune.nbr_medecins(user)


@register.simple_tag
def is_weekend(date):
    return date.datestrftime("%A")  in ["Friday", "Saturday"]


@register.simple_tag
def plan_get_user(plans):
    # print("plans ********",)
    try:
        plans[0][0].user
    except:
        return " "    