# Generated by Django 5.1.6 on 2025-04-03 23:44

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('authors', '0002_remove_foreignpostlike_foreign_authors_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='foreigncomment',
            name='post',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='foreign_comments', to='authors.foreignpost'),
        ),
    ]
