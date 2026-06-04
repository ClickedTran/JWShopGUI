import asyncio
from typing import Callable

from endstone.plugin import Plugin
from endstone.command import Command, CommandSender
from endstone import Player

from jweconomy.main import JWEconomy

from shopgui.menu.shop_menu import ShopMenu
from shopgui.manager.shop_manager import ShopManager
from shopgui.listener import EventListener

class ShopGUI(Plugin):
    prefix = "ShopGUI"
    api_version = "0.5"
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
        self.economy = self.server.plugin_manager.get_plugin("jweconomy")
        self.register_events(EventListener(self))

    def get_economy_api(self) -> JWEconomy:
        if not self.economy:
            self.logger.error("Không tìm thấy plugin JWEconomy! Hãy đảm bảo rằng JWEconomy đã được cài đặt và kích hoạt.")
            raise RuntimeError("JWEconomy plugin not found")
        else:
            return self.economy
    
    def get_shop_menu(self) -> ShopMenu:
        return ShopMenu(self)
    
    def get_shop_manager(self) -> ShopManager:
        return ShopManager(self)

    def on_command(self, sender: CommandSender, command: Command, args: list[str]) -> bool:
        if command.name in ["shopgui", "sg", "shop"]:
            if not isinstance(sender, Player):
                    sender.send_message("Lệnh này chỉ có thể được sử dụng bởi người chơi!")
                    return True
                
            else:
                    if not args:
                        self.get_shop_menu().openMenu(sender)
                        return True
                        
                    if args[0] == "create":
                        if not sender.has_permission("shopgui.create"):
                            sender.send_error_message("Bạn không có quyền sử dụng lệnh này!")
                            return True
                        
                        if len(args[1]) < 2:
                            sender.send_message("Sử dụng: /shop create <tên cửa hàng>")
                            return True
                        
                        if not args[2] or not args[2].isdigit():
                            sender.send_message("Sử dụng: /shop create <tên cửa hàng> <slot> <icon>, trong đó <slot> phải là số nguyên")
                            return True
                        
                        item = sender.inventory.item_in_main_hand
                        if item is None or item.type == "minecraft:air":
                            sender.send_message("Bạn phải cầm một món đồ làm biểu tượng cho cửa hàng hoặc cung cấp tên món đồ trong lệnh!")
                            return True
                        
                        shop_name = args[1]
                        icon = str(item.type)
                        slot = args[2]
                        if self.shop_manager.exists(shop_name):
                            sender.send_error_message("Cửa hàng đã tồn tại!")
                        else:
                            self.shop_manager.create(shop_name, icon, slot)
                            sender.send_message("Cửa hàng '{}' đã được tạo thành công!".format(shop_name))
                    
                    if args[0] == "remove":
                        if not sender.has_permission("shopgui.remove"):
                            sender.send_error_message("Bạn không có quyền sử dụng lệnh này!")
                            return True
                        
                        if len(args[1]) < 2:
                            sender.send_message("Sử dụng: /shop remove <tên cửa hàng>")
                            return True
                        
                        shop_name = args[1]
                        if not self.shop_manager.exists(shop_name):
                            sender.send_error_message("Cửa hàng không tồn tại!")
                        else:
                            self.shop_manager.remove(shop_name)
                            sender.send_message("Cửa hàng '{}' đã được xóa thành công!".format(shop_name))
                    
                    if args[0] == "setup":
                        if not sender.has_permission("shopgui.setup"):
                            sender.send_error_message("Bạn không có quyền sử dụng lệnh này!")
                            return True
                        
                        if len(args[1]) < 2:
                            sender.send_message("Sử dụng: /shop setup <tên cửa hàng>")
                            return True
                        
                        shop_name = args[1]
                        if not self.get_shop_manager().exists(shop_name):
                            sender.send_error_message("Cửa hàng không tồn tại!")
                        else:
                            self.get_shop_manager().editMode[sender.name] = shop_name
                            sender.send_message(f"§6Bạn đã vào chế độ chỉnh sửa cho cửa hàng {shop_name}")
                            sender.send_message("§l§7help§r§7 - Display available commands")
                            sender.send_message("§l§7done§r§7 - save and leave edit mode")
        return False
    
    def on_disable(self) -> None:
        self.get_shop_manager().save_all()
