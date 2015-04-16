#!/bin/bash

if [ "$1" == "rc" ];then
    git archive --format=tar HEAD:webkit | gzip > instalador-webkit-`git rev-parse --short HEAD`.tar.gz
else
    tar czvf instalador-webkit-devel.tar.gz webkit
fi
