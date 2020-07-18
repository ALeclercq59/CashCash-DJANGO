from django.conf.urls import url
from django.contrib import admin
from django.urls import path

from . import views

urlpatterns = [
    path('', views.home),
    url('connexion$', views.connexion, name='connexion'),
    url('deconnexion$', views.deconnexion, name='deconnexion'),
    path("technicien/<int:matricule>/", views.Liste_interventions.as_view(), name='liste_visites'),
    url(r'^intervention/(?P<pk>\d+)$', views.LireInterventions.as_view(), name='lire_visite'),
    path('materiel/<int:matricule>/<int:intervention>/', views.nb_materielForm, name='nb_materiel'),
    path('controle/<int:matricule>/<int:intervention>/<int:nombre>/<int:controle>', views.controlerForm, name='controler'),
    path('accueil/<int:matricule>/', views.accueil, name='accueil'),
    path('accueil1/', views.retourAccueil, name='accueil1'),
    path('fiche_client/<int:matricule>/', views.rechercheFicheClientForm, name='rechercheFicheClient'),
    path('fiche_client/<int:matricule>/<int:numero>/', views.ficheClientForm, name='ficheClientForm'),
    path('affecter_intervention/<int:matricule>/', views.rechercheInterClient, name='rechercheInterClient'),
    path('affecter_intervention/<int:matricule>/<int:numero>/<int:agence>', views.affecterInter, name='affecterInterClient'),
    path('consulter_intervention/<int:matricule>/', views.rechercheIntervention, name="consulterIntervention"),
    path('consulter_intervention/<int:matricule>/<int:year>/<int:month>/<int:day>', views.Liste_interventions_Date.as_view(), name="listeIntervention1"),
    path('consulter_intervention/<int:matricule>/<int:numero>', views.Liste_interventions_Tech.as_view(), name="listeIntervention2"),
    path('consulter_intervention/<int:matricule>/<int:numero>/<int:year>/<int:month>/<int:day>', views.Liste_interventions_DateTech.as_view(), name="listeIntervention3"),
    path('supprimer_intervention/<int:id>', views.supprimerIntervention, name='supprimerIntervention'),
    path('editer_intervention/<int:id>/<int:numero_client>', views.editerIntervention, name='editerIntervention'),
    path('interventionPDF/<int:id>', views.interventionPDF, name="interventionPDF"),
    path('statistiques/<int:matricule>', views.rechercheStat, name='rechercheStat'),
    path('statistiques/<int:matricule>/<int:numero>/<int:mois>/<int:annee>', views.stat, name='stat'),
    path('contrats/<int:matricule>', views.contrat, name="contrats"),
    path('pdfAffecter/', views.pdfAffecter, name="pdfAffecter"),
]