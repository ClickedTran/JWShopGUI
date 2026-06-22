import asyncio
from typing import Callable
import os

from endstone.plugin import Plugin
from endstone.command import Command, CommandSender
from endstone import Player

from jweconomy.main import JWEconomy

from shopgui.menu.shop_menu import ShopMenu
from shopgui.manager.shop_manager import ShopManager
from shopgui.listener import EventListener
from shopgui.language.language import LanguageManager

class ShopGUI(Plugin):
    api_version = "0.5"
    prefix = "ShopGUI"
    commands = {
        "shopgui": {
            "description": "Mở menu cửa hàng",
            "usages": [
                "/shopgui",
                "/shopgui create <category: string> <slot: int>",    
                "/shopgui remove <category: string>",
                "/shopgui setup <category: string>"
            ],
            "aliases": ["sg", "shop"],
            "permission": "shopgui.command"
        }
    }

    permissions = {
        "shopgui.command": {"description": "Cho phép sử dụng lệnh shopgui", "default": "true"},
        "shopgui.command.create": {"description": "Cho phép tạo cửa hàng mới", "default": "op"},
        "shopgui.command.remove": {"description": "Cho phép xóa cửa hàng", "default": "op"},
        "shopgui.command.setup": {"description": "Cho phép cài đặt cửa hàng", "default": "op"}
    }

    def on_enable(self) -> None:
        self.logger.info("ShopGUI đang được kích hoạt!")
        self.logger.info(f"§b[CheckPath] File đang chạy thực tế nằm tại: {os.path.abspath(__file__)}")
        self.language = LanguageManager(self)
        self.economy = self.server.plugin_manager.get_plugin("jweconomy")
        self.register_events(EventListener(self))

    def get_economy_api(self) -> JWEconomy:
        if not self.economy:
            self.logger.error(LanguageManager.get_translate("plugin_info.economy_not_found"))
            raise RuntimeError("JWEconomy plugin not found")
        else:
            return self.economy
    
    def get_shop_menu(self) -> ShopMenu:
        return ShopMenu(self) 
    
    def get_shop_manager(self) -> ShopManager:
        return ShopManager(self)

    def on_command(self, sender: CommandSender, command: Command, args: list[str]) -> bool:
        if command.name in ["shopgui", "shop", "sg"]:
            if not isinstance(sender, Player):
                    sender.send_message(LanguageManager.get_translate("plugin_info.use_ingame"))
                    return True
                
            else:
                    if not args:
                        self.get_shop_menu().openMenu(sender)
                        return True
                        
                    if args[0] == "create":
                        if not sender.has_permission("shopgui.command.create"):
                            sender.send_error_message(LanguageManager.get_translate("plugin_info.no_permission"))
                            return True
                        
                        if len(args[1]) < 2:
                            sender.send_message(LanguageManager.get_translate("plugin_info.command.create.usage"))
                            return True
                        
                        if not args[2] or not args[2].isdigit():
                            sender.send_message(LanguageManager.get_translate("plugin_info.command.create.usage"))
                            return True
                        
                        item = sender.inventory.item_in_main_hand
                        if item is None or item.type == "minecraft:air":
                            sender.send_message(LanguageManager.get_translate("plugin_info.command.create.error_1"))
                            return True
                        
                        shop_name = args[1]
                        icon = str(item.type)
                        slot = args[2]
                        if self.shop_manager.exists(shop_name):
                            sender.send_error_message(LanguageManager.get_translate("plugin_info.command.create.error_2"))
                        else:
                            self.shop_manager.create(shop_name, icon, slot)
                            sender.send_message(LanguageManager.get_translate("plugin_info.command.create.success", [shop_name]))
                    
                    if args[0] == "remove":
                        if not sender.has_permission("shopgui.command.remove"):
                            sender.send_error_message(LanguageManager.get_translate("plugin_info.no_permission"))
                            return True
                        
                        if len(args[1]) < 2:
                            sender.send_message(LanguageManager.get_translate("plugin_info.command.remove.usage"))
                            return True
                        
                        shop_name = args[1]
                        if not self.shop_manager.exists(shop_name):
                            sender.send_error_message(LanguageManager.get_translate("plugin_info.command.remove.error_1"))
                        else:
                            self.shop_manager.remove(shop_name)
                            sender.send_message(LanguageManager.get_translate("plugin_info.command.remove.success", [shop_name]))
                    
                    if args[0] == "setup":
                        if not sender.has_permission("shopgui.command.setup"):
                            sender.send_error_message(LanguageManager.get_translate("plugin_info.no_permission"))
                            return True
                        
                        if len(args[1]) < 2:
                            sender.send_message(LanguageManager.get_translate("plugin_info.command.setup.usage"))
                            return True
                        
                        shop_name = args[1]
                        if not self.get_shop_manager().exists(shop_name):
                            sender.send_error_message(LanguageManager.get_translate("plugin_info.command.setup.error"))
                        else:
                            self.get_shop_manager().editMode[sender.name] = shop_name
                            data = LanguageManager.get_raw("plugin_info.command.setup.join_help")
                            sender.send_message(LanguageManager.get_translate("plugin_info.command.setup.join_title", [shop_name]))
                            sender.send_message(data)
        return False
    
    def on_disable(self) -> None:
        self.get_shop_manager().save_all()
