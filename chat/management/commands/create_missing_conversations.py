from django.core.management.base import BaseCommand
from matching.models import Connection
from chat.models import Conversation


class Command(BaseCommand):
    help = 'Create conversations for all accepted connections that don\'t have one'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be created without actually creating',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        
        # Get all connections that don't have a conversation
        connections_without_conversation = Connection.objects.filter(
            conversation__isnull=True
        ).select_related('user1', 'user2', 'connection_request')
        
        count = connections_without_conversation.count()
        
        if count == 0:
            self.stdout.write(
                self.style.SUCCESS('All connections already have conversations!')
            )
            return
        
        self.stdout.write(
            self.style.WARNING(
                f'Found {count} connection(s) without conversation'
            )
        )
        
        if dry_run:
            self.stdout.write(
                self.style.NOTICE('DRY RUN - No changes will be made')
            )
            for connection in connections_without_conversation:
                self.stdout.write(
                    f'  Would create conversation for: '
                    f'{connection.user1.full_name} <-> {connection.user2.full_name}'
                )
            return
        
        # Create conversations
        created_count = 0
        for connection in connections_without_conversation:
            try:
                conversation = Conversation.objects.create(
                    connection=connection
                )
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(
                        f'✓ Created conversation #{conversation.id} for: '
                        f'{connection.user1.full_name} <-> {connection.user2.full_name}'
                    )
                )
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(
                        f'✗ Failed to create conversation for connection #{connection.id}: {e}'
                    )
                )
        
        self.stdout.write(
            self.style.SUCCESS(
                f'\nSuccessfully created {created_count} conversation(s)!'
            )
        )


