from endstone.event import event_handler, PlayerChatEvent

from shopgui.manager.shop_manager import ShopManager

class EventListener:
    def __init__(self, plugin):
        self.plugin = plugin
        self.manager = ShopManager(self.plugin)

    @event_handler
    def on_chat(self, event: PlayerChatEvent):
        player = event.player
        if player.name in self.manager.editMode:
            event.cancelled = True
            clear_message = event.message.strip()
            args = [arg for arg in clear_message.split() if arg.strip()]
            shop_name = self.manager.editMode[player.name]
            match args[0].lower():
                case "help" | "?":
                    player.send_message("§6> All Edit Commands <")
                    player.send_message("§l§7help§r§7 - Display available commands")
                    player.send_message("§l§7add <item_name> <buy_price> <sell_price>§r§7 - Add an item to the shop with specified buy and sell prices")
                    player.send_message("§l§7remove <item_name | slot>§r§7 - Remove an item from the shop")
                    player.send_message("§l§7done§r§7 - Save changes and exit edit mode")
                
                case "add":
                    item_name = args[1]
                    buy_price = args[2]
                    sell_price = args[3]

                    if not buy_price.isdigit() or not sell_price.isdigit():
                        player.send_message("§cBuy price and sell price must be valid numbers!")
                        return
                    
                    self.manager.addItem(shop_name, item_name, buy_price, sell_price)
                    player.send_message(f"§aItem '{item_name}' has been added to the shop with buy price {buy_price} and sell price {sell_price}.")

                case "remove":
                    item_name = args[1]
                    success, remove_type, final_name = self.manager.removeItem(shop_name, item_name)
            
                    if success:
                        if remove_type == "slot":
                            player.send_message(f"§aItem in slot {final_name} has been removed from the shop.")
                        else:
                            player.send_message(f"§aItem '{final_name}' has been removed from the shop.")
                    else:
                        if remove_type == "slot":
                            player.send_message(f"§cNo item found in slot {final_name}.")
                        else:
                            player.send_message(f"§cNo item named '{final_name}' found in the shop.")
                
                case "done":
                    del self.manager.editMode[player.name]
                    player.send_message(f"§6You have exited edit mode for shop {shop_name}.")