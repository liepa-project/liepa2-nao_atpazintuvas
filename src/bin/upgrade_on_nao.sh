#!/bin/bash
#upgrade on nao
liepa_asr_version=`curl --silent https://api.github.com/repos/liepa-project/nao-liepa-asr/releases/latest | grep '"tag_name":'| sed -E 's/.*"([^"]+)".*/\1/'`
echo "Liepa ASR version: $liepa_asr_version "
killall -9 LiepaASR
rm /home/nao/naoqi/lib/LiepaASR* -rf
rm /tmp/nao-liepa-asr* -rf
wget https://github.com/liepa-project/nao-liepa-asr/releases/download/$liepa_asr_version/nao-liepa-asr.tar.gz -P /tmp
mkdir -p /tmp/nao-liepa-asr
tar xvzf /tmp/nao-liepa-asr.tar.gz -C /tmp/nao-liepa-asr
cp /tmp/nao-liepa-asr/* /home/nao/naoqi/lib -r
