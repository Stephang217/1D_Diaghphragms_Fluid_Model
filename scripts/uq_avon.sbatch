#!/bin/bash
# UQ ensemble on SCRTP (one hetmathsys/Avon node).
# Submit from the repository root:   sbatch scripts/uq_avon.sbatch
# Total work: 288 runs (main) + 80 runs (edge), ~50 s each single-core
# -> well under an hour on one node; comfortably inside the few-hour cap.
#SBATCH --job-name=diaphragm-uq
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=16
#SBATCH --time=02:00:00
#SBATCH --output=uq_sweep_%j.out

module purge
module load GCC OpenMPI SciPy-bundle   # provides python3 + numpy/scipy/pandas

python3 scripts/uq_sweep.py --mode main --workers "$SLURM_CPUS_PER_TASK"
python3 scripts/uq_sweep.py --mode edge --workers "$SLURM_CPUS_PER_TASK"
