==================================================================
Practical I - Detectio of Open Chromatin regions & Footprint calling & Transcription factor prediction
==================================================================
In the first practical, we will perform footprint analysis and motif matching with `HINT <http://www.regulatory-genomics.org/hint/>`_ to identify cell specific binding sites from open chromatin data (ATAC-seq).


Example data 
-----------------------------------------------
We will analyse here chromatin (ATAC-seq) and gene expression data during human mesoderm development from `_Koh PW et al 2016 <
https://pubmed.ncbi.nlm.nih.gov/27996962/#&gid=article-figures&pid=figure-1-uid-0>`_. Here, we will focus on regulatory changes between hESC cells and Cardiac mesoderm cells, which were performed in biological duplicates. 


Step 1: Quality check, aligment and peak calling of ATAC-seq data
-----------------------------------------------
A first step in the analysis of ATAC-seq data are the so callled low levels steps including quality check analysis, aligment and peak calling. We have used for this the `nfcore/atacseq <https://github.com/nf-core/atacseq>`_, a rather complete and simple to use pipeline for ATAC-seq data. Due to the computational time to run such pipeline, we have pre-computed results and we provide all important files under */data/session1/nf_core_atacseq*.

Among other things, the pipeline will generate important files, which will be used during this tutorial. 

quality check statistics: XXX
algiment files: XXX
peak calling results: XXX
IGV session for data vizualistaion: XXX 

@li, include location of relevant files 

You can take a look at QC statistics to check if atac-seq libraries have any quality issue. 

You can use then `IGV <http://software.broadinstitute.org/software/igv/>`_ to vizualise ATAC-seq signals and peaks particular loci. Open the previously mentioned IGV session and take a look at cardiac related genes, i.e. Gata6, or stem cell related genes, i.e. Sox2. 

If you are interested in running nf-core at a latter stage, you can chekc the script `here <https://github.com/SchulzLab/EpigenomeAnalysisTutorial-2020/blob/master/session1/run.sh>`_.


Step 2: Footprint calling
-----------------------------------------------

Next, we will use `HINT <http://www.regulatory-genomics.org/hint/>`_ to find genomic regions (footprints) with cell specific TF binding sites. For this, HINT requires (1) a sorted bam file containing the aligned reads from the sequencing library (DNase-,ATAC- or histone ChIP-seq) (2) and a bed file including peaks detected in the same sequencing library provided in (1). These peak regions are used by HINT to reduce the search space. 

We will perform footprinting analysis for each cell type independetly (hESC and Cardiac). For this we will use bam files contatining reads from all replicates and consensus peaks obtained in replicates. 

We will only consider peaks inside chromosome 1 so that the whole analysis can be done in 30 minutes.

**1.** First, go to EpigenomeAnalysisTutorial-2020 and create a folder for results:
::
    cd EpigenomeAnalysisTutorial-2020
    mkdir -p ./session1/results/hint_chr1

**2.** Select peaks from chromosome 1 (this step is only performed to reduce computing time). 
::
    mkdir -p ./session1/results/hint_chr1/peaks
    awk '$1 ~ /^chr(1)$/' ./results/bwa/mergedReplicate/macs/narrowPeak/hESC.mRp.clN_peaks.narrowPeak > ./session1/results/hint_chr1/peaks/hESC.bed
    awk '$1 ~ /^chr(1)$/' ./results/bwa/mergedReplicate/macs/narrowPeak/Cardiac.mRp.clN_peaks.narrowPeak > ./session1/results/hint_chr1/peaks/Cardiac.bed

**3.** Finally, we can execute HINT twice to find footprints specific to hESC and cardiac cells. This can be done as:
::

    mkdir -p ./session1/results/hint_chr1/footprints
    rgt-hint footprinting --atac-seq --paired-end --organism=hg38 --output-location=./session1/results/hint_chr1/footprints --output-prefix=hESC ./results/bwa/mergedReplicate/hESC.mRp.clN.sorted.bam ${output_dir}/peaks/hESC.bed
    rgt-hint footprinting --atac-seq --paired-end --organism=hg38 --output-location=./session1/results/hint_chr1/footprints --output-prefix=Cardiac ./results/bwa/mergedReplicate/Cardiac.mRp.clN.sorted.bam ${output_dir}/peaks/Cardiac.bed

