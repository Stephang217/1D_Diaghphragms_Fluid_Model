#!/bin/bash
# UQ ensemble on SCRTP (one hetmathsys/Avon node).
# Submit from the repository root:   sbatch scripts/uq_avon.sbatch
#
# Total work: 288 runs (main) + 80 runs (edge), ~50 s each single-core
# -> well under an hour on 16 cores; comfortably inside the few-hour cap.
#
# ---------------------------------------------------------------------------
# BEFORE THE FIRST SUBMISSION -- three things that cannot be known without an
# account, so they need checking on the node itself:
#
#   1. MODULE NAMES.  The `module load` line below is a guess at a standard
#      EasyBuild stack.  Find the real names first:
#          module spider SciPy-bundle
#          module avail python
#      This job needs only python3 + numpy.  pandas, scikit-learn and matplotlib
#      are used by the notebook locally, not here.
#
#   2. PARTITION / ACCOUNT.  Many SCRTP queues reject jobs that name neither.
#      Check `sinfo` and your account documentation, then uncomment and fill in
#      the two #SBATCH lines below.
#
#   3. SMOKE TEST BEFORE QUEUEING.  Run this interactively first -- about a
#      minute, and it exercises the imports, the process pool and the CSV write,
#      so a bad module load surfaces immediately instead of after a queue wait:
#          python3 scripts/uq_sweep.py --n-train 4 --n-test 2 --workers 4
# ---------------------------------------------------------------------------

#SBATCH --job-name=diaphragm-uq
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=16
#SBATCH --time=02:00:00
#SBATCH --output=uq_sweep_%j.out
# #SBATCH --partition=<queue>        # see note 2 above
# #SBATCH --account=<code>           # see note 2 above

set -euo pipefail                    # fail loudly rather than leave half a CSV

module purge
module load GCC OpenMPI SciPy-bundle   # PLACEHOLDER -- see note 1 above

echo "host     : $(hostname)"
echo "python   : $(python3 --version 2>&1)"
echo "numpy    : $(python3 -c 'import numpy; print(numpy.__version__)')"
echo "cpus     : ${SLURM_CPUS_PER_TASK}"
echo "started  : $(date --iso-8601=seconds)"

python3 scripts/uq_sweep.py --mode main --workers "${SLURM_CPUS_PER_TASK}"
python3 scripts/uq_sweep.py --mode edge --workers "${SLURM_CPUS_PER_TASK}"

# Per-diaphragm disorder (Section 3.5). Only ~4 min locally, so run it here only
# if you would rather every ensemble in the appendix came off the cluster.
# python3 scripts/disorder_sweep.py --workers "${SLURM_CPUS_PER_TASK}"

echo "finished : $(date --iso-8601=seconds)"
echo "CSVs are in results/ -- copy back, then rerun uq_reproducible_result.ipynb"
