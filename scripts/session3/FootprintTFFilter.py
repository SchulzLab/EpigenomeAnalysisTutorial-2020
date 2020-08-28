import argparse
import sys
from pybedtools import BedTool
import os

# Choose one TF or multiple ones and get their motif hit regions that also intersect with differential ATAC-peaks.

parser = argparse.ArgumentParser()

parser.add_argument("-m", "--motif_hit_file", help="Path to the motif hits for all TFs")
parser.add_argument("-p", "--differential_peaks", help="Path to the differential ATAC-peak file")
parser.add_argument("-tf", "--transcription_factors", nargs='+', help="Transcription factor names, multiple separated by whitespace")
parser.add_argument("-o", "--output", help="Folder to create for the output file")
args = parser.parse_args()


if not os.path.exists(args.output):  # We will create a new directory for the TF
    os.makedirs(args.output)

# Format the TF argument to only have the TF name, in case the full ID was given as input
tf_list = []
for tf in args.transcription_factors:
    if 'var.' in tf:
        tf_list.append('.'.join(tf.replace(' ', '').split('.')[-2:]))
    else:
        tf_list.append(tf.replace(' ', '').split('.')[-1])

# Get the motif hits of the TF of interest
motif_hits = [x.split('\t')[:4] for x in open(args.motif_hit_file).read().strip().split('\n') if x.split('\t')[3].split('.')[-1] in tf_list]
print(len(motif_hits), 'motif hits found')

# Intersect the filtered motif hits with the differential peaks
motif_hits_bed = BedTool('\n'.join(['\t'.join(x) for x in motif_hits]), from_string=True)
diff_peak_filtered = motif_hits_bed.intersect(args.differential_peaks)
print(len(str(diff_peak_filtered).strip().split('\n')), 'of motif hits intersect with a differential peak')

open(args.output + '/' + '_'.join(tf_list) + '_Hits.bed', 'w').write(str(diff_peak_filtered))

