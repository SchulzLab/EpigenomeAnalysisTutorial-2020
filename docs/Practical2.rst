==================================================================
Practical II - Linking regions to genes and integration with gene expression data
==================================================================
Step 1: Extracting TF motifs of TFs expressed in the cell types of interest
----------------------------------------------------

Ensure that you are in the directory 
::

  /data/EpigenomeAnalysisTutorial-2020/

and create a directory where we can write our results to: 
::

 mkdir results/session2/

DYNAMITE requires as input a list of known TF binding motifs. In this step, we want to extract the TF binding motifs of TFs which are expressed in pluripotent cells (hESCs), cardiac mesoderms (CM) or in both cell types. Therefore, we provide the script *extractPSEMsOfExpressedTFs.py*, which expects as input

-	Gene expression values (TPM) from hESCs
-	Gene expression values (TPM) of CMs
-	A file containing all available TF binding motifs as Position specific energy matrices (PSEMs)
-	Output file
-	A mapping from ensembl IDs to gene names
-	TPM value. If the expression value of a TF is higher than  the TPM value, we consider this TF as expressed.

Please run the script using the following command:

::

  scripts/session2/extractPSEMsOfExpressedTFs.py data/meanTPM_hESC.txt  data/meanTPM_CM.txt  data/PSEM_JASPAR2020.txt results/session2/PSEMs_JASPAR2020_TPM_0.5.txt data/ensemblID_GeneName.txt 0.5

Step 2: Intersect the footprint from HINT with differentially ATAC-peaks
----------------------------------------------------

TODO: einleitungssatz

Before we can perform the intersection step, we first have to preprocess the footprint. Please run 

::

  awk '{print $1 "\t" $2 "\t" $3 "\t" $4 "\t" $5}' results/session1/hint/footprints/hESC.bed  > results/session2/footprints_hESC.bed
and 
::
 
  awk '{print $1 "\t" $2 "\t" $3 "\t" $4 "\t" $5}' results/session1/hint/footprints/Cardiac.bed  > results/session2/footprints_CM.bed
  
To intersect the footprint of the hESC and the cardiac mesoderms with the differentially ATAC-peaks, we use bedtools intersect command. Please run: 

::

  bedtools intersect -a  results/session2/footprints_hESC.bed -b data/nf_core_atacseq/macs/narrowPeak/consensus/deseq2/CardiacvshESC/CardiacvshESC.mRp.clN.deseq2.FDR0.05.results.bed  > results/session2/footprints_DiffPeaks_hESC.bed

and

::

  bedtools intersect -a  results/session2/footprints_CM.bed -b data/nf_core_atacseq/macs/narrowPeak/consensus/deseq2/CardiacvshESC/CardiacvshESC.mRp.clN.deseq2.FDR0.05.results.bed  > results/session2/footprints_DiffPeaks_CM.bed

Since the footprints are rather short, we need to extend the region by some base pairs, such that all regions are longer than the longest TF binding motif (>21bp). This is necessary to probably compute the TF binding affinity per footprint region during the *DYNAMITE* analysis. Please run the following two commands:

::

  awk '{print $1 "\t" $2 -10 "\t" $3 +10 "\t" $4 "\t" $5}' results/session2/footprints_DiffPeaks_CM.bed  >results/session2/footprints_DiffPeaks_CM_extended.bed 
  
and 
::

  awk '{print $1 "\t" $2 -10 "\t" $3 +10 "\t" $4 "\t" $5}' results/session2/footprints_DiffPeaks_hESC.bed  >results/session2/footprints_DiffPeaks_hESC_extended.bed

Step 3: Deriving candidate transcriptional regulators using *DYNAMITE*
----------------------------------------------------

During a *DYNAMITE* analysis, two main computational tasks are undertaken:

#. We calculate TF binding affinities for TFs expressed in hESC, cardiac mesoderms or both cell types and aggregate those to gene-TF scores using *TEPIC*. TF affinities are a quantitative measure of TF binding to a distinct genomic region. 
#. A logistic regression classifier is learned that uses changes in TF gene scores between two samples to predict which genes are up/down- regulated between them. Investigating the features of the model allows the inference of potentially interesting regulators that are correlated to the observed expression changes. 

