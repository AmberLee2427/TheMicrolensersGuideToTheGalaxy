import os
import sys
import math
import numpy as np
import fcntl
import multiprocessing as mp
import time

# Constants
mmin = math.log10(0.1)
mmax = math.log10(100)
amin = math.log10(0.3)
amax = amin + 2
pi = math.pi
mE = 3.00348959632e-6  # samples are drawn in solar masses and saved in earth masses

# Required arguments
script_name = sys.argv[0].split('/')[-1]
try:
    nl = int(sys.argv[1])  # length of a gulls sub run
    nf = int(sys.argv[2])  # number of gulls subruns
    rundes = sys.argv[3]
except IndexError:
    print(f"Usage: python {script_name} nl nf file_ext")
    sys.exit(1)

# Optional arguments
try:
    file_ext = sys.argv[4]
except IndexError:
    file_ext = ""

# Environment variables
#fs/proj/gulls/data/planets/test_run_name/test_run_name.planets.001.0001 (field.subrun)
#readPlanet.cpp <- new gulls, check what header it is looking for
#                  also check what filename it is looking for

data_dir = '/fs/project/gaudi.1/gulls/data'
if data_dir[-1] != '/':
    data_dir += '/'

def get_unique_indexes(master_list_file, nl):
    '''
    This function exists so that multiple versions of this script can be run at once without 
    overlapping file indexing. It reserves n indexes in the master list file and returns them.
    '''
    with open(master_list_file, 'a+') as f:
        f.seek(0)
        fcntl.flock(f, fcntl.LOCK_EX)
        lines = f.readlines()
        if lines:
            last_lines = lines[-1].strip()
            last_index = int(last_lines.split('_')[-1])
            start_index = last_index + 1
        else:
            start_index = 0
        end_index = start_index + nl
        index_ext = f"{start_index}_{end_index}"
        f.write(f"{index_ext}\n")
        fcntl.flock(f, fcntl.LOCK_UN)
    return index_ext

def worker(i):
    base = f"{data_dir}/planets/{rundes}/{rundes}.planets"
    master_list_file = f"{base}.master.lists"
    
    # Reserve the next nl of indexes
    index_ext = get_unique_indexes(master_list_file, nl)
    pfile = f"{base}.{index_ext}.{file_ext}"
    if os.path.exists(pfile):
        print(f"File {pfile} already exists. Skipping.")
    else:
        # Generate arrays of size nl using NumPy
        a_array = 10 ** (amin + (amax - amin) * np.random.rand(nl))
        mass_array = mE * 10 ** (mmin + np.random.rand(nl) * (mmax - mmin))
        rnd = np.random.rand(nl)
        inc_array = 180 * np.where(rnd < 0.5, np.arccos(2 * rnd), -np.arccos(2 - 2 * rnd)) / pi
        p_array = 360.0 * np.random.rand(nl)
        
        # Combine arrays into a single array
        combined_array = np.empty((nl, 4))
        combined_array[:, 0] = mass_array
        combined_array[:, 1] = a_array
        combined_array[:, 2] = inc_array
        combined_array[:, 3] = p_array

        # Save the array to a file
        if file_ext == "npy":
            np.save(pfile, combined_array)
        else:
            np.savetxt(pfile, combined_array, delimiter=' ', header='mass a inc p', format='%.8f')

def main():
    dir_name = f"{data_dir}/planets/{rundes}"
    if not os.path.exists(dir_name):
        os.makedirs(dir_name)
    if dir_name[-1] != '/':
        dir_name += '/'

    base = f"{dir_name}{rundes}.planets"  # Base file name

    master_list_file = f"{base}.master.lists"  # Master list file name
    # Ensure the master list file exists and if not create it
    if not os.path.exists(master_list_file):
        open(master_list_file, 'w').close()

    # Use multiprocessing to parallelize the loop
    with mp.Pool(mp.cpu_count()) as pool:
        pool.map(worker, range(nf))

if __name__ == "__main__":
    start_time = time.time()
    main()
    end_time = time.time()
    print(f"Execution time: {end_time - start_time:.2f} seconds")