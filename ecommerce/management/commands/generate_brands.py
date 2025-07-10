from django.core.management.base import BaseCommand
from ecommerce.models import Brand
from django.utils.text import slugify
import random

class Command(BaseCommand):
    help = 'Create 20 real-world brand names'

    def handle(self, *args, **kwargs):
        brand_data = [
            ("Apple", "https://www.apple.com"),
            ("Samsung", "https://www.samsung.com"),
            ("Sony", "https://www.sony.com"),
            ("Nike", "https://www.nike.com"),
            ("Adidas", "https://www.adidas.com"),
            ("Microsoft", "https://www.microsoft.com"),
            ("Dell", "https://www.dell.com"),
            ("HP", "https://www.hp.com"),
            ("Lenovo", "https://www.lenovo.com"),
            ("Asus", "https://www.asus.com"),
            ("LG", "https://www.lg.com"),
            ("Puma", "https://www.puma.com"),
            ("Under Armour", "https://www.underarmour.com"),
            ("Google", "https://www.google.com"),
            ("Amazon", "https://www.amazon.com"),
            ("Huawei", "https://www.huawei.com"),
            ("OnePlus", "https://www.oneplus.com"),
            ("Canon", "https://www.canon.com"),
            ("Panasonic", "https://www.panasonic.com"),
            ("Philips", "https://www.philips.com"),
        ]

        for name, website in brand_data:
            slug = slugify(name)
            description = f"{name} is a global brand known for quality and innovation."
            
            brand, created = Brand.objects.get_or_create(
                name=name,
                defaults={
                    'slug': slug,
                    'description': description,
                    'website': website,
                    'is_active': random.choice([True, True, True, False])  # mostly active
                }
            )

            if created:
                self.stdout.write(self.style.SUCCESS(f"Created brand: {name}"))
            else:
                self.stdout.write(self.style.WARNING(f"Brand already exists: {name}"))
