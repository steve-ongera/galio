import random
import string
from decimal import Decimal

from django.core.management.base import BaseCommand
from django.utils.text import slugify
from django.db import transaction

from ecommerce.models import Product, Category, Brand


# ---------- util helpers ----------
def random_sku(prefix: str = "SKU") -> str:
    suffix = "".join(random.choices(string.ascii_uppercase + string.digits, k=6))
    return f"{prefix}-{suffix}"


def money(val) -> Decimal:
    return Decimal(f"{val:.2f}")


# ---------- product seed data ----------
PRODUCT_DATA = [
    {"name": "Apple MacBook Air M3", "category": "Laptops", "brand": "Apple", "price": 1299, "compare_price": 1499, "stock": 25},
    {"name": "Dell XPS 13 Plus (2025)", "category": "Laptops", "brand": "Dell", "price": 1399, "compare_price": 1599, "stock": 40},
    {"name": "Samsung Galaxy S25 Ultra", "category": "Smartphones", "brand": "Samsung", "price": 1199, "compare_price": 1299, "stock": 60},
    {"name": "Apple iPhone 17 Pro Max", "category": "Smartphones", "brand": "Apple", "price": 1399, "compare_price": 1499, "stock": 55},
    {"name": "Sony WH‑1000XM6 Wireless", "category": "Headphones", "brand": "Sony", "price": 399, "compare_price": 449, "stock": 75},
    {"name": "Bose QuietComfort Ultra", "category": "Headphones", "brand": "Bose", "price": 379, "compare_price": 429, "stock": 70},
    {"name": "LG OLED evo G4 65‑inch", "category": "Televisions", "brand": "LG", "price": 2599, "compare_price": 2999, "stock": 18},
    {"name": "Samsung Neo QLED 8K QN900D 75‑inch", "category": "Televisions", "brand": "Samsung", "price": 4499, "compare_price": 4999, "stock": 10},
    {"name": "Apple Watch Series 11", "category": "Wearables", "brand": "Apple", "price": 499, "compare_price": 549, "stock": 90},
    {"name": "Garmin Fenix 9 Pro", "category": "Wearables", "brand": "Garmin", "price": 799, "compare_price": 899, "stock": 35},
    {"name": "Canon EOS R6 Mark II", "category": "Cameras", "brand": "Canon", "price": 2299, "compare_price": 2499, "stock": 22},
    {"name": "Sony Alpha A7 V", "category": "Cameras", "brand": "Sony", "price": 2499, "compare_price": 2699, "stock": 24},
]

# Generate up to 50 products by cloning
while len(PRODUCT_DATA) < 50:
    base = random.choice(PRODUCT_DATA)
    clone = base.copy()
    clone["name"] += f" ({random.choice(['Blue', 'Silver', '2025 Edition', 'Special'])})"
    delta = random.randint(-50, 50)
    clone["price"] = max(50, base["price"] + delta)
    clone["compare_price"] = clone["price"] + random.randint(50, 150)
    clone["stock"] = random.randint(5, 120)
    PRODUCT_DATA.append(clone)


class Command(BaseCommand):
    help = "Generate 50 real‑looking products with categories & brands."

    def add_arguments(self, parser):
        parser.add_argument(
            "--drop-existing",
            action="store_true",
            help="Delete all existing Product rows first.",
        )

    @transaction.atomic
    def handle(self, *args, **options):
        if options["drop_existing"]:
            deleted, _ = Product.objects.all().delete()
            self.stdout.write(self.style.WARNING(f"Deleted {deleted} existing products."))

        created_count = 0

        for item in PRODUCT_DATA:
            # Create or get Category by slug
            cat_slug = slugify(item["category"])
            category_obj, _ = Category.objects.get_or_create(
                slug=cat_slug,
                defaults={"name": item["category"]}
            )

            # Create or get Brand by slug
            brand_slug = slugify(item["brand"])
            brand_obj, _ = Brand.objects.get_or_create(
                slug=brand_slug,
                defaults={
                    "name": item["brand"],
                    "description": f"{item['brand']} is a world‑class manufacturer.",
                    "is_active": True,
                }
            )

            # Unique slug for product
            product_slug = slugify(item["name"])
            if Product.objects.filter(slug=product_slug).exists():
                product_slug += f"-{random.randint(1000, 9999)}"

            product, created = Product.objects.get_or_create(
                name=item["name"],
                defaults={
                    "slug": product_slug,
                    "description": f"Authentic {item['brand']} {item['category'].lower()}",
                    "short_description": f"Latest {item['name']} from {item['brand']}.",
                    "sku": random_sku(item["brand"][:3].upper()),
                    "category": category_obj,
                    "brand": brand_obj,
                    "price": money(item["price"]),
                    "compare_price": money(item["compare_price"]),
                    "cost_price": money(item["price"] * 0.7),
                    "stock_quantity": item["stock"],
                    "low_stock_threshold": 5,
                    "status": "active",
                    "is_featured": random.choice([True, False]),
                    "is_hot_deal": random.choice([True, False]),
                    "is_best_seller": random.choice([True, False]),
                    "view_count": random.randint(0, 2500),
                    "sales_count": random.randint(0, 500),
                },
            )

            if created:
                created_count += 1

        self.stdout.write(self.style.SUCCESS(f"✅ Created {created_count} products successfully."))
