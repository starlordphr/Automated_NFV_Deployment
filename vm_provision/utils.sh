#!/bin/bash

# Utils that can be used in other scripts

RED='\033[1;31m'
GREEN='\033[1;32m'
YELLOW='\033[1;33m'
CYAN='\033[1;36m'
GRAY='\033[1;37m'
NC='\033[0m' # No Color

print-colored() {
	COLOR=$1; shift
	printf "${COLOR}$*${NC}\n"
}
export -f print-colored

print-error() {
	print-colored $RED $*
}
export -f print-error

print-highlight() {
	print-colored $CYAN $*
}
export -f print-highlight

print-warning() {
	print-colored $YELLOW $*
}
export -f print-warning

print-pass() {
	print-colored $GREEN $*
}
export -f print-pass

print-gray() {
	print-colored $GRAY $*
}
export -f print-gray

testcmds() {
	while [[ $# -ge 1 ]]; do
		bash -c $1 &> /dev/null	# suppress output
		if [[ $? -ne 0 ]]; then
			print-error "[ERROR] Please install '$1' first!"
			exit $?
		fi
		shift
	done
}
export -f testcmds
