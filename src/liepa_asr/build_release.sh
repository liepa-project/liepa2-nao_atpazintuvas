#!/bin/bash
(cd sphinxbase && ./autogen.sh)
(cd pocketsphinx && ./autogen.sh)
qibuild configure -c atom
qibuild make -c atom -j 5


rm target/* -rf
mkdir -p target/generated
cp build-atom/sdk/bin/LiepaASR target/generated/
cp ../../models/LiepaASRResources/ target/generated/ -R
cp ../bin/upgrade_on_nao.sh target/generated/
(cd target/generated && tar -czvf ../nao-liepa-asr.tar.gz  .)
