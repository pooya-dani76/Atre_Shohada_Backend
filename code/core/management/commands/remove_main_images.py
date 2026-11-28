
from pathlib import PurePosixPath

from django.apps import apps
from django.core.management.base import BaseCommand
from PIL import Image


class Command(BaseCommand):
    help = "Switch existing ImageFields to WebP and optionally delete originals."

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Only show what would happen without changing anything.",
        )

        parser.add_argument(
            "--keep-originals",
            action="store_true",
            help="Update database paths but keep original files.",
        )

    def is_valid_image(self, storage, name):
        """Check whether the WebP file exists and is readable."""
        if not storage.exists(name):
            return False

        try:
            with storage.open(name, "rb") as file:
                with Image.open(file) as image:
                    if image.format != "WEBP":
                        return False
                    image.verify()

            return True

        except Exception as exc:
            self.stderr.write(
                self.style.WARNING(
                    f"Invalid WebP: {name} ({exc})"
                )
            )
            return False

    def is_referenced(self, filename):
        """Check whether any model still references this file."""

        for model in apps.get_models():

            if model._meta.proxy:
                continue

            for field in model._meta.local_fields:

                from django.db import models

                if not isinstance(field, models.ImageField):
                    continue

                if model._base_manager.filter(
                    **{field.name: filename}
                ).exists():
                    return True

        return False

    def handle(self, *args, **options):
        dry_run = options["dry_run"]
        keep_originals = options["keep_originals"]

        candidates = set()

        converted = 0
        skipped = 0
        failed = 0

        if dry_run:
            self.stdout.write(
                self.style.WARNING("DRY RUN: No changes will be made.")
            )

        for model in apps.get_models():

            if model._meta.proxy:
                continue

            image_fields = [
                field
                for field in model._meta.local_fields
                if self.is_image_field(field)
            ]

            if not image_fields:
                continue

            self.stdout.write(
                f"\nProcessing {model._meta.label}"
            )

            for instance in model._base_manager.iterator():

                for field in image_fields:

                    image = getattr(instance, field.name)

                    if not image or not image.name:
                        continue

                    original_name = image.name

                    if original_name.lower().endswith(".webp"):
                        skipped += 1
                        continue

                    webp_name = str(
                        PurePosixPath(original_name).with_suffix(".webp")
                    )

                    storage = field.storage

                    if not self.is_valid_image(storage, webp_name):
                        self.stderr.write(
                            self.style.WARNING(
                                f"Skipped: {model.__name__}.{field.name} "
                                f"-> {webp_name}"
                            )
                        )
                        failed += 1
                        continue

                    self.stdout.write(
                        f"{original_name} -> {webp_name}"
                    )

                    if dry_run:
                        converted += 1
                        continue

                    updated = model._base_manager.filter(
                        pk=instance.pk,
                        **{field.name: original_name},
                    ).update(**{field.attname: webp_name})

                    if not updated:
                        self.stderr.write(
                            self.style.WARNING(
                                f"Database update failed: {original_name}"
                            )
                        )
                        failed += 1
                        continue

                    candidates.add((storage, original_name))
                    converted += 1

        # Delete originals only after all database updates.
        deleted = 0

        if not dry_run and not keep_originals:

            self.stdout.write("\nChecking original files...")

            for storage, original_name in candidates:

                if self.is_referenced(original_name):
                    self.stdout.write(
                        self.style.WARNING(
                            f"Still referenced, keeping: {original_name}"
                        )
                    )
                    continue

                if storage.exists(original_name):
                    storage.delete(original_name)
                    deleted += 1

        self.stdout.write("\n========== Summary ==========")
        self.stdout.write(f"Converted: {converted}")
        self.stdout.write(f"Skipped: {skipped}")
        self.stdout.write(f"Failed: {failed}")

        if dry_run:
            self.stdout.write(
                self.style.WARNING(
                    "Dry run completed. No files or database records changed."
                )
            )
        elif keep_originals:
            self.stdout.write(
                self.style.SUCCESS(
                    "Database updated. Original files were kept."
                )
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(
                    f"Original files deleted: {deleted}"
                )
            )

    @staticmethod
    def is_image_field(field):
        from django.db import models
        return isinstance(field, models.ImageField)
