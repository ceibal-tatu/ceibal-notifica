#!/bin/bash

git archive --format=tar HEAD:webkit | gzip > instalador-webkit-`git rev-parse --short HEAD`.tar.gz
