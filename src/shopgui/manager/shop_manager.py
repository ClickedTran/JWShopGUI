import os
import json
from endstone import Player

from shopgui.language.language import LanguageManager

class ShopManager:
    editMode = {}

    def __init__(self, plugin):
        self.plugin = plugin
        self.shops = {}
        self.load_shops()

    def load_shops(self):
        shops_file = os.path.join(self.plugin.data_folder, "shops.json")
        if os.path.exists(shops_file):
            with open(shops_file, "r", encoding="utf-8") as f:
                self.shops = json.load(f)

    def save_all(self):
        shops_file = os.path.join(self.plugin.data_folder, "shops.json")
        os.makedirs(self.plugin.data_folder, exist_ok=True)
        with open(shops_file, "w", encoding="utf-8") as f:
            json.dump(self.shops, f, indent=4, ensure_ascii=False)

    def get_all(self) -> dict:
        return self.shops

    def exists(self, shop_name: str) -> bool:
        return shop_name in self.shops

    def create(self, shop_name: str, icon: str, slot: int = 0):
        self.shops[shop_name] = {
            "icon": icon,
            "slot": slot,
            "items": {}
        }
        self.save_all()

    def remove(self, shop_name: str):
        if shop_name in self.shops:
            del self.shops[shop_name]
            self.save_all()
    
    def reload(self) -> bool:
        shops_file = os.path.join(self.plugin.data_folder, "shops.json")
        if not os.path.exists(shops_file):
            self.save_all()
            return True

        try:
            with open(shops_file, "r", encoding="utf-8") as f:
                new_data = json.load(f)
                
            if not isinstance(new_data, dict):
                return False

            for shop_name, shop_config in new_data.items():
                if shop_name not in self.shops:
                    self.shops[shop_name] = shop_config
                else:
                    self.shops[shop_name]["icon"] = shop_config.get("icon", self.shops[shop_name]["icon"])
                    self.shops[shop_name]["slot"] = shop_config.get("slot", self.shops[shop_name]["slot"])
                    
                    if "items" in shop_config:
                        self.shops[shop_name]["items"].update(shop_config["items"])
            
            self.plugin.logger.info(LanguageManager.get_translate("plugin_info.update_item.success"))
            return True
            
        except Exception as e:
            self.plugin.logger.error(LanguageManager.get_translate("plugin_info.update_item.error", [e]))
            return False

    def getItems(self, shop_name: str) -> dict:
        shop_name = self.shops.get(shop_name)
        if not shop_name:
            self.plugin.logger.error(LanguageManager.get_translate("plugin_info.shop_data_not_found", [shop_name]))
            return {} 
        
        return shop_name.get("items", {})

    def addItem(self, shop_name: str, item_name: str, buy: int, sell: int):
        if not item_name.startswith("minecraft:"):
            item_name = "minecraft:" + item_name

        self.shops.get(shop_name)["items"][item_name] = f"{buy}:{sell}"
        self.save_all()

    def removeItem(self, shop_name: str, item_name_or_slot: str) -> tuple[bool, str, str]:
        items = self.getItems(shop_name)
        if not items:
            return False, "error", item_name_or_slot

        if item_name_or_slot.isdigit():
            item_to_remove = None
            for slot, [name, key] in enumerate(items.items()):
                if slot == int(item_name_or_slot):
                    item_to_remove = name
                    break
            
            if item_to_remove and item_to_remove in self.shops[shop_name]["items"]:
                del self.shops[shop_name]["items"][item_to_remove]
                self.save_all()
                return True, "slot", item_name_or_slot
            else:
                return False, "slot", item_name_or_slot
        else:
            clean_item_name = item_name_or_slot
            if not clean_item_name.startswith("minecraft:"):
                clean_item_name = f"minecraft:{clean_item_name}"

            if clean_item_name in self.shops[shop_name]["items"]:
                del self.shops[shop_name]["items"][clean_item_name]
                self.save_all()
                return True, "name", clean_item_name
            else:
                return False, "name", clean_item_name
    
    def get_money(self, player: Player, type: str, callback) -> None:
        uuid = str(player.unique_id)
        async def task():
            try:
                balance = await self.plugin.get_economy_api().get_api().get_balance(uuid, type)
                self.plugin.server.scheduler.run_task(self.plugin, lambda: callback(balance))
            except Exception as e:
                self.plugin.logger.error(f"Error fetching balance: {e}")
            return
        
        self.plugin.get_economy_api().run_async(task())

    def add_money(self, player: Player, type: str, amount: float, callback) -> None:
        uuid = str(player.unique_id)
        async def task():
            try:
                balance = await self.plugin.get_economy_api().get_api().add_balance(uuid, amount, type)
                self.plugin.server.scheduler.run_task(self.plugin, lambda: callback(balance))
            except Exception as e:
                self.plugin.logger.error(f"Error fetching balance: {e}")
        self.plugin.get_economy_api().run_async(task())

    def reduce_money(self, player: Player, type: str, amount: float, callback) -> None:
        uuid = str(player.unique_id)
        async def task():
            try:
                balance = await self.plugin.get_economy_api().get_api().remove_balance(uuid, amount, type)
                self.plugin.server.scheduler.run_task(self.plugin, lambda: callback(balance))
            except Exception as e:
                self.plugin.logger.error(f"Error fetching balance: {e}")
        self.plugin.get_economy_api().run_async(task())
    
    def has_money(self, player: Player, type: str, amount: float, callback) -> None:
        uuid = str(player.unique_id)
        async def task():
            try:
                balance = await self.plugin.get_economy_api().get_api().get_balance(uuid, type)
                has_enough = float(balance) >= amount
                self.plugin.server.scheduler.run_task(self.plugin, lambda: callback(has_enough))
            except Exception as e:
                self.plugin.logger.error(f"Error fetching balance: {e}")
                self.plugin.server.scheduler.run_task(self.plugin, lambda: callback(False))
        return self.plugin.get_economy_api().run_async(task())