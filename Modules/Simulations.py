import numpy as np
import os
import sys
import math
import fcntl
import multiprocessing as mp
from ctypes import c_double



class Planet:

    def __init__(self, 
                 mass_function='Cassan', 
                 a_min = np.log10(0.3), 
                 a_max = np.log10(0.3) + 2, 
                 mass_min = -1, 
                 mass_max = 2, 
                 nf = None, 
                 nl = 1000, 
                 data_dir = './Data', 
                 live_run = True,
                 rundes = 'toybox_planets',
                 cores = 0,
                 file_ext = "list",
                 fuck_this=""
                 ):
        '''Initialize the Planet class'''
        
        print("Initializing Planet class...")  # Debug print at the very beginning

        self.fuck_this = fuck_this
        if cores:  # if != 0 then set the number of cores to the input value
            self.cores = cores
        else:  # if 0 then set the number of cores to half the number of available cores
            self.cores = int(mp.cpu_count()/2)
        self.mass_function = mass_function
        self.a_min = a_min
        self.a_max = a_max
        self.mass_min = mass_min
        self.mass_max = mass_max
        self.live_run = live_run
        self.rundes = rundes
        self.data_dir = data_dir
        self.nl = int(nl)
        self.nf = nf
        if self.data_dir[-1] != '/':
            self.data_dir += '/'
        self.nl = nl  # number of lines in a planet file
        if self.live_run and nf is None:
            self.nf = self.cores  # number of planet "files"
            manager = mp.Manager()
            self.shared_list = manager.list([np.empty((self.nl, 4)) for _ in range(self.nf)])
            self.state = np.empty((self.nf,self.nl,4))
        elif nf is not None and not self.live_run:
            self.nf = nf
        else:
            sys.exit("Incompatible nf and live_run arguments")
        self.nf = int(self.nf)
        self.dir_name = f"{self.data_dir}planets/{self.rundes}"
        if not os.path.exists(self.dir_name):
            os.makedirs(self.dir_name)
        if self.dir_name[-1] != '/':
            self.dir_name += '/'
        self.base = f"{self.dir_name}{self.rundes}.planets"  # Base file name
        self.master_list_file = f"{self.base}.master.lists"  # Master list file name
        # Ensure the master list file exists and if not create it
        if not os.path.exists(self.master_list_file) and not self.live_run:
            open(self.master_list_file, 'w').close()
        self.file_ext = file_ext

    def get_unique_indexes(self):
            '''
            This function exists so that multiple versions of this script can be run at once without 
            overlapping file indexing. It reserves n indexes in the master list file and returns them.
            '''
            with open(self.master_list_file, 'a+') as f:
                f.seek(0)
                fcntl.flock(f, fcntl.LOCK_EX)
                lines = f.readlines()
                if lines:
                    last_lines = lines[-1].strip()
                    last_index = int(last_lines.split('_')[-1])
                    start_index = last_index + 1
                else:
                    start_index = 0
                end_index = start_index + self.nl
                index_ext = f"{start_index}_{end_index}"
                f.write(f"{index_ext}\n")
                fcntl.flock(f, fcntl.LOCK_UN)
            return index_ext

    def draw_planet_sample(self):

        '''# Use multiprocessing to parallelize the loop
        for start in range(0, self.nf, self.cores):
            end = min(start + self.cores, self.nf)
            processes = []
            for i in range(start, end):
                p = mp.Process(target=self.worker, args=(i, self.shared_array_base))
                processes.append(p)
                p.start()

            for p in processes:
                p.join()'''
        
        with mp.Pool(processes=self.cores) as pool:
            pool.starmap(self.worker, [(i, self.shared_list) for i in range(self.nf)])

        self.state = np.array(self.shared_list)  # because lists are gross
        #print('draw_planet_sample: 0:', self.state[0])

    def worker(self, i, shared_list):       

        #constants
        pi = math.pi
        mE = 3.00348959632e-6
        
        # Reserve the next nl of indexes
        if not self.live_run:
            index_ext = self.get_unique_indexes(self.master_list_file, self.nl)
            pfile = f"{self.base}.{index_ext}.{self.file_ext}"

            if os.path.exists(pfile):
                print(f"File {pfile} already exists. Skipping.")
                pass
        else:
            pfile = "live_run"  # so that os.path.exists(pfile) doesn't throw an error

        if not os.path.exists(pfile) or self.live_run:
            # Generate 4 arrays of size nl using NumPy, as a matrix
            combined_array = np.empty((self.nl, 4))
            rnd = np.random.rand(self.nl)
            
            combined_array[:, 0] = mE * 10.0 ** (self.mass_min + np.random.rand(self.nl) * 
                                                 (self.mass_max - self.mass_min))
            combined_array[:, 1] = 10.0 ** (self.a_min + (self.a_max - self.a_min) * 
                                            np.random.rand(self.nl))
            combined_array[:, 2] = 180.0 * np.where(rnd < 0.5, 
                                         np.arccos(2.0 * rnd), 
                                         -np.arccos(2.0 - 2.0 * rnd)
                                         ) / pi
            combined_array[:, 3] = 360.0 * np.random.rand(self.nl)

            # Save the array to a file
            if self.file_ext == "npy" and not self.live_run:
                np.save(pfile, combined_array)
            elif not self.live_run:
                np.savetxt(pfile, 
                           combined_array, 
                           delimiter=',', 
                           header='mass,a,inc,p'
                           )
            else:
                shared_list[i] = combined_array.copy() # copy might be necessary to avoid overwriting ???
                #print(f'worker: planet_state: {i}:', shared_list[i])
