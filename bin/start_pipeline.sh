#!/usr/bin/env bash
snakemake -r -p -s .../pipeapp/etc/pipeline.snake --config species=${species}
echo 'pipeline finished'
