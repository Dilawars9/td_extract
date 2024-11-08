import re
import argparse
import os

# Conversion functions
def eV_to_kcalmol(ev):
    return ev * 23.0605

def eV_to_cm1(ev):
    return ev * 8065.54

def eV_to_hartree(ev):
    return ev * 0.0367493

def parse_td_log(file_path):
    excitation_pattern = re.compile(r'Excited State\s+(\d+):\s+(\w+)-\S+\s+([\d.]+) eV\s+([\d.]+) nm\s+f=([\d.]+)')
    scf_done_pattern = re.compile(r'SCF Done:\s+E\(\w+\)\s+=\s+([-.\d]+)\s+A\.U\.')

    excited_states = []
    s0_energy = None
    singlet_states = []
    triplet_states = []

    singlet_count = 0
    triplet_count = 0

    with open(file_path, 'r') as file:
        lines = file.readlines()
        
        for line in lines:
            scf_done_match = scf_done_pattern.search(line)
            if scf_done_match:
                s0_energy = float(scf_done_match.group(1))
            
            excitation_match = excitation_pattern.search(line)
            if excitation_match:
                state_number = int(excitation_match.group(1))
                state_type = excitation_match.group(2)
                energy_ev = float(excitation_match.group(3))
                wavelength_nm = float(excitation_match.group(4))
                oscillator_strength = float(excitation_match.group(5))
                
                if state_type == 'Singlet':
                    label = f"S{singlet_count}"
                    singlet_states.append(energy_ev)
                    singlet_count += 1
                elif state_type == 'Triplet':
                    label = f"T{triplet_count}"
                    triplet_states.append(energy_ev)
                    triplet_count += 1
                
                energy_hartree = s0_energy + eV_to_hartree(energy_ev)

                excited_state = {
                    "State": state_number,
                    "Label": label,
                    "Energy (eV)": energy_ev,
                    "Wavelength (nm)": wavelength_nm,
                    "Oscillator Strength": oscillator_strength,
                    "Energy (kcal/mol)": eV_to_kcalmol(energy_ev),
                    "Energy (cm-1)": eV_to_cm1(energy_ev),
                    "Energy (Hartree)": energy_hartree
                }
                
                excited_states.append(excited_state)
    
    return s0_energy, excited_states, singlet_states, triplet_states

def calculate_st_gaps(singlet_states, triplet_states):
    st_gap_matrix = []
    for singlet_energy in singlet_states:
        row = [(singlet_energy - triplet_energy) for triplet_energy in triplet_states]
        st_gap_matrix.append(row)
    return st_gap_matrix

def write_energy_data(s0_energy, excited_states, output_file, full_output=False):
    with open(output_file, 'w') as file:
        if s0_energy is not None:
            file.write(f"S0 Energy (A.U.): {s0_energy:.12f}\n")
        
        if full_output:
            file.write("Type    eV        nm        kcal/mol    cm^-1      f       Hartree\n")
            file.write("--------------------------------------------------------------------------\n")
        else:
            file.write("Type    eV        nm        f        Hartree\n")
            file.write("---------------------------------------------\n")
        
        for state in excited_states:
            if full_output:
                line = (
                    f"{state['Label']}      {state['Energy (eV)']:.4f}       {state['Wavelength (nm)']:.2f}    "
                    f"{state['Energy (kcal/mol)']:.4f}   {state['Energy (cm-1)']:.2f}     "
                    f"{state['Oscillator Strength']:.4f}   {state['Energy (Hartree)']:.8f}\n"
                )
            else:
                line = (
                    f"{state['Label']}      {state['Energy (eV)']:.4f}       {state['Wavelength (nm)']:.2f}    "
                    f"{state['Oscillator Strength']:.4f}   {state['Energy (Hartree)']:.8f}\n"
                )
            file.write(line)

def write_st_gaps(singlet_states, triplet_states, output_file):
    st_gap_matrix = calculate_st_gaps(singlet_states, triplet_states)
    with open(output_file, 'a') as file:
        file.write("\nSinglet-Triplet Gaps (eV):\n")
        file.write("Triplets  " + "   ".join([f"T{i}" for i in range(len(triplet_states))]) + "\n")
        file.write("----------------------------------------------------\n")
        for i, row in enumerate(st_gap_matrix):
            row_str = "   ".join([f"{gap:.4f}" for gap in row])
            file.write(f"S{i}        {row_str}\n")

def main():
    parser = argparse.ArgumentParser(description="Parse Gaussian TD log file and extract excited state data.")
    parser.add_argument("-i", "--input", required=True, help="Path to the Gaussian log file.")
    parser.add_argument("--full", action="store_true", help="Display full data including kcal/mol and cm^-1.")
    parser.add_argument("--minimal", action="store_true", help="Display minimal data without S-T gaps.")
    args = parser.parse_args()

    log_file = args.input
    output_file = os.path.splitext(log_file)[0] + "_excited_states.txt"

    s0_energy, excited_states_data, singlet_states, triplet_states = parse_td_log(log_file)
    write_energy_data(s0_energy, excited_states_data, output_file, full_output=args.full)
    
    # Write S-T gaps only if --minimal is not specified
    if not args.minimal:
        write_st_gaps(singlet_states, triplet_states, output_file)

    print(f"Data has been written to {output_file}")

# Execute main function if the script is run directly
if __name__ == "__main__":
    main()
