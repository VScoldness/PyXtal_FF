from ase.db import connect
from ase.io import read
from ase import units
from monty.serialization import loadfn
from tqdm import tqdm

def outcar2db_list(outcar_path_list, db_path, group="Surface"):
    with connect(db_path) as _database:
        for cur_outcar in tqdm(outcar_path_list):
            try:
                cur_structure , dat = outcar2db(cur_outcar, group)
                _database.write(cur_structure, data=dat)
            except:
                print("Wrong data: ", cur_outcar)


def outcar2db(cur_outcar, group="Surface"):
    cur_structure = read(cur_outcar)
    dat = {'energy': cur_structure.get_potential_energy(),
            'force':  cur_structure.get_forces(),
            'stress': cur_structure.get_stress()/units.GPa,
            'group':  group}
    return cur_structure, dat


def json2db(json_path_list, db_path, group="NoElastic"):
    with connect(db_path) as _database:
        for cur_json in json_path_list:
            data_list = loadfn(cur_json)
            for d in data_list:
                dat = {'energy':  d['outputs']['energy'],
                        'force':  d['outputs']['forces'],
                        'stress': d['outputs']['stress'],
                        'group':  group}
                structure = d['structure'].to_ase_atoms()
                _database.write(structure, data=dat)



