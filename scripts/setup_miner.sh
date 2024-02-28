#!/bin/bash

ROOT="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && cd .. && pwd )"
SCRIPTS_DIR="${ROOT}"/scripts

wallet_name=$1

source "${SCRIPTS_DIR}"/setup.sh
