from django.core.management.base import BaseCommand
from django.apps import apps
from utils.abstracts import OptimizedImageModel


class Command(BaseCommand):

    help = "Generate optimized WebP images for existing records"

    def handle(self, *args, **options):

        for model in apps.get_models():

            if not issubclass(model, OptimizedImageModel):
                continue

            if model._meta.abstract:
                continue

            self.stdout.write(f"Processing {model.__name__}")

            for instance in model.objects.iterator():

                instance.generate_optimized_images()

            self.stdout.write(
                self.style.SUCCESS(
                    f"{model.__name__} completed."
                )
            )