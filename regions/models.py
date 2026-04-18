from django.db import models


REGION_CHOICES = [
    ("Centre", "Centre"),
    ("Sud", "Sud"),
    ("Est", "Est"),
    ("Ouest", "Ouest"),
    ("Vide", "Vide"),
]


class Region(models.Model):
    name = models.CharField(max_length=10, choices=REGION_CHOICES, unique=True)

    class Meta:
        db_table = "regions_region"
        verbose_name = "Région"
        verbose_name_plural = "Régions"

    def __str__(self):
        return self.name


MEDICAL = [
    "Généraliste",
    "Diabetologue",
    "Neurologue",
    "Psychologue",
    "Gynécologue",
    "Rumathologue",
    "Allergologue",
    "Phtisio",
    "Cardiologue",
    "Urologue",
    "Hematologue",
    "Orthopedie",
    "Nutritionist",
    "Dermatologue",
    "Interniste",
    "Gastrologue",
]
COMMERCIAL = ["Pharmacie", "Grossiste", "SuperGros"]


class Pays(models.Model):
    nom = models.CharField(max_length=255)

    def __str__(self):
        return self.nom

    @property
    def wilayas(self):
        wilayas = Wilaya.objects.filter(pays=self)
        wilayas_list = []
        for wilaya in wilayas:
            wilayas_list.append(
                {"id": wilaya.id, "nom": wilaya.nom, "communes": wilaya.get_communes()}
            )
        return wilayas_list


class Wilaya(models.Model):
    nom = models.CharField(max_length=255)
    code_name = models.CharField(max_length=10, null=True, blank=True)
    pays = models.ForeignKey(Pays, on_delete=models.CASCADE)
    region = models.ForeignKey(
        Region,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="wilayas",
    )

    def __str__(self):
        return self.nom

    def get_communes(self):
        communes = Commune.objects.filter(wilaya=self)
        communes_list = []
        for commune in communes:
            communes_list.append({"id": commune.id, "nom": commune.nom})

        return communes_list


class Commune(models.Model):
    nom = models.CharField(max_length=255)
    wilaya = models.ForeignKey(Wilaya, on_delete=models.CASCADE)

    def nbr_medecins(self, user):
        return self.medecin_set.filter(
            users__username=user, specialite__in=MEDICAL
        ).count()

    # def nbr_medecins_all(self, user):
    #     if user.is_superuser or user.userprofile.rolee == "CountryManager":
    #         return self.medecin_set.filter(specialite__in=MEDICAL).count()
    #     else:
    #         return self.medecin_set.filter(users__in=[user, *user.userprofile.usersunder.all()]).distinct().count()

    def nbr_medecins_all(self, user):
        if user.is_superuser or user.userprofile.rolee == "CountryManager":
            # Si l'utilisateur est superuser ou CountryManager, retourner tous les médecins ayant la spécialité "MEDICAL" dans cette commune
            return self.medecin_set.filter(specialite__in=MEDICAL).count()
        else:
            # Sinon, ne retourner que les médecins directement associés à cet utilisateur
            return self.medecin_set.filter(users=user).distinct().count()

    def nbr_commercial(self, user):
        return self.medecin_set.filter(
            users__username=user, specialite__in=COMMERCIAL
        ).count()

    def nbr_commercial_all(self, user):
        if user.is_superuser or user.userprofile.rolee == "CountryManager":
            return self.medecin_set.filter(specialite__in=COMMERCIAL).count()
        else:
            return (
                self.medecin_set.filter(
                    users__in=[user, *user.userprofile.usersunder.all()]
                )
                .distinct()
                .count()
            )

    def __str__(self):
        return self.nom


# content = [{'id':1,'nom':'Généraliste'},{'id':2,'nom':'Diabetologue'}]
