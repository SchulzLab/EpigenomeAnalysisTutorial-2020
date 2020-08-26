Practical III - Target gene identification of candidate regions
---------

In the previous steps we looked at footprints of TF and how we can evaluate their difference in activity in between hESC and cardiac mesoderm. This enables us to select TFs of interest and further explore their role in the regulatory machinery that drives the differentiation from hESC to cardiac mesoderm cells. In this step we want to look into different approaches of identifying target genes of genomic regions with regulatory potential. We will use the nearest gene, window-based and association-based approach and compare their results. In the following commands we will use GATA2 as a placeholder, replace it with the TF you are interested in.

1. Fetching candidate regions
=================

First of all, we need a directory where we can write our results to::

   mkdir results/session3

As we do not have any candidate regions yet, we take the regions where HINT annotated a binding site of our selected TF and intersect them with differential ATAC-peaks. This will leave us with regions where we expect a binding of our TF and where the cell types differ in their chromatin accessibility. Thus, we can assume that these regions play a role in the change of gene expression. The differential peaks were already called by the nf-core preprocessing pipeline. Execute the following script in your console to receive a bed-file with our filtered regions ::

   python3 FootprintTFFilter.py -m hint/motifmatching/Cardiac_mpbs.bed -p CardiacvshESC/CardiacvshESC.mRp.clN.deseq2.FDR0.05.results.bed -tf GATA2 -o GATA2_Hits.bed

* **-m**: path to the motif hits, exchange the file name to hESC_mpbs.bed when having a TF that scores higher in hESC
* **-p**: path to the differential ATAC-peaks
* **-tf**: name of the TF of interest
* **-o**: output path

2.1 Nearest gene
=================

For linking the nearest gene to a region we make use of the BedTools command closest, or more precisely the `Python implementation <https://daler.github.io/pybedtools/autodocs/pybedtools.bedtool.BedTool.closest.html>`_ of it. We created a file with the 5' TSS of genes in which *closest* will search in. It is included in the script *NearestGeneFinder.py* which you call like follows::

  python3 NearestGeneFinder.py -f GATA2_Hits.bed -t 5TSS_GRCh38p13.txt -o NearestGenes_GATA2.txt
  
* **-f**: path to the bed-file of the candidate regions
* **-t**: path to a file wiht the 5' TSS of genes
* **-o**: output path

2.2 Window-based approach
=================
The window-based approach looks in a defined window around the TSS of a gene and all candidate regions that are located inside of this window are linked to this gene. 


2.3 Association-based approach
=================
Both of the other methods are based on coordinates. Although they can yield good results in some cases, they are not able to capture long-ranged enhancer-gene interactions. Association-based methods can overcome this issue by combining data like ATAC-seq or DNase-seq for annotation of regulatory elements (REMs)/enhancers with gene expression data. We will make use of the webserver `EpiRegio <https://epiregio.de/>`_, which incorporates the results of the tool STITCHIT. STITCHIT interprets differences in DNase-signal to explain changes in gene expression among samples of different cell and tissue types. We will use EpiRegio's *Region Query* which will return all annotated regulatory elements and their target genes that overlap with our candidate regions. As required overlap we choose 50%, meaning that at least half of the length of our candidate region has to overlap with a REM. But instead of using the website (feel free to 'try it out <https://epiregio.de/regionQuery/>`_ as well), we will call EpiRegio's REST API via the Python package `Requests <https://requests.readthedocs.io/en/master/>`_. Requests allows to make HTTP queries and we can directly continue working with the results. Call the following script::

  python3 EpiRegio_Request.py -f GATA2.bed -ov 50 -o AssociationGenes_GATA2.txt

* **-f**: path to the bed-file with the candidate regions
* **-ov**: overlap as percentage of the length of the candidate regions
* **-o**: output path 

For more details on STITCHIT have a look at the `preprint <https://www.biorxiv.org/content/10.1101/585125v1.full>`_.The publication on EpiRegio can be found `here <https://academic.oup.com/nar/article/48/W1/W193/5847772>`_.

3. Intersecting the identified target genes
=================

Now we have three lists of target genes for our candidate regions from different approaches. To compare them, we will create an Upset plot, displaying the intersection with the list of differentially expressed genes which were called by DESeq2 (FDR 0.01). To create the plot use the command::

  python3 UpSetPlot_DEGenes.py -f NearestGenes_GATA2.txt WindowGenes_GATA2.txt AssociationGenes_GATA2.txt -g DESeq2_result_file_CM_hESC.tabular -t 0.01 -o GATA2_TargetGenes_intersection.pdf
  
* **-f**: files of gene lists from the different approaches
* **-g**: path to the result file of DESeq2
* **-t**: threshold for the adjusted p-value
* **-o**: ouput path for the Upset plot


