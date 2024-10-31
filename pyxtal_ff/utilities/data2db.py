from ase.db import connect
from ase.io import read, write
from ase.io.vasp import read_vasp_out
from ase import units
from monty.serialization import loadfn
from tqdm import tqdm
import numpy as np 



def outcar2db_AIMD_list(outcar_path_list, db_path, idx_list = None, n_list = 0, group="Non-Elastic"):
    wrong_files = []
    
    if idx_list is None or n_list > 0:
        read_idx = True
    else:
        read_idx = False

    with connect(db_path) as _database:
        for cur_outcar in tqdm(outcar_path_list):
            if read_idx:

                idx_list = [i for i in range(len(read_vasp_out(cur_outcar, index=':')))]
                if n_list > 0:
                    idx_list = evenly_select_elements(idx_list, n_list)
      
            for cur_idx in tqdm(idx_list):
                try:
                    cur_structure, dat = outcar2db(cur_outcar, group, cur_idx)
                except:
                    print("\nWrong data: ", cur_outcar)
                    wrong_files.append(cur_outcar)
                    break
                finally:
                    _database.write(cur_structure, data=dat)
    print(len(wrong_files)) 


def outcar2db_list(outcar_path_list, db_path, group="Non-Elastic"):
    wrong_files = []
    with connect(db_path) as _database:
        for cur_outcar in tqdm(outcar_path_list):
            try:
                cur_structure, dat = outcar2db(cur_outcar, group)
                _database.write(cur_structure, data=dat)
            except:
                print("\nWrong data: ", cur_outcar)
                wrong_files.append(cur_outcar)
            finally:
                pass
    print(len(wrong_files))


def outcar2db(cur_outcar, group="Non-Elastic", idx=-1):
    cur_structure = read(cur_outcar, index=idx)
    stress = -1 * cur_structure.get_stress()/units.GPa
    stress[-1], stress[-3] = stress[-3], stress[-1]

    cur_energy = cur_structure.get_potential_energy()

    dat = {'energy': cur_energy,
            'force':  cur_structure.get_forces(),
            'stress': stress,
            'group':  group}
    return cur_structure, dat

def combineDB(output: str, combined_bds: list[str]):
    with connect(output) as _database:
        for bd in combined_bds:
            with connect(bd) as database:
                for row in database.select():
                    structure = database.get_atoms(row.id)
                    dat = {'energy': row.data['energy'],
                        'force': row.data['force'],
                        'stress': row.data['stress'],
                        'group': row.data['group']}
                    _database.write(structure, data=dat)

        

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


def evenly_select_elements(input_list, n):
    if n <= 0:
        return []
    
    if n >= len(input_list):
        return input_list


    step = len(input_list) / n
    selected_elements = [input_list[int(i * step)] for i in range(n-1)]
    
    selected_elements.append(input_list[-1])

    return selected_elements


def db2XYZ(src, dst):
    with connect(src) as database:
        atom_list = []
        for row in tqdm(database.select()):
            structure = database.get_atoms(row.id)
            force = np.array(row.data["force"])
            structure.info["energy"] = row.data["energy"]
            structure.arrays['force'] = force
            
            atom_list.append(structure)

        write(dst, atom_list, format='extxyz')