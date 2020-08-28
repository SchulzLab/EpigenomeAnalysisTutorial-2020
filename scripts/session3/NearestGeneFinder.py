import sys
from pybedtools import BedTool
import argparse

# Get the nearest gene for a set of regions. Requires a file in bed-format, a file with the TSS of all potential genes
# and the output path. Returns a file with the unique ensembl IDs of the nearest genes.

parser = argparse.ArgumentParser()

parser.add_argument("-f", "--region_file", help="Bed-file with regions to find the nearest gene for")
parser.add_argument('-t', '--tss_file', help='File with the 5-TSS of genes')
parser.add_argument("-o", "--output", help="Output path for the gene list")
args = parser.parse_args()

# Convert the TSS file to a BedTools object and sort it
tss_bed = BedTool('\n'.join('\t'.join([x.split('\t')[1], x.split('\t')[2], str(int(x.split('\t')[2])+1), x.split('\t')[0]])
                    for x in open(args.tss_file).read().strip().split('\n')), from_string=True).sort()

# Use BedTool's closest to get the closest TSS for every region
closest_hit = BedTool(args.region_file).sort().closest(tss_bed)

# Extract the geneIDs of the closest TSS and write them into the output file
closest_genes = list(set([x.split('\t')[-1] for x in str(closest_hit).strip().split('\n')]))

open(args.output, 'w').write('\n'.join(closest_genes))

