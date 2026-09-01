import uuid
from datetime import date, timedelta
from decimal import Decimal

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.db import transaction
from business.models import Business
from finance.models import FarmExpense
from goats.models import (
    Goat,
    Disease,
    DiseaseGoat,
    DeathGoat,
    Rack,
    RackGoat,
)
from breeding.models import Mating, ParentMapping
from inventory.models import FeedStock, FeedStockTransaction
from production.models import GoatWeight, GoatMilk


User = get_user_model()


class Command(BaseCommand):
    help = "Create demo seed data"

    @transaction.atomic
    def handle(self, *args, **kwargs):

        self.stdout.write(
            self.style.WARNING("Creating demo seed data...")
        )

        # =====================================================
        # USER
        # =====================================================

        user, created = User.objects.get_or_create(
            username="demo",
            defaults={
                "email": "demo@example.com",
                "first_name": "Demo",
                "last_name": "User",
            },
        )

        if created:
            user.set_password("demo123")
            user.save()

        self.stdout.write(
            self.style.SUCCESS("User created: demo")
        )

        # =====================================================
        # BUSINESS
        # =====================================================

        business, created = Business.objects.get_or_create(
            name="Demo Goat Farm",
            defaults={
                "address": "Chennai, Tamil Nadu",
                "gstn": "33ABCDE1234F1Z5",
                "phone_number": "9876543210",
                "created_by": user,
                "owner": user,
                "status": True,
            },
        )

        self.stdout.write(
            self.style.SUCCESS(
                f"Business ready: {business.name}"
            )
        )

        # =====================================================
        # GOATS - 20
        # =====================================================

        goats = []

        breeds = [
            "Jakhrana",
            "Boer",
            "Beetal",
            "Jamunapari",
            "Sirohi",
        ]

        for i in range(1, 21):

            goat, _ = Goat.objects.update_or_create(
                token_no=f"DEMO-G{i:03d}",
                defaults={
                    "rfid": f"RFID-DEMO-{i:03d}",
                    "breed_variety": breeds[(i - 1) % len(breeds)],
                    "dob": date.today() - timedelta(days=400 + i * 10),
                    "age": 1,
                    "live": True,
                    "gender": "MALE" if i % 2 == 0 else "FEMALE",
                    "maturity": "ADULT",
                    "created_by": user,
                    "business": business,
                },
            )

            goats.append(goat)

        self.stdout.write(
            self.style.SUCCESS("20 goats created")
        )

        # =====================================================
        # DISEASE - 20
        # =====================================================

        disease_names = [
            "Pneumonia",
            "PPR",
            "Mastitis",
            "Foot Rot",
            "Enterotoxemia",
            "Coccidiosis",
            "Diarrhea",
            "Bloat",
            "Anemia",
            "Orf",
            "Worm Infection",
            "Parasite Infection",
            "Respiratory Infection",
            "Skin Infection",
            "Eye Infection",
            "Liver Fluke",
            "Joint Infection",
            "Fever",
            "Udder Infection",
            "Digestive Disorder",
        ]

        diseases = []

        for i, name in enumerate(disease_names, start=1):

            disease, _ = Disease.objects.update_or_create(
                name=name,
                business=business,
                defaults={
                    "symptoms": f"Sample symptoms for {name}",
                    "impact_goat": f"Sample impact of {name}",
                    "treatment": f"Sample treatment for {name}",
                    "created_by": user,
                },
            )

            diseases.append(disease)

        self.stdout.write(
            self.style.SUCCESS("20 diseases created")
        )

        # =====================================================
        # RACKS - 20
        # =====================================================

        racks = []

        for i in range(1, 21):

            rack, _ = Rack.objects.update_or_create(
                name=f"Rack-{i:02d}",
                business=business,
                defaults={
                    "capacity": 20 + i,
                    "created_by": user,
                },
            )

            racks.append(rack)

        self.stdout.write(
            self.style.SUCCESS("20 racks created")
        )

        # =====================================================
        # FARM EXPENSE - 20
        # =====================================================

        categories = [
            "Feed",
            "Medicine",
            "Labour",
            "Transport",
            "Electricity",
            "Maintenance",
        ]

        for i in range(1, 21):

            FarmExpense.objects.create(
                date=date.today() - timedelta(days=i),
                category=categories[(i - 1) % len(categories)],
                amount=Decimal("1000.00") + Decimal(i * 250),
                comment=f"Demo expense {i}",
                created_by=user,
                business=business,
            )

        self.stdout.write(
            self.style.SUCCESS("20 farm expenses created")
        )

        # =====================================================
        # FEED STOCK - 20
        # =====================================================

        fodders = [
            "Alfalfa",
            "Moringa",
            "Indigofera",
            "Gliricidia",
            "Dry Fodder",
            "Maize",
            "Rice Bran",
        ]

        feed_stocks = []

        for i in range(1, 21):

            stock_weight = Decimal("100.000") + Decimal(i * 10)
            rate = Decimal("15.00") + Decimal(i)

            feed_stock = FeedStock.objects.create(
                date=date.today() - timedelta(days=i),
                fodder_variety=fodders[(i - 1) % len(fodders)],
                stock_weight=stock_weight,
                rate=rate,
                total_amount=stock_weight * rate,
                current_stock_kg=stock_weight,
                created_by=user,
                business=business,
            )

            feed_stocks.append(feed_stock)

        self.stdout.write(
            self.style.SUCCESS("20 feed stocks created")
        )

        # =====================================================
        # FEED STOCK TRANSACTION - 20
        # =====================================================

        for i in range(20):

            FeedStockTransaction.objects.create(
                feed_stock=feed_stocks[i],
                date=date.today() - timedelta(days=i),
                transaction_type="IN",
                quantity_kg=Decimal("20.000") + Decimal(i),
                note=f"Demo feed transaction {i + 1}",
                created_by=user,
            )

        self.stdout.write(
            self.style.SUCCESS(
                "20 feed stock transactions created"
            )
        )

        # =====================================================
        # MALE / FEMALE GOATS
        # =====================================================

        male_goats = [
            goat for goat in goats
            if goat.gender == "MALE"
        ]

        female_goats = [
            goat for goat in goats
            if goat.gender == "FEMALE"
        ]

        # =====================================================
        # MATING - 20
        # =====================================================

        for i in range(20):

            Mating.objects.create(
                male=male_goats[i % len(male_goats)],
                female=female_goats[i % len(female_goats)],
                mating_date=date.today() - timedelta(days=i * 5),
                comment=f"Demo mating record {i + 1}",
                created_by=user,
            )

        self.stdout.write(
            self.style.SUCCESS("20 mating records created")
        )

        # =====================================================
        # PARENT MAPPING - 20
        # =====================================================

        for i in range(20):

            child = goats[i]

            parent = female_goats[
                i % len(female_goats)
            ]

            # Avoid child == parent
            if child.id == parent.id:
                parent = male_goats[
                    i % len(male_goats)
                ]

            ParentMapping.objects.get_or_create(
                child=child,
                parent=parent,
                defaults={
                    "created_by": user,
                },
            )

        self.stdout.write(
            self.style.SUCCESS(
                "20 parent mappings created"
            )
        )

        # =====================================================
        # DISEASE GOAT - 20
        # =====================================================

        for i in range(20):

            DiseaseGoat.objects.create(
                goat=goats[i],
                disease=diseases[i],
                disease_date=date.today() - timedelta(days=i),
                comment=f"Demo disease record {i + 1}",
                status=True,
                created_by=user,
                business=business,
            )

        self.stdout.write(
            self.style.SUCCESS(
                "20 goat disease records created"
            )
        )

        # =====================================================
        # DEATH GOATS + DEATH RECORDS - 20
        # =====================================================
        #
        # Separate dead goats are created so that the original
        # 20 active goats remain available for testing.
        #

        for i in range(1, 21):

            dead_goat, _ = Goat.objects.get_or_create(
                token_no=f"DEMO-DEAD-{i:03d}",
                defaults={
                    "rfid": f"RFID-DEAD-{i:03d}",
                    "breed_variety": breeds[
                        (i - 1) % len(breeds)
                    ],
                    "dob": date.today() - timedelta(
                        days=700 + i
                    ),
                    "age": 2,
                    "live": False,
                    "gender": (
                        "MALE"
                        if i % 2 == 0
                        else "FEMALE"
                    ),
                    "maturity": "ADULT",
                    "created_by": user,
                    "business": business,
                },
            )

            DeathGoat.objects.create(
                goat=dead_goat,
                disease=diseases[i - 1],
                died_date=date.today() - timedelta(days=i),
                comment=f"Demo death record {i}",
                created_by=user,
                business=business,
            )

        self.stdout.write(
            self.style.SUCCESS(
                "20 death goat records created"
            )
        )

        # =====================================================
        # RACK GOAT - 20
        # =====================================================

        for i in range(20):

            RackGoat.objects.create(
                goat=goats[i],
                rack=racks[i],
                created_by=user,
                business=business,
            )

        self.stdout.write(
            self.style.SUCCESS(
                "20 rack goat allocations created"
            )
        )

        # =====================================================
        # GOAT WEIGHT - 20
        # =====================================================

        for i in range(20):

            GoatWeight.objects.create(
                goat=goats[i],
                user=user,
                weight=Decimal("20.00") + Decimal(i),
                date=date.today() - timedelta(days=i),
                note=f"Demo weight record {i + 1}",
                created_by=user,
            )

        self.stdout.write(
            self.style.SUCCESS(
                "20 goat weight records created"
            )
        )

        # =====================================================
        # GOAT MILK - 20
        # =====================================================

        for i in range(20):

            GoatMilk.objects.create(
                goat=female_goats[
                    i % len(female_goats)
                ],
                user=user,
                milk_weight=(
                    Decimal("1.200")
                    + Decimal(i) / Decimal("100")
                ),
                date=date.today() - timedelta(days=i),
                note=f"Demo milk record {i + 1}",
                time=(
                    GoatMilk.MilkingTime.MORNING
                    if i % 2 == 0
                    else GoatMilk.MilkingTime.EVENING
                ),
                created_by=user,
            )

        self.stdout.write(
            self.style.SUCCESS(
                "20 goat milk records created"
            )
        )

        # =====================================================
        # SUMMARY
        # =====================================================

        self.stdout.write("")
        self.stdout.write(
            self.style.SUCCESS(
                "======================================"
            )
        )
        self.stdout.write(
            self.style.SUCCESS(
                "DEMO SEED DATA CREATED SUCCESSFULLY"
            )
        )
        self.stdout.write(
            self.style.SUCCESS(
                "======================================"
            )
        )

        self.stdout.write(
            f"Login User : demo"
        )
        self.stdout.write(
            f"Password   : demo123"
        )
        self.stdout.write(
            f"Business   : {business.name}"
        )

        self.stdout.write("")
        self.stdout.write(
            self.style.SUCCESS(
                "20 records created for each requested table."
            )
        )