Please check the `documentation <https://github.com/SchulzLab/TEPIC/blob/master/docs/Description.pdf>`_ for details on the method.

We provide a script that automatically performs steps (1) and (2) as well as necessary data processing and formatting steps (See `DYNAMITE documentation <https://github.com/SchulzLab/TEPIC/blob/master/MachineLearningPipelines/DYNAMITE/README.md>`_ for details).
All files used in this step are available in ``/data/EpigenomeAnalysisTutorial-202 EpigenomeAnalysisTutorial-2020/data/ ``. 

Note that we precomputed the differential gene expression estimates. Computing those is neither part of the actual tutorial nor of the *DYNAMITE* workflow.

**1.** Assure that you are in the directory ``/data/EpigenomeAnalysisTutorial-2020/``, otherwise *cd* to that directory.

**2.** Generate an output folder for the resulting files:
::

  mkdir results/session2/DYNAMITE/
  
**3.** To run the *DYNAMITE* script go to the *DYNAMITE* folder in the *TEPIC* repository `` ../../root/TEPIC2-2/MachineLearningPipelines/DYNAMITE/``. We provide two configuration files for the *DYNAMITE* analyses:

#. DYNAMITE-hESCvsCM-Top800DEGs.cfg
#. DYNMAITE-hESCvsCM-DEGs-fdr0.1.cfg

The configuration files list all parameters that are needed for a run of *DYNAMITE*. 
To help you customize these files for later usage, we explain the essential parameters here:

* open_regions_Group1: One or more files containing candidate transcription factor binding sites for samples belonging to group 1
* open_regions_Group2: One or more files containing candidate transcription factor binding sites for samples belonging to group 2
* differential_Gene_Expression_Data: Differential gene expression data denoted with log2 fold changes
* outputDirectory: Directory to write the results to
* referenceGenome: Path to the reference genome that should be used
* chrPrefix: Flag indicating whether the reference genome uses a chr prefix
* pwm: Path to the PSEMs that should be used
* cores_TEPIC: Number of cores that are used in the TEPIC analysis
* geneAnnotation: Gene annotation file that should be used
* window: Size of the window around a genes TSS that is screened for TF binding sites
* decay: Flag indicating whether TEPIC should be using exponential decay to downweight far away regions while computing gene-TF scores
* peakFeatures: Flag indicating whether TEPIC should compute features based on peaks, e.g. peak count, peak length, or signal intensity within a peak

In the scope of the tutorial, you do not have to change any of those. A full description of all parameters is provided `here <https://github.com/SchulzLab/TEPIC/blob/master/MachineLearningPipelines/DYNAMITE/README.md>`_.


TODO: ... ab hier
**4.** Run the individual pairwise comparisons for LSK vs B:
::
  
  bash runDYNAMITE.sh $HOME/EpigenomicsTutorial-ISMB2017/session2/step3/input/DYNAMITE-LSKvsB.cfg

LSK vs CD4:
::
  bash runDYNAMITE.sh $HOME/EpigenomicsTutorial-ISMB2017/session2/step3/input/DYNAMITE-LSKvsCD4.cfg

and B vs CD4:
::
  bash runDYNAMITE.sh $HOME/EpigenomicsTutorial-ISMB2017/session2/step3/input/DYNAMITE-BvsCD4.cfg

Note that you have to **replace** the prefix ``$HOME`` with the proper path to the tutorial repository, if you have not cloned it to your *home* directory. 
The results of the analysis will be stored separately for each run in ``EpigenomicsTutorial-ISMB2017/session2/step3/output``. There are three subfolders for
each comparison:

#. Affinities
#. IntegratedData
#. Learning_Results

The folder *Affinities* contains TF affinities calculated in the provided regions for both groups, gene TF scores for both groups, and a metadata file that
lists all settings used for the TF annotation with *TEPIC* (subfolders *group1* and *group2*). The subfolder *mean* contains the mean gene TF scores computed for group1 and group2. This is needed if you analyze more than one biological replicate per group. The folder *ratio* contains the gene TF score ratios computed between
the gene TF scores of group1 and group2.

