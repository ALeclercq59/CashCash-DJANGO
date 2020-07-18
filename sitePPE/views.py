from datetime import datetime

from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.views.generic import ListView, DetailView
from .models import Intervention, Controler, Client, Technicien, Assistant, ContratMaintenance

from .forms import ConnexionForm, MaterielForm, ControlerForm, RechercheClientForm, ClientForm, \
    AffecterInterventionForm, RechercheInterventionForm, EditerInterventionForm, StatistiquesForm

from django.db.models import Count

import io
from django.http import FileResponse
from reportlab.pdfgen import canvas


# Create your views here.

def home(request):
    return redirect('connexion')

def connexion(request):
    """Connexion, si l'user a le bon user et le bon mdp on va chercher si il est dans le groupe technicien ou assistant pour après les rediriger sur eurs pages respectifs"""
    error = False

    if request.method == "POST":
        form = ConnexionForm(request.POST)

        if form.is_valid():
            username = form.cleaned_data["username"]
            password = form.cleaned_data["password"]
            user = authenticate(username=username, password=password)  # Nous vérifions si les données sont correctes

            if user:  # Si l'objet renvoyé n'est pas None
                login(request, user)  # nous connectons l'utilisateur

                if user.groups.filter(name='Technicien').exists():
                    technicien1 = Technicien.objects.get(user_id=user.id)
                    return redirect('liste_visites', matricule=technicien1.id)

                if user.groups.filter(name='Assistant').exists():
                    assistant1 = Assistant.objects.get(user_id=user.id)
                    return redirect('accueil', matricule=assistant1.id)

            else: # sinon une erreur sera affichée
                error = True

    else:
        form = ConnexionForm()

    return render(request, 'sitePPE/connexion.html', locals())



def deconnexion(request):
    logout(request)
    return redirect(reverse(connexion))


class Liste_interventions(LoginRequiredMixin, ListView):
    """Retourne l'ensemble des interventions du technicien connecté"""
    login_url = "connexion"
    model = Intervention
    context_object_name = "interventions"
    template_name = "sitePPE/liste_interventions.html"
    paginate_by = 5

    def get_queryset(self):
        return Intervention.objects.filter(matricule_technicien=self.kwargs['matricule']).filter(statut=False)


class LireInterventions(LoginRequiredMixin, DetailView):
    """Retourne l'intervention séléctionné sur la première page"""
    login_url = "connexion"
    context_object_name = "intervention"
    model = Intervention
    template_name = 'sitePPE/lireInter.html'


@login_required(login_url="connexion")
def nb_materielForm(request, matricule, intervention):
    """Demande au technicien combien de matériels il a contrôlé"""
    if request.method == "POST":
        form = MaterielForm(request.POST)

        if form.is_valid():
            nombre = form.cleaned_data['nombre_materiel']
            return redirect('controler', matricule=matricule, intervention=intervention, nombre=nombre, controle=0)

    else:
        form = MaterielForm()

    return render(request, 'sitePPE/nb_materiels.html', locals())


@login_required(login_url="connexion")
def controlerForm(request, matricule, intervention, nombre, controle):
    """Formulaire du contrôle de chaque matériel. Le formulaire demande le numéro de série, le temps passées au contrôle du matériel et le commentaire"""
    error = False
    if request.method == "POST":
        form = ControlerForm(request.POST)
        if form.is_valid():

            controler = Controler()
            controler.numero_intervention = intervention
            controler.numero_serie = form.cleaned_data["numero_serie"]
            controler.temps_passee = form.cleaned_data["temps_passee"]
            controler.commentaires = form.cleaned_data["commentaires"]
            controler.save()
            controle += 1

            if controle == nombre: #Si il a fini ses contrôle on le redirige
                intervention1 = Intervention.objects.get(id=intervention)
                intervention1.statut = True
                intervention1.save()
                return redirect('liste_visites', matricule=matricule)

            else:
                return redirect('controler', matricule=matricule, intervention=intervention, nombre=nombre, controle=controle)
    else:
        form = ControlerForm()
        error = True

    return render(request, 'sitePPE/controle.html', locals())


