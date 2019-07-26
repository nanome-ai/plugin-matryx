import os
import re
from functools import partial

import nanome
import utils
from nanome.util import Logs

class FirstToHashMenu():
    def __init__(self, plugin, on_close):
        self._plugin = plugin

        menu = nanome.ui.Menu.io.from_json('menus/json/firsttohash.json')
        menu.register_closed_callback(on_close)
        self._menu = menu

        self._is_component = False
        self._workpaths = {}
        self._paths_selected = 0

        self._text = menu.root.find_node('Text').get_content()
        self._txt_banner = "Hashing your work on Matryx is final. You've selected the following structures for submission. Are you sure you would like to hash this work?"
        self._txt_no_selection = "You haven't selected anything from the workspace. Please first make a selection before trying to hash to Matryx."

        self._ln_list = menu.root.find_node('List')
        self._ln_confirm = menu.root.find_node('Confirm Button')
        self._ln_cancel = menu.root.find_node('Cancel Button')
        self._ln_refresh = menu.root.find_node('Refresh')
        self._ln_refresh.get_content().register_pressed_callback(self.display_selected)

        self._list = self._ln_list.get_content()
        self._btn_confirm = self._ln_confirm.get_content()
        self._btn_confirm.register_pressed_callback(self.hash_work)
        self._btn_cancel = self._ln_cancel.get_content()
        self._btn_cancel.register_pressed_callback(on_close)

        self._prefab_entry = menu.root.find_node('Entry Item')
        self._icon_path = os.path.join(os.path.dirname(__file__), '..', 'images', 'checkmark.png')

    def display_selected(self, as_component, button=None):
        def _display_selected(workspace):
            paths_names = self.write_selection(workspace)
            self._paths_selected = len(paths_names)
            self.set_display(len(paths_names) != 0)

            self._list.items = []
            for path_name in paths_names:
                self._workpaths[path_name[0]] = True
                Logs.debug('filename:', path_name[1])
                clone = self._prefab_entry.clone()
                clone.find_node('Label').get_content().text_value = path_name[1]
                icon_ln = clone.find_node('Selected Icon')
                icon_ln.add_new_image(self._icon_path)
                icon_ln.selected = True
                icon_ln.path = path_name[0]
                clone.get_content().register_pressed_callback(partial(self.toggle_selected, icon_ln))
                self._list.items.append(clone)

            if self._is_component:
                self._ln_cancel.enabled = False
                self._plugin.refresh_menu()

            else:
                self._ln_cancel.enabled = True
                self._plugin.open_menu(self._menu)

        self._plugin.request_workspace(_display_selected)

    def use_as_component(self):
        self._ln_confirm.set_padding(left=0)
        self._list.display_rows = 2
        self._is_component = True

    def use_as_menu(self):
        self._ln_confirm.set_padding(left=0.01)
        self._list.display_rows = 6
        self._is_component = False

    def set_display(self, has_selection):
        self._text.text_value = self._txt_banner if has_selection else self._txt_no_selection
        self._ln_list.enabled = has_selection
        self._ln_confirm.enabled = has_selection
        self._ln_cancel.enabled = has_selection
        self._btn_confirm.unusable = not has_selection

    def toggle_selected(self, l_node, button):
        if l_node.selected:
            l_node.remove_content()
            self._paths_selected -= 1
        else:
            l_node.add_new_image(self._icon_path)
            self._paths_selected += 1

        l_node.selected = not l_node.selected
        self._workpaths[l_node.path] = l_node.selected
        self._btn_confirm._unusable = self._paths_selected == 0

        Logs.debug('unusable: ' + str(self._paths_selected == 0))

        self._plugin.refresh_menu()

    def hash_work(self, button):
        if len(self._workpaths) == 0 or self._paths_selected == 0:
            return

        self._plugin._modal.show_message('Hashing your work to Matryx')

        selected_paths = [wp_entry[0] for wp_entry in self._workpaths.items() if wp_entry[1]]
        ipfs_hash = self._plugin._cortex.upload_files(selected_paths)

        sender = self._plugin._account.address
        salt = utils.random_bytes()
        commit_hash = self._plugin._web3.solidity_sha3(['address', 'bytes32', 'string'], [sender, salt, ipfs_hash])

        tx_hash = self._plugin._web3._commit.claimCommit(commit_hash)
        self._plugin._web3.wait_for_tx(tx_hash)

        tx_hash = self._plugin._web3._commit.createCommit('0x' + '0' * 64, False, salt, ipfs_hash, 1)
        self._plugin._web3.wait_for_tx(tx_hash)

        if self._is_component:
            self._plugin._menu_tournament.submit_to_tournament(commit_hash, button)
        else:
            self._plugin._modal.show_message('Your work has been published to Matryx')

    def write_selection(self, workspace):
        structures = self.get_fully_selected(workspace)

        paths_names = []
        for structure in structures:
            if structure is not nanome.api.structure.Residue and structure is not nanome.api.structure.Atom:
                path, name = self.write_mmcif(structure)
                paths_names.append((path, name))
            else:
                path, name = self.write_sdf(structure)
                paths_names.append((path, name))
        return paths_names

    def get_fully_selected(self, workspace):
        complexes = []
        #adding complexes
        for complex in workspace.complexes:
            if not complex.get_selected():
                continue

            selection_complex = nanome.api.structure.Complex()
            selection_complex.name = 'Partial_' + complex.name
            fully_selected = True
            for atom in complex.atoms:
                if not atom.selected:
                    Logs.debug('atom not selected:' + atom.name)
                    fully_selected = False
                    break
            if fully_selected:
                Logs.debug('complex',complex.name,'fully selected')
                complexes.append(complex)
                continue
            else:
                complexes.append(selection_complex)
                Logs.debug('complex', complex.name, 'partially selected')
            #adding molecules
            for molecule in complex.molecules:
                selection_molecule = nanome.api.structure.Molecule()
                selection_complex.add_molecule(selection_molecule)
                selection_molecule.name = molecule.name
                fully_selected = True
                for atom in molecule.atoms:
                    if not atom.selected:
                        fully_selected = False
                        break
                if fully_selected:
                    Logs.debug('molecule',molecule.name,'fully selected')
                    selection_complex.add_molecule(molecule)
                    selection_complex.name += '-' + molecule.name
                    continue
                #adding chains
                for chain in complex.chains:
                    selection_chain = nanome.api.structure.Chain()
                    selection_molecule.add_chain(selection_chain)
                    selection_chain.name = chain.name
                    fully_selected = True
                    for atom in chain.atoms:
                        if not atom.selected:
                            fully_selected = False
                            break
                    if fully_selected:
                        Logs.debug('chain',chain.name,'fully selected')
                        selection_molecule.add_chain(chain)
                        selection_complex.name += '-' + chain.name
                        continue
                    #adding residues
                    for residue in chain.residues:
                        selection_residue = nanome.api.structure.Residue()
                        selection_chain.add_residue(selection_residue)
                        selection_residue.name = residue.name
                        fully_selected = True
                        for atom in residue.atoms:
                            if not atom.selected:
                                fully_selected = False
                                break
                        if fully_selected:
                            Logs.debug('residue',residue.name,'fully selected')
                            selection_chain.add_residue(residue)
                            selection_complex.name += '-' + residue.name
                            continue
                        #addint atoms
                        for atom in residue.atoms:
                            if atom.selected:
                                Logs.debug('atom',atom.name,'selected')
                                selection_residue.add_atom(atom)
                                selection_complex.name += '-' + atom.name

        return complexes

    def write_pdb(self, structure):
        path = os.path.join(os.path.dirname(__file__), '..', 'temp', 'molecules', structure.name + '.pdb')
        structure.io.to_pdb(path)
        return ( path, structure.name )

    def write_mmcif(self, structure):
        path = os.path.join(os.path.dirname(__file__), '..', 'temp', 'molecules', structure.name + '.cif')
        structure.io.to_mmcif(path)
        return ( path, structure.name )

    def write_sdf(self, structure):
        path = os.path.join(os.path.dirname(__file__),  '..', 'temp', 'molecules', structure.name + '.sdf')
        structure.to_sdf(path)
        return ( path, structure.name )