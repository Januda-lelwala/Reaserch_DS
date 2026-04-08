import subprocess
import os
import sys

scripts = [
    "03_exchange_rate.py",
    "04_temp_disagg.py",
    "05_handle_lfs_artefact.py",
    "06_impute_and_audit.py",
    "07_agri_index.py"
]

def main():
    print("==================================================")
    print("      Research Data Pipeline Master Execution     ")
    print("==================================================")
    
    # Clean output manually if desired, but we'll ensure it exists
    os.makedirs("output", exist_ok=True)
    
    for script in scripts:
        print(f"\n[RUNNING] ---> {script}")
        if not os.path.exists(script):
            print(f"[ERROR]: {script} not found in this directory!")
            sys.exit(1)
            
        result = subprocess.run([sys.executable, script])
        if result.returncode != 0:
            print(f"\n[ERROR]: Pipeline HALTED. {script} failed with exit code {result.returncode}")
            sys.exit(1)
            
    print("\n==================================================")
    print("          Pipeline Execution Completed!           ")
    print("==================================================")
    print(f"All {len(scripts)} steps completed successfully.")
    print("Please verify the analytical datasets in data_pipeline/output/\n")

if __name__ == "__main__":
    main()
