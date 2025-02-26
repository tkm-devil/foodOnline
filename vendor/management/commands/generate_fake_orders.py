import random
from decimal import Decimal
from django.core.management.base import BaseCommand
from django.utils.timezone import now
from vendor.models import Vendor, Order
from accounts.models import User

class Command(BaseCommand):
    help = "Generate random orders for testing"

    def handle(self, *args, **kwargs):
        vendors = Vendor.objects.all()
        customers = User.objects.filter(role=User.CUSTOMER)  # Select only customers

        if not vendors or not customers:
            self.stdout.write(self.style.ERROR("Ensure you have vendors and customers in the database!"))
            return

        for _ in range(20):  # Generate 20 orders
            vendor = random.choice(list(vendors))
            customer = random.choice(list(customers))
            total_price = round(random.uniform(100, 2000), 2)
            charges = round(total_price * random.uniform(0.05, 0.15), 2)
            received = total_price - charges
            status = random.choice(["Processing", "Completed", "Cancelled"])

            Order.objects.create(
                vendor=vendor,
                customer=customer,
                total_price=Decimal(total_price),
                charges=Decimal(charges),
                received=Decimal(received),
                status=status,
                created_at=now(),
                updated_at=now()
            )

        self.stdout.write(self.style.SUCCESS("✅ 20 random orders inserted successfully!"))
