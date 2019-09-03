#!/bin/bash
#upgrade on nao
killall -9 LiepaASR
rm /home/nao/naoqi/lib/LiepaASR* -rf
rm /tmp/nao-liepa-asr* -rf
wget https://github.com/liepa-project/nao-liepa-asr/releases/download/0.2/nao-liepa-asr.tar.gz -P /tmp
mkdir -p /tmp/nao-liepa-asr
tar xvzf /tmp/nao-liepa-asr.tar.gz -C /tmp/nao-liepa-asr
cp /tmp/nao-liepa-asr/* /home/nao/naoqi/lib -r
