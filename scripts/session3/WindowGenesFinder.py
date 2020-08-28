import sys
from pybedtools import BedTool
import argparse

# Find the target genes of regions by looking in a window around the TSS. The window spans the whole search window,
# meaning window/2 down- and window/2 upstream

parser = argparse.ArgumentParser()

parser.add_argument("-f", "--region_file", help="Bed-file with regions to find the nearest gene for")
parser.add_argument('-t', '--tss_file', help='File with the 5-TSS of genes')
parser.add_argument('-w', '--window', help='Size of the search window around a gene TSS')
parser.add_argument("-o", "--output", help="Output path for the gene list")
args = parser.parse_args()

# Write a BedTool object containing the windows around the TSS for every gene
tss_bed = BedTool('\n'.join('\t'.join([x.split('\t')[1], str(max(0, int(x.split('\t')[2])-int(int(args.window)/2))), str(int(x.split('\t')[2])+int(int(args.window)/2)), x.split('\t')[0]])
                    for x in open(args.tss_file).read().strip().split('\n')), from_string=True).sort()

# Intersect the TSS BedTool object with the candidate regions
window_hits = tss_bed.intersect(args.region_file, F=1)

# Extract the geneIDs and write them into the output file
window_genes = list(set([x.split('\t')[-1] for x in str(window_hits).strip().split('\n')]))

open(args.output, 'w').write('\n'.join(window_genes))

