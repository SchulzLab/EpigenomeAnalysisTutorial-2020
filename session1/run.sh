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

#########################################################################################
# We first show the pre-processing of sequence data
#########################################################################################
# downloading of SRA
# prefetch -v SRR3689759
# prefetch -v SRR3689760
# prefetch -v SRR3689933	
# prefetch -v SRR3689934	

# Dump each read into separate file. Files will receive suffix corresponding to read number.
# fastq-dump --split-files --gzip /hpcwork/izkf/ncbi/sra/SRR3689759.sra
# fastq-dump --split-files --gzip /hpcwork/izkf/ncbi/sra/SRR3689760.sra
# fastq-dump --split-files --gzip /hpcwork/izkf/ncbi/sra/SRR3689933.sra
# fastq-dump --split-files --gzip /hpcwork/izkf/ncbi/sra/SRR3689934.sra

#/home/rs619065/miniconda3/bin/nextflow run nf-core/atacseq --input design.csv --genome hg38 --narrow_peak 

## only use chr1-22 and chrX for downstream analysis
mkdir -p ./results/hint/peaks
awk '$1 ~ /^chr(1?[0-9]|2[0-2]|X)$/' ./results/bwa/mergedReplicate/macs/narrowPeak/hESC.mRp.clN_peaks.narrowPeak > ./results/hint/peaks/hESC.bed

awk '$1 ~ /^chr(1?[0-9]|2[0-2]|X)$/' ./results/bwa/mergedReplicate/macs/narrowPeak/Cardiac.mRp.clN_peaks.narrowPeak > ./results/hint/peaks/Cardiac.bed



mkdir -p ./results/hint/footprints

rgt-hint footprinting --atac-seq --paired-end --organism=hg38 --output-location=./results/hint/footprints \
--output-prefix=hESC ./results/bwa/mergedReplicate/hESC.mRp.clN.sorted.bam ./results/hint/peaks/hESC.bed

rgt-hint footprinting --atac-seq --paired-end --organism=hg38 --output-location=./results/hint/footprints \
--output-prefix=Cardiac ./results/bwa/mergedReplicate/Cardiac.mRp.clN.sorted.bam ./results/hint/peaks/Cardiac.bed

mkdir -p ./results/hint/tracks

rgt-hint tracks --bc --bigWig --organism=hg38 --output-location=./results/hint/tracks --output-prefix=hESC \
./results/bwa/mergedReplicate/hESC.mRp.clN.sorted.bam ./results/hint/peaks/hESC.bed

rgt-hint tracks --bc --bigWig --organism=hg38 --output-location=./results/hint/tracks --output-prefix=Cardiac \
./results/bwa/mergedReplicate/Cardiac.mRp.clN.sorted.bam ./results/hint/peaks/Cardiac.bed

mkdir -p ./results/hint/motifmatching

rgt-motifanalysis matching --organism=hg38 --output-location=./results/hint/motifmatching --input-files ./results/hint/footprints/hESC.bed ./results/hint/footprints/Cardiac.bed


mkdir -p ./results/hint/diff_footprints
rgt-hint differential --organism=hg38 --bc --nc 30 --mpbs-files=./results/hint/motifmatching/hESC_mpbs.bed,./results/hint/motifmatching/Cardiac_mpbs.bed \
--reads-files=./results/bwa/mergedReplicate/hESC.mRp.clN.sorted.bam,./results/bwa/mergedReplicate/Cardiac.mRp.clN.sorted.bam \
--conditions=hESC,Cardiac --output-location=./results/hint/diff_footprints