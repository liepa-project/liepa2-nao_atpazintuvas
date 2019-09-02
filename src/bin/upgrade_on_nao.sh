#!/bin/bash
#upgrade on now
killall -9 LiepaASR
wget https://github.com/liepa-project/nao-liepa-asr/releases/download/0.1/nao-liepa-asr.tar.gz -P /tmp
mkdir -p /tmp/liepa
tar xvzf /tmp/nao-liepa-asr.tar.gz -C /tmp/liepa
cp /tmp/liepa /home/nao/naoqi/lib -r
