#!/bin/bash

POSITIONAL=()
while [[ $# -gt 0 ]]
do
key="$1"

case $key in
    -m|--motif_hit_file)
    motif="$2"
    shift # past argument
    shift # past value
    ;;
    -t|--TFs)
    TFs="$2"
    shift # past argument
    shift # past value
    ;;
esac
done
set -- "${POSITIONAL[@]}" # restore positional parameters

echo "Motif hit file: ${motif}"
echo "Transcription factors: ${TFs}"

for TF in ${TFs}
do
  echo "${TF}"

  python3 scripts/session3/FootprintTFFilter.py  -m "${motif}" -p data/nf_core_atacseq/macs/narrowPeak/consensus/deseq2/CardiacvshESC/CardiacvshESC.mRp.clN.deseq2.FDR0.05.results.bed  -tf "${TF}" -o results/session3/"${TF}"_Targets

  python3 scripts/session3/NearestGeneFinder.py -f results/session3/"${TF}"_Targets/"${TF}"_Hits.bed -t data/5TSS_GRCh38p13.txt -o results/session3/"${TF}"_Targets/Nearest_Genes.txt

  python3 scripts/session3/WindowGenesFinder.py -f results/session3/"${TF}"_Targets/"${TF}"_Hits.bed -t data/5TSS_GRCh38p13.txt -w 50000 -o results/session3/"${TF}"_Targets/Window_Genes.txt

  python3 scripts/session3/EpiRegio_Request.py -f results/session3/"${TF}"_Targets/"${TF}"_Hits.bed -ov 50 -o results/session3/"${TF}"_Targets/Association_Genes.txt

  python3 scripts/session3/UpSetPlot_DEGenes.py -f results/session3/"${TF}"_Targets/Nearest_Genes.txt results/session3/"${TF}"_Targets/Window_Genes.txt results/session3/"${TF}"_Targets/Association_Genes.txt -g data/DESeq2_result_file_CM_hESC.tabular -t 0.01 -o results/session3/"${TF}"_Targets -s 0

done
