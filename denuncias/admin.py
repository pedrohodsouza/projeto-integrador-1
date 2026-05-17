from django.contrib import admin
from .models import Denuncia

@admin.register(Denuncia)
class DenunciaAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'categoria', 'status', 'anonimo', 'cidade', 'zona', 'criado_em')
    list_filter = ('categoria', 'status', 'anonimo', 'cidade', 'zona', 'criado_em')
    search_fields = ('titulo', 'descricao', 'cep', 'endereco', 'bairro', 'cidade', 'zona', 'localizacao')
    list_editable = ('status',)
    readonly_fields = ('criado_em', 'atualizado_em', 'localizacao')
    fieldsets = (
        ('Informações da Denúncia', {
            'fields': ('titulo', 'categoria', 'descricao', 'foto', 'anonimo')
        }),
        ('Endereço da Ocorrência', {
            'fields': ('cep', 'endereco', 'numero', 'bairro', 'cidade', 'estado', 'zona', 'latitude', 'longitude', 'localizacao')
        }),
        ('Controle da Gestão', {
            'fields': ('status', 'resposta_gestor')
        }),
        ('Metadados', {
            'fields': ('criado_em', 'atualizado_em'),
            'classes': ('collapse',),
        }),
    )