@login_required(login_url="connexion")
def accueil(request, matricule):
    """Page d'accueil pour les assistants avec un menu pour les différentes autres pages. Montre aussi les contrats des clients arrivant à échéance"""
    request.session['matricule_assistant'] = matricule
    assistant = Assistant.objects.get(id=matricule)
    contrat = ContratMaintenance.objects.filter(numero_client__numero_agence__code_region=assistant.code_region.id)
    cmpt = 0
    dictContrat = {}

    for c in contrat:
        date_echeance = datetime(c.date_echance.year, c.date_echance.month, c.date_echance.day)
        ajd = datetime.now()
        difference = date_echeance - ajd

        if difference.days <= 30:
            cmpt += 1
            dictContrat[c.id] = difference.days

    request.session['contrats'] = dictContrat

    return render(request, 'sitePPE/accueil.html', locals())


@login_required(login_url="connexion")
def contrat(request, matricule):
    """Retournes les différents contrats arrivant à échéance"""
    dictContrat = request.session['contrats']

    return render(request, 'sitePPE/contrats.html', locals())


@login_required(login_url="connexion")
def rechercheFicheClientForm(request, matricule):
    """Formulaire pour rechercher une fiche client demandé"""
    error = False
    if request.method == "POST":
        form = RechercheClientForm(request.POST)

        if form.is_valid():
            numero_client = form.cleaned_data["numero_client"]
            if Client.objects.filter(id=numero_client):
                client = Client.objects.get(id=numero_client)
                return redirect('ficheClientForm', matricule=matricule, numero=client.id)
            else:
                error = True
    else:
        form = RechercheClientForm()

    return render(request, 'sitePPE/rechercheFicheClient.html', locals())


@login_required(login_url="connexion")
def ficheClientForm(request, matricule, numero):
    """Si l'assistant souhaite modifier une fiche client, c'est un formulaire déjà rempli avec les différentes données du client"""
    client = Client.objects.get(id=numero)
    form = ClientForm(request.POST or None, instance=client)

    if form.is_valid():
        nom = form.cleaned_data["nom"]
        prenom = form.cleaned_data["prenom"]
        raison_sociale = form.cleaned_data["raison_sociale"]
        siren = form.cleaned_data["siren"]
        code_ape = form.cleaned_data["code_ape"]
        adresse = form.cleaned_data["adresse"]
        telephone = form.cleaned_data["telephone"]
        fax = form.cleaned_data["fax"]
        email = form.cleaned_data["email"]
        duree_deplacement = form.cleaned_data["duree_deplacement"]
        distance_km = form.cleaned_data["distance_km"]
        numero_agence = form.cleaned_data["raison_sociale"]
        form.save()
        return redirect('rechercheFicheClient', matricule=matricule)

    return render(request, 'sitePPE/ficheClient.html', locals())


@login_required(login_url="connexion")
def rechercheInterClient(request, matricule):
    """Formulaire pour rechercher si un client a déjà une intervention programmée"""
    error = False
    error1 = False
    if request.method == "POST":
        form = RechercheClientForm(request.POST)

        if form.is_valid():
            numero_client = form.cleaned_data["numero_client"]

            if Client.objects.filter(id=numero_client):
                if not Intervention.objects.filter(numero_client_id=numero_client).filter(statut=0):
                    client = Client.objects.get(id=numero_client)
                    return redirect('affecterInterClient', matricule=matricule, numero=client.id, agence=client.numero_agence.id)

                else:
                    error = True

            else:
                error1 = True

    else:
        form = RechercheClientForm()

    return render(request, 'sitePPE/rechercheInterClient.html', locals())


