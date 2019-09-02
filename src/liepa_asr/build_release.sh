#!/bin/bash
(cd sphinxbase && ./autogen.sh)
(cd pocketsphinx && ./autogen.sh)
qibuild configure -c atom
qibuild make -c atom -j 5



mkdir -p target/generated
cp build-atom/sdk/bin/LiepaASR target/generated/
cp ../../models/LiepaASRResources/ target/generated/ -R
(cd target/generated && tar -czvf ../nao-liepa-asr.tar.gz  .)
