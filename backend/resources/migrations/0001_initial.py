# Generated by Django 5.1.3 on 2024-12-02 12:09

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('assessment', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Resource',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('resource_type', models.CharField(choices=[('syllabus', 'syllabus'), ('slides', 'slides'), ('handwritten note', 'handwritten note'), ('textbook', 'textbook'), ('past exam', 'past exam')], max_length=50)),
                ('title', models.CharField(max_length=255)),
                ('is_scanned', models.BooleanField(default=False)),
                ('resource_pdf_file', models.FileField(upload_to='resources/')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('assessment', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='resources', to='assessment.assessment')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
