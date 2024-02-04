"""Contains a migration that inserts/deletes categories."""

import arrow
from bson import ObjectId
from mongodb_migrations.base import BaseMigration


class Migration(BaseMigration):  # type: ignore
    """Migration that inserts/deletes categories."""

    def upgrade(self) -> None:
        """Inserts categories."""

        # Generate ObjectIds for each category
        electronics_id = ObjectId()
        computers_id = ObjectId()
        desktops_id = ObjectId()
        laptops_id = ObjectId()
        all_in_one_id = ObjectId()
        tvs_id = ObjectId()
        smartphones_id = ObjectId()
        game_consoles_id = ObjectId()
        accessories_id = ObjectId()
        computer_accessories_id = ObjectId()
        processors_id = ObjectId()
        ssds_id = ObjectId()
        hdds_id = ObjectId()
        ram_modules_id = ObjectId()
        graphics_cards_id = ObjectId()
        power_supplies_id = ObjectId()
        motherboards_id = ObjectId()
        cases_id = ObjectId()
        cooling_systems_id = ObjectId()
        keyboards_id = ObjectId()
        mice_id = ObjectId()
        monitors_id = ObjectId()
        speakers_id = ObjectId()
        headsets_id = ObjectId()
        webcams_id = ObjectId()
        mobile_accessories_id = ObjectId()
        cases_covers_id = ObjectId()
        screen_protectors_id = ObjectId()
        chargers_cables_id = ObjectId()
        power_banks_id = ObjectId()
        mounts_holders_id = ObjectId()

        self.db["categories"].insert_many(
            [
                {
                    "_id": electronics_id,
                    "name": "Electronics",
                    "description": "Electronic devices",
                    "parent_id": None,
                    "path": "/electronics",
                    "path_name": "electronics",
                    "created_at": arrow.utcnow().datetime,
                    "updated_at": None,
                },
                {
                    "_id": computers_id,
                    "name": "Computers",
                    "description": "Computing devices",
                    "parent_id": electronics_id,
                    "path": "/electronics/computers",
                    "path_name": "computers",
                    "created_at": arrow.utcnow().datetime,
                    "updated_at": None,
                },
                {
                    "_id": desktops_id,
                    "name": "Desktop Computers",
                    "description": "Desktop PCs",
                    "parent_id": computers_id,
                    "path": "/electronics/computers/desktops",
                    "path_name": "desktops",
                    "created_at": arrow.utcnow().datetime,
                    "updated_at": None,
                },
                {
                    "_id": laptops_id,
                    "name": "Laptop Computers",
                    "description": "Laptop PCs",
                    "parent_id": computers_id,
                    "path": "/electronics/computers/laptops",
                    "path_name": "laptops",
                    "created_at": arrow.utcnow().datetime,
                    "updated_at": None,
                },
                {
                    "_id": all_in_one_id,
                    "name": "All-in-One Computers",
                    "description": "All-in-One PCs",
                    "parent_id": computers_id,
                    "path": "/electronics/computers/all-in-one",
                    "path_name": "all-in-one",
                    "created_at": arrow.utcnow().datetime,
                    "updated_at": None,
                },
                {
                    "_id": tvs_id,
                    "name": "TVs",
                    "description": "Television sets",
                    "parent_id": electronics_id,
                    "path": "/electronics/tvs",
                    "path_name": "tvs",
                    "created_at": arrow.utcnow().datetime,
                    "updated_at": None,
                },
                {
                    "_id": smartphones_id,
                    "name": "Smartphones",
                    "description": "Mobile phones",
                    "parent_id": electronics_id,
                    "path": "/electronics/smartphones",
                    "path_name": "smartphones",
                    "created_at": arrow.utcnow().datetime,
                    "updated_at": None,
                },
                {
                    "_id": game_consoles_id,
                    "name": "Game Consoles",
                    "description": "Gaming consoles",
                    "parent_id": electronics_id,
                    "path": "/electronics/game-consoles",
                    "path_name": "game-consoles",
                    "created_at": arrow.utcnow().datetime,
                    "updated_at": None,
                },
                {
                    "_id": accessories_id,
                    "name": "Accessories",
                    "description": "Electronic accessories",
                    "parent_id": electronics_id,
                    "path": "/electronics/accessories",
                    "path_name": "accessories",
                    "created_at": arrow.utcnow().datetime,
                    "updated_at": None,
                },
                {
                    "_id": computer_accessories_id,
                    "name": "Computer Accessories",
                    "description": "Accessories for computers",
                    "parent_id": accessories_id,
                    "path": "/electronics/accessories/computer-accessories",
                    "path_name": "computer-accessories",
                    "created_at": arrow.utcnow().datetime,
                    "updated_at": None,
                },
                {
                    "_id": processors_id,
                    "name": "Processors",
                    "description": "Computer processors",
                    "parent_id": computer_accessories_id,
                    "path": "/electronics/accessories/computer-accessories/processors",
                    "path_name": "processors",
                    "created_at": arrow.utcnow().datetime,
                    "updated_at": None,
                },
                {
                    "_id": hdds_id,
                    "name": "HDDs",
                    "description": "Hard disk drives",
                    "parent_id": computer_accessories_id,
                    "path": "/electronics/accessories/computer-accessories/hdds",
                    "path_name": "hdds",
                    "created_at": arrow.utcnow().datetime,
                    "updated_at": None,
                },
                {
                    "_id": ssds_id,
                    "name": "SSDs",
                    "description": "Solid-state drives",
                    "parent_id": computer_accessories_id,
                    "path": "/electronics/accessories/computer-accessories/ssds",
                    "path_name": "ssds",
                    "created_at": arrow.utcnow().datetime,
                    "updated_at": None,
                },
                {
                    "_id": ram_modules_id,
                    "name": "RAM Modules",
                    "description": "Computer RAM modules",
                    "parent_id": computer_accessories_id,
                    "path": "/electronics/accessories/computer-accessories/ram-modules",
                    "path_name": "ram-modules",
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
                    "path_name": "graphics-cards",
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
                    "path_name": "power-supplies",
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
                    "path_name": "motherboards",
                    "created_at": arrow.utcnow().datetime,
                    "updated_at": None,
                },
                {
                    "_id": cases_id,
                    "name": "Cases",
                    "description": "Computer cases",
                    "parent_id": computer_accessories_id,
                    "path": "/electronics/accessories/computer-accessories/cases",
                    "path_name": "cases",
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
                    "path_name": "cooling-systems",
                    "created_at": arrow.utcnow().datetime,
                    "updated_at": None,
                },
                {
                    "_id": keyboards_id,
                    "name": "Keyboards",
                    "description": "Computer keyboards",
                    "parent_id": computer_accessories_id,
                    "path": "/electronics/accessories/computer-accessories/keyboards",
                    "path_name": "keyboards",
                    "created_at": arrow.utcnow().datetime,
                    "updated_at": None,
                },
                {
                    "_id": mice_id,
                    "name": "Mice",
                    "description": "Computer mice",
                    "parent_id": computer_accessories_id,
                    "path": "/electronics/accessories/computer-accessories/mice",
                    "path_name": "mice",
                    "created_at": arrow.utcnow().datetime,
                    "updated_at": None,
                },
                {
                    "_id": monitors_id,
                    "name": "Monitors",
                    "description": "Computer monitors",
                    "parent_id": computer_accessories_id,
                    "path": "/electronics/accessories/computer-accessories/monitors",
                    "path_name": "monitors",
                    "created_at": arrow.utcnow().datetime,
                    "updated_at": None,
                },
                {
                    "_id": speakers_id,
                    "name": "Speakers",
                    "description": "Computer speakers",
                    "parent_id": computer_accessories_id,
                    "path": "/electronics/accessories/computer-accessories/speakers",
                    "path_name": "speakers",
                    "created_at": arrow.utcnow().datetime,
                    "updated_at": None,
                },
                {
                    "_id": headsets_id,
                    "name": "Headsets",
                    "description": "Computer headsets",
                    "parent_id": computer_accessories_id,
                    "path": "/electronics/accessories/computer-accessories/headsets",
                    "path_name": "headsets",
                    "created_at": arrow.utcnow().datetime,
                    "updated_at": None,
                },
                {
                    "_id": webcams_id,
                    "name": "Webcams",
                    "description": "Computer webcams",
                    "parent_id": computer_accessories_id,
                    "path": "/electronics/accessories/computer-accessories/webcams",
                    "path_name": "webcams",
                    "created_at": arrow.utcnow().datetime,
                    "updated_at": None,
                },
                {
                    "_id": mobile_accessories_id,
                    "name": "Mobile Accessories",
                    "description": "Accessories for mobile devices",
                    "parent_id": accessories_id,
                    "path": "/electronics/accessories/mobile-accessories",
                    "path_name": "mobile-accessories",
                    "created_at": arrow.utcnow().datetime,
                    "updated_at": None,
                },
                {
                    "_id": cases_covers_id,
                    "name": "Cases and Covers",
                    "description": "Cases and covers for mobile devices",
                    "parent_id": mobile_accessories_id,
                    "path": "/electronics/accessories/mobile-accessories/cases-covers",
                    "path_name": "cases-covers",
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
                    "path_name": "screen-protectors",
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
                    "path_name": "chargers-cables",
                    "created_at": arrow.utcnow().datetime,
                    "updated_at": None,
                },
                {
                    "_id": power_banks_id,
                    "name": "Power Banks",
                    "description": "Power banks for mobile devices",
                    "parent_id": mobile_accessories_id,
                    "path": "/electronics/accessories/mobile-accessories/power-banks",
                    "path_name": "power-banks",
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
                    "path_name": "mounts-holders",
                    "created_at": arrow.utcnow().datetime,
                    "updated_at": None,
                },
            ]
        )

    def downgrade(self) -> None:
        """Drops categories."""
        self.db["categories"].delete_many(filter={})
