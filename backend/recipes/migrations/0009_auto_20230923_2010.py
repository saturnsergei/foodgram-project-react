# Generated by Django 3.2.3 on 2023-09-23 20:10

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0008_auto_20230920_1821'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='ingredientsamount',
            options={'verbose_name': 'Количество', 'verbose_name_plural': 'Количество'},
        ),
        migrations.AlterModelOptions(
            name='recipes',
            options={'ordering': ('-date_create',), 'verbose_name': 'Рецепт', 'verbose_name_plural': 'Рецепты'},
        ),
        migrations.AddField(
            model_name='recipes',
            name='date_create',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now, verbose_name='Дата создания'),
            preserve_default=False,
        ),
    ]
