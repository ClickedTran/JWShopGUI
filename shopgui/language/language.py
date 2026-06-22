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
            "plugin_info":{
                "reload_language": "§aĐã tải lại ngôn ngữ: %1",
                "message_not_found": "§cKhông tìm thấy tin nhắn: %1",
                "economy_not_found": "Không tìm thấy plugin JWEconomy! Hãy đảm bảo rằng JWEconomy đã được cài đặt và kích hoạt.",
                "no_permission": "Bạn không có quyền để sử dụng lệnh này!",
                "use_ingame": "Lệnh này chỉ có thể được sử dụng bởi người chơi!",
                "update_item": {
                    "success": "§aĐã cập nhật dữ liệu cấu hình từ file shops.json vào RAM thành công!",
                    "error": "Lỗi khi đọc file cấu hình để reload: %1"
                },
                "shop_data_not_found": "Không tìm thấy cấu hình cho shop có tên: %1!",
                "command": {
                    "create": {
                        "success": "Cửa hàng %1 đã được tạo thành công!",
                        "usage": "Sử dụng: /shop create <tên cửa hàng> <slot> <icon>, trong đó <slot> phải là số nguyên",
                        "error_1": "Bạn phải cầm một món đồ làm biểu tượng cho cửa hàng hoặc cung cấp tên món đồ trong lệnh!",
                        "error_2": "Cửa hàng đã tồn tại!"
                    },
                    "remove": {
                        "success": "Cửa hàng %1 đã được xóa thành công!",
                        "usage": "Sử dụng: /shop remove <tên cửa hàng>",
                        "error_1": "Cửa hàng không tồn tại!"
                    },
                    "setup": {
                        "usage": "Sử dụng: /shop setup <tên cửa hàng>",        
                        "error": "Cửa hàng không tồn tại!",
                        "join_title": "§6>> Bạn đã vào chế độ chỉnh sửa của cửa hàng %1 <<",
                        "join_help": [
                            "§l§7help§r§7 - Hiển thị các lệnh có sẵn",
                            "§l§7done§r§7 - Lưu và thoát chế độ chỉnh sửa"
                        ],
                        "help": [
                            "§6>> Tất cả các lệnh chỉnh sửa <<",
                            "§l§7help§r§7 - Hiển thị các lệnh có sẵn",
                            "§l§7add <item_name> <buy_price> <sell_price>§r§7 - Thêm một mặt hàng vào cửa hàng với giá mua và bán đã chỉ định",
                            "§l§7remove <item_name | slot>§r§7 - Xóa một vật phẩm khỏi cửa hàng",
                            "§l§7done§r§7 - Lưu và thoát chế độ chỉnh sửa"
                        ],
                        "add": {
                            "success": "§aVật phẩm %1 đã được thêm vào cửa hàng %2 với giá mua: %3 và giá bán %4",
                            "error": "§cGiá mua và giá bán phải là số"
                        },
                        "remove": {
                            "success_1": "§aVật phẩm tại ô %1 đã bị loại bỏ!",
                            "success_2": "§aVật phẩm tên %1 đã bị loại bỏ!",
                            "error_1": "§cKhông tìm thấy vật phẩm tại ô %1!",
                            "error_2": "§cKhông tìm thấy vật phẩm với tên %1!"
                        },
                        "done": "§6Bạn đã thoát khỏi chế độ chỉnh sửa của cửa hàng §a%1"
                    }
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
                        "name": "Mua | Bán số lượng nhiều",
                        "barrier": "§l§b<-- MUA | BÁN -->",
                        "buy": "Mua x%1 Stack",
                        "sell": "Bán x%1 Stack"
                    },
                    "not_found": "Ở slot này không có cửa hàng nào!",
                    "open": "ẤN VÀO ĐỂ MỞ CỬA HÀNG"
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