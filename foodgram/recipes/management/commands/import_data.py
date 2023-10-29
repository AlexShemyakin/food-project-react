import csv
import os

from django.core.management.base import BaseCommand
from django.conf import settings
from django.db.utils import IntegrityError

from recipes.models import Ingredient, Tag


class Command(BaseCommand):
    help = 'Import ingridients and tags to database from csv file'

    def handle(self, *args, **kwargs):
        path_to_file = os.path.join(
            settings.BASE_DIR,
            'data/',
            'ingredients.csv'
        )

        with open(path_to_file) as f:
            rows = csv.DictReader(f, fieldnames=['name', 'measurement_unit'])
            for row in rows:
                try:
                    Ingredient.objects.get_or_create(**row)
                except IntegrityError:
                    continue

        path_to_file = os.path.join(
            settings.BASE_DIR,
            'data/',
            'tags.csv'
        )

        with open(path_to_file) as f:
            rows = csv.DictReader(f, fieldnames=['name', 'slug', 'color'])
            for row in rows:
                try:
                    Tag.objects.get_or_create(**row)
                except IntegrityError:
                    continue
