from pyppl import Proc, Box
from . import params
from .utils import fs2name

"""
@name:
	pSort
@description:
	Sort file using linux command `sort`
@input:
	`infile:file`: The input file
@output:
	`outfile:file`: The output file
@args:
	`inopts`: The input options for infile:
		- `skip`   : First N lines to skip. Default: `0`
		- `delimit`: The delimit. Default          : `\t`
		- `comment`: The comment line mark. Default: `#`
	`case`:   Case-sensitivity. Default: True
		- If True, will set $LANG as C
		- Otherwise, $LANG will be set as en_US.UTF-8
	`mem`    : The buffer size. Default: 4G
	`tmpdir` : The tmpdir.
	`unique` : Just keep the unique lines. Default: False
	`delimit`: The delimit to separate the fields. Default: '\t'
	`params` : The arguments used by `sort`
"""
pSort                     = Proc(desc = 'Sort file.')
pSort.input               = "infile:file"
pSort.output              = "outfile:file:{{i.infile | bn}}"
pSort.args.params         = Box()
pSort.args.inopts         = Box(skip = 0, delimit = '\t', comment = '#')
pSort.args.case           = True
pSort.args.mem            = params.mem4G.value
pSort.args.tmpdir         = params.tmpdir.value
pSort.args.unique         = False
pSort.args.sorted         = False
pSort.lang                = params.python.value
pSort.script              = "file:scripts/common/pSort.py"

"""
@name:
	pFiles2Dir
@description:
	A helper process to convert a list of files into a directory, so that some processes can take it as input
@input:
	`infiles:files`: The input files
@output:
	`outdir:dir`:    The output directory
"""
pFiles2Dir                = Proc(desc = 'Put files to a directory using symbolic links.')
pFiles2Dir.input          = "infiles:files"
pFiles2Dir.output         = "outdir:dir:{{i.infiles | lambda x: sorted(x) | [0] | fn}}.dir"
pFiles2Dir.lang           = params.python.value
pFiles2Dir.script         = "file:scripts/common/pFiles2Dir.py"

"""
@name:
	pFile2Proc
@description:
	Convert a file to a proc so it can be used as dependent
@input:
	`infile:file`: The input file
@output:
	`outfile:file`: The output file
"""
pFile2Proc                = Proc(desc="Convert a file to a proc so it can be used as dependent")
pFile2Proc.input          = "infile:file"
pFile2Proc.output         = "outfile:file:{{i.infile | bn}}"
pFile2Proc.script         = 'ln -s "{{i.infile}}" "{{o.outfile}}"'

"""
@name:
	pStr2File
@description:
	Save string to a file.
@input:
	`in:var`: The input string.
@output:
	`outfile:file`: The output file.
"""
pStr2File                 = Proc(desc = "Save string to a file.")
pStr2File.input           = "instr:var"
pStr2File.output          = "outfile:file:{{i.instr | encode}}.txt"
pStr2File.args.breakOn    = ','
pStr2File.args.trimLine   = True
pStr2File.envs.encode     = lambda x: __import__('re').sub(r'[^\w_]', '', x)[:16]
pStr2File.lang            = params.python.value
pStr2File.script          = "file:scripts/common/pStr2File.py"

"""
@name:
	pHead
@description:
	Get the top N lines from a file
@input:
	`infile:file`: The input file
@output:
	`outfile:file`: The output file
@args:
	`n`: Top n lines. You may use '-n' to skip last n lines.
"""
pHead                     = Proc(desc = "Like linux's head command")
pHead.input               = "infile:file"
pHead.output              = "outfile:file:{{i.infile | fn}}.head.txt"
pHead.args.n              = 10
pHead.script              = 'head -n {{args.n}} {{i.infile | squote}} > {{o.outfile | squote}}'

"""
@name:
	pTail
@description:
	Get the bottom N lines from a file
@input:
	`infile:file`: The input file
@output:
	`outfile:file`: The output file
@args:
	`n`: Bottom n lines. You may use '+n' to skip first n lines.
"""
pTail                     = Proc(desc = "Like linux's tail command")
pTail.input               = "infile:file"
pTail.output              = "outfile:file:{{i.infile | fn}}.tail.txt"
pTail.args.n              = 10
pTail.script              = 'tail -n {{args.n | lambda x: "+"+str(int(x)+1) if x.startswith("+") else x}} {{i.infile | squote}} > {{out.outfile | squote}}'

"""
@name:
	pPrepend
@description:
	Prepend a string to a file
@input:
	`in:var`: The input string.
	`infile:file`: The input file.
@output:
	`outfile:file`: The output file.
"""
pPrepend                  = Proc(desc = "Prepend string to a file.")
pPrepend.input            = "in:var, infile:file"
pPrepend.output           = "outfile:file:{{i.infile | fn2}}.prepend{{i.infile | ext}}"
pPrepend.script           = '''
printf {{i.in | squote}} > {{out.outfile | squote}}
cat {{i.infile | squote}} >> {{out.outfile | squote}}
'''

