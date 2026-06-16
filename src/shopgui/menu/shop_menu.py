import math
from typing import TYPE_CHECKING
from endstone import Player
from endstone.inventory import ItemStack, ItemType
from endstone.plugin import Plugin

from jwinventoryapi import Menu, MenuType
from jwinventoryapi.menu.inventory import UIInventory

from shopgui.manager.shop_manager import ShopManager
from shopgui.language.language import LanguageManager

class ShopMenu:
    def __init__(self, plugin):
        self.plugin = plugin
        self.manager = ShopManager(self.plugin)

    def openMenu(self, player: Player):
        menu = Menu(MenuType.CHEST, "ShopGUI")
        all_shop = self.manager.get_all()
        barrier = ItemStack("minecraft:barrier")
        barrier_meta = barrier.item_meta
        barrier_meta.display_name = LanguageManager.get_translate("menu.category.not_found")
        barrier.set_item_meta(barrier_meta)
        menu.inventory.contents = [barrier] * 27
        for shop_name, shop_data in all_shop.items():
            icon = ItemStack(shop_data["icon"])
            icon_meta = icon.item_meta
            icon_meta.display_name = f"§e{shop_name}"
            icon_meta.lore = [str(LanguageManager.get_translate("menu.category.open"))]
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
        b_meta.display_name = LanguageManager.get_translate("menu.page.back_to_shop")
        back_shop.set_item_meta(b_meta)
        menu.inventory.set_item(45, back_shop)

        def set_item(balance):
            money = ItemStack("minecraft:emerald")
            m_meta = money.item_meta
            m_meta.display_name = LanguageManager.get_translate("player_money", [float(balance)])
            money.set_item_meta(m_meta)
            menu.inventory.set_item(49, money)

        self.manager.get_money(player, "coins", set_item)
        if page > 1:
            a_meta = arrow.item_meta
            a_meta.display_name = LanguageManager.get_translate("menu.page.previous")
            arrow.set_item_meta(a_meta)
            menu.inventory.set_item(48, arrow)

        #i = 0
        SHOP_ITEM_MAX = 45
        total_page = math.ceil(len(item) / SHOP_ITEM_MAX)
        start = (page - 1) * SHOP_ITEM_MAX
        end = min(start + SHOP_ITEM_MAX, len(item))
        listed = list(item.items())[start:end]

        for slot, [name, price] in enumerate(listed):
            ex = price.split(":")
            item_type = ItemStack(name)
            item_meta = item_type.item_meta

            #if slot >= start and slot < end:
            item_meta.lore = [
                "", # Dòng trống tương đương \n ở đầu
                str(LanguageManager.get_translate("menu.category.lore.buy", [ex[0]])),
                str(LanguageManager.get_translate("menu.category.lore.sell", [ex[1]])),
                f"§e➼ §l§bCATEGORY: §e{shop_name.upper()}"
            ]
            item_type.set_item_meta(item_meta)
            menu.inventory.set_item(slot, item_type)
            #i += 1                   
        
        if total_page > page:
            a_meta = arrow.item_meta
            a_meta.display_name = LanguageManager.get_translate("menu.page.next")
            arrow.set_item_meta(a_meta)
            menu.inventory.set_item(50, arrow)

        def on_shop(player: Player, slot: int, item_clicked: ItemStack, inv: UIInventory) -> None:
            if item_clicked is None or item_clicked.type in ["minecraft:air", "minecraft:barrier"]:
                menu.close(player)
                return
            
            display_name = item_clicked.item_meta.display_name

            if display_name == LanguageManager.get_translate("menu.page.back_to_shop"):
                menu.close(player)
                self.openMenu(player)
                return
                
            elif display_name == LanguageManager.get_translate("menu.page.previous"):
                if page > 1:
                    menu.close(player)
                    self.openShop(player, shop_name, page - 1)
                return
                
            elif display_name == LanguageManager.get_translate("menu.page.next"):
                if page < total_page:
                    menu.close(player)
                    self.openShop(player, shop_name, page + 1)
                return
                
            else:
                menu.close(player)
                self.openConfirm(player, item_clicked)
        
        menu.set_name(LanguageManager.get_translate("menu.category.name", [shop_name, int(page), int(total_page)]))
        menu.set_listener(on_shop)
        menu.send_to(player)

    def openConfirm(self, player: Player, item: ItemStack, amount: int = 1):
        menu = Menu(MenuType.CHEST, LanguageManager.get_translate("menu.confirm.name"))
        
        for i in range(0, 27):
            iron_bar = ItemStack("minecraft:iron_bars")
            iron_bar_meta = iron_bar.item_meta
            iron_bar_meta.display_name = "§r"
            iron_bar.set_item_meta(iron_bar_meta)
            menu.inventory.set_item(i, iron_bar)

        items = {
            14: {
                "id": "minecraft:paper", 
                "name": LanguageManager.get_translate("menu.confirm.add_count"), 
                "count": 1
                },
            15: {
                "id": "minecraft:paper", 
                "name": LanguageManager.get_translate("menu.confirm.add_count"), 
                "count": 32
                },
            16: {
                "id": "minecraft:paper", 
                "name": LanguageManager.get_translate("menu.confirm.add_count"), 
                "count": 64
                },

            10: {
                "id": "minecraft:paper", 
                "name": LanguageManager.get_translate("menu.confirm.reduce_count"), 
                "count": 64
                },
            11: {
                "id": "minecraft:paper", 
                "name": LanguageManager.get_translate("menu.confirm.reduce_count"), 
                "count": 32
                },
            12: {
                "id": "minecraft:paper", 
                "name": LanguageManager.get_translate("menu.confirm.reduce_count"), 
                "count": 1
                },
            20: {
                "id": "minecraft:red_concrete", 
                "name": LanguageManager.get_translate("menu.confirm.sell_item"), 
                "count": 1
                },
            24: {
                "id": "minecraft:lime_concrete", 
                "name": LanguageManager.get_translate("menu.confirm.buy_item"), 
                "count": 1
                },
            22: {
                "id": "minecraft:chest", 
                "name": LanguageManager.get_translate("menu.confirm.custom"), 
                "count": 1
                }
        }
        for slot, data in items.items():
            item_stack = ItemStack(data["id"], data["count"])
            itemmeta = item_stack.item_meta
            itemmeta.display_name = data["name"]
            item_stack.set_item_meta(itemmeta)
            menu.inventory.set_item(slot, item_stack)
        
        item.amount = amount
        menu.inventory.set_item(13, item)

        def on_confirm(player: Player, slots: int, item_clicked: ItemStack, inv: UIInventory) -> None:
            if item_clicked is None or item_clicked.type in ["minecraft:air", "minecraft:iron_bars"]:
                return
            
            item_confirm = inv.get_item(13)
            display_name = item_clicked.item_meta.display_name
            if display_name == LanguageManager.get_translate("menu.confirm.add_count"):
                count = item_clicked.amount
                new_amount = min(item_confirm.amount + count, 64)
        
                new_item = item_confirm.type.create_item_stack(new_amount)
                if item_confirm.item_meta:
                    new_item.set_item_meta(item_confirm.item_meta.clone())

                inv.begin_batch()

                inv.set_item(13, new_item)

                inv._dirty_slots.clear()
                inv._batch_mode = False
                menu.refresh_contents()
                        
            elif display_name == LanguageManager.get_translate("menu.confirm.reduce_count"):
                count = item_clicked.amount
                new_amount = max(item_confirm.amount - count, 1)

                new_item = item_confirm.type.create_item_stack(new_amount)
                if item_confirm.item_meta:
                    new_item.set_item_meta(item_confirm.item_meta.clone())

                inv.begin_batch()

                inv.set_item(13, new_item)
                
                inv._dirty_slots.clear()
                inv._batch_mode = False
                menu.refresh_contents()

            elif display_name == LanguageManager.get_translate("menu.confirm.custom"):
                menu.close(player)
                self.openCustomBuy(player, item_confirm)
                
            elif display_name == LanguageManager.get_translate("menu.confirm.buy_item"):
                item_confirm = menu.inventory.get_item(13)

                if item_confirm is None or item_confirm.type in ["minecraft:air", "minecraft:iron_bars"]:
                    return
                
                item_meta = item_confirm.item_meta
                button = LanguageManager.get_raw("button.buy_item")
                price = None
                for lore in item_meta.lore:
                    if lore and button in lore and "$" in lore:
                        try:
                            price_str = lore.split("$")[1]
                            price = float(price_str.strip())
                            break
                        except (IndexError, ValueError):
                            continue
                        
                if price is None:
                    player.send_message(LanguageManager.get_translate("menu.errors.price_is_none"))
                    return
                
                total_price = item_confirm.amount * price
                name = str(item_confirm.type).replace("minecraft:", "").replace("_", " ").upper()
                def has_money(player_has_money: bool):
                    if player_has_money:
                        def add_item(new_balance):
                            item_add = ItemStack(str(item_confirm.type))
                            item_add.amount = item_confirm.amount
                            if player.inventory.first_empty == -1:                           
                                player.send_message(LanguageManager.get_translate("menu.errors.no_room"))
                                menu.close(player)
                                return
                            player.inventory.add_item(item_add)
                            player.send_message(LanguageManager.get_translate("success.buy", [int(item_add.amount), name, float(total_price)]))
                            player.send_message(LanguageManager.get_translate("success.balance", [float(new_balance)]))
                        self.manager.reduce_money(player, "coins", total_price, add_item)
                    else:
                        player.send_message(LanguageManager.get_translate("errors.no_money", [float(total_price)]))
                        menu.close(player)
                        return
                self.manager.has_money(player, "coins", total_price, has_money)
                
            elif display_name == LanguageManager.get_translate("menu.confirm.sell_item"):
                item_confirm = menu.inventory.get_item(13)
                if item_confirm is None or item_confirm.type in ["minecraft:air", "minecraft:iron_bars"]:
                    return
                
                item_meta = item_confirm.item_meta
                button = LanguageManager.get_raw("button.sell_item")
                price = None
                for lore in item_meta.lore:
                    if lore and button in lore and "$" in lore:
                        try:
                            price_str = lore.split("$")[1]
                            price = float(price_str.strip())
                            break
                        except (IndexError, ValueError):
                            continue

                if price is None:
                    player.send_message(LanguageManager.get_translate("menu.errors.price_is_none"))
                    return
                total_price = item_confirm.amount * price
                name = str(item_confirm.type).replace("minecraft:", "").replace("_", " ").upper()
                
                def remove_item(new_balance):
                    item_sell = ItemStack(str(item_confirm.type))
                    item_sell.amount = item_confirm.amount
                    if not player.inventory.contains_at_least(item_sell, item_sell.amount):
                        player.send_message(LanguageManager.get_translate("menu.errors.no_item_to_sell"))
                        menu.close(player)
                        return
                    
                    player.inventory.remove_item(item_sell)
                    player.send_message(LanguageManager.get_translate("success.sell", [int(item_sell.amount), name, float(total_price)]))
                    player.send_message(LanguageManager.get_translate("success.balance", [float(new_balance)]))
                
                self.manager.add_money(player, "coins", total_price, remove_item)

        menu.set_listener(on_confirm)
        menu.send_to(player)

    def openCustomBuy(self, player: Player, item: ItemStack):
        menu = Menu(MenuType.DOUBLE_CHEST, "Mua | Bán số lượng nhiều")     
        for i in range(0, 54):
            irron_bar = ItemStack("minecraft:iron_bars")
            irron_bar_meta = irron_bar.item_meta
            irron_bar_meta.display_name = "§r"
            irron_bar.set_item_meta(irron_bar_meta)
            menu.inventory.set_item(i, irron_bar)
        
        for slot in [13, 22, 31]:
            irron_bar = ItemStack("minecraft:iron_bars")
            irron_bar_meta = irron_bar.item_meta
            irron_bar_meta.display_name = "§l§b<-- MUA | BÁN -->"
            irron_bar.set_item_meta(irron_bar_meta)
            menu.inventory.set_item(slot, irron_bar)


        matrix_slots = {
            # Cánh trái (Nút x1 đến x9)
            "x1": 10,  "x2": 11,  "x3": 12,
            "x4": 19, "x5": 20, "x6": 21,
            "x7": 28, "x8": 29, "x9": 30,
            
            # Cánh phải (Nút x10 đến x18)
            "x10": 14,  "x11": 15,  "x12": 16,
            "x13": 23, "x14": 24, "x15": 25,
            "x16": 32, "x17": 33, "x18": 34
        }

        buttons = {}

        # 🌟 1. TỰ ĐỘNG ĐẺ 9 NÚT MUA (từ x1 -> x9)
        for i in range(1, 10):
            # Hàm get_translate tự động thế số i vào biến %1 trong chuỗi "§lMua x%1 Stack"
            btn_name = LanguageManager.get_translate("button.buy_stack")
            buttons[f"x{i}"] = {
                "name": btn_name + str(i) + " Stack", 
                "count": i
            }

        # 🌟 2. TỰ ĐỘNG ĐẺ 9 NÚT BÁN (từ x10 -> x18)
        for i in range(1, 10):
            btn_name = LanguageManager.get_translate("button.sell_stack")
            buttons[f"x{i + 9}"] = {
                "name": btn_name + str(i) + " Stack", 
                "count": i
            }

        for key, data in buttons.items():
           if key in matrix_slots:
                button = ItemStack(str(item.type))
                button_meta = item.item_meta.clone()
                button.amount = data["count"]
                button_meta.display_name = data["name"]
                button.set_item_meta(button_meta)
                menu.inventory.set_item(matrix_slots[key], button)
        
        def set_item(balance):
            money = ItemStack("minecraft:emerald")
            m_meta = money.item_meta
            m_meta.display_name = LanguageManager.get_translate("player_money", [float(balance)])
            money.set_item_meta(m_meta)
            menu.inventory.set_item(49, money)

        self.manager.get_money(player, "coins", set_item)
        
        def on_custom_buy_confirm(player: Player, slot: int, item_clicked: ItemStack, inv: UIInventory) -> None:
            if item_clicked is None or item_clicked.type in ["minecraft:air", "minecraft:iron_bars"]:
                return
            
            item_meta = item_clicked.item_meta
            buy_stack = LanguageManager.get_raw("button.buy_stack")
            buy_item = LanguageManager.get_raw("button.buy_item")

            sell_stack = LanguageManager.get_raw("button.sell_stack")
            sell_item = LanguageManager.get_raw("button.sell_item")
            if buy_stack in item_meta.display_name:
                for lore in item_meta.lore:
                    if lore and buy_item in lore:
                        price = float(lore.split()[-1].lstrip("$"))
                        amount = item_clicked.amount * 64
                        total_price = amount * price
                        name = str(item_clicked.type).replace("minecraft:", "").replace("_", " ").upper()
                        def has_money(player_has_money: bool):
                            if player_has_money:
                                if player.inventory.first_empty == -1:
                                    player.send_message(LanguageManager.get_translate("menu.errors.no_room"))
                                    menu.close(player)
                                    return
                                
                                def add_item(new_balance):
                                    for _ in range(item_clicked.amount):
                                        new_item = ItemStack(str(item_clicked.type))
                                        new_item.amount = 64
                                        player.inventory.add_item(new_item)
                                    player.send_message(LanguageManager.get_translate("success.buy", [int(amount), name, float(total_price)]))
                                    player.send_message(LanguageManager.get_translate("success.balance", [float(new_balance)]))
                                self.manager.reduce_money(player, "coins", total_price, add_item)
                            else:
                                player.send_message(LanguageManager.get_translate("errors.no_money", [float(total_price)]))
                                menu.close(player)
                                return
                        self.manager.has_money(player, "coins", total_price, has_money)

            elif sell_stack in item_meta.display_name:
                for lore in item_meta.lore:        
                    if lore and sell_item in lore:  
                        price = float(lore.split()[-1].lstrip("$"))
                        amount = item_clicked.amount * 64
                        total_price = amount * price
                        name = str(item_clicked.type).replace("minecraft:", "").replace("_", " ").upper()
                        def remove_item(new_balance):
                            new_item = ItemStack(str(item_clicked.type))
                            if player.inventory.contains_at_least(new_item, amount):
                                for _ in range(item_clicked.amount):       
                                    new_item.amount = 64
                                    player.inventory.remove_item(new_item)
                                player.send_message(LanguageManager.get_translate("success.sell", [int(amount), name, float(total_price)]))
                                player.send_message(LanguageManager.get_translate("success.balance", [float(new_balance)]))
                            else:
                                player.send_message(LanguageManager.get_translate("menu.errors.no_item_to_sell"))
                                menu.close(player)
                        self.manager.add_money(player, "coins", total_price, remove_item)

        menu.set_listener(on_custom_buy_confirm)
        menu.send_to(player)