@login_required(login_url="connexion")
def affecterInter(request, matricule, numero, agence):
    """Formulaire pour affecter une intervention à un client"""
    error = False
    statut = False
    client = Client.objects.get(id=numero)
    form = AffecterInterventionForm(request.POST or None)
    form.fields['matricule_technicien'].queryset = Technicien.objects.filter(numero_agence_id=agence)

    if form.is_valid():
        intervention = Intervention()
        intervention.numero_client = client
        intervention.date_visite = form.cleaned_data["date_visite"]
        intervention.heure_visite = form.cleaned_data["heure_visite"]
        intervention.matricule_technicien = form.cleaned_data["matricule_technicien"]
        intervention.save()
        statut = True

        intervention = Intervention.objects.get(numero_client=client, date_visite=form.cleaned_data["date_visite"], heure_visite=form.cleaned_data["heure_visite"], matricule_technicien= form.cleaned_data["matricule_technicien"])
        request.session['intervention'] = intervention.id

    return render(request, 'sitePPE/affecterIntervention.html', locals())


@login_required(login_url="connexion")
def pdfAffecter(request):
    """Générer PDF après l'affectation de l'intervention"""
    id = request.session['intervention']
    return redirect('interventionPDF', id=id)


@login_required(login_url="connexion")
def rechercheIntervention(request, matricule):
    """Rechercher les interventions soit par la date, soit par le technicien ou soit par les deux"""
    error = False
    error1 = False
    error2 = False
    error3 = False

    assistant = Assistant.objects.get(id=matricule)
    form = RechercheInterventionForm(request.POST or None)
    form.fields['numero_technicien'].queryset = Technicien.objects.filter(numero_agence__code_region_id=assistant.code_region)

    if form.is_valid():
        date = form.cleaned_data["date"]
        num_tech = form.cleaned_data['numero_technicien']
        request.session['matricule_assistant'] = matricule

        if date is None and num_tech is None:
            error = True

        if date is not None and num_tech is None:
            if Intervention.objects.filter(date_visite=date):
                request.session['matricule_tech'] = 0
                request.session['year'] = date.year
                request.session['month'] = date.month
                request.session['day'] = date.day
                return redirect('listeIntervention1', matricule=matricule, year=date.year, month=date.month, day=date.day)
            else:
                error1 = True

        if num_tech is not None and date is None:
            request.session['matricule_tech'] = num_tech.id
            request.session['year'] = 0
            if Intervention.objects.filter(matricule_technicien_id=num_tech):
                return redirect('listeIntervention2', matricule=matricule, numero=num_tech.id)
            else:
                error2 = True

        if num_tech is not None and date is not None:
            request.session['matricule_tech'] = num_tech.id
            request.session['year'] = date.year
            request.session['month'] = date.month
            request.session['day'] = date.day
            if Intervention.objects.filter(matricule_technicien_id=num_tech).filter(date_visite=date):
                return redirect('listeIntervention3', matricule=matricule, numero=num_tech.id, year=date.year, month=date.month, day=date.day)
            else:
                error3 = True

    return render(request, 'sitePPE/rechercheIntervention.html', locals())



class Liste_interventions_Date(LoginRequiredMixin, ListView):
    """Liste des interventions par rapport à la date"""
    login_url = "connexion"
    model = Intervention
    context_object_name = "interventions"
    template_name = "sitePPE/liste_interventions_assistant.html"
    paginate_by = 5

    def get_queryset(self):
        date = datetime(year=self.kwargs['year'], month=self.kwargs['month'], day=self.kwargs['day'])
        return Intervention.objects.filter(date_visite=date)


class Liste_interventions_Tech(LoginRequiredMixin, ListView):
    """Liste des interventions par rapport au technicien"""
    login_url = "connexion"
    model = Intervention
    context_object_name = "interventions"
    template_name = "sitePPE/liste_interventions_assistant.html"
    paginate_by = 5

    def get_queryset(self):
        return Intervention.objects.filter(matricule_technicien=self.kwargs['numero']).filter(statut=False)


