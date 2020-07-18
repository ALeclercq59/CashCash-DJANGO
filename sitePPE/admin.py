from django.contrib import admin

from .models import Client, Region, Agence, Intervention, Technicien, Assistant, TypeContrat, ContratMaintenance


# Register your models here.

class RegionAdmin(admin.ModelAdmin):
    list_display = ('nom', )
    search_fields = ('nom',)


class AgenceAdmin(admin.ModelAdmin):
    list_display = ('nom', 'adresse', 'telephone', 'fax', 'code_region')
    search_fields = ('nom',)


class ClientAdmin(admin.ModelAdmin):
    list_display = ('id', 'nom', 'prenom', 'numero_agence')
    search_fields = ('id', 'nom', 'prenom')


class InterventionAdmin(admin.ModelAdmin):
    list_display = ('id', 'date_visite', 'heure_visite', 'matricule_technicien', 'numero_client', 'statut')
    search_fields = ('id', 'date_visite', 'heure_visite', 'matricule_technicien', 'numero_client')


class TechnicienAdmin(admin.ModelAdmin):
    list_display = ('id', 'nom', 'prenom', 'numero_agence')
    search_fields = ('id', 'nom', 'prenom',)


class AssistantAdmin(admin.ModelAdmin):
    list_display = ('id', 'nom', 'prenom', 'code_region')
    search_fields = ('id', 'nom', 'prenom',)


class TypeContratAdmin(admin.ModelAdmin):
    list_display = ('id', 'delai_intervention', 'taux_applicable')
    search_fields = ('id', 'delai_intervention', 'taux_applicable')


class ContratMaintenanceAdmin(admin.ModelAdmin):
    list_display = ('id', 'numero_client', 'date_signature', 'date_echance', 'type_contrat')
    search_fields = ('id', 'numero_client', 'date_signature', 'date_echance', 'type_contrat')


admin.site.register(Client, ClientAdmin)
admin.site.register(Region, RegionAdmin)
admin.site.register(Agence, AgenceAdmin)
admin.site.register(Intervention, InterventionAdmin)
admin.site.register(Technicien, TechnicienAdmin)
admin.site.register(Assistant, AssistantAdmin)
admin.site.register(TypeContrat, TypeContratAdmin)
admin.site.register(ContratMaintenance, ContratMaintenanceAdmin)