This will generate an output file, i.e  ``./session1/results/hint_chr1/footprints/hESC.bed``, containing the genomic locations of the footprints.  HINT also produces a file with ending ".info", which has general statistics from the analysis as no. of footprints, total number of reads and so on. You can use the head command to check the information contained in footprints.

@li, example of head? 

**4.** HINT performs footprinting analysis by considering reads at each genomic position after signal normalization and cleveage bias correction. T. You need to perform an extra command to generate such signals. 

::
    mkdir -p ./session1/results/hint_chr1/tracks
    rgt-hint tracks --bc --bigWig --organism=hg38 --output-location=${output_dir}/tracks --output-prefix=hESC ./results/bwa/mergedReplicate/hESC.mRp.clN.sorted.bam ${output_dir}/peaks/hESC.bed
    rgt-hint tracks --bc --bigWig --organism=hg38 --output-location=${output_dir}/tracks --output-prefix=Cardiac ./results/bwa/mergedReplicate/Cardiac.mRp.clN.sorted.bam ${output_dir}/peaks/Cardiac.bed
    
 You can load the newly generated bigwig files and fooptrints with`IGV <http://software.broadinstitute.org/software/igv/>`_ together with the signals and peaks detected by nf-core. Are the bigwig files performed by nf-core and HINT comparable?  Check for example the genomic profiles around the gene XXX. 

Step2: TF binding site prediction
-----------------------------------

An important question when doing footprint analysis is to evaluate which TF motifs overlap with footprints and evaluate the ATAC-seq profiles around these motifs. RGT suite also offers a tool for finding motif predicted binding sites (MPBSs).

Execute the following commands to do motif matching inside footprints for chromosome 1:
::
    mkdir -p ./session1/results/hint_chr1/motifmatching
    rgt-motifanalysis matching --organism=hg38 --output-location=./session1/results/hint_chr1/motifmatching --input-files ${output_dir}/footprints/hESC.bed ${output_dir}/footprints/Cardiac.bed

The above commands will generate bed files (i.e. Cardiac_mpbs.bed) containing MPBSs overlapping with distinct footprint regions. The 4th column contains the motif name and the 5th column the bit-score of the motif matching.

Step3: Differential footprinting analysis
-----------------------------------

Finally, we use HINT to generate average ATAC-seq profiles around MPBSs. This analysis allows us to inspect the chromatin accessibility around the binding sites of a particular factor. Moreover, by comparing the profiles from two ATAC-seq libraries (i.s. hESC vs Cardiac cells), we can get insights on changes in transcription factors with increase in activity (or binding) in two cells. For this, execute the following commands:
::

    mkdir -p ./session1/results/hint_chr1/diff_footprints
    rgt-hint differential --organism=hg38 --bc --nc 30 --mpbs-files=./session1/results/hint_chr1/motifmatching/hESC_mpbs.bed,./session1/results/hint_chr1/motifmatching/Cardiac_mpbs.bed --reads-files=./results/bwa/mergedReplicate/hESC.mRp.clN.sorted.bam,./results/bwa/mergedReplicate/Cardiac.mRp.clN.sorted.bam --conditions=hESC,Cardiac --output-location=./session1/results/hint_chr1/diff_footprints

@ivan, select one or two factors for visualization

The above commands will generate files with a ATAC-seq profile for each of the motifs founds in the provided mpbs bed files. Let's check the profiles in the comparison LSK and CD4, you will see that ELK4 has higher number of ATAC-seq counts in CD4 cells, while SPI1 has more ATAC-seq in LSK cells. Higher ATAC counts indicates higher activity of the factor in that particular cell. This fits with the results discussed in Lara-Astiaso that SPI1 are more relevant/active in LSK, while ELK4 in CD4 cells.
