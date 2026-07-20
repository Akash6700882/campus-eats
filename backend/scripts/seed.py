"""Idempotent seed script: default admin, campus roles, sample menu, placeholder geofence.

Run inside the backend container/venv:
    python -m scripts.seed
"""

import asyncio
import json
import uuid

from sqlalchemy import select

from app.core.config import get_settings
from app.core.db import AsyncSessionLocal
from app.core.security import hash_password
from app.models import Category, DeliveryZone, Food, Role, User
from app.models.enums import RoleName

settings = get_settings()

ROLE_NAMES = [RoleName.CUSTOMER, RoleName.ADMIN, RoleName.KITCHEN, RoleName.DELIVERY]

CATEGORIES = [
    ("Breakfast", "breakfast"),
    ("South Indian", "south-indian"),
    ("Lunch", "lunch"),
    ("Dinner", "dinner"),
    ("Snacks", "snacks"),
    ("Juices & Beverages", "juices-beverages"),
    ("Desserts", "desserts"),
]

# (name, category_slug, price, is_veg, prep_time, description, popular, special_today, image_url)
# image_url values are real Wikimedia Commons photo URLs, verified per-dish (or, where noted,
# the closest same-dish relative). Left as None where no trustworthy match exists rather than
# force a misleading photo (wrong cuisine, wrong protein, or a raw-ingredient shot).
DOSA_IMG = "https://upload.wikimedia.org/wikipedia/commons/thumb/9/9f/Dosa_at_Sri_Ganesha_Restauran%2C_Bangkok_%2844570742744%29.jpg/3840px-Dosa_at_Sri_Ganesha_Restauran%2C_Bangkok_%2844570742744%29.jpg"
MASALA_DOSA_IMG = "https://upload.wikimedia.org/wikipedia/commons/thumb/8/8f/Rameshwaram_Cafe_Dosa.jpg/3840px-Rameshwaram_Cafe_Dosa.jpg"
MEDU_VADA_IMG = "https://upload.wikimedia.org/wikipedia/commons/1/1b/Medu_Vada.JPG"
UPMA_IMG = "https://upload.wikimedia.org/wikipedia/commons/thumb/8/86/A_photo_of_Upma.jpg/3840px-A_photo_of_Upma.jpg"
PULIHORA_IMG = "https://upload.wikimedia.org/wikipedia/commons/d/d4/Pulihara.JPG"
PUNUGULU_IMG = "https://upload.wikimedia.org/wikipedia/commons/0/05/Punugulu1.JPG"

