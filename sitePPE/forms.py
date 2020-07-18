from django import forms

from .models import Client, Intervention, Technicien


class ConnexionForm(forms.Form):
    username = forms.CharField(label="Nom d'utilisateur", max_length=30)
    password = forms.CharField(label="Mot de passe", widget=forms.PasswordInput)


class MaterielForm(forms.Form):
    nombre_materiel = forms.IntegerField(label="Matériel(s) vérifié(s) durant la visite effectuée :")


class ControlerForm(forms.Form):
    numero_serie = forms.IntegerField(label="Numéro de série")
    temps_passee = forms.CharField(label="Temps passées (hh:mm)", widget=forms.TimeInput(attrs={'type': 'time'}))
    commentaires = forms.CharField(widget=forms.Textarea, label="Commentaires")


class RechercheClientForm(forms.Form):
    numero_client = forms.IntegerField(label="Numéro du client :")


class ClientForm(forms.ModelForm):
    class Meta:
        model = Client
        fields = '__all__'


class AffecterInterventionForm(forms.ModelForm):
    class Meta:
        model = Intervention
        exclude = ('numero_client', 'statut')
        widgets = {
            'date_visite' : forms.DateInput(attrs={'class' : 'datetime-input'}),
            'heure_visite' : forms.TimeInput(attrs={'type' : 'time'}),
        }


class RechercheInterventionForm(forms.Form):
    date = forms.DateField(label='Date', required=False, widget=forms.DateInput(attrs={'class':'datetime-input'}))
    numero_technicien = forms.ModelChoiceField(label='Technicien', required=False, queryset=Technicien.objects.all())


class EditerInterventionForm(forms.ModelForm):
    class Meta:
        model = Intervention
        fields = ('numero_client', 'matricule_technicien', 'date_visite', 'heure_visite')
        widgets = {
            'date_visite': forms.DateInput(attrs={'class': 'datetime-input'}),
            'heure_visite': forms.TimeInput(attrs={'type': 'time'}),
        }


class StatistiquesForm(forms.Form):
    technicien = forms.ModelChoiceField(label='Technicien', queryset=Technicien.objects.all())
    date = forms.CharField(label="Choisissez le mois et l'année", widget=forms.DateInput(attrs={'class': 'datetime-input'}))


