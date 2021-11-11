#!/usr/bin/env bash
#SBATCH --partition gpu
#SBATCH --time 0-10:00
#SBATCH --account comsm0045
#SBATCH --mem 64GB
#SBATCH --gres gpu:1

# get rid of any modules already loaded
module purge
# load in the module dependencies for this script
module load "languages/anaconda3/2019.07-3.6.5-tflow-1.14"

python lab-2.py