FOODS = [
    ("Idli", "south-indian", 40, True, 10, "Steamed rice cakes served with sambar and chutney.", True, False, "https://upload.wikimedia.org/wikipedia/commons/1/11/Idli_Sambar.JPG"),
    ("Plain Dosa", "south-indian", 50, True, 12, "Classic crispy rice-and-lentil crepe.", True, False, DOSA_IMG),
    ("Masala Dosa", "south-indian", 70, True, 14, "Dosa filled with spiced potato masala.", True, True, MASALA_DOSA_IMG),
    ("Onion Dosa", "south-indian", 65, True, 14, "Dosa topped with crispy onions.", False, False, DOSA_IMG),
    ("Poori", "breakfast", 50, True, 10, "Deep-fried puffed bread with curry.", False, False, "https://upload.wikimedia.org/wikipedia/commons/thumb/5/50/Fluffy_Poori_%28cropped%29.JPG/1920px-Fluffy_Poori_%28cropped%29.JPG"),
    ("Vada", "south-indian", 35, True, 8, "Crispy fried lentil doughnuts.", False, False, "https://upload.wikimedia.org/wikipedia/commons/thumb/0/0c/Medu_Vadas.JPG/3840px-Medu_Vadas.JPG"),
    ("Pongal", "breakfast", 45, True, 12, "Savory rice and lentil porridge with pepper and ghee.", False, False, "https://upload.wikimedia.org/wikipedia/commons/2/21/Ven_pongal_with_sambar_and_chutney.jpg"),
    ("Uttapam", "south-indian", 60, True, 13, "Thick savory pancake topped with vegetables.", False, False, "https://upload.wikimedia.org/wikipedia/commons/c/c6/Mini_Uttappam.jpg"),
    ("Meals (Veg)", "lunch", 90, True, 20, "Full South Indian thali with rice, sambar, rasam, curries.", True, False, "https://upload.wikimedia.org/wikipedia/commons/9/95/Sadhya_DSW.jpg"),
    ("Curd Rice", "lunch", 45, True, 8, "Comfort rice tempered curd rice.", False, False, "https://upload.wikimedia.org/wikipedia/commons/5/58/Curd_Rice.jpg"),
    ("Lemon Rice", "lunch", 50, True, 10, "Tangy tempered lemon rice.", False, False, "https://upload.wikimedia.org/wikipedia/commons/f/f4/Chitranna_and_Payasa.jpg"),
    ("Fried Rice", "dinner", 70, True, 15, "Wok-tossed vegetable fried rice.", False, False, "https://upload.wikimedia.org/wikipedia/commons/thumb/c/c3/Koh_Mak%2C_Thailand%2C_Fried_rice_with_seafood%2C_Thai_fried_rice.jpg/3840px-Koh_Mak%2C_Thailand%2C_Fried_rice_with_seafood%2C_Thai_fried_rice.jpg"),
    ("Noodles", "dinner", 70, True, 15, "Stir-fried veg noodles.", False, False, "https://upload.wikimedia.org/wikipedia/commons/thumb/a/a6/Homemade_Chow_mein_with_shrimps_and_meat_with_a_choy_and_Choung.jpg/3840px-Homemade_Chow_mein_with_shrimps_and_meat_with_a_choy_and_Choung.jpg"),
    ("Tea", "juices-beverages", 15, True, 5, "Classic Indian masala chai.", True, False, "https://upload.wikimedia.org/wikipedia/commons/8/89/Chai_In_Sakora.jpg"),
    ("Coffee", "juices-beverages", 20, True, 5, "South Indian filter coffee.", True, False, "https://upload.wikimedia.org/wikipedia/commons/thumb/5/51/Filter_kaapi.JPG/3840px-Filter_kaapi.JPG"),
    ("Badam Milk", "juices-beverages", 40, True, 5, "Chilled almond-flavoured milk.", False, False, "https://upload.wikimedia.org/wikipedia/commons/thumb/d/de/Home-made_almond_milk%2C_November_2012.jpg/500px-Home-made_almond_milk%2C_November_2012.jpg"),
    ("Fresh Lime", "juices-beverages", 30, True, 5, "Fresh lime soda, sweet or salted.", False, False, "https://upload.wikimedia.org/wikipedia/commons/8/82/Shikanji-_served_with_pomegranate%2Cgrated_apple_and_mint.jpg"),
    ("Fruit Juice (Mixed)", "juices-beverages", 45, True, 5, "Seasonal mixed fruit juice.", False, True, "https://upload.wikimedia.org/wikipedia/commons/f/fd/Orange_juice_1.jpg"),
    ("Mango Milkshake", "juices-beverages", 55, True, 5, "Thick mango milkshake.", True, False, "https://upload.wikimedia.org/wikipedia/commons/6/68/Strawberry_milk_shake_%28cropped%29.jpg"),
    ("Lassi", "juices-beverages", 40, True, 5, "Sweet churned yogurt drink.", False, False, "https://upload.wikimedia.org/wikipedia/commons/f/f1/Salt_lassi.jpg"),
    ("Ice Cream", "desserts", 35, True, 3, "Two scoops, ask for today's flavours.", False, False, "https://upload.wikimedia.org/wikipedia/commons/2/2e/Ice_cream_with_whipped_cream%2C_chocolate_syrup%2C_and_a_wafer_%28cropped%29.jpg"),
    # South Indian regional expansion — Tamil Nadu, Kerala, Karnataka, Andhra & Telangana
    ("Rava Dosa", "south-indian", 65, True, 14, "Crispy semolina dosa with onions and cumin.", False, False, DOSA_IMG),
    ("Set Dosa", "south-indian", 55, True, 12, "Soft, spongy mini dosas served in sets of three.", False, False, DOSA_IMG),
    ("Mysore Masala Dosa", "south-indian", 80, True, 15, "Dosa spread with spicy red chutney and potato masala.", True, False, MASALA_DOSA_IMG),
    ("Pesarattu", "south-indian", 60, True, 13, "Andhra-style green gram dosa, usually served with upma.", False, False, "https://upload.wikimedia.org/wikipedia/commons/6/6c/Pesarattu.jpg"),
    ("Medu Vada", "south-indian", 40, True, 8, "Soft, fluffy urad dal doughnuts with a crisp shell.", False, False, MEDU_VADA_IMG),
    ("Rava Idli", "south-indian", 45, True, 10, "Semolina steamed idlis tempered with mustard and curry leaves.", False, False, "https://upload.wikimedia.org/wikipedia/commons/b/b4/Rava_Idli_%286005561226%29.jpg"),
    ("Adai", "south-indian", 55, True, 12, "Thick, protein-rich mixed lentil dosa.", False, False, None),
    ("Appam", "south-indian", 55, True, 12, "Lacy rice-and-coconut pancake with a soft centre.", False, False, "https://upload.wikimedia.org/wikipedia/commons/c/c3/Appam_-_%E0%AE%85%E0%AE%AA%E0%AF%8D%E0%AE%AA%E0%AE%AE%E0%AF%8D.jpg"),
    ("Neer Dosa", "south-indian", 50, True, 10, "Thin, delicate rice crepe from coastal Karnataka.", False, False, "https://upload.wikimedia.org/wikipedia/commons/f/f3/Neer-dosa.jpg"),
    ("Ragi Dosa", "south-indian", 55, True, 12, "Finger-millet dosa, a healthy Karnataka favourite.", False, False, DOSA_IMG),
    ("Upma", "breakfast", 40, True, 10, "Semolina cooked with mustard seeds, curry leaves and vegetables.", False, False, UPMA_IMG),
    ("Idiyappam", "breakfast", 50, True, 12, "Steamed rice noodle nests, served with coconut milk or curry.", False, False, "https://upload.wikimedia.org/wikipedia/commons/thumb/8/8a/Idiyappam_with_Egg_Masala_Curry.jpg/3840px-Idiyappam_with_Egg_Masala_Curry.jpg"),
    ("Puttu with Kadala Curry", "breakfast", 60, True, 15, "Steamed rice-flour and coconut cylinders with black chickpea curry.", False, False, "https://upload.wikimedia.org/wikipedia/commons/thumb/c/ca/Puttu_%28Rice_Flour_steamed_cake%29.jpg/3840px-Puttu_%28Rice_Flour_steamed_cake%29.jpg"),
    ("Semiya Upma", "breakfast", 40, True, 10, "Vermicelli tempered with mustard seeds and vegetables.", False, False, UPMA_IMG),
    ("Sambar Rice", "lunch", 55, True, 12, "Rice mixed with lentil and vegetable sambar.", False, False, "https://upload.wikimedia.org/wikipedia/commons/b/bb/Pumpkin_sambar.JPG"),
    ("Bisi Bele Bath", "lunch", 70, True, 15, "Karnataka-style spiced rice, lentils and vegetables cooked together.", False, False, "https://upload.wikimedia.org/wikipedia/commons/thumb/0/04/Bisi_Bele_Bath_%28Bisibelebath%29.JPG/3840px-Bisi_Bele_Bath_%28Bisibelebath%29.JPG"),
    ("Pulihora", "lunch", 55, True, 10, "Andhra tangy tamarind rice tempered with peanuts.", False, False, PULIHORA_IMG),
    ("Andhra Gongura Meals", "lunch", 95, True, 18, "Andhra thali featuring tangy sorrel-leaf chutney with rice.", False, False, "https://upload.wikimedia.org/wikipedia/commons/b/bd/Guntur_Gongura1.jpg"),
    ("Hyderabadi Veg Biryani", "lunch", 110, True, 25, "Fragrant basmati rice layered with spiced vegetables.", True, False, None),
    ("Rasam Rice", "lunch", 45, True, 8, "Comforting peppery rasam served over steamed rice.", False, False, "https://upload.wikimedia.org/wikipedia/commons/f/fa/Rasam.JPG"),
    ("Vangi Bath", "lunch", 65, True, 14, "Karnataka brinjal rice tempered with a roasted spice blend.", False, False, "https://upload.wikimedia.org/wikipedia/commons/c/cd/Brinjal_rice_bath.jpg"),
    ("Coconut Rice", "lunch", 50, True, 8, "Rice tempered with coconut, curry leaves and cashews.", False, False, None),
    ("Puliyodarai", "lunch", 55, True, 10, "Tamil Nadu-style tangy tamarind rice.", False, False, PULIHORA_IMG),
    ("Hyderabadi Chicken Biryani", "dinner", 180, False, 30, "Slow-cooked dum biryani with tender chicken and saffron.", True, False, "https://upload.wikimedia.org/wikipedia/commons/thumb/7/7c/Hyderabadi_Chicken_Biryani.jpg/3840px-Hyderabadi_Chicken_Biryani.jpg"),
    ("Andhra Chicken Curry", "dinner", 150, False, 25, "Fiery Andhra-style chicken curry with red chillies.", False, False, "https://upload.wikimedia.org/wikipedia/commons/thumb/6/6f/Taj_Mahal_-_Lamb_Curry_Madras.jpg/3840px-Taj_Mahal_-_Lamb_Curry_Madras.jpg"),
    ("Gutti Vankaya Kura", "dinner", 90, True, 20, "Stuffed baby brinjals in a peanut-sesame Andhra gravy.", False, False, "https://upload.wikimedia.org/wikipedia/commons/thumb/f/fe/Azerbaijani_Bad%C4%B1mcan_dolmas%C4%B1_1.JPG/3840px-Azerbaijani_Bad%C4%B1mcan_dolmas%C4%B1_1.JPG"),
    ("Natukodi Pulusu", "dinner", 170, False, 30, "Andhra country chicken simmered in a tangy tamarind gravy.", False, False, None),
    ("Chepala Pulusu", "dinner", 160, False, 25, "Andhra-style tangy tamarind fish curry.", False, False, None),
    ("Royyala Vepudu", "dinner", 175, False, 20, "Spicy Andhra-style pan-fried prawns.", False, False, None),
    ("Kodi Vepudu", "dinner", 155, False, 22, "Dry-roasted Andhra chicken fry with curry leaves.", False, False, "https://upload.wikimedia.org/wikipedia/commons/thumb/2/2c/Fried-Chicken-Set.jpg/3840px-Fried-Chicken-Set.jpg"),
    ("Gongura Mutton", "dinner", 190, False, 35, "Mutton slow-cooked with tangy sorrel leaves, an Andhra classic.", True, False, "https://upload.wikimedia.org/wikipedia/commons/thumb/8/80/Bengali_Mutton_Curry.JPG/3840px-Bengali_Mutton_Curry.JPG"),
    ("Andhra Egg Curry", "dinner", 90, False, 15, "Boiled eggs in a spicy Andhra masala gravy.", False, False, None),
    ("Mirchi Bajji", "snacks", 40, True, 10, "Andhra-style stuffed chilli fritters.", False, False, "https://upload.wikimedia.org/wikipedia/commons/7/7b/Stuffed_mirchi_bajji_%2816164286908%29.jpg"),
    ("Punugulu", "snacks", 35, True, 10, "Bite-sized fried fritters made from fermented rice batter.", False, False, PUNUGULU_IMG),
    ("Mysore Bonda", "snacks", 35, True, 10, "Fluffy deep-fried lentil-batter fritters.", False, False, PUNUGULU_IMG),
    ("Sabudana Vada", "snacks", 40, True, 10, "Crispy tapioca pearl and peanut fritters.", False, False, "https://upload.wikimedia.org/wikipedia/commons/f/f5/Sabudana_vada.JPG"),
    ("Onion Pakoda", "snacks", 35, True, 8, "Crispy gram-flour battered onion fritters.", False, False, "https://upload.wikimedia.org/wikipedia/commons/c/cf/Onion_pakora_-_a.jpg"),
    ("Masala Vada", "snacks", 35, True, 10, "Crunchy spiced chana dal fritters.", False, False, MEDU_VADA_IMG),
    ("Dahi Vada", "snacks", 45, True, 8, "Lentil dumplings soaked in spiced yogurt.", False, False, "https://upload.wikimedia.org/wikipedia/commons/2/2d/Dahi_bhalla_or_dahi_wada_or_dahi_bada.PNG"),
    ("Sakinalu", "snacks", 40, True, 12, "Crispy Telangana rice-flour spirals, a festive favourite.", False, False, "https://upload.wikimedia.org/wikipedia/commons/thumb/7/77/Sakinalu%2C_dark_and_light-2159.jpg/3840px-Sakinalu%2C_dark_and_light-2159.jpg"),
    ("Chekkalu", "snacks", 35, True, 10, "Crispy Andhra rice crackers seasoned with peanuts and curry leaves.", False, False, None),
    ("Bobbatlu", "desserts", 45, True, 15, "Andhra sweet flatbread stuffed with jaggery and lentil filling.", False, False, "https://upload.wikimedia.org/wikipedia/commons/1/13/Puran_Poli.jpg"),
    ("Ariselu", "desserts", 40, True, 15, "Traditional Telangana rice-and-jaggery fried sweet.", False, False, "https://upload.wikimedia.org/wikipedia/commons/a/ab/Adhirasam2a.jpg"),
    ("Double Ka Meetha", "desserts", 55, True, 12, "Hyderabadi bread pudding soaked in sweet milk and dry fruits.", True, False, "https://upload.wikimedia.org/wikipedia/commons/7/7d/Double_ka_meetha_with_a_big_spoon.jpg"),
    ("Qubani Ka Meetha", "desserts", 50, True, 10, "Hyderabadi stewed apricot dessert served with cream.", False, False, "https://upload.wikimedia.org/wikipedia/commons/3/3c/Khobani_Ka_Meetha.JPG"),
    ("Semiya Payasam", "desserts", 40, True, 10, "Sweet vermicelli pudding with cardamom and cashews.", False, False, "https://upload.wikimedia.org/wikipedia/commons/4/46/Kheer.jpg"),
    ("Poornalu", "desserts", 35, True, 12, "Deep-fried sweet dumplings filled with jaggery and lentils.", False, False, "https://upload.wikimedia.org/wikipedia/commons/3/39/Poornalu.JPG"),
    ("Buttermilk", "juices-beverages", 25, True, 5, "Spiced Andhra-style majjiga, chilled and tempered.", False, False, "https://upload.wikimedia.org/wikipedia/commons/thumb/2/23/Buttermilk-%28right%29-and-Milk-%28left%29.jpg/3840px-Buttermilk-%28right%29-and-Milk-%28left%29.jpg"),
    ("Panakam", "juices-beverages", 25, True, 5, "Jaggery and dry-ginger cooler, a South Indian festive drink.", False, False, "https://upload.wikimedia.org/wikipedia/commons/thumb/2/2c/Panagam_picture.JPG/1920px-Panagam_picture.JPG"),
    ("Tender Coconut Water", "juices-beverages", 40, True, 3, "Fresh, chilled tender coconut water.", False, False, "https://upload.wikimedia.org/wikipedia/commons/thumb/7/78/Young_Coconut_Drink.jpg/1920px-Young_Coconut_Drink.jpg"),
    ("Rose Milk", "juices-beverages", 40, True, 5, "Chilled milk flavoured with rose syrup.", False, False, "https://upload.wikimedia.org/wikipedia/commons/8/85/Faluda.JPG"),
]

