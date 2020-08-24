#!/usr/bin/env zsh
#
#### Job name
#SBATCH -J preprocessing
#SBATCH -e ./preprocessing.txt
#SBATCH -o ./preprocessing.txt
#SBATCH -t 120:00:00
#SBATCH --mem=180G -c 48 -A rwth0233

source ~/.zshrc
conda activate nf-core-atacseq-1.2.1

## only use chr1-22 and chrX for downstream analysis
mkdir -p ./results/session1/hint/peaks
awk '$1 ~ /^chr(1?[0-9]|2[0-2]|X)$/' ./data/nf_core_atacseq/macs/narrowPeak/hESC.mRp.clN_peaks.narrowPeak > ./results/session1/hint/peaks/hESC.bed

awk '$1 ~ /^chr(1?[0-9]|2[0-2]|X)$/' ./data/nf_core_atacseq/macs/narrowPeak/Cardiac.mRp.clN_peaks.narrowPeak > ./results/session1/hint/peaks/Cardiac.bed

mkdir -p ./results/session1/hint/footprints

rgt-hint footprinting --atac-seq --paired-end --organism=hg38 --output-location=./results/session1/hint/footprints \
--output-prefix=hESC ./data/nf_core_atacseq/hESC.mRp.clN.sorted.bam ./results/session1/hint/peaks/hESC.bed

rgt-hint footprinting --atac-seq --paired-end --organism=hg38 --output-location=./results/session1/hint/footprints \
--output-prefix=Cardiac ./data/nf_core_atacseq/Cardiac.mRp.clN.sorted.bam ./results/session1/hint/peaks/Cardiac.bed

mkdir -p ./results/session1/hint/tracks

rgt-hint tracks --bc --bigWig --organism=hg38 --output-location=./results/session1/hint/tracks --output-prefix=hESC \
./data/nf_core_atacseq/hESC.mRp.clN.sorted.bam ./results/session1/hint/peaks/hESC.bed

rgt-hint tracks --bc --bigWig --organism=hg38 --output-location=./results/session1/hint/tracks --output-prefix=Cardiac \
./data/nf_core_atacseq/Cardiac.mRp.clN.sorted.bam ./results/session1/hint/peaks/Cardiac.bed

mkdir -p ./results/session1/hint/motifmatching

rgt-motifanalysis matching --organism=hg38 --output-location=./results/session1/hint/motifmatching --input-files ./results/session1/hint/footprints/hESC.bed ./results/session1/hint/footprints/Cardiac.bed


mkdir -p ./results/session1/hint/diff_footprints

rgt-hint differential --organism=hg38 --bc --nc 30 --mpbs-files=./results/session1/hint/motifmatching/hESC_mpbs.bed,./results/session1/hint/motifmatching/Cardiac_mpbs.bed \
--reads-files=./data/nf_core_atacseq/hESC.mRp.clN.sorted.bam,./data/nf_core_atacseq/Cardiac.mRp.clN.sorted.bam \
--conditions=hESC,Cardiac --output-location=./results/session1/hint/diff_footprints