class Liste_interventions_DateTech(LoginRequiredMixin, ListView):
    """Liste des interventions par rapport à la date et par rapport au technicien"""
    login_url = "connexion"
    model = Intervention
    context_object_name = "interventions"
    template_name = "sitePPE/liste_interventions_assistant.html"
    paginate_by = 5


    def get_queryset(self):
        date = datetime(year=self.kwargs['year'], month=self.kwargs['month'], day=self.kwargs['day'])
        return Intervention.objects.filter(matricule_technicien=self.kwargs['numero']).filter(statut=False).filter(date_visite=date)



@login_required(login_url="connexion")
def supprimerIntervention(request, id):
    """Pour supprimer l'intervention choisi"""
    Intervention.objects.filter(id=id).delete()

    if request.session['year'] is not None and request.session['matricule_tech'] == 0:
        year = request.session['year']
        month = request.session['month']
        day = request.session['day']
        matricule = request.session.get('matricule_assistant')
        return redirect('listeIntervention1', matricule=matricule, year=year, month=month, day=day)

    if request.session['year'] == 0 and request.session['matricule_tech'] != 0:
        matricule = request.session.get('matricule_assistant')
        num_tech = request.session['matricule_tech']
        return redirect('listeIntervention2', matricule=matricule, numero=num_tech)

    if request.session['year'] != 0 and request.session['matricule_tech'] != 0:
        year = request.session['year']
        month = request.session['month']
        day = request.session['day']
        matricule = request.session.get('matricule_assistant')
        num_tech = request.session['matricule_tech']
        return redirect('listeIntervention3', matricule=matricule, numero=num_tech, year=year, month=month, day=day)


@login_required(login_url="connexion")
def editerIntervention(request, id, numero_client):
    """Pour éditer l'intervention choisi"""
    intervention = Intervention.objects.get(id=id)
    client = Client.objects.get(id=numero_client)
    date = intervention.date_visite
    date1 = str(date.year) + "-" + str(date.month) + "-" + str(date.day)
    form = EditerInterventionForm(request.POST or None, instance=intervention)
    form.fields['matricule_technicien'].queryset = Technicien.objects.filter(numero_agence_id=client.numero_agence.id)
    form.fields['numero_client'].queryset = Client.objects.filter(id=numero_client)

    if form.is_valid():
        numero_client = form.cleaned_data["numero_client"]
        matricule_technicien = form.cleaned_data["matricule_technicien"]
        date_visite = form.cleaned_data["date_visite"]
        heure_visite = form.cleaned_data["heure_visite"]
        form.save()

        if request.session['year'] is not None and request.session['matricule_tech'] == 0:
            year = request.session['year']
            month = request.session['month']
            day = request.session['day']
            matricule = request.session.get('matricule_assistant')
            return redirect('listeIntervention1', matricule=matricule, year=year, month=month, day=day)

        if request.session['year'] == 0 and request.session['matricule_tech'] != 0:
            matricule = request.session.get('matricule_assistant')
            num_tech = request.session['matricule_tech']
            return redirect('listeIntervention2', matricule=matricule, numero=num_tech)

        if request.session['year'] != 0 and request.session['matricule_tech'] != 0:
            year = request.session['year']
            month = request.session['month']
            day = request.session['day']
            matricule = request.session.get('matricule_assistant')
            num_tech = request.session['matricule_tech']
            return redirect('listeIntervention3', matricule=matricule, numero=num_tech, year=year, month=month, day=day)

    return render(request, 'sitePPE/EditerIntervention.html', locals())


@login_required(login_url="connexion")
def retourAccueil(request):
    """Pour retourner à l'accueil"""
    return redirect('accueil', matricule=request.session['matricule_assistant'])