The folder *IntegratedData* encloses matrices that are composed of (1) gene TF score ratios and (2) a measure of differential gene expression. In the folder *Log2* the differential gene expression
is represented as the log2 expression ratio between group1 and group2. In the folder *Binary*, the differential gene expression is shown in a binary way. Here, a 1 means a gene is upregulated in group 1 compared to group 2, whereas a 0 means it is down-regulated in group1. The binary format is used as input for the classification. 

The folder *Learning_Results* comprises the results of the logistic regression classifier. The following files should be produced if all R dependencies are available:

#. Performance_overview.txt
#. Confusion-Matrix_<1..6>_Integrated_Data_For_Classification.txt
#. Regression_Coefficients_Cross_Validation_Integrated_Data_For_Classification.txt
#. Regression_Coefficients_Entire_Data_Set_Integrated_Data_For_Classification.txt
#. Performance_Barplots.png
#. Regression_Coefficients_Cross_Validation_Heatmap_Integrated_Data_For_Classification.svg
#. Regression_Coefficients_Entire_Data_SetIntegrated_Data_For_Classification.png
#. Misclassification_Lambda_<1..6>_Integrated_Data_For_Classification.svg

The file *Performance_overview.txt* contains accuracy on Test and Training data sets as well as F1 measures. These values are visualized in *Performance_Barplots.png*.
As the name suggests, the files *Confusion-Matrix_<1..6>_Integrated_Data_For_Classification.txt* contain the confusion matrix computed on the test data sets.
They show model performance by reporting True Positives (TP), False Positives (FP), True Negatives (TN), and False Negatives (FN) in the following layout:

+---------------------+----------+----------+
| Observed/Predicted  | Positive | Negative |
+=====================+==========+==========+
| Positive            |    TP    |    FN    |
+---------------------+----------+----------+
| Negative            |    FP    |    TN    |
+---------------------+----------+----------+

The heatmap *Regression_Coefficients_Cross_Validation_Heatmap_Integrated_Data_For_Classification.svg* shows the regression coefficients of all selected features in
the outer cross validation. This is very well suited to find features that are stably selected in all outer cross validation folds. The raw data used to generate the figure is stored in 
*Regression_Coefficients_Cross_Validation_Integrated_Data_For_Classification.txt*. The stronger a regression coefficient, the more important it is in the model.

In addition to the heatmap showing the regression coefficients during the outer cross validation, we also show the regression coefficients learned on the full
data set: *Regression_Coefficients_Entire_Data_SetIntegrated_Data_For_Classification.png* and *Regression_Coefficients_Entire_Data_Set_Integrated_Data_For_Classification.txt*.

The figures *Misclassification_Lambda_<1..6>_Integrated_Data_For_Classification.svg* are of technical nature. They show the relationship between the misclassification error and the lambda parameter of the logistic regression function. 

**5.** In addition to the plots describing model performance and feature selection generated by *DYNAMITE* (as described `here <https://github.com/SchulzLab/TEPIC/blob/master/MachineLearningPipelines/DYNAMITE/README.md>`_), you can create further Figures for a distinct feature of interest
using the script ``TEPIC/MachineLearningPipelines/DYNAMITE/Scripts/generateFeaturePlots.R``. This will provide you with density plots showing the distribution of the feature in 
the two cell types, scatter plots linking feature value to gene expression changes, and a mini heatmap visualising the features regression coefficients. 

To use this script, go to the output folder of step 3 ``EpigenomicsTutorial-ISMB2017/session2/step3/output`` and use the command
::

  Rscript $HOME/TEPIC/MachineLearningPipelines/DYNAMITE/Scripts/generateFeaturePlots.R LSK-vs-CD4 HOXA3 LSK CD4


This command will generate a plot comparing HOXA3 in LSK against CD4. Feel free to look at further features as you wish. The figure will be stored in the specified directory that contains the results of the *DYNAMITE* analysis.
Again, note that you have to **replace** the prefix ``$HOME`` with the proper path used on your system, if necessary.
Precomputed results are stored in ``/EpigenomicsTutorial-ISMB2017/session2/step3/result``.
