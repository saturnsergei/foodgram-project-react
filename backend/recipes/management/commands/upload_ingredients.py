import os
from csv import DictReader

from django.core.management import BaseCommand

from recipes.models import Ingredient
from foodgram_backend.settings import STATIC_ROOT


class Command(BaseCommand):
    help = 'Загрузка ингредиентов из csv-файла'

    def add_arguments(self, parser):
        parser.add_argument("file_name", type=str)

    def handle(self, *args, **options):
        file_path = os.path.join(
            STATIC_ROOT, 'data/', options['file_name'])

        self.stdout.write('Загрузка csv-файла')
        with open(file_path, 'r', encoding='utf-8') as csv_file:
            csv_data = DictReader(csv_file, ['name', 'measurement_unit'])
            ingredients = []
            for row in csv_data:

                ingredient = Ingredient(
                    name=row['name'],
                    measurement_unit=row['measurement_unit']
                )
                ingredients.append(ingredient)

            Ingredient.objects.bulk_create(ingredients)
            self.stdout.write(
                self.style.SUCCESS('Загрузка завершена')
            )
