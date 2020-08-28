import sys
from matplotlib import pyplot as plt
import upsetplot
import argparse

# Create an Upset plot of the gene lists from the different approaches visualizing their overlap. Also creates a
# barplot illustrating the fraction of target genes that are also differnetially expressed. This script
# theoretically allows for unlimited input files separated by whitespace when called from the command line. The
# file of the differential genes is handled separately, as the significant ones still have to be filtered.
# We will also write lists for each input file which genes intersect with the DE genes and an additional one which
# merges the target genes of all approaches and intersect them with the DE genes.

parser = argparse.ArgumentParser()

parser.add_argument("-f", "--gene_files", nargs='+', help="Files with gene IDs, or with a gene ID column separated by whitespace")
parser.add_argument("-g", "--differential_genes", help="Result file of DESeq2, needs a column with geneID and p-adj")
parser.add_argument("-t", "--threshold", help="Threshold for the adjusted p-value")
parser.add_argument("-s", "--split", help="If the DE genes should be split (1) into negative and positive fold-change or not (0)")
parser.add_argument("-o", "--output_folder", help="Output folder for the generated files")
args = parser.parse_args()

file_list = args.gene_files
output = args.output_folder

# Create a dictionary to enter the unqiue genes of all files as well as a dictionary for the intersection with DE genes
gene_lists = {}
intersection_dict = {}

# The DE genes get added separately, as this file is the output of DESeq2 and hast to be filtered by the adjusted
# p-value still.
de_rows = [x.split('\t') for x in open(args.differential_genes).read().strip().split('\n')]
de_gene_col = [i for i, x in enumerate(de_rows[-1]) if x.startswith('ENSG')][0]  # find the column index
de_p_adj_col = [i for i, x in enumerate(de_rows[0]) if x == 'p-adj'][0]  # find the column index
logFC_col = [i for i, x in enumerate(de_rows[0]) if x == 'log2(FC)'][0]  # find the column index

if args.split == '1':  # Split the DE genes into positive log-fold change and negative log-fold change
    de_genes_negFC = []
    de_genes_posFC = []
    for row in de_rows:
        try:
            if row[de_gene_col].startswith('ENSG') and float(row[de_p_adj_col]) <= float(args.threshold):
                if float(row[logFC_col]) < 0:
                    de_genes_negFC.append(row[de_gene_col].split('.')[0])
                elif float(row[logFC_col]) >= 0:
                    de_genes_posFC.append(row[de_gene_col].split('.')[0])
        except ValueError:
            continue

    gene_lists['DE genes_t' + str(args.threshold) + 'negFC'] = list(set(de_genes_negFC))
    gene_lists['DE genes_t' + str(args.threshold) + 'posFC'] = list(set(de_genes_posFC))
    all_de_genes = list(set(de_genes_negFC)) + list(set(de_genes_posFC))
else:  # when -s not specified or 0
    de_genes = []
    for row in de_rows:
        try:
            if row[de_gene_col].startswith('ENSG') and float(row[de_p_adj_col]) <= float(args.threshold):
                de_genes.append(row[de_gene_col].split('.')[0])
        except ValueError:
            continue
    gene_lists['DE genes_t' + str(args.threshold)] = list(set(de_genes))
    all_de_genes = list(set(de_genes))

combined_list = []  # to merge the list from the approaches
for file in file_list:  # go through the gene list of each approach
    file_rows = [x.split('\t') for x in open(file).read().strip().split('\n')]
    gene_col = [i for i, x in enumerate(file_rows[-1]) if x.startswith('ENSG')][0]  # find the column index
    these_genes = list(set([x[gene_col].split('.')[0] for x in file_rows if x[gene_col].startswith('ENSG')]))
    gene_lists[file.split('/')[-1].split('.')[0]] = these_genes
    combined_list += these_genes
    de_intersection = list(set(these_genes) & set(all_de_genes))
    intersection_dict[file.split('/')[-1].split('.')[0]] = len(de_intersection)/len(these_genes)
    # Write the file with genes that intersect with DE genes
    open(output + '/' + file.split('/')[-1].split('.')[0] + '_DEGenes_Intersection.txt', 'w').write\
        ('\n'.join(de_intersection))

# Write another file that intersects the merged gene IDs from all approaches with the DE genes
open(output + '/' + 'ApproachesMerged_DEGenes_intersection.txt', 'w').write\
    ('\n'.join(list(set(combined_list) & set(all_de_genes))))


# create the barplot
f, ax = plt.subplots(1, figsize=(8, 6))
plt.ylabel('Percentage of intersection with DE genes', fontsize=14)
plt.title('Fraction of identified target genes that\nare also differentially expressed', fontsize=16, fontweight='bold')
ax.set_facecolor('#f2f2f2')
ax.grid(True, axis='y', color='white', linewidth=1, which='major')
ax.bar([x for x in range(len(file_list))], [intersection_dict[x] for x in list(intersection_dict.keys())], width=0.8, color='#045f8c', zorder=12)
plt.xticks([x for x in range(len(file_list))], [x for x in list(intersection_dict.keys())], fontsize=14)
plt.savefig(output + '/DEGenes_Intersection_Fraction.pdf', bbox_inches='tight')


# Upsetplot creates the intersection between each pairing of elements
intersection = upsetplot.from_contents(gene_lists)

upset = upsetplot.UpSet(intersection, show_counts=True, element_size=40, intersection_plot_elements=8)
upset.plot()
plt.savefig(output + '/DE_Genes_Intersection_UpSet.pdf', bbox_inches='tight')
