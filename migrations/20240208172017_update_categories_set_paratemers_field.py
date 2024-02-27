"""Contains a migration that updates categories by adding/removing parameters field."""

import arrow
from mongodb_migrations.base import BaseMigration

from app.services.mongo.constants import MongoCollectionsEnum


class Migration(BaseMigration):  # type: ignore
    """Migration that updates categories by adding/removing parameters field."""

    def upgrade(self) -> None:
        """Updates categories by adding parameters field."""

        # path to list of parameter machine names mapping
        categories_parameter_names = {
            "/electronics": None,
            "/electronics/computers": None,
            "/electronics/computers/desktops": [
                "brand",
                "cpu",
                "cpu_cores_number",
                "graphics_card",
                "graphics_card_type",
                "vram",
                "ram",
                "ram_type",
                "hdd",
                "hdd_space",
                "ssd",
                "ssd_space",
                "monitor",
                "monitor_screen_size",
                "class",  # for work/study, games, etc.
                "has_wifi",
                "has_bluetooth",
                "no_wireless_connection",
                "os",
                "year",
                "warranty",
                "country_of_production",
            ],
            "/electronics/computers/laptops": [
                "brand",
                "cpu",
                "cpu_cores_number",
                "graphics_card",
                "graphics_card_type",
                "vram",
                "motherboard_chipset",
                "ram",
                "ram_slots",
                "ram_type",
                "hdd",
                "hdd_space",
                "ssd",
                "ssd_space",
                "screen_type",
                "screen_resolution",
                "screen_refresh_rate",
                "screen_size",
                "battery_capacity",
                "class",  # for work/study, games, business, etc.
                "has_wifi",
                "has_bluetooth",
                "no_wireless_connection",
                "has_fingerprint_identification",
                "has_keyboard_backlight",
                "has_touch_screen",
                "os",
                "color",
                "year",
                "warranty",
                "country_of_production",
            ],
            "/electronics/computers/all-in-one": [
                "brand",
                "cpu",
                "cpu_cores_number",
                "graphics_card",
                "graphics_card_type",
                "vram",
                "motherboard_chipset",
                "ram",
                "ram_type",
                "hdd",
                "hdd_space",
                "ssd",
                "ssd_space",
                "monitor",
                "monitor_screen_size",
                "class",  # for work/study, games, etc.
                "has_wifi",
                "has_bluetooth",
                "no_wireless_connection",
                "os",
                "year",
                "warranty",
                "country_of_production",
            ],
            "/electronics/tvs": [
                "brand",
                "screen_size",
                "screen_resolution",
                "screen_refresh_rate",
                "has_smarttv",
                "has_wifi",
                "has_bluetooth",
                "platform",  # AndroidTV, AppleTV, Linux, Sony Smart TV, etc.
                "tv_tuner",
                "supports_3d",
                "supports_hdr",
                "supports_vrr",
                "sound_output_power",
                "class",  # for design, gaming, kitchen etc.
                "year",
                "warranty",
                "country_of_production",
            ],
            "/electronics/smartphones": [
                "brand",
                "cpu",
                "built_in_memory",
                "ram",
                "battery_capacity",
                "screen_size",
                "screen_resolution",
                "screen_refresh_rate",
                "class",  # protected, button_phones, smartphones, flagships, etc.
                "has_wifi",
                "has_bluetooth",
                "has_nfc",
                "has_infrared_port",
                "supports_wireless_charging",
                "has_micro_jack",
                "has_mini_jack",
                "has_apple_lightning",
                "has_usb_type_c",
                "main_camera_resolution",
                "front_camera_resolution",
                "os",
                "sim_cards_number",
                "body_material",
                "color",
                "year",
                "warranty",
                "country_of_production",
            ],
            "/electronics/game-consoles": [
                "brand",
                "platform",
                "model",
                "complete_set",
                "game_console",
                "built_in_memory",
                "ram",
                "has_disk_drive",
                "supports_vr",
                "has_touch_screen",
                "control_tool",
                "maximum_supported_resolution",
                "type",
                "color",
                "year",
                "warranty",
                "country_of_production",
            ],
            "/electronics/accessories": None,
            "/electronics/accessories/computer-accessories": None,
            "/electronics/accessories/computer-accessories/processors": [
                "brand",
                "family",
                "socket",
                "cpu_cores_number",
                "cpu_threads_number",
                "base_clock_frequency",
                "maximum_clock_frequency",
                "intel_generation",
                "amd_generation",
                "supports_integrated_graphics",
                "year",
                "warranty",
                "country_of_production",
            ],
            "/electronics/accessories/computer-accessories/hdds": [
                "brand",
                "storage",
                "type",  # inner, outer, etc.
                "connection_interface",
                "form_factor",
                "purpose",  # for desktops, laptops, etc.
                "spindle_rotation_speed",
                "technology",  # hdd, hdd + ssd, sshd
                "year",
                "warranty",
                "country_of_production",
            ],
            "/electronics/accessories/computer-accessories/ssds": [
                "brand",
                "storage",
                "type",  # inner, outer, etc.
                "connection_interface",
                "form_factor",
                "purpose",  # for desktops, laptops, etc.
                "type_of_memory_elements",
                "year",
                "warranty",
                "country_of_production",
            ],
            "/electronics/accessories/computer-accessories/ram-modules": [
                "brand",
                "memory",
                "memory_frequency",
                "memory_type",
                "purpose",
                "bar_numbers",
                "cas_latency",
                "form_factor",
                "year",
                "warranty",
                "country_of_production",
            ],
            "/electronics/accessories/computer-accessories/graphics-cards": [
                "brand",
                "graphic_chip",
                "family",
                "memory",
                "memory_bus_bit_size",
                "memory_type",
                "form_factor",
                "connection_interface",
                "purpose",
                "additional_power",
                "cooling_system_type",
                "year",
                "warranty",
                "country_of_production",
            ],
            "/electronics/accessories/computer-accessories/power-supplies": [
                "brand",
                "power",
                "supports_80_plus",
                "form_factor",
                "connector",
                "protection_technologies",
                "motherboard_power_supply",
                "voltage",
                "number_of_additional_power_connectors_for_video_cards",
                "sata_connections_number",
                "purpose",
                "cooling_system_type",
                "year",
                "warranty",
                "country_of_production",
            ],
            "/electronics/accessories/computer-accessories/motherboards": [
                "brand",
                "socket",
                "motherboard_chipset",
                "form_factor",
                "memory_types_support",
                "wireless_interface",
                "m2_connectors_number",
                "maximum_memory_frequency",
                "purpose",
                "voltage",
                "video_outputs",
                "pci_express_x16",
                "pci_express_x8",
                "pci_express_x4",
                "pci_express_x1",
                "pci",
                "network_interface",
                "usb",
                "digital_audio_jack",
                "u2_connector",
                "satae",
                "msata",
                "year",
                "warranty",
                "country_of_production",
            ],
            "/electronics/accessories/computer-accessories/cases": [
                "brand",
                "motherboard_form_factor",
                "power_of_the_power_supply",
                "installed_fans_number",
                "body_type",
                "front_panel_connectors",
                "color",
                "voltage",
                "view",
                "body_material",
                "year",
                "warranty",
                "country_of_production",
            ],
            "/electronics/accessories/computer-accessories/cooling-systems": [
                "brand",
                "purpose",
                "type",
                "fan_size",
                "maximum_tdp",
                "power_supply_connector",
                "color",
                "bearing_type",
                "cooling_system_type",
                "year",
                "warranty",
                "country_of_production",
            ],
            "/electronics/accessories/computer-accessories/keyboards": [
                "brand",
                "type",
                "connection_type",
                "connection_interface",
                "voltage",
                "color",
                "body_material",
                "year",
                "warranty",
                "country_of_production",
            ],
            "/electronics/accessories/computer-accessories/mice": [
                "brand",
                "connection_type",
                "connection_interface",
                "size",
                "buttons_number",
                "maximum_sensor_resolution",
                "type",
                "voltage",
                "color",
                "body_material",
                "year",
                "warranty",
                "country_of_production",
            ],
            "/electronics/accessories/computer-accessories/monitors": [
                "brand",
                "screen_type",
                "screen_resolution",
                "screen_refresh_rate",
                "screen_size",
                "screen_ratio",
                "connection_interface",
                "purpose",
                "color",
                "year",
                "warranty",
                "country_of_production",
            ],
            "/electronics/accessories/computer-accessories/speakers": [
                "brand",
                # Add more parameters later
                "year",
                "warranty",
                "country_of_production",
            ],
            "/electronics/accessories/computer-accessories/headsets": [
                "brand",
                # Add more parameters later
                "year",
                "warranty",
                "country_of_production",
            ],
            "/electronics/accessories/computer-accessories/webcams": [
                "brand",
                # Add more parameters later
                "year",
                "warranty",
                "country_of_production",
            ],
            "/electronics/accessories/mobile-accessories": None,
            "/electronics/accessories/mobile-accessories/cases-covers": [
                "brand",
                # Add more parameters later
                "year",
                "warranty",
                "country_of_production",
            ],
            "/electronics/accessories/mobile-accessories/screen-protectors": [
                "brand",
                # Add more parameters later
                "year",
                "warranty",
                "country_of_production",
            ],
            "/electronics/accessories/mobile-accessories/chargers-cables": [
                "brand",
                # Add more parameters later
                "year",
                "warranty",
                "country_of_production",
            ],
            "/electronics/accessories/mobile-accessories/power-banks": [
                "brand",
                # Add more parameters later
                "year",
                "warranty",
                "country_of_production",
            ],
            "/electronics/accessories/mobile-accessories/mounts-holders": [
                "brand",
                # Add more parameters later
                "year",
                "warranty",
                "country_of_production",
            ],
        }

        # all existing parameters
        parameters = {
            parameter["machine_name"]: parameter["_id"]
            for parameter in self.db[MongoCollectionsEnum.PARAMETERS.value].find(
                filter={}, projection={"_id": 1, "machine_name": 1}
            )
        }

        categories_parameter_ids = {
            category_path: [
                parameters[category_parameter]
                for category_parameter in category_parameters
            ]
            if category_parameters is not None
            else None
            for category_path, category_parameters in categories_parameter_names.items()
        }

        for category_path, category_parameters in categories_parameter_ids.items():
            self.db[MongoCollectionsEnum.CATEGORIES.value].update_one(
                filter={"path": category_path},
                update={
                    "$set": {
                        "parameters": category_parameters,
                        "updated_at": arrow.utcnow().datetime,
                    }
                },
            )

    def downgrade(self) -> None:
        """Updates categories by removing parameters field."""
        self.db[MongoCollectionsEnum.CATEGORIES.value].update_many(
            filter={},
            update={"$unset": {"parameters": ""}, "$set": {"updated_at": None}},
        )
