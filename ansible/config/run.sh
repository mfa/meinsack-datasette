#!/bin/bash

BASE=/home/meinsack/

${BASE}/.local/bin/datasette -p 21476 ${BASE}/meinsack.db -m metadata.yml --template-dir templates --plugins-dir plugins --static static:static/
