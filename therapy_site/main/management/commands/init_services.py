from django.core.management.base import BaseCommand

from main.models import Service


class Command(BaseCommand):
    help = 'Initialize default services'

    def handle(self, *args, **options):
        services = [
            {
                'title': 'Conflict Resolution',
                'slug': 'conflict-resolution',
                'description': 'Learn effective strategies to resolve conflicts with empathy and understanding.',
                'service_type': 'conflict_resolution',
                'icon': '⚡',
                'order': 1
            },
            {
                'title': 'Renewing Connections',
                'slug': 'renewing-connections',
                'description': 'Rediscover and strengthen emotional connections in your relationships.',
                'service_type': 'renewing_connections',
                'icon': '💞',
                'order': 2
            },
            {
                'title': 'Relationship Stages',
                'slug': 'relationship-stages',
                'description': 'Navigate through different relationship stages with confidence and understanding.',
                'service_type': 'relationship_stages',
                'icon': '📈',
                'order': 3
            },
            {
                'title': 'Finding Serenity',
                'slug': 'finding-serenity',
                'description': 'Achieve peace and balance in your relationships through mindfulness and acceptance.',
                'service_type': 'serenity',
                'icon': '☮️',
                'order': 4
            },
            {
                'title': 'Effective Communication',
                'slug': 'effective-communication',
                'description': 'Explore educational exercises for clearer, more thoughtful communication.',
                'service_type': 'effective_communication',
                'icon': '🗣️',
                'order': 5
            },
        ]

        for service_data in services:
            service, created = Service.objects.get_or_create(
                slug=service_data['slug'],
                defaults=service_data,
            )
            result = 'Created' if created else 'Kept existing'
            self.stdout.write(
                self.style.SUCCESS(f'{result} service: {service.title}')
            )
