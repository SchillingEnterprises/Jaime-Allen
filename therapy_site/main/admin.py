from django.contrib import admin
from .models import Service, ClientInteraction, AIConfig

@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ['title', 'service_type', 'order', 'is_active']
    list_editable = ['order', 'is_active']
    prepopulated_fields = {'slug': ('title',)}

@admin.register(ClientInteraction)
class ClientInteractionAdmin(admin.ModelAdmin):
    list_display = ['session_id', 'timestamp']
    readonly_fields = ['timestamp']

@admin.register(AIConfig)
class AIConfigAdmin(admin.ModelAdmin):
    list_display = ['name', 'is_enabled']
