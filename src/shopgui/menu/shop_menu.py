import math
import asyncio
from typing import TYPE_CHECKING
from endstone import Player
from endstone.inventory import ItemStack, ItemType
from endstone.plugin import Plugin

from jwinventoryapi import Menu, MenuType
from jwinventoryapi.menu.inventory import UIInventory


from shopgui.manager.shop_manager import ShopManager

class ShopMenu:
    def __init__(self, plugin):
        self.plugin = plugin
        self.manager = ShopManager(self.plugin)

    def openMenu(self, player: Player):
        menu = Menu(MenuType.CHEST, "ShopGUI")
        all_shop = self.manager.get_all()
        barrier = ItemStack("minecraft:barrier")
        barrier_meta = barrier.item_meta
        barrier_meta.display_name = "§cKhông có cửa hàng nào!"
        barrier.set_item_meta(barrier_meta)
        menu.inventory.contents = [barrier] * 27
        for shop_name, shop_data in all_shop.items():
            icon = ItemStack(shop_data["icon"])
            icon_meta = icon.item_meta
            icon_meta.display_name = f"§e{shop_name}"
            icon_meta.lore = ["§7Nhấn để mở cửa hàng!"]
            icon.set_item_meta(icon_meta)
            menu.inventory.set_item(int(shop_data["slot"]), icon)

        def on_click_shop(player: Player, slot: int, item: ItemStack, inv: UIInventory) -> None:
            items = inv.get_item(slot)
            name = items.item_meta.display_name
            if items is None or items.type in ["minecraft:air", "minecraft:barrier"]:
                return
            
            menu.close(player)
            self.openShop(player, name.replace("§e", ""))

        menu.set_listener(on_click_shop)
        menu.send_to(player)

    def openShop(self, player: Player, shop_name: str, page: int = 1):
        uuid = str(player.unique_id)
        item = self.manager.getItems(shop_name)
        menu = Menu(MenuType.DOUBLE_CHEST)
        for i in range(45, 54):
            barrier = ItemStack("minecraft:barrier")
            barrier_meta = barrier.item_meta
            barrier_meta.display_name = "§r"
            barrier.set_item_meta(barrier_meta)
            menu.inventory.set_item(i, barrier)
        arrow = ItemStack("minecraft:arrow")

        back_shop = ItemStack("minecraft:paper")
        b_meta = back_shop.item_meta
        b_meta.display_name = "§cTrở về shop"
        back_shop.set_item_meta(b_meta)
        menu.inventory.set_item(45, back_shop)

        def set_item(balance):
            money = ItemStack("minecraft:emerald")
            m_meta = money.item_meta
            m_meta.display_name = f"§aSố tiền hiện có: {balance} xu"
            money.set_item_meta(m_meta)
            menu.inventory.set_item(53, money)

        self.manager.get_money(player, "coins", set_item)
        if page > 1:
            a_meta = arrow.item_meta
            a_meta.display_name = "§aTrang trước"
            arrow.set_item_meta(a_meta)
            menu.inventory.set_item(48, arrow)

        #i = 0
        SHOP_ITEM_MAX = 45
        total_page = math.ceil(len(item) / SHOP_ITEM_MAX)
        start = (page - 1) * SHOP_ITEM_MAX
        end = min(start + SHOP_ITEM_MAX, len(item))
        listed = list(item.items())[0:3]

        for slot, [name, price] in enumerate(listed):
            ex = price.split(":")
            item_type = ItemStack(name)
            item_meta = item_type.item_meta

            #if slot >= start and slot < end:
            item_meta.lore = [
                "", # Dòng trống tương đương \n ở đầu
                f" §e➼ §l§6BUY:§o§7 ${ex[0]}",
                f" §e➼ §l§6SELL:§o§7 ${ex[1]}",
                f" §e➼ §l§bCATEGORY: §e{shop_name.upper()}"
            ]
            item_type.set_item_meta(item_meta)
            menu.inventory.set_item(slot, item_type)
            #i += 1                   
        
        if total_page > page:
            a_meta = arrow.item_meta
            a_meta.display_name = "§aTrang sau"
            arrow.set_item_meta(a_meta)
            menu.inventory.set_item(50, arrow)

        def on_shop(player: Player, slot: int, item_clicked: ItemStack, inv: UIInventory) -> None:
            if item_clicked is None or item_clicked.type in ["minecraft:air", "minecraft:barrier"]:
                menu.close(player)
                return
            
            match item_clicked.item_meta.display_name:
                case "§cTrở về shop":
                    menu.close(player)
                    self.openMenu(player)
                    return
                
                case "§aTrang trước":
                    if page > 1:
                        menu.close(player)
                        self.openShop(player, shop_name, page - 1)
                    return
                
                case "§aTrang sau":
                    if page < total_page:
                        menu.close(player)
                        self.openShop(player, shop_name, page + 1)
                    return
                
                case _:
                    menu.close(player)
                    self.openConfirm(player, item_clicked)
        
        menu.set_name(f"§e{shop_name} SHOP - Trang {page}/{total_page}")
        menu.set_listener(on_shop)
        menu.send_to(player)

    def openConfirm(self, player: Player, item: ItemStack, amount: int = 1):
        menu = Menu(MenuType.CHEST, "Xác nhận giao dịch")
        
        for i in range(0, 27):
            iron_bar = ItemStack("minecraft:iron_bars")
            iron_bar_meta = iron_bar.item_meta
            iron_bar_meta.display_name = "§r"
            iron_bar.set_item_meta(iron_bar_meta)
            menu.inventory.set_item(i, iron_bar)

        items = {
            14: {"id": "minecraft:paper", "name": "§l§aThêm", "count": 1},
            15: {"id": "minecraft:paper", "name": "§l§aThêm", "count": 32},
            16: {"id": "minecraft:paper", "name": "§l§aThêm", "count": 64},

            10: {"id": "minecraft:paper", "name": "§l§aBớt", "count": 64},
            11: {"id": "minecraft:paper", "name": "§l§aBớt", "count": 32},
            12: {"id": "minecraft:paper", "name": "§l§aBớt", "count": 1},

            20: {"id": "minecraft:red_concrete", "name": "§l§aXác Nhận Bán", "count": 1},
            24: {"id": "minecraft:lime_concrete", "name": "§l§aXác Nhận Mua", "count": 1},
            22: {"id": "minecraft:chest", "name": "§l§cMua Số Lượng Nhiều", "count": 1}
        }
        for slot, data in items.items():
            item_stack = ItemStack(data["id"], data["count"])
            itemmeta = item_stack.item_meta
            itemmeta.display_name = data["name"]
            item_stack.set_item_meta(itemmeta)
            menu.inventory.set_item(slot, item_stack)
        
        item.amount = amount
        menu.inventory.set_item(13, item)

        def on_confirm(player: Player, slot: int, item_clicked: ItemStack, inv: UIInventory) -> None:
            if item_clicked is None or item_clicked.type in ["minecraft:air", "minecraft:iron_bars"]:
                return
            
            item_confirm = menu.inventory.get_item(13)
            match item_clicked.item_meta.display_name:
                case "§l§aThêm":
                    count = item_clicked.amount
                    current_amount = item_confirm.amount
        
                    # Tính toán số lượng mới trước khi đặt vào menu
                    
                    new_amount = current_amount + count
                    item_type = item_confirm.type
                    if new_amount > 64:
                        menu.close(player)
                        self.openConfirm(player, item_confirm, 64)
                    else:
                        menu.close(player)
                        self.openConfirm(player, item_confirm, new_amount)
                        return
                
                case "§l§aBớt":
                    count = item_clicked.amount
                    if item_confirm.amount - count < 1:
                        menu.close(player)
                        self.openConfirm(player, item_confirm, 1)
                    else:
                        menu.close(player)
                        self.openConfirm(player, item_confirm, item_confirm.amount - count)
                
                case "§l§cMua Số Lượng Nhiều":
                    menu.close(player)
                    self.openCustomBuy(player, item_confirm)
                
                case "§l§aXác Nhận Mua":
                    item_confirm = menu.inventory.get_item(13)

                    if item_confirm is None or item_confirm.type in ["minecraft:air", "minecraft:iron_bars"]:
                        return
                    
                    if not player.inventory.first_empty == -1:
                        item_meta = item_confirm.item_meta

                        for lore in item_meta.lore:
                            if "BUY" in lore:
                                try:
                                    parts = lore.split(":")
                                    price = float(parts[1].strip().replace("§o§7 $", ""))
                                    break
                                except IndexError:
                                    continue

                        if price is not None:
                            total_price = item_confirm.amount * price
                            item_meta.lore = []
                            item_confirm.set_item_meta(item_meta)
                            name = str(item_confirm.type)
                            
                            def add_item(new_balance):
                                player.inventory.add_item(item_confirm)
                                player.send_message(f"§aBạn đã mua {item_confirm.amount}x {name} với giá {total_price} xu! Số dư hiện tại: {new_balance} xu")
                                menu.close(player)
                            self.manager.reduce_money(player, "coins", total_price, add_item)
                        else:
                            player.send_message("§cKhông thể xác định giá của món đồ này!")
                            menu.close(player)
                            return
                    else:
                        player.send_message("§cKhông đủ chỗ trong hành trang để mua món đồ này!")
                        menu.close(player)
                        return
                
                case "§l§aXác Nhận Bán":
                    item_confirm = menu.inventory.get_item(13)
                    if item_confirm is None or item_confirm.type in ["minecraft:air", "minecraft:iron_bars"]:
                        return
                    
                    price = None
                    item_meta = item_confirm.item_meta
                    for lore in item_meta.lore:
                        if "SELL" in lore:
                            try:
                                parts = lore.split(":")
                                price = float(parts[1].strip().replace("§o§7 $", ""))
                                break
                            except IndexError:
                                continue

                    if price is not None:
                        total_price = item_confirm.amount * price
                        item_meta.lore = []
                        item_confirm.set_item_meta(item_meta)
                        name = str(item_confirm.type)
                        
                        def remove_item(new_balance):
                            if not player.inventory.contains_at_least(item_confirm.type.id, item_confirm.amount):
                                player.send_message("§cBạn không có đủ số lượng món đồ này để bán!")
                                menu.close(player)
                                return
                            
                            player.inventory.remove_item(item_confirm)
                            player.send_message(f"§aBạn đã bán {item_confirm.amount}x {name} với giá {total_price} xu! Số dư hiện tại: {new_balance} xu")
                            menu.close(player)
                        
                        self.manager.add_money(player, "coins", total_price, remove_item)
                    else:
                        player.send_message("§cKhông thể xác định giá của món đồ này!")
                        menu.close(player)
                        return

        menu.set_listener(on_confirm)
        menu.send_to(player)

    def openCustomBuy(self, player: Player, item: ItemStack):
        menu = Menu(MenuType.CHEST, "Mua số lượng nhiều")     
        for i in [4, 13, 22]:
            irron_bar = ItemStack("minecraft:iron_bars")
            irron_bar_meta = irron_bar.item_meta
            irron_bar_meta.display_name = "§r"
            irron_bar.set_item_meta(irron_bar_meta)
            menu.inventory.set_item(i, irron_bar)

        matrix_slots = {
            # Cánh trái (Nút x1 đến x9)
            "x1": 1,  "x2": 2,  "x3": 3,
            "x4": 10, "x5": 11, "x6": 12,
            "x7": 19, "x8": 20, "x9": 21,
            
            # Cánh phải (Nút x10 đến x18)
            "x10": 5,  "x11": 6,  "x12": 7,
            "x13": 14, "x14": 15, "x15": 16,
            "x16": 23, "x17": 24, "x18": 25
        }

        buttons = {
            "x1": {"name": "§lx1 Stack", "count": 1},
            "x2": {"name": "§lx2 Stack", "count": 2},
            "x3": {"name": "§lx3 Stack", "count": 3},
            "x4": {"name": "§lx4 Stack", "count": 4},
            "x5": {"name": "§lx5 Stack", "count": 5},
            "x6": {"name": "§lx6 Stack", "count": 6},
            "x7": {"name": "§lx7 Stack", "count": 7},
            "x8": {"name": "§lx8 Stack", "count": 8},
            "x9": {"name": "§lx9 Stack", "count": 9},

            "x10": {"name": "§lx10 Stack", "count": 10},
            "x11": {"name": "§lx11 Stack", "count": 11},
            "x12": {"name": "§lx12 Stack", "count": 12},
            "x13": {"name": "§lx13 Stack", "count": 13},
            "x14": {"name": "§lx14 Stack", "count": 14},
            "x15": {"name": "§lx15 Stack", "count": 15},
            "x16": {"name": "§lx16 Stack", "count": 16},
            "x17": {"name": "§lx17 Stack", "count": 17},
            "x18": {"name": "§lx18 Stack", "count": 18}
        }

        for key, data in buttons.items():
           if key in matrix_slots:
                button = ItemStack(str(item.type))
                button_meta = button.item_meta
                button.amount = data["count"]
                button_meta.display_name = data["name"]
                button.set_item_meta(button_meta)
                menu.inventory.set_item(matrix_slots[key], button)
        
        #menu.set_listener(on_custom_buy_confirm)
        menu.send_to(player)

