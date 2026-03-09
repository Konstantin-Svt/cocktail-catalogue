from django.core.management import BaseCommand, call_command

from cocktail.models import Cocktail


class Command(BaseCommand):
    def handle(self, *args, **options):
        if Cocktail.objects.exists():
            return

        call_command("loaddata", "fixtures/data.json")
        self.stdout.write(self.style.SUCCESS("Successfully loaded sample data"))
