Practical III - Target gene identification of candidate regions
---------

In the previous steps we looked at footprints of TF and how we can evaluate their difference in activity in between hESC and cardiac mesoderm. This enables us to select TFs of interest and further explore their role in the regulatory machinery that drives the differentiation from hESC to cardiac mesoderm cells. In this step we want to look into different approaches for identifying target genes of genomic regions with regulatory potential. We will use the nearest gene, window-based and association-based approach and compare their results. In the following commands we will use GATA2 as a placeholder, replace it with the TF you are interested in.

Step 1: Fetching candidate regions
=================

First of all, we need a directory where we can write our results to::

   mkdir results/session3

As we do not have any candidate regions yet, we take the regions where HINT annotated a binding site of our selected TF and intersect them with differential ATAC-peaks. This will leave us with regions where we expect a binding of our TF and where the cell types differ in their chromatin accessibility. Thus, we can assume that these regions play a role in the differences in gene expression. The differential peaks were already called by the nf-core preprocessing pipeline. Execute the following command to receive a bed-file with our candidate regions: ::

   python3 scripts/session3/FootprintTFFilter.py -m results/session1/hint/motifmatching/Cardiac_mpbs.bed -p data/nf_core_atacseq/macs/narrowPeak/consensus/deseq2/CardiacvshESC/CardiacvshESC.mRp.clN.deseq2.FDR0.05.results.bed -tf GATA4 -o results/session3/GATA4_Targets

* **-m**: path to the motif hits, exchange the file name to hESC_mpbs.bed when looking at a TF that scores higher in hESC
* **-p**: path to the differential ATAC-peaks
* **-tf**: name of the TF of interest
* **-o**: Folder to create for the ouput file

A new folder will be created under *results/session3/GATA4_Targets*. It will contain the file *GATA4_Hits.bed*. This is our candidate region file which we will need for the next steps.

Step 2.1: Target genes - Nearest gene
=================

For linking the nearest gene to a region we make use of the BedTools command closest, or more precisely the `Python implementation <https://daler.github.io/pybedtools/autodocs/pybedtools.bedtool.BedTool.closest.html>`_ of it. For each candidate region we will find the closest TSS. We created a file with the 5' TSS of genes in which *closest* will search in. To get the list with the IDs of all closest genes execute: ::

  python3 scripts/session3/NearestGeneFinder.py -f results/session3/GATA4_Targets/GATA4_Hits.bed -t data/5TSS_GRCh38p13.txt -o results/session3/GATA4_Targets/Nearest_Genes.txt

  
* **-f**: path to the bed-file of the candidate regions
* **-t**: path to a file with the 5' TSS of genes
* **-o**: output path

You will find the file *Nearest_Genes.txt* in the *results/session3/GATA4_Targets* folder.

Step 2.2: Target genes - Window-based approach
=================

The window-based approach looks in a defined window around the TSS of a gene and all candidate regions that are located inside of this window are linked to this gene. Call: ::

   python3 scripts/session3/WindowGenesFinder.py -f results/session3/GATA4_Targets/GATA4_Hits.bed -t data/5TSS_GRCh38p13.txt -w 50000 -o results/session3/GATA4_Targets/Window_Genes.txt

* **-f**: path to the bed-file of the candidate regions
* **-t**: path to a file with the 5' TSS of genes
* **-w**: window size
* **-o**: output path

The script creates intervals of size **-w** centered around the TSS of each gene and then intersects them with our candidate regions. You will find the identified target genes in *results/session3/GATA4_Targets/Window_Genes.txt*.

Step 2.3: Target genes - Association-based approach
=================
Both of the other methods are based on coordinates. Although they can yield good results in some cases, they are not able to capture long-ranged enhancer-gene interactions. Association-based methods can overcome this issue by combining data like ATAC-seq or DNase-seq for annotation of regulatory elements (REMs)/enhancers with gene expression data. We will make use of the webserver `EpiRegio <https://epiregio.de/>`_, which incorporates the results of the tool STITCHIT. STITCHIT interprets differences in DNase-signal to explain changes in gene expression among samples of different cell and tissue types. We will use EpiRegio's *Region Query* which will return all annotated regulatory elements and their target genes that overlap with our candidate regions. As required overlap we choose 50%, meaning that at least half of the length of our candidate region has to overlap with a REM. But instead of using the website (feel free to `try it out <https://epiregio.de/regionQuery/>`_ as well), we will call EpiRegio's REST API via the Python package `Requests <https://requests.readthedocs.io/en/master/>`_. Requests allows to make HTTP queries and we can directly continue working with the results. Call the following script::

  python3 scripts/session3/EpiRegio_Request.py -f results/session3/GATA4_Targets/GATA4_Hits.bed -ov 50 -o results/session3/GATA4_Targets/Association_Genes.txt

* **-f**: path to the bed-file with the candidate regions
* **-ov**: overlap as percentage of the length of the candidate regions
* **-o**: output path 

For more details on STITCHIT have a look at the `preprint <https://www.biorxiv.org/content/10.1101/585125v1.full>`_.The publication on EpiRegio can be found `here <https://academic.oup.com/nar/article/48/W1/W193/5847772>`_.

Step 3: Intersecting the identified target genes
=================

Now we have three lists of target genes for our candidate regions from different approaches. To compare them, we will create an Upset plot, displaying the intersection with the list of differentially expressed genes which were called by DESeq2 (FDR 0.01). To create the plot use the command::

  python3 scripts/session3/UpSetPlot_DEGenes.py -f results/session3/GATA4_Targets/Nearest_Genes.txt results/session3/GATA4_Targets/Window_Genes.txt results/session3/GATA4_Targets/Association_Genes.txt -g data/DESeq2_result_file_CM_hESC.tabular -t 0.01 -s 0 -o results/session3/GATA4_Targets/

  
* **-f**: files of gene lists from the different approaches, separated by whitespace
* **-g**: path to the result file of DESeq2
* **-t**: threshold for the adjusted p-value
* **-s**: whether to split the DE genes into negative and positive change (1) or not (0)
* **-o**: ouput path for the files

In addition to the Upset plot, the script will also create a bar plot which depicts the percentage of target genes that are differentially expressed (DE) for all approaches. Further, you will find four new gene ID files. For each approach we filter the target genes for differentially expressed genes and write them into a new file (*...DEGenes_intersection*). The fourth file */Users/dennis/Dev/ECCB20Tutorial/GATA2_TargetGenes/ApproachesMerged_DEGenes_intersection.txt* merges the target genes of all approaches and filters for the DE genes. These files can be used to paste the IDs to functional enrichment analysis tools like `gProfiler <https://biit.cs.ut.ee/gprofiler/gost>`_.

Step 4: All steps in one
=================
All of the steps above can also be performed by calling the script *TF_to_UpSet_series.sh*: ::

   bash ./scripts/session3/TF_to_UpSet_series.sh -m results/session1/hint/motifmatching/Cardiac_mpbs.bed -t "GATA2 GATA4"

* **-m**: path to the motif hits, exchange the file name to hESC_mpbs.bed when looking at a TF that scores higher in hESC
* **-t**: TF(s) of interest

This will call all scripts needed one after another, create the output folder and write the files into it. It is adapted to the folder structure of our Docker image, so be sure to edit all paths when you want to call it in a different environment. Like in the example, you can call the script with multiple TFs, don't forget the quotation marks when doing so.

