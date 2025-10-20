from django.db import models


class Service(models.Model):
    SERVICE_TYPES = [
        ('conflict_resolution', 'Conflict Resolution'),
        ('renewing_connections', 'Renewing Connections'),
        ('relationship_stages', 'Relationship Stages'),
        ('serenity', 'Finding Serenity'),
        ('effective_communication', 'Effective Communication'),
    ]

    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    description = models.TextField()
    service_type = models.CharField(max_length=25, choices=SERVICE_TYPES)  # Increased to 25
    icon = models.CharField(max_length=100, default='❤️')
    ai_optimized_content = models.JSONField(default=dict, blank=True)
    is_active = models.BooleanField(default=True)
    order = models.IntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return self.title


class ClientInteraction(models.Model):
    session_id = models.CharField(max_length=100)
    message = models.TextField()
    sentiment = models.JSONField(null=True, blank=True)
    ai_response = models.TextField(blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']


class AIConfig(models.Model):
    name = models.CharField(max_length=100)
    is_enabled = models.BooleanField(default=True)
    config_data = models.JSONField(default=dict)

    def __str__(self):
        return self.name
