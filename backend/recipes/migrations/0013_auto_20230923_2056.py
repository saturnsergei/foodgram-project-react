# Generated by Django 3.2.3 on 2023-09-23 20:56

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0012_rename_tags_tag'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='Ingredients',
            new_name='Ingredient',
        ),
        migrations.RenameModel(
            old_name='IngredientsAmount',
            new_name='IngredientAmount',
        ),
    ]
