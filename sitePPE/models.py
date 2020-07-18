from django.contrib.auth.models import User
from django.db import models

# Create your models here.

class Region(models.Model):
    nom = models.CharField(max_length=30)

    def __str__(self):
        return self.nom


class Agence(models.Model):
    nom = models.CharField(max_length=30)
    adresse = models.TextField()
    telephone = models.CharField(max_length=10)
    fax = models.CharField(max_length=30)
    code_region = models.ForeignKey('Region', on_delete=models.CASCADE)

    def __str__(self):
        return self.nom


class Technicien(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    nom = models.CharField(max_length=30)
    prenom = models.CharField(max_length=30)
    adresse = models.TextField()
    date_embauche = models.DateTimeField(verbose_name="Date d'embauche")
    telephone = models.CharField(max_length=10)
    qualification = models.CharField(max_length=30)
    date_obtention = models.DateTimeField(verbose_name="Date d'obtention")
    numero_agence = models.ForeignKey('Agence', on_delete=models.CASCADE)

    def __str__(self):
        return self.nom + " " + self.prenom


class Assistant(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    nom = models.CharField(max_length=30)
    prenom = models.CharField(max_length=30)
    adresse = models.TextField()
    date_embauche = models.DateTimeField(verbose_name="Date d'embauche")
    code_region = models.ForeignKey('Region', on_delete=models.CASCADE)

    def __str__(self):
        return self.nom + " " + self.prenom


class Client(models.Model):
    nom = models.CharField(max_length=30)
    prenom = models.CharField(max_length=30)
    raison_sociale = models.CharField(max_length=30, verbose_name="Raison Sociale")
    siren = models.CharField(max_length=30)
    code_ape = models.CharField(max_length=30, verbose_name="Code APE")
    adresse = models.TextField()
    telephone = models.CharField(max_length=10)
    fax = models.CharField(max_length=30)
    email = models.CharField(max_length=50)
    duree_deplacement = models.IntegerField(verbose_name="Durée de déplacement")
    distance_km = models.IntegerField(verbose_name="Distance en km")
    numero_agence = models.ForeignKey('Agence', on_delete=models.CASCADE, verbose_name="Agence")

    def __str__(self):
        return self.nom + " " + self.prenom


class Intervention(models.Model):
    date_visite = models.DateField(verbose_name="Date de la visite")
    heure_visite = models.TimeField(verbose_name="Heure de la visite")
    matricule_technicien = models.ForeignKey('Technicien', on_delete=models.CASCADE, verbose_name='Technicien')
    numero_client = models.ForeignKey('Client', on_delete=models.CASCADE, verbose_name='Client')
    statut = models.BooleanField(default=False,)

    class Meta:
        ordering = ['date_visite', 'heure_visite']


class TypeContrat(models.Model):
    delai_intervention = models.CharField(max_length=50, verbose_name="Délai d'intervention")
    taux_applicable = models.DecimalField(max_digits=5, decimal_places=2, verbose_name="Taux applicable")

    def __str__(self):
        return str(self.id)

class ContratMaintenance(models.Model):
    date_signature = models.DateField(verbose_name="Date de la signature")
    date_echance = models.DateField(verbose_name="Date Echeance")
    numero_client = models.ForeignKey('Client', on_delete=models.CASCADE, verbose_name='Client')
    type_contrat = models.ForeignKey('TypeContrat', on_delete=models.CASCADE)

    def __str__(self):
        return str(self.id)


class FamilleProduit(models.Model):
    libelle = models.CharField(max_length=50)

    def __str__(self):
        return self.libelle


class TypeMateriel(models.Model):
    libelle = models.CharField(max_length=50)
    code_famille = models.ForeignKey('FamilleProduit', on_delete=models.CASCADE)

    def __str__(self):
        return self.libelle


class Materiel(models.Model):
    prix_de_vente = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Prix de vente")
    date_de_vente = models.DateTimeField(verbose_name="Date de la vente")
    date_installation = models.DateTimeField(verbose_name="Date de l'installation")
    emplacement = models.CharField(max_length=50)
    type_materiel = models.ForeignKey('TypeMateriel', on_delete=models.CASCADE)

    def __str__(self):
        return self.id


class Controler(models.Model):
    numero_serie = models.IntegerField(verbose_name="Numéro de série")
    numero_intervention = models.IntegerField(verbose_name="Numéro d'intervention")
    temps_passee = models.CharField(max_length=30, verbose_name="Temps passées")
    commentaires = models.TextField()

    def __str__(self):
        return self.id


