# Generated by Django 3.2.3 on 2023-09-23 20:52

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0011_delete_tagsrecipe'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='Tags',
            new_name='Tag',
        ),
    ]
