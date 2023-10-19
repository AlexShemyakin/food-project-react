import csv
import os

from django.core.management.base import BaseCommand
from django.conf import settings

from recipes.models import Ingredient


class Command(BaseCommand):
    help = 'Import ingridients to database from csv file'

    def handle(self, *args, **kwargs):
        path_to_file = os.path.join(
            settings.BASE_DIR.parent,
            'data/',
            'ingredients.csv'
        )

        with open(path_to_file) as f:
            rows = csv.DictReader(f, fieldnames=['name', 'measurement_unit'])
            for row in rows:
                Ingredient.objects.get_or_create(**row)