@login_required(login_url="connexion")
def interventionPDF(request, id):
    """Pour générer le PDF de l'intervention grâce à l'id de l'intervention"""
    intervention = Intervention.objects.get(id=id)

    # Create a file-like buffer to receive PDF data.
    buffer = io.BytesIO()

    # Create the PDF object, using the buffer as its "file."
    p = canvas.Canvas(buffer)

    # Draw things on the PDF. Here's where the PDF generation happens.
    # See the ReportLab documentation for the full list of functionality.
    p.drawString(260, 750, "Fiche Intervention")

    p.drawString(50, 700, "N° Intervention :")
    p.drawString(140, 700, str(intervention.id))

    p.drawString(50, 660, "Technicien : ")
    p.drawString(120, 660, str(intervention.matricule_technicien))

    p.drawString(50, 620, "Client : ")
    p.drawString(95, 620, str(intervention.numero_client))
    p.drawString(50, 600, "Adresse : ")
    p.drawString(108, 600, str(intervention.numero_client.adresse))
    p.drawString(50, 580, "Téléphone : ")
    p.drawString(118, 580, str(intervention.numero_client.telephone))
    p.drawString(50, 560, "Email : ")
    p.drawString(95, 560, str(intervention.numero_client.email))

    p.drawString(50, 520, "Date de la visite :")
    p.drawString(150, 520, str(intervention.date_visite.day) + "/" + str(intervention.date_visite.month) + "/" + str(intervention.date_visite.year))
    p.drawString(50, 500, "Heure de la visite :")
    p.drawString(155, 500, str(intervention.heure_visite.hour) + "h" + str(intervention.heure_visite.minute))



    # Close the PDF object cleanly, and we're done.
    p.showPage()
    p.save()

    filename = "Fiche Intervention N°" + str(intervention.id) + " .pdf"
    # FileResponse sets the Content-Disposition header so that browsers
    # present the option to save the file.
    buffer.seek(0)
    return FileResponse(buffer, as_attachment=True, filename=filename)


@login_required(login_url="connexion")
def rechercheStat(request, matricule):
    """Pour chercher les statistiques d'un technicien pour un mois donnée"""
    global mois2
    form = StatistiquesForm(request.POST or None)
    assistant = Assistant.objects.get(id=matricule)
    form.fields['technicien'].queryset = Technicien.objects.filter(numero_agence__code_region_id=assistant.code_region)

    if form.is_valid():
        technicien = form.cleaned_data["technicien"]
        date = form.cleaned_data["date"]
        mois = date.split(' ')
        mois1 = mois[0]
        annee = mois[1]

        switcher = {
            'Janvier': 1,
            'Février': 2,
            'Mars': 3,
            'Avril': 4,
            'Mai': 5,
            'Juin': 6,
            'Juillet': 7,
            'Août': 8,
            'Septembre': 9,
            'Octobre': 10,
            'Novembre': 11,
            'Décembre': 12,
        }
        mois2 = switcher.get(mois1)
        request.session['moisl'] = mois1
        return redirect('stat', matricule=matricule, numero=technicien.id, mois=mois2, annee=annee)

    return render(request, 'sitePPE/rechercheStatistiques.html', locals())




@login_required(login_url="connexion")
def stat(request, matricule, numero, mois, annee):
    """Montrer les statistiques du technicien pour un mois donnée"""
    technicien = Technicien.objects.get(id=numero)
    intervention = Intervention.objects.filter(date_visite__contains=mois).filter(date_visite__contains=annee).filter(statut=1)
    nb_inter = Intervention.objects.filter(date_visite__contains=mois).filter(date_visite__contains=annee).filter(statut=1).aggregate(Count('id'))
    moislettre = request.session['moisl']
    min = 0
    distance_km = 0

    for inter in intervention:
        controler = Controler.objects.filter(numero_intervention=inter.id)
        for c in controler:
            temps = c.temps_passee.split(':')
            min = min + int(temps[0]) * 60
            min = min + int(temps[1])

        distance_km = distance_km + inter.numero_client.distance_km

    heure = min // 60
    min = min % 60
    return render(request, 'sitePPE/statistiques.html', locals())
