#!/bin/bash
(cd sphinxbase && ./autogen.sh)
(cd pocketsphinx && ./autogen.sh)
qibuild configure -c atom286
qibuild make -c atom286 -j 5


rm target/* -rf
mkdir -p target/generated
cp build-atom286/sdk/bin/LiepaASR target/generated/
cp ../../models/LiepaASRResources/ target/generated/ -R
cp ../bin/upgrade_on_nao.sh target/generated/
(cd target/generated && tar -czvf ../nao-liepa-asr.tar.gz  .)
