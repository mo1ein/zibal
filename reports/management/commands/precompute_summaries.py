from django.core.management.base import BaseCommand

from reports.services.aggregations import build_and_store_summary


class Command(BaseCommand):
    help = "Compute transaction_summary from transactions collection and upsert into transaction_summary."

    def handle(self, *args, **options):
        self.stdout.write("Starting transaction.bin summary build...")
        build_and_store_summary()
        self.stdout.write(self.style.SUCCESS("transaction_summary build completed."))