pAppend                   = Proc(desc = "Append string to a file")
pAppend.input             = "in:var, infile:file"
pAppend.output            = "outfile:file:{{i.infile | fn2}}.append{{i.infile | ext}}"
pAppend.script            = 'cat {{i.infile | squote}} > {{out.outfile | squote}}; printf {{i.in | squote}} >> {{out.outfile | squote}}'

"""
@name:
	pUnique
@description:
	Make the input file with unique rows (at certain column)
@input:
	`infile:file`: The input file.
@output:
	`outfile:file`: The output file.
@args:
	`inopts`: The options for input file
		- `delimit`: delimit for columns 
		- `skip`: skip first lines
		- `comment`: signs for treating lines as comments
	`outopts`: The output options
		- `head`: Output head or not. Default: `False`
		- `headPrefix`: The prefix for the head
		- `headDelimit`: The delimit for the head
		- `headTransform`: The transform function for the head
		- `delimit`: The delimit for the data.
	`col`: The column to compare. Default: `*` (all columns)
	`sorted`: Whether the input file is sorted. Default: `False`
"""
pUnique                   = Proc(desc = "Make the input file unique")
pUnique.input             = "infile:file"
pUnique.output            = "outfile:file:{{i.infile | fn2}}.unique{{i.infile | ext}}"
pUnique.args.inopts       = Box(delimit = "\t", skip = 0, comment = "#")
pUnique.args.outopts      = Box(head = False, headPrefix = '', headDelimit = '\t', headTransform = None, delimit = '\t')
pUnique.args.col          = '*'
pUnique.args.sorted       = False
pUnique.lang              = params.python.value
pUnique.script            = "file:scripts/common/pUnique.py"

"""
@name:
	pAddHeader
@description:
	Add the header of 1st file to 2nd file.
@input:
	`infile1:file`: The first file containing the header.
	`infile2:file`: The second file with the body.
@output:
	`outfile:file`: The output file with the header from 1st input file, body from 2nd file.
@args:
	`n`: The number of header lines.
"""
pAddHeader                = Proc(desc = 'Add the header of 1st file to 2nd file.')
pAddHeader.input          = "infile1:file, infile2:file"
pAddHeader.output         = "outfile:file:{{i.infile2 | bn}}"
pAddHeader.args.n         = 1
pAddHeader.script         = '''
head -n {{args.n}} {{i.infile1 | squote}} > {{out.outfile | squote}}
cat {{i.infile2 | squote}} >> {{out.outfile | squote}}
'''

"""
@name:
	pMergeFiles
@description:
	Merge files.
@input:
	`infiles:files`: The input files
@output:
	`outfile:file`: The output file
@args:
	`header`: Whether the input files have header. Default: `False`
		- If `True`, input files must have the same header line.
"""
pMergeFiles              = Proc(desc = 'Merge files.')
pMergeFiles.input        = "infiles:files"
pMergeFiles.output       = "outfile:file:{{i.infiles | fs2name}}{{i.infiles | :a[0] if a else '' | ext }}"
pMergeFiles.args.header  = False
pMergeFiles.envs.fs2name = fs2name
pMergeFiles.lang         = params.python.value
pMergeFiles.script       = "file:scripts/common/pMergeFiles.py"

pGrep              = Proc(desc = 'Filter a file using linux grep')
pGrep.input        = 'infile:file'
pGrep.output       = 'outfile:file:{{i.infile | bn}}'
pGrep.args.params  = Box()
pGrep.args.keyword = ''
pGrep.lang         = params.python.value
pGrep.script       = "file:scripts/common/pGrep.py"

"""
@name:
	pSplitRows
@description:
	Split a file by rows, specially usefull to split a job into multithreads/multiprocesses.
@input:
	`infile:file`: The input file
@output:
	`outdir:dir`: The output directory including the split files
@args:
	`skip`: The skip first n lines. Default: `0`
	`cnames`: The column names. If True, the column names will be added to each split file. Default: `True`
	`n`: Number of files to split. Default: `8`
"""
pSplitRows                = Proc(desc = 'Split a file by rows.')
pSplitRows.input          = 'infile:file'
pSplitRows.output         = 'outdir:dir:{{i.infile | bn}}.rows'
pSplitRows.args.skip      = 0
pSplitRows.args.cnames    = True
pSplitRows.args.n         = 8
pSplitRows.lang           = params.python.value
pSplitRows.script         = "file:scripts/common/pSplitRows.py"

