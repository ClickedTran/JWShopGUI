import os
import json
from typing import Union, List, Any

from shopgui.main import ShopGUI

class LanguageManager:
    # Các biến static (Class variables) tương đương với private static trong PHP
    _plugin: ShopGUI = None
    _lang_data: dict = {}
    _lang_file_path: str = ""

    def __init__(self, plugin: ShopGUI):
        # Nạp cứng dữ liệu vào biến Class để tất cả các hàm @classmethod ở dưới đều với tới được
        LanguageManager._plugin = plugin
        LanguageManager._lang_file_path = os.path.join(plugin.data_folder, "messages.json")
        
        # Tiến hành tạo file và nạp ngôn ngữ
        self.generate_default_file()
        self.load_language()
    
    def base_language(self) -> dict:
        return {
            "reset": False,
            "version": 1,
            "plugin_info":{
                "reload_language": "§aĐã tải lại ngôn ngữ: %1",
                "message_not_found": "§cKhông tìm thấy tin nhắn: %1",
                "economy_not_found": "Không tìm thấy plugin JWEconomy! Hãy đảm bảo rằng JWEconomy đã được cài đặt và kích hoạt.",
                "command": {
                    "name": "shopgui",
                    "description": "Mở hệ thống cửa hàng",
                    "aliases": ["shop", "sg"],
                    "usages": [
                        "/shopgui",
                        "/shopgui create <category: string> <slot: int>",    
                        "/shopgui remove <category: string>",
                        "/shopgui setup <category: string>"
                    ],
                    "permission": "shopgui.command" 
                },
                "permissions": {
                    "shopgui.command": {"description": "Cho phép sử dụng lệnh shopgui", "default": "true"},
                    "shopgui.command.create": {"description": "Cho phép tạo cửa hàng mới", "default": "op"},
                    "shopgui.command.remove": {"description": "Cho phép xóa cửa hàng", "default": "op"},
                    "shopgui.command.setup": {"description": "Cho phép cài đặt cửa hàng", "default": "op"}
                }
            },
            "prefix": "§l§e[ShopGUI] §r",
            "player_money": "§aSố tiền hiện có: %1 xu",
            "menu": {
                "name": "ShopGUI - MENU",
                "category": {
                    "name": "CỬA HÀNG %1 - Trang %2/%3",
                    "lore": {
                        "buy": "§e➼ §l§6MUA:§o§7 $%1",
                        "sell": "§e➼ §l§6BÁN:§o§7 $%1",
                        "open": "BẤM ĐỂ MỞ CỬA HÀNG"
                    },
                    "stack": {
                        "buy": "Mua x%1 Stack",
                        "sell": "Bán x%1 Stack"
                    },
                    "not_found": "Ở slot này không có cửa hàng nào!"
                },
                "confirm": {
                    "name": "XÁC NHẬN GIAO DỊCH",
                    "add_count": "THÊM",
                    "reduce_count": "BỚT",
                    "buy_item": "§l§aXác Nhận Mua",
                    "sell_item": "§l§aXác Nhận Bán",
                    "custom": "§l§cMua Bán Số Lượng Nhiều"
                },

                "page": {
                    "next": "Trang Trước",
                    "previous": "Trang Sau",
                    "back_to_shop": "Trở về danh sách cửa hàng"
                }
            },
            "errors": {
                "no_room": "§cKhông đủ chỗ trong hành trang để mua món đồ này!",
                "no_money": "§cBạn không đủ %1 xu để mua vật phẩm này!",
                "no_items_to_sell": "§cBạn không có đủ số lượng món đồ này trong hành trang để bán!",
                "price_is_none": "Không thể xác định giá tiền của vật phẩm này!"
            },
            "success": {
                "buy": "§aBạn đã mua thành công %1x %2 với giá %3 xu!",
                "sell": "§aBạn đã bán thành công %1x %2 với giá %3 xu!",
                "balance": "Số dư hiện tại của bạn: %1 xu"
            },
            "button": {
                "buy_item": "MUA",
                "buy_stack": "Mua x",

                "sell_item": "BÁN",
                "sell_stack": "Bán x"
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
            return f"{prefix}{message}"
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
            return str(message)
        return ""

    @classmethod
    def get_plugin(cls) -> ShopGUI:
        return cls._plugin

    @classmethod
    def get_lang_data(cls) -> dict:
        return cls._lang_data