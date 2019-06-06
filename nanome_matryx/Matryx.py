import nanome
from nanome.util import Logs

from MatryxCortex import MatryxCortex
from AccountsMenu import AccountsMenu

import web3
import blockies

class Matryx(nanome.PluginInstance):
    def start(self):
        self._matryx_menu = nanome.ui.Menu.io.from_json("_matryx_menu.json")
        menu = self._matryx_menu
        
        self._cortex = MatryxCortex('https://cortex-staging.matryx.ai')
        self._accounts_menu = AccountsMenu(self, self.open_matryx_menu)

        self._list = menu.root.find_node("List", True).get_content()

        self._account_button = menu.root.find_node("Account Button", True).get_content()
        self._account_button.register_pressed_callback(self._accounts_menu.show_menu)
        
        self._account_blockie = menu.root.find_node("Blockie")
        self._account_eth = menu.root.find_node("ETH Balance").get_content()
        self._account_mtx = menu.root.find_node("MTX Balance").get_content()

        self._all_tournaments_button = menu.root.find_node('All Tournaments').get_content()
        self._all_tournaments_button.register_pressed_callback(self.populate_all_tournaments)

        self._my_tournaments_button = menu.root.find_node('My Tournaments').get_content()
        self._my_tournaments_button.register_pressed_callback(self.populate_my_tournaments)

        self._my_creations_button = menu.root.find_node('My Creations').get_content()
        self._my_creations_button.register_pressed_callback(self.populate_my_creations)

        self._tournament_item_prefab = menu.root.find_node('Tournament Item Prefab')

        self._commit_item_prefab = nanome.ui.LayoutNode()
        self._commit_item_prefab.layout_orientation = nanome.ui.LayoutNode.LayoutTypes.horizontal
        child = self._commit_item_prefab.create_child_node()
        child.forward_dist = 0.002
        child.add_new_button()
        
        self.menu = menu
        self.refresh()

    def on_run(self):
        self.open_matryx_menu(None)
        self.populate_all_tournaments(self._all_tournaments_button)

    def refresh(self):
        self.menu.enabled = True
        self.update_menu(self.menu)

    def open_matryx_menu(self, button):
        self.menu.enabled = False
        self.menu = self._matryx_menu
        self.refresh()

    def update_account(self, account):
        self._account = account
        self._account_button.text.value_idle = account.short_address
        self._account_blockie.add_new_image(account.blockie)
        self.populate_all_tournaments(self._all_tournaments_button)

        # TODO ETH and MTX
    
    def toggle_tab(self, active_tab):
        tabs = [
            self._all_tournaments_button,
            self._my_tournaments_button,
            self._my_creations_button
        ]

        for tab in tabs:
            tab.selected = False
        
        active_tab.selected = True
        self.refresh()
    
    def populate_tournaments(self, status='abandoned', mine=False):
        params = {
            'offset': 0,
            'sortBy': 'round_end',
            'status': status
        }
        
        if mine:
            params['owner'] = self._accounts_menu._account.address

        tournaments = self._cortex.get_tournaments(params)
        self._list.items = []

        for tournament in tournaments:
            clone = self._tournament_item_prefab.clone()
            clone.enabled = True
            
            title = clone.find_node('Title').get_content()
            text = tournament['title']
            text = text[0:55] + ("..." if len(text) > 55 else "") 
            title.text_value = text
            
            bounty = clone.find_node('Bounty').get_content()
            bounty.text_value = str(tournament['bounty']) + ' MTX'
            self._list.items.append(clone)
    
    def populate_all_tournaments(self, button):
        self.populate_tournaments()
        self.toggle_tab(button)

    def populate_my_tournaments(self, button):
        self.populate_tournaments(mine=True)
        self.toggle_tab(button)

    def populate_my_creations(self, button):
        commits = self._cortex.get_commits(self._account.address)
        self._list.items = []

        for commit in commits:
            clone = self._commit_item_prefab.clone()
            clone.enabled = True

            btn = clone.get_children()[0].get_content()
            btn.set_all_text(commit['hash'])
            # btn.register_pressed_callback()
            self._list.items.append(clone)

        self.toggle_tab(button)
        


def main():
    plugin = nanome.Plugin("Matryx", "Interact with the Matryx platform", "Utilities", False)
    plugin.set_plugin_class(Matryx)
    plugin.run('127.0.0.1', 8888)

if __name__ == "__main__":
    main()

# !!!!!!!!!!!!!!!!!!!!!!!!!!!!
# TODO
#   - tournament menu
# !!!!!!!!!!!!!!!!!!!!!!!!!!!!