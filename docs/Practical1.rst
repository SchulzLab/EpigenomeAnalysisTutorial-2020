==================================================================
Practical I - Detectio of Open Chromatin regions & Footprint calling & Transcription factor prediction
==================================================================
In the first practical, we will perform standard ATAC-seq analysis, footprint analysis and motif matching with `HINT <http://www.regulatory-genomics.org/hint/>`_ to identify cell specific binding sites from open chromatin data (ATAC-seq). **Note, be sure you have installed Docker and pulled the container which includes all tools and data for this tutorial.**


Example data 
-----------------------------------------------
We will analyse here chromatin (ATAC-seq) and gene expression data during human mesoderm development from `Koh PW et al 2016 <https://pubmed.ncbi.nlm.nih.gov/27996962/#&gid=article-figures&pid=figure-1-uid-0>`_. Here, we focus on regulatory changes between hESC cells and Cardiac mesoderm cells, which were performed in biological duplicates. 


Step 1: Quality check, aligment and peak calling of ATAC-seq data
-----------------------------------------------
A first step in the analysis of ATAC-seq data are the so callled low level analysis, which includes read trimming, quality check, aligment and peak calling. We have used for this the `nfcore/atacseq <https://github.com/nf-core/atacseq>`_, a rather complete  pipeline for ATAC-seq data. Due to the computational time to run such pipeline, we have pre-computed results and we provide all important files under */data/session1/nf_core_atacseq*.

Among other things, the pipeline will generate important files, which will be used during this tutorial: 

