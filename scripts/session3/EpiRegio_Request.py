import sys
import argparse
import requests

# This script uses the requests package to talk to the REST API of EpiRegio. We create URLs from a region bed file
# and chunk it to not exceed the maximal character length of URLs.

parser = argparse.ArgumentParser()

parser.add_argument("-f", "--region_file", help="Bed file of the regions of interest")
parser.add_argument('-ov', "--overlap", help="Overlap as percentage of a region length eg 50")
parser.add_argument("-o", "--output", help="Output path for the gene list")
args = parser.parse_args()


def chunker(seq, size):
    return [seq[pos:pos + size] for pos in range(0, len(seq), size)]


# Extract chr, start and end as list out of the bed file
candidate_regions = [x.split('\t')[0:3] for x in open(args.region_file).read().strip().split('\n')]

chunked_regions = chunker(candidate_regions, 40)

association_genes = []  # Let's already define our output

print('Requesting results via REST API')
for chunk in chunked_regions:
    our_url = 'https://epiregio.de/REST_API/RegionQuery/'+str(args.overlap)+'/'+'_'.join([region[0]+':'+str(region[1])+'-'+str(region[2]) for region in chunk])+'/'
    api_call = requests.get(our_url)  # call the REST API via our adapted URL
    if api_call.status_code != 200:  # In case the page does not work properly.
        print("Page Error")
    for hit in api_call.json():
        association_genes.append(hit['geneID'])  # fetch the gene IDs from the Json dictionary

# Make the gene list unique and write them to the output file
open(args.output, 'w').write('\n'.join(list(set(association_genes))))

