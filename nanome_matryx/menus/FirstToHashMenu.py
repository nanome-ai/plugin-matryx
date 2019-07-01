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

        self._text = menu.root.find_node('Text').get_content()
        self._list = menu.root.find_node('List').get_content()
        self._btn_confirm = menu.root.find_node('Confirm Button').get_content()
        self._btn_cancel = menu.root.find_node('Cancel Button').get_content()
        self._btn_cancel.register_pressed_callback(on_close)

        self._prefab_entry = menu.root.find_node('Entry Item')

    def display_selected(self, button):
        def _display_selected(workspace):
            file_paths = self.write_selection(workspace)
            file_names = [re.search('(?<=\\\\temp\\\\).*$', file_path).group(0) for file_path in file_paths]

            self._list.items = []
            for file_name in file_names:
                Logs.debug('filename:', file_name)
                clone = self._prefab_entry.clone()
                clone.get_content().set_all_text(file_name)
                self._list.items.append(clone)

            self._btn_confirm.register_pressed_callback(partial(self.hash_work, file_paths))
            self._plugin.open_menu(self._menu)

        self._plugin.request_workspace(_display_selected)


    def hash_work(self, work_paths, button):
        self._plugin._modal.show_message('Hashing your work to Matryx')
        Logs.debug('paths:', work_paths)
        ipfs_hash = self._plugin._cortex.upload_files(work_paths)

        sender = self._plugin._account.address
        salt = utils.random_bytes()
        commit_hash = self._plugin._web3.solidity_sha3(['address', 'bytes32', 'string'], [sender, salt, ipfs_hash])

        tx_hash = self._plugin._web3._commit.claimCommit(commit_hash)
        self._plugin._web3.wait_for_tx(tx_hash)

        tx_hash = self._plugin._web3._commit.createCommit('0x' + '0' * 64, False, salt, ipfs_hash, 1)
        self._plugin._web3.wait_for_tx(tx_hash)

        self._plugin._modal.show_message('Your work has been published to Matryx')
        return

    def write_selection(self, workspace):
        structures = self.get_fully_selected(workspace)

        paths = []
        for structure in structures:
            if structure is not nanome.api.structure.Residue and structure is not nanome.api.structure.Atom:
                paths.append(self.write_mmcif(structure))
            else:
                paths.append(self.write_sdf(structure))
        return paths

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
        path = os.path.join(os.path.dirname(__file__), '../temp/molecules', structure.name + '.pdb')
        structure.io.to_pdb(path)
        return path

    def write_mmcif(self, structure):
        path = os.path.join(os.path.dirname(__file__), '../temp/molecules', structure.name + '.cif')
        structure.io.to_mmcif(path)
        return path

    def write_sdf(self, structure):
        path = os.path.join(os.path.dirname(__file__),  '../temp/molecules', structure.name + '.sdf')
        structure.to_sdf(path)
        return path