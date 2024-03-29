"""Contains a migration that inserts/deletes categories."""

import arrow
from bson import ObjectId
from mongodb_migrations.base import BaseMigration

from app.services.mongo.constants import MongoCollectionsEnum


class Migration(BaseMigration):  # type: ignore
    """Migration that inserts/deletes categories."""

    def upgrade(self) -> None:
        """Inserts categories."""

        # Generate ObjectIds for each category
        electronics_id = ObjectId("65d24f2a260fb739c605b28a")
        computers_id = ObjectId("65d24f2a260fb739c605b28b")
        desktops_id = ObjectId("65d24f2a260fb739c605b28c")
        laptops_id = ObjectId("65d24f2a260fb739c605b28d")
        all_in_one_id = ObjectId("65d24f2a260fb739c605b28e")
        tvs_id = ObjectId("65d24f2a260fb739c605b28f")
        smartphones_id = ObjectId("65d24f2a260fb739c605b290")
        game_consoles_id = ObjectId("65d24f2a260fb739c605b291")
        accessories_id = ObjectId("65d24f2a260fb739c605b292")
        computer_accessories_id = ObjectId("65d24f2a260fb739c605b293")
        processors_id = ObjectId("65d24f2a260fb739c605b294")
        hdds_id = ObjectId("65d24f2a260fb739c605b295")
        ssds_id = ObjectId("65d24f2a260fb739c605b296")
        ram_modules_id = ObjectId("65d24f2a260fb739c605b297")
        graphics_cards_id = ObjectId("65d24f2a260fb739c605b298")
        power_supplies_id = ObjectId("65d24f2a260fb739c605b299")
        motherboards_id = ObjectId("65d24f2a260fb739c605b29a")
        cases_id = ObjectId("65d24f2a260fb739c605b29b")
        cooling_systems_id = ObjectId("65d24f2a260fb739c605b29c")
        keyboards_id = ObjectId("65d24f2a260fb739c605b29d")
        mice_id = ObjectId("65d24f2a260fb739c605b29e")
        monitors_id = ObjectId("65d24f2a260fb739c605b29f")
        speakers_id = ObjectId("65d24f2a260fb739c605b2a0")
        headsets_id = ObjectId("65d24f2a260fb739c605b2a1")
        webcams_id = ObjectId("65d24f2a260fb739c605b2a2")
        mobile_accessories_id = ObjectId("65d24f2a260fb739c605b2a3")
        cases_covers_id = ObjectId("65d24f2a260fb739c605b2a4")
        screen_protectors_id = ObjectId("65d24f2a260fb739c605b2a5")
        chargers_cables_id = ObjectId("65d24f2a260fb739c605b2a6")
        power_banks_id = ObjectId("65d24f2a260fb739c605b2a7")
        mounts_holders_id = ObjectId("65d24f2a260fb739c605b2a8")

        self.db[MongoCollectionsEnum.CATEGORIES].insert_many(
            [
                {
                    "_id": electronics_id,
                    "name": "Electronics",
                    "description": "Electronic devices",
                    "parent_id": None,
                    "path": "/electronics",
                    "machine_name": "electronics",
                    "created_at": arrow.utcnow().datetime,
                    "updated_at": None,
                },
                {
                    "_id": computers_id,
                    "name": "Computers",
                    "description": "Computing devices",
                    "parent_id": electronics_id,
                    "path": "/electronics/computers",
                    "machine_name": "computers",
                    "created_at": arrow.utcnow().datetime,
                    "updated_at": None,
                },
                {
                    "_id": desktops_id,
                    "name": "Desktop Computers",
                    "description": "Desktop PCs",
                    "parent_id": computers_id,
                    "path": "/electronics/computers/desktops",
                    "machine_name": "desktops",
                    "created_at": arrow.utcnow().datetime,
                    "updated_at": None,
                },
                {
                    "_id": laptops_id,
                    "name": "Laptop Computers",
                    "description": "Laptop PCs",
                    "parent_id": computers_id,
                    "path": "/electronics/computers/laptops",
                    "machine_name": "laptops",
                    "created_at": arrow.utcnow().datetime,
                    "updated_at": None,
                },
                {
                    "_id": all_in_one_id,
                    "name": "All-in-One Computers",
                    "description": "All-in-One PCs",
                    "parent_id": computers_id,
                    "path": "/electronics/computers/all-in-one",
                    "machine_name": "all-in-one",
                    "created_at": arrow.utcnow().datetime,
                    "updated_at": None,
                },
                {
                    "_id": tvs_id,
                    "name": "TVs",
                    "description": "Television sets",
                    "parent_id": electronics_id,
                    "path": "/electronics/tvs",
                    "machine_name": "tvs",
                    "created_at": arrow.utcnow().datetime,
                    "updated_at": None,
                },
                {
                    "_id": smartphones_id,
                    "name": "Smartphones",
                    "description": "Mobile phones",
                    "parent_id": electronics_id,
                    "path": "/electronics/smartphones",
                    "machine_name": "smartphones",
                    "created_at": arrow.utcnow().datetime,
                    "updated_at": None,
                },
                {
                    "_id": game_consoles_id,
                    "name": "Game Consoles",
                    "description": "Gaming consoles",
                    "parent_id": electronics_id,
                    "path": "/electronics/game-consoles",
                    "machine_name": "game-consoles",
                    "created_at": arrow.utcnow().datetime,
                    "updated_at": None,
                },
                {
                    "_id": accessories_id,
                    "name": "Accessories",
                    "description": "Electronic accessories",
                    "parent_id": electronics_id,
                    "path": "/electronics/accessories",
                    "machine_name": "accessories",
                    "created_at": arrow.utcnow().datetime,
                    "updated_at": None,
                },
                {
                    "_id": computer_accessories_id,
                    "name": "Computer Accessories",
                    "description": "Accessories for computers",
                    "parent_id": accessories_id,
                    "path": "/electronics/accessories/computer-accessories",
                    "machine_name": "computer-accessories",
                    "created_at": arrow.utcnow().datetime,
                    "updated_at": None,
                },
                {
                    "_id": processors_id,
                    "name": "Processors",
                    "description": "Computer processors",
                    "parent_id": computer_accessories_id,
                    "path": "/electronics/accessories/computer-accessories/processors",
                    "machine_name": "processors",
                    "created_at": arrow.utcnow().datetime,
                    "updated_at": None,
                },
                {
                    "_id": hdds_id,
                    "name": "HDDs",
                    "description": "Hard disk drives",
                    "parent_id": computer_accessories_id,
                    "path": "/electronics/accessories/computer-accessories/hdds",
                    "machine_name": "hdds",
                    "created_at": arrow.utcnow().datetime,
                    "updated_at": None,
                },
                {
                    "_id": ssds_id,
                    "name": "SSDs",
                    "description": "Solid-state drives",
                    "parent_id": computer_accessories_id,
                    "path": "/electronics/accessories/computer-accessories/ssds",
                    "machine_name": "ssds",
                    "created_at": arrow.utcnow().datetime,
                    "updated_at": None,
                },
                {
                    "_id": ram_modules_id,
                    "name": "RAM Modules",
                    "description": "Computer RAM modules",
                    "parent_id": computer_accessories_id,
                    "path": "/electronics/accessories/computer-accessories/ram-modules",
                    "machine_name": "ram-modules",
                    "created_at": arrow.utcnow().datetime,
                    "updated_at": None,
                },
                {
                    "_id": graphics_cards_id,
                    "name": "Graphics Cards",
                    "description": "Computer graphics cards",
                    "parent_id": computer_accessories_id,
                    "path": (
                        "/electronics/accessories/computer-accessories/graphics-cards"
                    ),
                    "machine_name": "graphics-cards",
                    "created_at": arrow.utcnow().datetime,
                    "updated_at": None,
                },
                {
                    "_id": power_supplies_id,
                    "name": "Power Supplies",
                    "description": "Computer power supplies",
                    "parent_id": computer_accessories_id,
                    "path": (
                        "/electronics/accessories/computer-accessories/power-supplies"
                    ),
                    "machine_name": "power-supplies",
                    "created_at": arrow.utcnow().datetime,
                    "updated_at": None,
                },
                {
                    "_id": motherboards_id,
                    "name": "Motherboards",
                    "description": "Computer motherboards",
                    "parent_id": computer_accessories_id,
                    "path": (
                        "/electronics/accessories/computer-accessories/motherboards"
                    ),
                    "machine_name": "motherboards",
                    "created_at": arrow.utcnow().datetime,
                    "updated_at": None,
                },
                {
                    "_id": cases_id,
                    "name": "Cases",
                    "description": "Computer cases",
                    "parent_id": computer_accessories_id,
                    "path": "/electronics/accessories/computer-accessories/cases",
                    "machine_name": "cases",
                    "created_at": arrow.utcnow().datetime,
                    "updated_at": None,
                },
                {
                    "_id": cooling_systems_id,
                    "name": "Cooling Systems",
                    "description": "Computer cooling systems",
                    "parent_id": computer_accessories_id,
                    "path": (
                        "/electronics/accessories/computer-accessories/cooling-systems"
                    ),
                    "machine_name": "cooling-systems",
                    "created_at": arrow.utcnow().datetime,
                    "updated_at": None,
                },
                {
                    "_id": keyboards_id,
                    "name": "Keyboards",
                    "description": "Computer keyboards",
                    "parent_id": computer_accessories_id,
                    "path": "/electronics/accessories/computer-accessories/keyboards",
                    "machine_name": "keyboards",
                    "created_at": arrow.utcnow().datetime,
                    "updated_at": None,
                },
                {
                    "_id": mice_id,
                    "name": "Mice",
                    "description": "Computer mice",
                    "parent_id": computer_accessories_id,
                    "path": "/electronics/accessories/computer-accessories/mice",
                    "machine_name": "mice",
                    "created_at": arrow.utcnow().datetime,
                    "updated_at": None,
                },
                {
                    "_id": monitors_id,
                    "name": "Monitors",
                    "description": "Computer monitors",
                    "parent_id": computer_accessories_id,
                    "path": "/electronics/accessories/computer-accessories/monitors",
                    "machine_name": "monitors",
                    "created_at": arrow.utcnow().datetime,
                    "updated_at": None,
                },
                {
                    "_id": speakers_id,
                    "name": "Speakers",
                    "description": "Computer speakers",
                    "parent_id": computer_accessories_id,
                    "path": "/electronics/accessories/computer-accessories/speakers",
                    "machine_name": "speakers",
                    "created_at": arrow.utcnow().datetime,
                    "updated_at": None,
                },
                {
                    "_id": headsets_id,
                    "name": "Headsets",
                    "description": "Computer headsets",
                    "parent_id": computer_accessories_id,
                    "path": "/electronics/accessories/computer-accessories/headsets",
                    "machine_name": "headsets",
                    "created_at": arrow.utcnow().datetime,
                    "updated_at": None,
                },
                {
                    "_id": webcams_id,
                    "name": "Webcams",
                    "description": "Computer webcams",
                    "parent_id": computer_accessories_id,
                    "path": "/electronics/accessories/computer-accessories/webcams",
                    "machine_name": "webcams",
                    "created_at": arrow.utcnow().datetime,
                    "updated_at": None,
                },
                {
                    "_id": mobile_accessories_id,
                    "name": "Mobile Accessories",
                    "description": "Accessories for mobile devices",
                    "parent_id": accessories_id,
                    "path": "/electronics/accessories/mobile-accessories",
                    "machine_name": "mobile-accessories",
                    "created_at": arrow.utcnow().datetime,
                    "updated_at": None,
                },
                {
                    "_id": cases_covers_id,
                    "name": "Cases and Covers",
                    "description": "Cases and covers for mobile devices",
                    "parent_id": mobile_accessories_id,
                    "path": "/electronics/accessories/mobile-accessories/cases-covers",
                    "machine_name": "cases-covers",
                    "created_at": arrow.utcnow().datetime,
                    "updated_at": None,
                },
                {
                    "_id": screen_protectors_id,
                    "name": "Screen Protectors",
                    "description": "Screen protectors for mobile devices",
                    "parent_id": mobile_accessories_id,
                    "path": (
                        "/electronics/accessories/mobile-accessories/screen-protectors"
                    ),
                    "machine_name": "screen-protectors",
                    "created_at": arrow.utcnow().datetime,
                    "updated_at": None,
                },
                {
                    "_id": chargers_cables_id,
                    "name": "Chargers and Cables",
                    "description": "Chargers and cables for mobile devices",
                    "parent_id": mobile_accessories_id,
                    "path": (
                        "/electronics/accessories/mobile-accessories/chargers-cables"
                    ),
                    "machine_name": "chargers-cables",
                    "created_at": arrow.utcnow().datetime,
                    "updated_at": None,
                },
                {
                    "_id": power_banks_id,
                    "name": "Power Banks",
                    "description": "Power banks for mobile devices",
                    "parent_id": mobile_accessories_id,
                    "path": "/electronics/accessories/mobile-accessories/power-banks",
                    "machine_name": "power-banks",
                    "created_at": arrow.utcnow().datetime,
                    "updated_at": None,
                },
                {
                    "_id": mounts_holders_id,
                    "name": "Mounts and Holders",
                    "description": "Mounts and holders for mobile devices",
                    "parent_id": mobile_accessories_id,
                    "path": (
                        "/electronics/accessories/mobile-accessories/mounts-holders"
                    ),
                    "machine_name": "mounts-holders",
                    "created_at": arrow.utcnow().datetime,
                    "updated_at": None,
                },
            ]
        )

    def downgrade(self) -> None:
        """Drops categories."""
        self.db[MongoCollectionsEnum.CATEGORIES].delete_many(filter={})
