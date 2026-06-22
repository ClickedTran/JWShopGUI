import os
import json
from typing import Union, List, Any

class LanguageManager:
    # Các biến static (Class variables) tương đương với private static trong PHP
    _plugin = None
    _lang_data: dict = {}
    _lang_file_path: str = ""

    def __init__(self, plugin):
        # Nạp cứng dữ liệu vào biến Class để tất cả các hàm @classmethod ở dưới đều với tới được
        LanguageManager._plugin = plugin
        LanguageManager._lang_file_path = os.path.join(plugin.data_folder, "messages.json")
        
        # Tiến hành tạo file và nạp ngôn ngữ
        self.generate_default_file()
        self.load_language()
    
    def base_language(self) -> dict:
        return {
            "version": 1,
            "plugin_info": {
              "reload_language": "§aSuccessfully reloaded language: %1",
              "message_not_found": "§cMessage not found: %1",
              "economy_not_found": "JWEconomy plugin not found! Please ensure JWEconomy is installed and enabled.",
              "no_permission": "You do not have permission to use this command!",
              "use_ingame": "This command can only be used by players!",
              "update_item": {
                "success": "§aSuccessfully updated config data from shops.json to RAM!",
                "error": "Error reading config file to reload: %1"
              },
              "shop_data_not_found": "Could not find configuration for shop named: %1",
              "command": {
                "create": {
                  "success": "Shop %1 has been successfully created!",
                  "usage": "Usage: /shop create <shop_name> <slot> <icon>, where <slot> must be an integer",
                  "error_1": "You must hold an item to use as the shop icon or provide the item name in the command!",
                  "error_2": "Shop already exists!"
                },
                "remove": {
                  "success": "Shop %1 has been successfully removed!",
                  "usage": "Usage: /shop remove <shop_name>",
                  "error_1": "Shop does not exist!"
                },
                "setup": {
                  "usage": "Usage: /shop setup <shop_name>",
                  "error": "Shop does not exist!",
                  "join_title": "§6>> You have entered edit mode for shop %1 <<",
                  "join_help": [
                    "§1§7help§r§7 - Display available commands",
                    "§1§7done§r§7 - Save and exit edit mode"
                  ],
                  "help": [
                    "§6>> All edit commands <<",
                    "§1§7help§r§7 - Display available commands",
                    "§1§7add <item_name> <buy_price> <sell_price>§r§7 - Add an item to the shop with buy and sell prices",
                    "§1§7remove <item_name | slot>§r§7 - Remove an item from the shop",
                    "§1§7done§r§7 - Save and exit edit mode"
                  ],
                  "add": {
                    "success": "§aItem %1 has been added to shop %2 with buy price %3 and sell price %4",
                    "error": "§cBuy price and sell price must be numbers"
                  },
                  "remove": {
                    "success_1": "§aItem at slot %1 has been removed!",
                    "success_2": "§aItem named %1 has been removed!",
                    "error_1": "§cCould not find item at slot %1!",
                    "error_2": "§cCould not find item named %1!"
                  },
                  "done": "§6You have exited edit mode for shop §a%1"
                }
              },
              "prefix": "§l§e[ShopGUI] §r",
              "player_money": "§aCurrent balance: %1 xu",
              "menu": {
                "name": "ShopGUI - MENU",
                "category": {
                  "name": "SHOP %1 - Page %2/%3",
                  "lore": {
                    "buy": "§q•• §1§6BUY:§o§7 %1",
                    "sell": "§w•• §1§6SELL:§o§7 %1",
                    "open": "§bCLICK TO OPEN SHOP"
                  }
                },
                "stack": {
                  "name": "Bulk Buy | Sell",
                  "barrier": "§1§b<-- BUY | SELL -->",
                  "buy": "Buy x%1 Stack",
                  "sell": "Sell x%1 Stack"
                },
                "not_found": "There is no shop in this slot!",
                "open": "CLICK TO OPEN SHOP"
              },
              "confirm": {
                "name": "CONFIRM TRANSACTION",
                "add_count": "ADD",
                "reduce_count": "REMOVE",
                "buy_item": "§l§aConfirm Purchase",
                "sell_item": "§l§aConfirm Sale",
                "custom": "§l§cBulk Buy/Sell"
              },
              "page": {
                "next": "Next Page",
                "previous": "Previous Page",
                "back_to_shop": "Back to shop list"
              },
              "errors": {
                "no_room": "§cNot enough space in inventory to buy this item!",
                "no_money": "§cYou do not have enough %1 xu to buy this item!",
                "no_items_to_sell": "§cYou do not have enough of this item in your inventory to sell!",
                "price_is_none": "Cannot determine the price of this item!"
              },
              "success": {
                "buy": "§aYou have successfully bought %1x %2 for %3 xu!",
                "sell": "§aYou have successfully sold %1x %2 for %3 xu!",
                "balance": "Your current balance: %1 xu"
              },
              "button": {
                "buy_item": "BUY",
                "buy_stack": "Buy x",
                "sell_item": "SELL",
                "sell_stack": "Sell x"
              }
            }
        }

    def generate_default_file(self) -> None:
        """Tự động tạo file ngôn ngữ gốc (Base) nếu người dùng cài plugin lần đầu"""
        if not os.path.exists(LanguageManager._plugin.data_folder):
            os.makedirs(LanguageManager._plugin.data_folder)
            
        if not os.path.exists(LanguageManager._lang_file_path):
            base_content = self.base_language()
            with open(LanguageManager._lang_file_path, "w", encoding="utf-8") as f:
                json.dump(base_content, f, indent=4, ensure_ascii=False)
            LanguageManager._plugin.logger.info("The default language file (messages.json) has been initialized!")

    def load_language(self) -> None:
        if os.path.exists(LanguageManager._lang_file_path):
            try:
                with open(LanguageManager._lang_file_path, "r", encoding="utf-8") as f:
                    LanguageManager._lang_data = json.load(f)
            except Exception as e:
                LanguageManager._plugin.logger.error(f"Error reading file messages.json: {e}")

    @staticmethod
    def _get_nested(data: dict, path: str) -> Any:
        """Hàm helper mô phỏng y hệt hàm getNested() của PocketMine Config"""
        keys = path.split(".")
        current = data
        for key in keys:
            if isinstance(current, dict) and key in current:
                current = current[key]
            else:
                return None
        return current

    @classmethod
    def get_translate(cls, text: Union[str, int], args: List[Any] = None) -> str:
        """Hàm lấy dịch thuật chuỗi lồng nhau và format biến %1, %2..."""
        if args is None:
            args = []
            
        data = cls._lang_data
        path = str(text)
        
        # Tự động lấy Prefix ra đập vào đầu câu
        prefix = cls._get_nested(data, "prefix") or ""
        message = cls._get_nested(data, path)
        
        if message is not None:
            message = str(message)
            for i, val in enumerate(args):
                message = message.replace(f"%{i + 1}", str(val))
            return f"{message}"
        else:
            if path == "plugin_info.message_not_found":
                return f"{prefix}§c[Fatal Error] System error key not found in data!"
            
            return cls.get_translate(
                "plugin_info.message_not_found", 
                [text]
            )
    
    @classmethod
    def get_raw(cls, path: str) -> str:
        """Lấy chuỗi thô từ file ngôn ngữ ra (Không format, không prefix)"""
        data = cls._lang_data
        path = str(path)
        
        message = cls._get_nested(data, path)
        if message is not None:
            if isinstance(message, list):
                return "\n".join(str(line) for line in message)
            return str(message)
        return ""

    @classmethod
    def get_plugin(cls):
        return cls._plugin

    @classmethod
    def get_lang_data(cls) -> dict:
        return cls._lang_data
