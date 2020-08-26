==================================================================
Practical I - Detection of Open Chromatin regions & Footprint calling & Transcription factor prediction
==================================================================

In the first practical, we will perform basic analysis of ATAC-seq, footprint analysis and motif matching with `HINT <http://www.regulatory-genomics.org/hint/>`_ to identify cell specific binding sites from open chromatin data (ATAC-seq). Beforehand, be sure you have installed Docker and pulled the container which includes all tools and data for this tutorial.


Example data 
-----------------------------------------------
We will analyse here chromatin (ATAC-seq) and gene expression data during human mesoderm development from `Koh PW et al 2016 <https://pubmed.ncbi.nlm.nih.gov/27996962/#&gid=article-figures&pid=figure-1-uid-0>`_. Here, we focus on regulatory changes between hESC cells and Cardiac mesoderm cells. For each condition, we have two ATAC-seq libraries corresponding to biological duplicates. 


Step 1: Quality check, aligment and peak calling of ATAC-seq data
-----------------------------------------------
A first step in the analysis of ATAC-seq data are the so callled low level analysis, which includes read trimming, quality check, aligment and peak calling. We have used for this the `nfcore/atacseq <https://github.com/nf-core/atacseq>`_, a rather complete  pipeline for ATAC-seq data. Due to the computational time to run such pipeline, we have pre-computed results and we provide all important files under */data/nf_core_atacseq*.

Among other things, the pipeline will generate important files, which will be used during this tutorial: 

