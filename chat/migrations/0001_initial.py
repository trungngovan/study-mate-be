# Generated manually for chat app

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('matching', '0002_remove_mutual_conversation_states'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Conversation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('last_message_at', models.DateTimeField(blank=True, db_index=True, help_text='Timestamp of the last message in this conversation', null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('connection', models.OneToOneField(db_column='connection_id', help_text='Link to the connection between two users', on_delete=django.db.models.deletion.CASCADE, related_name='conversation', to='matching.connection')),
            ],
            options={
                'verbose_name': 'Conversation',
                'verbose_name_plural': 'Conversations',
                'db_table': 'conversations',
                'ordering': ['-last_message_at', '-created_at'],
                'indexes': [
                    models.Index(fields=['-last_message_at'], name='idx_conv_last_msg'),
                    models.Index(fields=['created_at'], name='idx_conv_created'),
                ],
            },
        ),
        migrations.CreateModel(
            name='Message',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('content', models.TextField(help_text='Message content')),
                ('read_at', models.DateTimeField(blank=True, db_index=True, help_text='Timestamp when the message was read', null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('conversation', models.ForeignKey(db_column='conversation_id', help_text='The conversation this message belongs to', on_delete=django.db.models.deletion.CASCADE, related_name='messages', to='chat.conversation')),
                ('sender', models.ForeignKey(db_column='sender_id', help_text='User who sent the message', on_delete=django.db.models.deletion.CASCADE, related_name='sent_messages', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Message',
                'verbose_name_plural': 'Messages',
                'db_table': 'messages',
                'ordering': ['created_at'],
                'indexes': [
                    models.Index(fields=['conversation', '-created_at'], name='idx_msg_conv_created'),
                    models.Index(fields=['sender', '-created_at'], name='idx_msg_sender_created'),
                    models.Index(fields=['conversation', 'read_at'], name='idx_msg_conv_read'),
                ],
            },
        ),
    ]


