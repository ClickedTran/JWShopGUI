from endstone.event import event_handler, PlayerChatEvent

from shopgui.manager.shop_manager import ShopManager
from shopgui.language.language import LanguageManager

class EventListener:
    def __init__(self, plugin):
        self.plugin = plugin
        self.manager = ShopManager(self.plugin)

    @event_handler
    def on_chat(self, event: PlayerChatEvent):
        player = event.player
        if player.name in self.manager.editMode:
            event.is_cancelled = True
            clear_message = event.message.strip()
            args = [arg for arg in clear_message.split() if arg.strip()]
            shop_name = self.manager.editMode[player.name]
            match args[0].lower():
                case "help" | "?":
                    data = LanguageManager.get_raw("plugin_info.command.setup.help")
                    player.send_message(data)
                
                case "add":
                    item_name = args[1]
                    buy_price = args[2]
                    sell_price = args[3]

                    if not buy_price.isdigit() or not sell_price.isdigit():
                        player.send_message(LanguageManager.get_translate("plugin_info.command.setup.add.error"))
                        return
                    
                    self.manager.addItem(shop_name, item_name, buy_price, sell_price)
                    player.send_message(LanguageManager.get_translate("plugin_info.command.setup.add.success", [item_name, shop_name, buy_price, sell_price]))

                case "remove":
                    item_name = args[1]
                    success, remove_type, final_name = self.manager.removeItem(shop_name, item_name)
            
                    if success:
                        if remove_type == "slot":
                            player.send_message(LanguageManager.get_translate("plugin_info.command.setup.remove.success_1", [final_name]))
                        else:
                            player.send_message(LanguageManager.get_translate("plugin_info.command.setup.remove.success_2", [final_name]))
                    else:
                        if remove_type == "slot":
                            player.send_message(LanguageManager.get_translate("plugin_info.command.setup.remove.error_1", [final_name]))
                        else:
                            player.send_messag(LanguageManager.get_translate("plugin_info.command.setup.remove.error_2", [final_name]))
                
                case "done":
                    del self.manager.editMode[player.name]
                    player.send_message(LanguageManager.get_translate("plugin_info.command.setup.done", [shop_name]))
                    self.manager.reload()