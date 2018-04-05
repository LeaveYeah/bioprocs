function cmdargs() {
	dash="auto"
	equal="auto"
	if [[ $# -gt 1 ]]; then
		dash=$2
	fi
	if [[ $# -gt 2 ]]; then
		equal=$3
	fi
	$__python__ -c "from bioprocs.utils import cmdargs; import sys; sys.stdout.write(cmdargs($1, dash='$dash', equal='$equal'))"
}