- quality check (QC) statistics: *./data/nf_core_atacseq/multiqc/narrowPeak/multiqc_report.html*
- alignment files: *./data/nf_core_atacseq/*
- genomic profiles (big wig): *./data/nf_core_atacseq/bigwig*
- peak calling results: *./data/nf_core_atacseq/macs/narrowPeak*
- differential peak calling results: *./data/nf_core_atacseq/macs/narrowPeak/consensus/deseq2/CardiacvshESC/*

First, you can inspect the QC statistics, just go to *~/container-data/EpigenomeAnalysisTutorial-2020//data/nf_core_atacseq/multiqc/narrowPeak* and double click *multiqc_report.html*. Do the atac-seq libraries have any quality issue before and after read trimming?

Next, you can use then `IGV <http://software.broadinstitute.org/software/igv/>`_ to vizualise ATAC-seq signals and peaks particular loci. Open the previously mentioned IGV session and take a look at cardiac related genes, i.e. GATA4 or GATA6, or stem cell related genes, i.e. POU5F1 (OCT4). 

The differential peaks file combined all peaks and here we can split it as hESC and Cardiac specific peaks by:
::
    mkdir -p ./results/session1/diff_peaks
    awk '{if ($5 < 0) print $0}' ./data/nf_core_atacseq/macs/narrowPeak/consensus/deseq2/CardiacvshESC/CardiacvshESC.mRp.clN.deseq2.FDR0.05.results.bed > ./results/session1/diff_peaks/hESC.bed
    awk '{if ($5 > 0) print $0}' ./data/nf_core_atacseq/macs/narrowPeak/consensus/deseq2/CardiacvshESC/CardiacvshESC.mRp.clN.deseq2.FDR0.05.results.bed > ./results/session1/diff_peaks/Cardiac.bed
    
The above commands will check the sign in 5th column and output as hESC specific peak if values are negative. 

If you are interested in running nf-core at a latter stage, you can chekc the script `here <https://github.com/SchulzLab/EpigenomeAnalysisTutorial-2020/blob/master/session1/run_nf_core_atacseq.sh>`_.


Step 2: Footprint calling
-----------------------------------------------

Next, we will use `HINT <http://www.regulatory-genomics.org/hint/>`_ to find genomic regions (footprints) with cell specific TF binding sites. For this, HINT requires (1) a sorted bam file containing the aligned reads from the sequencing library (DNase-,ATAC- or histone ChIP-seq) (2) and a bed file including peaks detected in the same sequencing library provided in (1). These peak regions are used by HINT to reduce the search space. 

HINT footprinting analysis is performed for each cell type independetly (hESC and Cardiac) and do not consider replicate information. For this we will use bam files contatining reads from all replicates as well as condition specific consensus peaks. 

We will only consider peaks inside chromosome 21 so that the whole analysis can be done in 30 minutes.

**1.** First, go to your docker image and create a folder for results:
::
    mkdir -p ./results/session1/hint_chr21

**2.** Select peaks from chromosome 21 (this step is only performed to reduce computing time for this practical exercise). 
::
    mkdir -p ./results/session1/hint_chr21/peaks
    awk '$1 ~ /^chr(21)$/' ./data/nf_core_atacseq/macs/narrowPeak/hESC.mRp.clN_peaks.narrowPeak > ./results/session1/hint_chr21/peaks/hESC.bed
    awk '$1 ~ /^chr(21)$/' ./data/nf_core_atacseq/macs/narrowPeak/Cardiac.mRp.clN_peaks.narrowPeak > ./results/session1/hint_chr21/peaks/Cardiac.bed

**3.** Next, we can execute HINT twice to find footprints specific to hESC and cardiac cells. This can be done as:
::

    mkdir -p ./results/session1/hint_chr21/footprints
    rgt-hint footprinting --atac-seq --paired-end --organism=hg38 --output-location=./results/session1/hint_chr21/footprints --output-prefix=hESC ./data/nf_core_atacseq/hESC.mRp.clN.sorted.bam ./results/session1/hint_chr21/peaks/hESC.bed
    rgt-hint footprinting --atac-seq --paired-end --organism=hg38 --output-location=./results/session1/hint_chr21/footprints --output-prefix=Cardiac ./data/nf_core_atacseq/Cardiac.mRp.clN.sorted.bam ./results/session1/hint_chr21/peaks/Cardiac.bed

This will generate an output file, i.e  ``./results/session1/hint_chr21/footprints/hESC.bed``, containing the genomic locations of the footprints.  HINT also produces a file with ending ".info", which has general statistics from the analysis as no. of footprints, total number of reads and so on. Input arguments indicate important information to HINT as genome verion (--organism), chromatin protocol (--atac-seq) and type of read configuration (--paired-end). You can check more information on HINT `here <http://www.regulatory-genomics.org/hint/introduction/>`_ . 

You can use the head command to check the information contained in footprints:
::
    head ./results/session1/hint_chr21/footprints/hESC.bed

The 5th column contains the number of reads around predicted footprint and can be used as metric for ordering footprints, i.e. the more reads the more likelly it is associated to an active binding site. 

**4.** HINT performs footprinting analysis by considering reads at each genomic position after signal normalization and cleveage bias correction.  You need to perform an extra command to generate such signals in order to vizualise this is a genome browser:
::
    mkdir -p ./results/session1/hint_chr21/tracks
    rgt-hint tracks --bc --bigWig --organism=hg38 --output-location=./results/session1/hint_chr21/tracks --output-prefix=hESC ./data/nf_core_atacseq/hESC.mRp.clN.sorted.bam ./results/session1/hint_chr21/peaks/hESC.bed
    rgt-hint tracks --bc --bigWig --organism=hg38 --output-location=./results/session1/hint_chr21/tracks --output-prefix=Cardiac ./data/nf_core_atacseq/Cardiac.mRp.clN.sorted.bam ./results/session1/hint_chr21/peaks/Cardiac.bed
    
You can load the newly generated bigwig files and fooptrints with `IGV <http://software.broadinstitute.org/software/igv/>`_ together with the signals and peaks detected by nf-core. Are the bigwig files performed by nf-core and HINT the same? Check for example the genomic profiles around the genes GATA6 and POU5F1 again. 

Step 3: TF binding site prediction
-----------------------------------

An important question when doing footprint analysis is to evaluate which TF motifs overlap with footprints and evaluate the ATAC-seq profiles around these motifs. RGT suite also offers a tool for finding motif predicted binding sites (MPBSs).

Execute the following commands to do motif matching inside footprints for chromosome 21:
::
    mkdir -p ./results/session1/hint_chr21/motifmatching
    rgt-motifanalysis matching --organism=hg38 --output-location=./results/session1/hint_chr21/motifmatching --input-files ./results/session1/hint_chr21/footprints/hESC.bed ./results/session1/hint_chr21/footprints/Cardiac.bed

The above commands will generate bed files (i.e. Cardiac_mpbs.bed) containing MPBSs overlapping with distinct footprint regions. The 4th column contains the motif name and the 5th column the bit-score of the motif matching. Higher bit-score indicates higher agreement of the motif with the DNA sequence. HINT uses Jaspar database as default for motifs, but it allows users to user other databased or to define `custom databases <https://www.regulatory-genomics.org/motif-analysis/additional-motif-data/>`_ as well. 

Step 4: Average footprint porifles and differential activity analysis
----------------------------------------------------------------------------

Finally, we use HINT to generate average ATAC-seq profiles around MPBSs. This analysis allows us to inspect the chromatin accessibility around the binding sites of a particular factor and indicates the TF activitiy, i.e. higher accessibility and clear footprints indicates higher TF activity. Moreover, by comparing the profiles from two ATAC-seq libraries (i.s. hESC vs Cardiac cells), we can get insights on changes in transcription factors with increase in activity (or binding) in two cells. For this, execute the following commands:
::

    mkdir -p ./results/session1/hint_chr21/diff_footprints
    rgt-hint differential --organism=hg38 --bc --nc 30 --mpbs-files=./results/session1/hint_chr21/motifmatching/hESC_mpbs.bed,./results/session1/hint_chr21/motifmatching/Cardiac_mpbs.bed --reads-files=./data/nf_core_atacseq/hESC.mRp.clN.sorted.bam,./data/nf_core_atacseq/Cardiac.mRp.clN.sorted.bam --conditions=hESC,Cardiac --output-location=./results/session1/hint_chr21/diff_footprints

The above command will read the motif matching files generated by step 3 and BAM files which contain the sequencing reads to perform the comparison. Note that here we specify –bc to use the bias-corrected signal (currently only  ATAC-seq is supported). The command –nc allow parallel execution of the job.

After the command is done, a txt file **differential_statistics.txt** will be created under *./results/session1/hint_chr21/diff_footprints* and it contains the transcription factor (TF) activity dynamics between hESC and Cardiac. HINT performs a statistical test to detect TFs with a significant increase or decrease in activity. In addition, a folder called **Lineplots** can be found, which contains the ATAC-seq profile for each of the motifs found in the mpbs bed files. 

The above analyses are based on chromosome 21 and the resutls are likelly to be underpowered, we therefore provide the complete results using all chromsomes in *./results/session1/hint*. The script for this analysis is found here `here <https://github.com/SchulzLab/EpigenomeAnalysisTutorial-2020/blob/master/session1/run_hint.sh>`_. 

Next, we use a R script to make a nicer visualization of the TF activity score:
::
    Rscript scripts/session1/plot_diff.R -i ./results/session1/hint/diff_footprints/differential_statistics.txt -o ./results/session1/hint/diff_footprints

The script will generate a divergent bar plot under *./results/session1/hint/diff_footprints* and two text files which include either Cardiac or hESC specific TFs. Note that it only consider TFs with significant change in activity (p-value < 0.05) and at least 1,000 binding sites for TF. Results rank several GATA TFs, which are well known to be related to cardiac cells, with increase in TF activity, while the well known ES cells factors SOX2:POU5F1 (OCT4) have the second highest decreased in TF activity.

You can check on the folder **Lineplots** for the average cleveage profiles of these factors and their corresponding DNA binding preference. 

You should compare the motifs/profiles of Gata factors. Are they similar to one another? One caveat of sequence based analysis is that we might predict several TFs, which have a similar motif, equaly. 

Finally, we will filter the motif matching results to only consider TFs enriched in a respective condition. You can do this with the following command:
::
    mkdir -p ./results/session1/hint/diff_motifmatching
    grep -f ./results/session1/hint/diff_footprints/Cardiac.txt ./results/session1/hint/motifmatching/Cardiac_mpbs.bed > ./results/session1/hint/diff_motifmatching/Cardiac_mpbs.bed
    grep -f ./results/session1/hint/diff_footprints/hESC.txt ./results/session1/hint/motifmatching/hESC_mpbs.bed > ./results/session1/hint/diff_motifmatching/hESC_mpbs.bed

You can then open these files in IGV and inspect motif hits close to relevant genes (POUF5F1, GATA6 or GATA4). Are you able to find any motif close to a gene? You can also zoom out of your IGV browser and check for potential enhancer regions.
