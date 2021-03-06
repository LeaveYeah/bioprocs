from pyppl import Proc, Box
from . import params

pDegree             = Proc(desc = 'List the degree of nodes, order descendingly.')
pDegree.input       = 'infile:file'
pDegree.output      = 'outfile:file:{{i.infile | fn2}}.degree.txt'
pDegree.args.inopts = Box()
pDegree.args.infmt  = 'pair-complete' # matrix
pDegree.args.cutoff = 0
pDegree.lang        = params.python.value
pDegree.script      = "file:scripts/network/pDegree.py"

