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

# (name, category_slug, price, is_veg, prep_time, description, popular, special_today)
FOODS = [
    ("Idli", "south-indian", 40, True, 10, "Steamed rice cakes served with sambar and chutney.", True, False),
    ("Plain Dosa", "south-indian", 50, True, 12, "Classic crispy rice-and-lentil crepe.", True, False),
    ("Masala Dosa", "south-indian", 70, True, 14, "Dosa filled with spiced potato masala.", True, True),
    ("Onion Dosa", "south-indian", 65, True, 14, "Dosa topped with crispy onions.", False, False),
    ("Poori", "breakfast", 50, True, 10, "Deep-fried puffed bread with curry.", False, False),
    ("Vada", "south-indian", 35, True, 8, "Crispy fried lentil doughnuts.", False, False),
    ("Pongal", "breakfast", 45, True, 12, "Savory rice and lentil porridge with pepper and ghee.", False, False),
    ("Uttapam", "south-indian", 60, True, 13, "Thick savory pancake topped with vegetables.", False, False),
    ("Meals (Veg)", "lunch", 90, True, 20, "Full South Indian thali with rice, sambar, rasam, curries.", True, False),
    ("Curd Rice", "lunch", 45, True, 8, "Comfort rice tempered curd rice.", False, False),
    ("Lemon Rice", "lunch", 50, True, 10, "Tangy tempered lemon rice.", False, False),
    ("Fried Rice", "dinner", 70, True, 15, "Wok-tossed vegetable fried rice.", False, False),
    ("Noodles", "dinner", 70, True, 15, "Stir-fried veg noodles.", False, False),
    ("Tea", "juices-beverages", 15, True, 5, "Classic Indian masala chai.", True, False),
    ("Coffee", "juices-beverages", 20, True, 5, "South Indian filter coffee.", True, False),
    ("Badam Milk", "juices-beverages", 40, True, 5, "Chilled almond-flavoured milk.", False, False),
    ("Fresh Lime", "juices-beverages", 30, True, 5, "Fresh lime soda, sweet or salted.", False, False),
    ("Fruit Juice (Mixed)", "juices-beverages", 45, True, 5, "Seasonal mixed fruit juice.", False, True),
    ("Mango Milkshake", "juices-beverages", 55, True, 5, "Thick mango milkshake.", True, False),
    ("Lassi", "juices-beverages", 40, True, 5, "Sweet churned yogurt drink.", False, False),
    ("Ice Cream", "desserts", 35, True, 3, "Two scoops, ask for today's flavours.", False, False),
    # South Indian regional expansion — Tamil Nadu, Kerala, Karnataka, Andhra & Telangana
    ("Rava Dosa", "south-indian", 65, True, 14, "Crispy semolina dosa with onions and cumin.", False, False),
    ("Set Dosa", "south-indian", 55, True, 12, "Soft, spongy mini dosas served in sets of three.", False, False),
    ("Mysore Masala Dosa", "south-indian", 80, True, 15, "Dosa spread with spicy red chutney and potato masala.", True, False),
    ("Pesarattu", "south-indian", 60, True, 13, "Andhra-style green gram dosa, usually served with upma.", False, False),
    ("Medu Vada", "south-indian", 40, True, 8, "Soft, fluffy urad dal doughnuts with a crisp shell.", False, False),
    ("Rava Idli", "south-indian", 45, True, 10, "Semolina steamed idlis tempered with mustard and curry leaves.", False, False),
    ("Adai", "south-indian", 55, True, 12, "Thick, protein-rich mixed lentil dosa.", False, False),
    ("Appam", "south-indian", 55, True, 12, "Lacy rice-and-coconut pancake with a soft centre.", False, False),
    ("Neer Dosa", "south-indian", 50, True, 10, "Thin, delicate rice crepe from coastal Karnataka.", False, False),
    ("Ragi Dosa", "south-indian", 55, True, 12, "Finger-millet dosa, a healthy Karnataka favourite.", False, False),
    ("Upma", "breakfast", 40, True, 10, "Semolina cooked with mustard seeds, curry leaves and vegetables.", False, False),
    ("Idiyappam", "breakfast", 50, True, 12, "Steamed rice noodle nests, served with coconut milk or curry.", False, False),
    ("Puttu with Kadala Curry", "breakfast", 60, True, 15, "Steamed rice-flour and coconut cylinders with black chickpea curry.", False, False),
    ("Semiya Upma", "breakfast", 40, True, 10, "Vermicelli tempered with mustard seeds and vegetables.", False, False),
    ("Sambar Rice", "lunch", 55, True, 12, "Rice mixed with lentil and vegetable sambar.", False, False),
    ("Bisi Bele Bath", "lunch", 70, True, 15, "Karnataka-style spiced rice, lentils and vegetables cooked together.", False, False),
    ("Pulihora", "lunch", 55, True, 10, "Andhra tangy tamarind rice tempered with peanuts.", False, False),
    ("Andhra Gongura Meals", "lunch", 95, True, 18, "Andhra thali featuring tangy sorrel-leaf chutney with rice.", False, False),
    ("Hyderabadi Veg Biryani", "lunch", 110, True, 25, "Fragrant basmati rice layered with spiced vegetables.", True, False),
    ("Rasam Rice", "lunch", 45, True, 8, "Comforting peppery rasam served over steamed rice.", False, False),
    ("Vangi Bath", "lunch", 65, True, 14, "Karnataka brinjal rice tempered with a roasted spice blend.", False, False),
    ("Coconut Rice", "lunch", 50, True, 8, "Rice tempered with coconut, curry leaves and cashews.", False, False),
    ("Puliyodarai", "lunch", 55, True, 10, "Tamil Nadu-style tangy tamarind rice.", False, False),
    ("Hyderabadi Chicken Biryani", "dinner", 180, False, 30, "Slow-cooked dum biryani with tender chicken and saffron.", True, False),
    ("Andhra Chicken Curry", "dinner", 150, False, 25, "Fiery Andhra-style chicken curry with red chillies.", False, False),
    ("Gutti Vankaya Kura", "dinner", 90, True, 20, "Stuffed baby brinjals in a peanut-sesame Andhra gravy.", False, False),
    ("Natukodi Pulusu", "dinner", 170, False, 30, "Andhra country chicken simmered in a tangy tamarind gravy.", False, False),
    ("Chepala Pulusu", "dinner", 160, False, 25, "Andhra-style tangy tamarind fish curry.", False, False),
    ("Royyala Vepudu", "dinner", 175, False, 20, "Spicy Andhra-style pan-fried prawns.", False, False),
    ("Kodi Vepudu", "dinner", 155, False, 22, "Dry-roasted Andhra chicken fry with curry leaves.", False, False),
    ("Gongura Mutton", "dinner", 190, False, 35, "Mutton slow-cooked with tangy sorrel leaves, an Andhra classic.", True, False),
    ("Andhra Egg Curry", "dinner", 90, False, 15, "Boiled eggs in a spicy Andhra masala gravy.", False, False),
    ("Mirchi Bajji", "snacks", 40, True, 10, "Andhra-style stuffed chilli fritters.", False, False),
    ("Punugulu", "snacks", 35, True, 10, "Bite-sized fried fritters made from fermented rice batter.", False, False),
    ("Mysore Bonda", "snacks", 35, True, 10, "Fluffy deep-fried lentil-batter fritters.", False, False),
    ("Sabudana Vada", "snacks", 40, True, 10, "Crispy tapioca pearl and peanut fritters.", False, False),
    ("Onion Pakoda", "snacks", 35, True, 8, "Crispy gram-flour battered onion fritters.", False, False),
    ("Masala Vada", "snacks", 35, True, 10, "Crunchy spiced chana dal fritters.", False, False),
    ("Dahi Vada", "snacks", 45, True, 8, "Lentil dumplings soaked in spiced yogurt.", False, False),
    ("Sakinalu", "snacks", 40, True, 12, "Crispy Telangana rice-flour spirals, a festive favourite.", False, False),
    ("Chekkalu", "snacks", 35, True, 10, "Crispy Andhra rice crackers seasoned with peanuts and curry leaves.", False, False),
    ("Bobbatlu", "desserts", 45, True, 15, "Andhra sweet flatbread stuffed with jaggery and lentil filling.", False, False),
    ("Ariselu", "desserts", 40, True, 15, "Traditional Telangana rice-and-jaggery fried sweet.", False, False),
    ("Double Ka Meetha", "desserts", 55, True, 12, "Hyderabadi bread pudding soaked in sweet milk and dry fruits.", True, False),
    ("Qubani Ka Meetha", "desserts", 50, True, 10, "Hyderabadi stewed apricot dessert served with cream.", False, False),
    ("Semiya Payasam", "desserts", 40, True, 10, "Sweet vermicelli pudding with cardamom and cashews.", False, False),
    ("Poornalu", "desserts", 35, True, 12, "Deep-fried sweet dumplings filled with jaggery and lentils.", False, False),
    ("Buttermilk", "juices-beverages", 25, True, 5, "Spiced Andhra-style majjiga, chilled and tempered.", False, False),
    ("Panakam", "juices-beverages", 25, True, 5, "Jaggery and dry-ginger cooler, a South Indian festive drink.", False, False),
    ("Tender Coconut Water", "juices-beverages", 40, True, 3, "Fresh, chilled tender coconut water.", False, False),
    ("Rose Milk", "juices-beverages", 40, True, 5, "Chilled milk flavoured with rose syrup.", False, False),
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
        for name, cat_slug, price, is_veg, prep_time, desc, popular, special in FOODS:
            slug = _slugify(name)
            result = await session.execute(select(Food).where(Food.slug == slug))
            existing = result.scalar_one_or_none()
            if existing is not None:
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
            )
            session.add(food)
            created_foods += 1
        if created_foods:
            print(f"Created {created_foods} food items")

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
