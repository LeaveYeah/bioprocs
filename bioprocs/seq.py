from pyppl import Proc
from .utils import runcmd, helpers, genenorm
from . import params

"""
@name:
	pConsvPerm
@description:
	Generate a null distribution of conservation scores.
@input:
	`seed`: The seed to generate the random regions. Default: None 
@output:
	`outfile:file`: A file with mean conservation scores sorted descendingly.
@args:
	`len`: The length of a random region. Default: 50
	`nperm`: Number of permutations. Default: 1000
	`gsize`: The chrom size file.
	`bedtools`: The path of bedtools.
	`bwtool`: The path of bwtool.
	`consvdir`: The directory containing bigwig files of conservation scores
		- The bigwig file should start with chr name: chrN.*
@requires:
	[bwtool](https://github.com/CRG-Barcelona/bwtool)
	[bedtools](http://bedtools.readthedocs.io/en/latest/content/bedtools-suite.html)
"""
pConsvPerm                     = Proc(desc = 'Generate a null distribution of conservation scores.')
pConsvPerm.input               = 'seed'
pConsvPerm.output              = 'outfile:file:consv-len{{args.len}}-nperm{{args.nperm}}-{{in.seed}}.txt'
pConsvPerm.args.len            = 50
pConsvPerm.args.nperm          = 1000
pConsvPerm.args.consvdir       = params.consvdir.value
pConsvPerm.args.gsize          = params.gsize.value
pConsvPerm.args.bedtools       = params.bedtools.value
pConsvPerm.args.bwtool         = params.bwtool.value
pConsvPerm.args.seed           = None
pConsvPerm.envs.runcmd         = runcmd.py
pConsvPerm.envs.params2CmdArgs = helpers.params2CmdArgs.py
pConsvPerm.lang                = params.python.value
pConsvPerm.script              = "file:scripts/seq/pConsvPerm.py"


"""
@name:
	pConsv
@description:
	Get the conservation scores of regions.
	It uses wigFix to find the conservation scores.
	But first you have to convert those wigFix.gz files to bigWig files using ucsc-wigToBigWig
@input:
	`bedfile:file`: The bedfile with regions in the same chromosome
	`permfile:file`:The permutaiton file generated by `pConsvPerm`, used to calculate p-values
@output:
	`outfile:file`: The output file
@args:
	`consvdir`:   The bigwig directory, the bigwig files must be named as "chrN.*.bw"
		- For example: `chr1.phyloP30way.bw`
	`bwtool`:   The path of bwtool executable. Default: `bwtool`
	`bedtools`: The path of bedtools executable. Default: `bedtools`
	`pval`:     Whether calculate pvalue of each region. Default: False
		- In this case, the `in.permfile` can be ignored.
@requires:
	[bwtool](https://github.com/CRG-Barcelona/bwtool)
	[bedtools](http://bedtools.readthedocs.io/en/latest/content/bedtools-suite.html)
"""
pConsv                = Proc(desc = 'Get the conservation scores of regions.')
pConsv.input          = "bedfile:file, permfile:file"
pConsv.output         = "outfile:file:{{in.bedfile | fn}}-consv.bed"
pConsv.args.bwtool    = params.bwtool.value
pConsv.args.consvdir  = params.consvdir.value
pConsv.args.pval      = False
pConsv.envs.runcmd    = runcmd.py
pConsv.lang           = params.python.value
pConsv.script         = "file:scripts/seq/pConsv.py"


"""
@name:
	pPromoters
@description:
	Get the promoter regions in bed format of a gene list give in infile.
@input:
	`infile:file`: the gene list file
@output:
	`outfile:file`: the bed file containing the promoter region
@args:
	`up`: the upstream to the tss, default: 2000
	`down`: the downstream to the tss, default: 2000
	`genome`: the genome, default: hg19
@require:
	[python-mygene](http://mygene.info/)
"""
pPromoters               = Proc(desc = 'Get the promoter regions in bed format of a gene list give in infile.')
pPromoters.input         = "infile:file"
pPromoters.output        = "outfile:file:{{in.infile | fn}}-promoters.bed"
pPromoters.args.up       = 2000
pPromoters.args.down     = 2000
pPromoters.errhow        = 'retry'
pPromoters.args.notfound = 'skip' # error
pPromoters.args.header   = False
pPromoters.args.skip     = 0
pPromoters.args.comment  = '#'
pPromoters.args.delimit  = '\t'
pPromoters.args.col      = 0
pPromoters.args.frm      = 'symbol, alias'
pPromoters.args.tmpdir   = params.tmpdir.value
pPromoters.args.genome   = params.genome.value
pPromoters.envs.genenorm = genenorm.py
pPromoters.lang          = params.python.value
pPromoters.script        = "file:scripts/seq/pPromoters.py"
