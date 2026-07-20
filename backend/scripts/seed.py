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

CAMPUS_ZONE_NAME = "IIT Guwahati Campus"

# Real IIT Guwahati campus boundary — OSM way 52435139 (amenity=university),
# fetched via Nominatim (polygon_geojson=1) and verified against Wikipedia's
# stated campus area (703.95 acres): this polygon encloses ~661 acres, within
# ~6% of that figure. [lng, lat] pairs per GeoJSON. Crowd-sourced OSM data, not
# an official surveyed boundary — good enough for "is this address on campus,"
# not survey-grade precision at the fence line.
IIT_GUWAHATI_POLYGON = [
    [91.6860336, 26.1907383], [91.6869961, 26.188822], [91.6871906, 26.1887857], [91.6876201, 26.1889114],
    [91.6879701, 26.1886482], [91.6879338, 26.1884217], [91.6879575, 26.1881055], [91.6878401, 26.1879838],
    [91.6877986, 26.1878973], [91.687805, 26.1877978], [91.6879057, 26.187628], [91.6880152, 26.1875013],
    [91.6881628, 26.187464], [91.6882875, 26.1875032], [91.688373, 26.1875588], [91.6884173, 26.1876044],
    [91.6885038, 26.1875984], [91.6885602, 26.1875486], [91.6885697, 26.1868499], [91.688496, 26.1867793],
    [91.6882907, 26.1861138], [91.6882277, 26.18577], [91.6882039, 26.1854505], [91.6880991, 26.184974],
    [91.6877908, 26.1850028], [91.6876442, 26.1842111], [91.6878388, 26.1841867], [91.6879127, 26.1844508],
    [91.6883143, 26.1845664], [91.6887774, 26.1845342], [91.6890297, 26.1844118], [91.689097, 26.1839997],
    [91.6889776, 26.1836908], [91.6886659, 26.1834841], [91.6892295, 26.1828537], [91.6907643, 26.1828665],
    [91.6907517, 26.1825515], [91.6919667, 26.1825645], [91.6942149, 26.1823597], [91.6954533, 26.1829844],
    [91.6960507, 26.1833633], [91.6961716, 26.18344], [91.6972615, 26.1838702], [91.6983454, 26.1841817],
    [91.6984266, 26.1842675], [91.6987423, 26.1843662], [91.6986736, 26.1846903], [91.6993897, 26.1849478],
    [91.6995787, 26.185239], [91.6996683, 26.1852584], [91.699633, 26.1854985], [91.7001382, 26.1855322],
    [91.7001322, 26.1857592], [91.7003543, 26.1857748], [91.7002692, 26.1863634], [91.7005867, 26.1864288],
    [91.7007131, 26.186439], [91.7008878, 26.1864798], [91.7011355, 26.1865429], [91.7011705, 26.1876173],
    [91.7017054, 26.1878701], [91.7032221, 26.1884086], [91.7032394, 26.1886021], [91.7032048, 26.1887766],
    [91.7042369, 26.1890344], [91.7038741, 26.1899702], [91.7038142, 26.19041], [91.703592, 26.1904727],
    [91.7033674, 26.1909644], [91.7032217, 26.1916938], [91.7028088, 26.191687], [91.7028387, 26.1932637],
    [91.7027258, 26.1963039], [91.7026511, 26.1979115], [91.7017923, 26.1973709], [91.7013798, 26.1971565],
    [91.7010097, 26.1970918], [91.700608, 26.19695], [91.7005196, 26.1969094], [91.7004708, 26.196887],
    [91.7004586, 26.1967565], [91.6995071, 26.1966866], [91.6989596, 26.1967208], [91.698782, 26.1972953],
    [91.6987872, 26.1984653], [91.6987814, 26.1988156], [91.6987921, 26.1989906], [91.6975047, 26.2018409],
    [91.6914462, 26.2006016], [91.6912617, 26.2005445], [91.6911165, 26.2004252], [91.6900889, 26.1985426],
    [91.6894991, 26.1987565], [91.6875529, 26.1979566], [91.6875634, 26.1971261], [91.6874281, 26.1964215],
    [91.687402, 26.1961487], [91.6872113, 26.1959634], [91.6871987, 26.195455], [91.6866486, 26.193324],
    [91.6860336, 26.1907383],
]


def _campus_polygon() -> str:
    return json.dumps({"type": "Polygon", "coordinates": [IIT_GUWAHATI_POLYGON]})


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

        # Campus delivery zone — there's only ever one "main" active zone, so
        # look up any active zone rather than by name (an earlier seed run may
        # have created one under an old placeholder name).
        result = await session.execute(select(DeliveryZone).where(DeliveryZone.is_active.is_(True)))
        zone = result.scalars().first()
        campus_polygon = _campus_polygon()
        if zone is None:
            zone = DeliveryZone(
                id=uuid.uuid4(),
                name=CAMPUS_ZONE_NAME,
                polygon_geojson=campus_polygon,
                is_active=True,
            )
            session.add(zone)
            print(f"Created delivery zone: {CAMPUS_ZONE_NAME}")
        elif zone.name != CAMPUS_ZONE_NAME or zone.polygon_geojson != campus_polygon:
            zone.name = CAMPUS_ZONE_NAME
            zone.polygon_geojson = campus_polygon
            print(f"Updated existing delivery zone to real boundary: {CAMPUS_ZONE_NAME}")

        await session.commit()
        print("Seed complete.")


if __name__ == "__main__":
    asyncio.run(seed())
