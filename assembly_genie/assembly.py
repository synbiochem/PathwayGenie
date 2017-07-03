'''
PathwayGenie (c) University of Manchester 2017

PathwayGenie is licensed under the MIT License.

To view a copy of this license, visit <http://opensource.org/licenses/MIT/>.

@author:  neilswainston
'''
from _collections import defaultdict
import re
import sys

from synbiochem.utils import plate_utils
from assembly_genie.build import BuildGenieBase


_WORKLIST_COLS = ['DestinationPlateBarcode',
                  'DestinationPlateWell',
                  'SourcePlateBarcode',
                  'SourcePlateWell',
                  'Volume',
                  'ComponentName',
                  'description',
                  'ice_id',
                  'plasmid_id']


class AssemblyGenie(BuildGenieBase):
    '''Class implementing AssemblyGenie algorithms.'''

    def __init__(self, ice_details, ice_ids, src_filenames=None):
        super(AssemblyGenie, self).__init__(ice_details, ice_ids)
        self.__comp_well = _get_src_comp_well(src_filenames)

    def export_lcr_recipe(self,
                          plate_ids=None,
                          def_reagents=None,
                          vols=None,
                          domino_vol=3):
        '''Exports LCR recipes.'''
        if plate_ids is None:
            plate_ids = {'domino_pools': 'domino_pools', 'lcr': 'lcr'}

        if def_reagents is None:
            def_reagents = {'mastermix': 7.0, 'Ampligase': 1.5}

        if vols is None:
            vols = {'backbone': 1, 'parts': 1, 'dom_pool': 1, 'total': 25,
                    'domino': domino_vol}

        pools = defaultdict(lambda: defaultdict(list))

        for ice_id in self._ice_ids:
            data = self._get_data(ice_id)

            for part in data[0].get_metadata()['linkedParts']:
                data = self._get_data(part['partId'])

                if data[4] == 'ORF':
                    pools[ice_id]['parts'].append(data)
                elif data[4] == 'DOMINO':
                    pools[ice_id]['dominoes'].append(data)
                else:
                    # Assume backbone:
                    pools[ice_id]['backbone'].append(data)

        self.__output_lcr_recipe(pools, plate_ids, def_reagents, vols)

    def __output_lcr_recipe(self, pools, plate_ids, def_reagents, vols):
        '''Outputs recipes.'''
        # Write domino pools worklist:
        self.__write_dom_pool_worklist(pools, plate_ids['domino_pools'],
                                       vols['domino'])

        print ''

        # Write LCR worklist:
        self.__write_lcr_worklist(plate_ids['lcr'], pools, def_reagents, vols)

    def __write_dom_pool_worklist(self, pools, dest_plate_id, vol):
        '''Write domino pool worklist.'''
        print '\t'.join(_WORKLIST_COLS)

        for idx, ice_id in enumerate(pools):
            dest_well = plate_utils.get_well(idx)

            for domino in pools[ice_id]['dominoes']:
                src_well = self.__comp_well[domino[1]]

                print '\t'.join([dest_plate_id, dest_well, src_well[1],
                                 src_well[0], str(vol),
                                 domino[2], domino[5], domino[1],
                                 ice_id])

            self.__comp_well[ice_id + '_domino_pool'] = \
                (dest_well, dest_plate_id)

    def __write_lcr_worklist(self, dest_plate_id, pools, def_reagents, vols):
        '''Writes LCR worklist.'''
        print '\t'.join(_WORKLIST_COLS)

        for idx, ice_id in enumerate(self.__ice_ids):
            dest_well = plate_utils.get_well(idx)

            # Write water:
            well = self.__comp_well['H2O']

            h2o_vol = vols['total'] - \
                sum(def_reagents.values()) - \
                len(pools[ice_id]['backbone']) * vols['backbone'] - \
                len(pools[ice_id]['parts']) * vols['parts'] - \
                vols['dom_pool']

            print '\t'.join([dest_plate_id, dest_well, well[1],
                             well[0], str(h2o_vol),
                             'H2O', 'H2O', '',
                             ice_id])

            # Write backbone:
            for comp in pools[ice_id]['backbone']:
                well = self.__comp_well[comp[1]]

                print '\t'.join([dest_plate_id, dest_well, well[1],
                                 well[0], str(vols['backbone']),
                                 comp[2], comp[5], comp[1],
                                 ice_id])

            # Write parts:
            for comp in pools[ice_id]['parts']:
                well = self.__comp_well[comp[1]]

                print '\t'.join([dest_plate_id, dest_well, well[1],
                                 well[0], str(vols['parts']),
                                 comp[2], comp[5], comp[1],
                                 ice_id])

            # Write domino pools:
            well = self.__comp_well[ice_id + '_domino_pool']

            print '\t'.join([dest_plate_id, dest_well, well[1],
                             well[0], str(vols['dom_pool']),
                             'domino pool', 'domino pool', '',
                             ice_id])

            # Write default reagents:
            for reagent, vol in def_reagents.iteritems():
                well = self.__comp_well[reagent]

                print '\t'.join([dest_plate_id, dest_well, well[1],
                                 well[0], str(vol),
                                 reagent, reagent, '',
                                 ice_id])

    def __get_data(self, ice_id):
        '''Gets data from ICE entry.'''
        if ice_id in self.__data:
            return self.__data[ice_id]

        ice_entry = self.__ice_client.get_ice_entry(ice_id)
        metadata = ice_entry.get_metadata()
        data = ice_entry, \
            metadata['partId'], \
            metadata['name'], \
            metadata['type'], \
            ice_entry.get_parameter('Type'), \
            re.sub('\\s*\\[[^\\]]*\\]\\s*', ' ',
                   metadata['shortDescription']).replace(' - ', '_'), \
            ice_entry.get_seq()

        self.__data[ice_id] = data

        return data


def _get_src_comp_well(src_filenames):
    '''Gets components to well / plate mappings.'''
    comp_well = {}

    if src_filenames:
        for src_filename in src_filenames:
            with open(src_filename) as fle:
                plate_id = src_filename[:src_filename.find('.')]

                for line in fle.read().splitlines():
                    if line.strip():
                        terms = line.split('\t')
                        comp_well[terms[1]] = (terms[0], plate_id)

    return comp_well


def main(args):
    '''main method.'''
    genie = AssemblyGenie({'url': args[0],
                           'username': args[1],
                           'password': args[2]},
                          args[4:],
                          args[3].split(','))

    plate_ids = {'domino_pools': 'SBC50042389', 'lcr': 'lcr'}
    genie.export_lcr_recipe(plate_ids)


if __name__ == '__main__':
    main(sys.argv[1:])