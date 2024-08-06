#!/bin/bash

set -eux -o pipefail

if [ "$MOUNTS_DIR" = "" ]; then
    MOUNTS_DIR="./mounts"
fi

mkdir -p $MOUNTS_DIR/cms
wget http://opendata.cern.ch/record/9538/files/assets/cms/MonteCarlo2012/Summer12_DR53X/TTGJets_8TeV-madgraph/AODSIM/PU_RD1_START53_V7N-v1/10000/0431F9FA-6202-E311-8B98-002481E1501E.root -P $MOUNTS_DIR/cms