- quality check statistics: *~/EpigenomeAnalysisTutorial-2020/data/nf_core_atacseq/multiqc/narrowPeak/multiqc_report.html*
- alignment files: *~/EpigenomeAnalysisTutorial-2020/data/nf_core_atacseq/*
- genomic profiles (big wig): *~/EpigenomeAnalysisTutorial-2020/data/nf_core_atacseq/bigwig*
- peak calling results: *~/EpigenomeAnalysisTutorial-2020/data/nf_core_atacseq/macs/narrowPeak*
- differential peak calling results: *~/EpigenomeAnalysisTutorial-2020/data/nf_core_atacseq/macs/narrowPeak/consensus/deseq2/CardiacvshESC/*
- IGV session for data vizualistaion: *~/EpigenomeAnalysisTutorial-2020/data/nf_core_atacseq/igv* 

You can take a look at QC statistics to check if atac-seq libraries have any quality issue after trimming procedure. 

You can use then `IGV <http://software.broadinstitute.org/software/igv/>`_ to vizualise ATAC-seq signals and peaks particular loci. Open the previously mentioned IGV session and take a look at cardiac related genes, i.e. GATA6, or stem cell related genes, i.e. POU5F1 (OCT4). 

The differential peaks file combined all peaks and here we can split it as hESC and Cardiac specific peaks by:
::
    cd EpigenomeAnalysisTutorial-2020
    mkdir -p ./results/session1/diff_peaks
    awk '{if ($5 < 0) print $0}' ~/EpigenomeAnalysisTutorial-2020/data/nf_core_atacseq/macs/narrowPeak/consensus/deseq2/CardiacvshESC/CardiacvshESC.mRp.clN.deseq2.FDR0.05.results.bed > ./results/session1/diff_peaks/hESC.bed
    awk '{if ($5 > 0) print $0}' ~/EpigenomeAnalysisTutorial-2020/data/nf_core_atacseq/macs/narrowPeak/consensus/deseq2/CardiacvshESC/CardiacvshESC.mRp.clN.deseq2.FDR0.05.results.bed > ./results/session1/diff_peaks/Cardiac.bed
    
The above commands will check the sign in 5th column and output as hESC specific peak if it is negative and Cardiac if positive.

If you are interested in running nf-core at a latter stage, you can chekc the script `here <https://github.com/SchulzLab/EpigenomeAnalysisTutorial-2020/blob/master/session1/run_nf_core_atacseq.sh>`_.


Step 2: Footprint calling
-----------------------------------------------

Next, we will use `HINT <http://www.regulatory-genomics.org/hint/>`_ to find genomic regions (footprints) with cell specific TF binding sites. For this, HINT requires (1) a sorted bam file containing the aligned reads from the sequencing library (DNase-,ATAC- or histone ChIP-seq) (2) and a bed file including peaks detected in the same sequencing library provided in (1). These peak regions are used by HINT to reduce the search space. 

HINT footprinting analysis is performed for each cell type independetly (hESC and Cardiac) and do not consider replicate information. For this we will use bam files contatining reads from all replicates as well as condition specific consensus peaks. 

We will only consider peaks inside chromosome 1 so that the whole analysis can be done in 30 minutes.

**1.** First, go to EpigenomeAnalysisTutorial-2020 and create a folder for results:
::
    mkdir -p ./results/session1/hint_chr1

**2.** Select peaks from chromosome 1 (this step is only performed to reduce computing time). 
::
    mkdir -p ./results/session1/hint_chr1/peaks
    awk '$1 ~ /^chr(1)$/' ./data/nf_core_atacseq/macs/narrowPeak/hESC.mRp.clN_peaks.narrowPeak > ./results/session1/hint_chr1/peaks/hESC.bed
    awk '$1 ~ /^chr(1)$/' ./data/nf_core_atacseq/macs/narrowPeak/Cardiac.mRp.clN_peaks.narrowPeak > ./results/session1/hint_chr1/peaks/Cardiac.bed

**3.** Finally, we can execute HINT twice to find footprints specific to hESC and cardiac cells. This can be done as:
::

    mkdir -p ./results/session1/hint_chr1/footprints
    rgt-hint footprinting --atac-seq --paired-end --organism=hg38 --output-location=./results/session1/hint_chr1/footprints --output-prefix=hESC ./data/nf_core_atacseq/hESC.mRp.clN.sorted.bam ./data/nf_core_atacseq/peaks/hESC.bed
    rgt-hint footprinting --atac-seq --paired-end --organism=hg38 --output-location=./results/session1/hint_chr1/footprints --output-prefix=Cardiac ./data/nf_core_atacseq/Cardiac.mRp.clN.sorted.bam ./data/nf_core_atacseq/peaks/Cardiac.bed

This will generate an output file, i.e  ``./results/session1/hint_chr1/footprints/hESC.bed``, containing the genomic locations of the footprints.  HINT also produces a file with ending ".info", which has general statistics from the analysis as no. of footprints, total number of reads and so on. You can use the head command to check the information contained in footprints:
::
    head ./results/session1/hint_chr1/footprints/hESC.bed

The 5th column contains the number of reads around predicted footprint and can be used as metric for filtering, i.e. the more reads the more likelly the footprint is associated to an active binding site. 

**4.** HINT performs footprinting analysis by considering reads at each genomic position after signal normalization and cleveage bias correction.  You need to perform an extra command to generate such signals in order to vizualise this is a genome browser:
::
    mkdir -p ./results/session1/hint_chr1/tracks
    rgt-hint tracks --bc --bigWig --organism=hg38 --output-location=./results/session1/hint_chr1/tracks --output-prefix=hESC ./data/nf_core_atacseq/hESC.mRp.clN.sorted.bam ./results/session1/hint_chr1/peaks/hESC.bed
    rgt-hint tracks --bc --bigWig --organism=hg38 --output-location=./results/session1/hint_chr1/tracks --output-prefix=Cardiac ./data/nf_core_atacseq/Cardiac.mRp.clN.sorted.bam ./results/session1/hint_chr1/peaks/Cardiac.bed
    
You can load the newly generated bigwig files and fooptrints with `IGV <http://software.broadinstitute.org/software/igv/>`_ together with the signals and peaks detected by nf-core. Are the bigwig files performed by nf-core and HINT the same? Check for example the genomic profiles around the genes GATA6 and POU5F1 again. 

Step 3: TF binding site prediction
-----------------------------------

An important question when doing footprint analysis is to evaluate which TF motifs overlap with footprints and evaluate the ATAC-seq profiles around these motifs. RGT suite also offers a tool for finding motif predicted binding sites (MPBSs).

Execute the following commands to do motif matching inside footprints for chromosome 1:
::
    mkdir -p ./results/session1/hint_chr1/motifmatching
    rgt-motifanalysis matching --organism=hg38 --output-location=./results/session1/hint_chr1/motifmatching --input-files ./results/session1/hint_chr1/footprints/hESC.bed ./results/session1/hint_chr1/footprints/Cardiac.bed

The above commands will generate bed files (i.e. Cardiac_mpbs.bed) containing MPBSs overlapping with distinct footprint regions. The 4th column contains the motif name and the 5th column the bit-score of the motif matching. Higher bit-score indicates higher agreement of the motif with the DNA sequence. 

Step 4: Average footprint porifles and differential activity analysis
----------------------------------------------------------------------------

Finally, we use HINT to generate average ATAC-seq profiles around MPBSs. This analysis allows us to inspect the chromatin accessibility around the binding sites of a particular factor and indicates the TF activitiy, i.e. higher accessibility and clear footprints indicates higher TF activity. Moreover, by comparing the profiles from two ATAC-seq libraries (i.s. hESC vs Cardiac cells), we can get insights on changes in transcription factors with increase in activity (or binding) in two cells. For this, execute the following commands:
::

    mkdir -p ./results/session1/hint_chr1/diff_footprints
    rgt-hint differential --organism=hg38 --bc --nc 30 --mpbs-files=./results/session1/hint_chr1/motifmatching/hESC_mpbs.bed,./results/session1/hint_chr1/motifmatching/Cardiac_mpbs.bed --reads-files=./data/nf_core_atacseq/hESC.mRp.clN.sorted.bam,./data/nf_core_atacseq/Cardiac.mRp.clN.sorted.bam --conditions=hESC,Cardiac --output-location=./results/session1/hint_chr1/diff_footprints
    
The above command will 

Step 5: Motif filtering
--------------------------------------------------------------------------
The above analyses are based on chromosome 1 and we provide here the results using all chromsomes. Results of the TF activity are provided in the table ``./session1/results/hint/diff_footprints/differential_statistics.txt`` . You can use the R script XXX to make a nice vizualisation. Note that this script only consider TFs with significant change in activity (p-value < 0.05) and at least 1.000 binding sites for TF.  This indicates that SOX .... 


XXX - filter motif file (MA1104.2.GATA6 |MA0482.2.GATA4 and MA0142.1.Pou5f1::Sox2).

- open bed files in IGV and look at their location. 
