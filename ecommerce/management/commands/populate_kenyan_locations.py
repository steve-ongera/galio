from django.core.management.base import BaseCommand
from ecommerce.models import County, DeliveryArea

class Command(BaseCommand):
    help = 'Populate Kenyan counties and delivery areas'
    
    def handle(self, *args, **options):
        counties_data = {
            'Nairobi': {
                'code': 'NRB',
                'areas': [
                    ('Westlands', 150),
                    ('CBD', 150),
                    ('Karen', 200),
                    ('Langata', 180),
                    ('Kileleshwa', 150),
                    ('Kilimani', 150),
                    ('Parklands', 150),
                    ('Eastleigh', 150),
                    ('Kasarani', 200),
                    ('Ruaraka', 200),
                ]
            },
            'Mombasa': {
                'code': 'MSA',
                'areas': [
                    ('Shanzu', 250),
                    ('Utange', 200),
                    ('Majaoni', 180),
                    ('Bamburi', 220),
                    ('Nyali', 200),
                    ('CBD', 150),
                    ('Likoni', 250),
                    ('Changamwe', 200),
                ]
            },
            'Kisumu': {
                'code': 'KSM',
                'areas': [
                    ('CBD', 300),
                    ('Milimani', 350),
                    ('Mamboleo', 350),
                    ('Kondele', 300),
                ]
            },
            'Nakuru': {
                'code': 'NKR',
                'areas': [
                    ('CBD', 250),
                    ('Milimani', 280),
                    ('Bahati', 300),
                    ('Lanet', 320),
                ]
            },
            'Eldoret': {
                'code': 'EDT',
                'areas': [
                    ('CBD', 350),
                    ('Pioneer', 380),
                    ('Langas', 400),
                ]
            }
        }
        
        for county_name, county_info in counties_data.items():
            county, created = County.objects.get_or_create(
                name=county_name,
                defaults={'code': county_info['code']}
            )
            
            if created:
                self.stdout.write(f"Created county: {county_name}")
            
            for area_name, shipping_fee in county_info['areas']:
                area, created = DeliveryArea.objects.get_or_create(
                    name=area_name,
                    county=county,
                    defaults={'shipping_fee': shipping_fee}
                )
                
                if created:
                    self.stdout.write(f"Created area: {area_name} in {county_name}")
        
        self.stdout.write(
            self.style.SUCCESS('Successfully populated Kenyan locations')
        )