# Placeholder campus geofence — approx a 3.2km half-width square (~10,000 acres)
# around a generic sample coordinate. Replace with the real campus GIS
# boundary in the admin delivery-zone editor (Phase 7) once available.
CAMPUS_CENTER = (12.9716, 77.5946)
_HALF_WIDTH_DEG = 0.029


def _placeholder_campus_polygon() -> str:
    lat, lng = CAMPUS_CENTER
    coords = [
        [lng - _HALF_WIDTH_DEG, lat - _HALF_WIDTH_DEG],
        [lng + _HALF_WIDTH_DEG, lat - _HALF_WIDTH_DEG],
        [lng + _HALF_WIDTH_DEG, lat + _HALF_WIDTH_DEG],
        [lng - _HALF_WIDTH_DEG, lat + _HALF_WIDTH_DEG],
        [lng - _HALF_WIDTH_DEG, lat - _HALF_WIDTH_DEG],
    ]
    return json.dumps({"type": "Polygon", "coordinates": [coords]})


def _slugify(name: str) -> str:
    return name.lower().replace(" ", "-").replace("(", "").replace(")", "")


async def seed() -> None:
    async with AsyncSessionLocal() as session:
        # Roles
        roles_by_name: dict[str, Role] = {}
        for role_name in ROLE_NAMES:
            result = await session.execute(select(Role).where(Role.name == role_name.value))
            role = result.scalar_one_or_none()
            if role is None:
                role = Role(id=uuid.uuid4(), name=role_name.value)
                session.add(role)
                await session.flush()
                print(f"Created role: {role_name.value}")
            roles_by_name[role_name.value] = role

        # Default admin
        result = await session.execute(select(User).where(User.email == settings.default_admin_email))
        admin = result.scalar_one_or_none()
        if admin is None:
            admin = User(
                id=uuid.uuid4(),
                full_name="Campus Eats Admin",
                email=settings.default_admin_email,
                phone=settings.default_admin_phone,
                hashed_password=hash_password(settings.default_admin_password),
                role_id=roles_by_name[RoleName.ADMIN.value].id,
                is_active=True,
                is_verified=True,
            )
            session.add(admin)
            await session.flush()
            print(f"Created default admin: {settings.default_admin_email}")
        else:
            print("Default admin already exists, skipping")

        # Categories
        categories_by_slug: dict[str, Category] = {}
        for sort_order, (name, slug) in enumerate(CATEGORIES):
            result = await session.execute(select(Category).where(Category.slug == slug))
            category = result.scalar_one_or_none()
            if category is None:
                category = Category(id=uuid.uuid4(), name=name, slug=slug, sort_order=sort_order)
                session.add(category)
                await session.flush()
                print(f"Created category: {name}")
            categories_by_slug[slug] = category

        # Foods
        created_foods = 0
        backfilled_images = 0
        for name, cat_slug, price, is_veg, prep_time, desc, popular, special, image_url in FOODS:
            slug = _slugify(name)
            result = await session.execute(select(Food).where(Food.slug == slug))
            existing = result.scalar_one_or_none()
            if existing is not None:
                if existing.image_url is None and image_url is not None:
                    existing.image_url = image_url
                    backfilled_images += 1
                continue
            food = Food(
                id=uuid.uuid4(),
                category_id=categories_by_slug[cat_slug].id,
                name=name,
                slug=slug,
                description=desc,
                price=price,
                is_veg=is_veg,
                prep_time_minutes=prep_time,
                is_available=True,
                is_popular=popular,
                is_special_today=special,
                image_url=image_url,
            )
            session.add(food)
            created_foods += 1
        if created_foods:
            print(f"Created {created_foods} food items")
        if backfilled_images:
            print(f"Backfilled image_url on {backfilled_images} existing food items")

        # Placeholder campus delivery zone
        result = await session.execute(select(DeliveryZone).where(DeliveryZone.name == "Main Campus (placeholder)"))
        zone = result.scalar_one_or_none()
        if zone is None:
            zone = DeliveryZone(
                id=uuid.uuid4(),
                name="Main Campus (placeholder)",
                polygon_geojson=_placeholder_campus_polygon(),
                is_active=True,
            )
            session.add(zone)
            print("Created placeholder campus delivery zone")

        await session.commit()
        print("Seed complete.")


if __name__ == "__main__":
    asyncio.run(seed())
