class MainMenu:
    def __init__(self, plugin):
        self._plugin = _plugin

        menu = nanome.ui.Menu.io.from_json('menus/json/matryx.json')
        self._menu = menu

        self._list_node = menu.root.find_node('List', True)
        self._list = self._list_node.get_content()
        self._error_message = menu.root.find_node('Error Message', True)

        self._button_account = menu.root.find_node('Account Button', True).get_content()
        self._button_account.register_pressed_callback(self._menu_accounts.show_menu)

        self._account_blockie = menu.root.find_node('Blockie')
        self._account_eth = menu.root.find_node('ETH Balance').get_content()
        self._account_mtx = menu.root.find_node('MTX Balance').get_content()

        self._button_all_tournaments = menu.root.find_node('All Tournaments').get_content()
        self._button_all_tournaments.register_pressed_callback(self.populate_all_tournaments)

        self._button_my_tournaments = menu.root.find_node('My Tournaments').get_content()
        self._button_my_tournaments.register_pressed_callback(self.populate_my_tournaments)

        self._button_my_creations = menu.root.find_node('My Creations').get_content()
        self._button_my_creations.register_pressed_callback(self.populate_my_creations)

        self._prefab_tournament_item = menu.root.find_node('Tournament Item Prefab')

        self._prefab_commit_item = nanome.ui.LayoutNode()
        self._prefab_commit_item.add_new_button()

    def show_error(self, error):
        self._list_node.enabled = False
        self._error_message.enabled = True
        self._error_message.get_content().text_value = error
