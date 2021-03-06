# Analysis of expression data from RNA-seq
from os import path
from glob import glob
from pyppl import Proc, Box
from . import params, rimport
from .utils import dirpat2name, fs2name

"""
@name:
	pExprDir2Matrix
@description:
	Convert expression files to expression matrix
	File names will be used as sample names (colnames)
	Each gene and its expression per line.
	Suppose each expression file has the same rownames and in the same order.
@input:
	`indir:file`:  the directory containing the expression files, could be gzipped
@output:
	`outfile:file`: the expression matrix file
	`outdir:dir`:   the directory containing expr file and plots
@args:
	`pattern` : The pattern to filter files. Default `'*'`
	`namefunc`: Transform filename (no extension) as column name. Default: "function(fn) fn"
	`header`  : Whether each expression file contains header. Default: `False`
	`exrows`  : Rows to be excluded, regular expression applied. Default: `["^Sample", "^Composite", "^__"]`
	`boxplot` : Whether to plot a boxplot. Default: False
	`heatmap` : Whether to plot a heatmap. Default: False
	`histplot`: Whether to plot a histgram. Default: False
	`devpars` : Parameters for png. Default: `{'res': 300, 'width': 2000, 'height': 2000}`
	`boxplotggs`: The ggplot parameters for boxplot. Default: `['r:ylab("Expression")']`
		- See ggplot2 documentation.
	`heatmapggs`: The ggplot parameters for heatmap. Default: `['r:theme(axis.text.y = element_blank())']`
	`histplotggs`: The ggplot parameters for histgram. Default: `['r:labs(x = "Expression", y = "# Samples")']`
"""
pExprDir2Matrix        = Proc(desc = 'Merge expression files to a matrix.')
pExprDir2Matrix.input  = "indir:file"
pExprDir2Matrix.output = [
	"outfile:file:{{i.indir, args.pattern | dirpat2name}}.dir/{{i.indir, args.pattern | dirpat2name}}.expr.txt",
	"outdir:dir:{{i.indir, args.pattern | dirpat2name}}.dir"
]
pExprDir2Matrix.lang           = params.Rscript.value
pExprDir2Matrix.args.pattern   = '*'
pExprDir2Matrix.args.fn2sample = 'function(fn) fn'
pExprDir2Matrix.args.exrows    = ["^Sample", "^Composite", "^__"]
pExprDir2Matrix.args.hmrows    = 500
pExprDir2Matrix.args.plot = Box(
	boxplot = False,
	heatmap = False,
	histogram = False
)
pExprDir2Matrix.args.ggs = Box(
	boxplot = Box(ylab = {0: "Expression"}),
	heatmap = Box(theme = {'axis.text.y': 'r:element_blank()'}),
	histogram = Box(labs = {'x': 'Expression', 'y': '# Genes'})
)
pExprDir2Matrix.envs.dirpat2name = dirpat2name
pExprDir2Matrix.envs.rimport = rimport
pExprDir2Matrix.args.devpars = Box(res = 300, width = 2000, height = 2000)
pExprDir2Matrix.script       = "file:scripts/rnaseq/pExprDir2Matrix.r"

"""
@name:
	pExprFiles2Mat
@description:
	Merge expression to a matrix from single samples.
@input:
	`infiles:files`: The expression file from single samples, typically with 2 columns: gene and expression value
@output:
	`outfile:file`: the expression matrix file
@args:
	`fn2sample`: Transform filename (no extension) as column name. Default: "function(fn) fn"
	`inopts`   : Options to read input files. Default: `Box(rname = True, cnames = True)`
"""
pExprFiles2Mat                = Proc(desc = 'Merge expression to a matrix from single samples.')
pExprFiles2Mat.input          = 'infiles:files'
pExprFiles2Mat.output         = 'outfile:file:{{i.infiles | fs2name}}.expr.txt'
pExprFiles2Mat.args.inopts    = Box(cnames = True, rnames = True)
pExprFiles2Mat.args.fn2sample = 'function(fn) fn'
pExprFiles2Mat.envs.fs2name   = fs2name
pExprFiles2Mat.envs.rimport   = rimport
pExprFiles2Mat.lang           = params.Rscript.value
pExprFiles2Mat.script         = "file:scripts/rnaseq/pExprFiles2Mat.r"

"""
@name:
	pExprStats
@description:
	Plot the expression out.
@input:
	`infile:file`: The expression matrix (rows are genes and columns are samples).
	`gfile:file` : The sample information file. Determines whether to do subgroup stats or not.
		- If not provided, not do for all samples
@output:
	`outdir:dir`: The directory containing the plots
		- If `args.filter` is given, a filtered expression matrix will be generated in `outdir`.
@args:
	`inopts`: Options to read `infile`. Default: `Box(cnames = True, rnames = True)`
	`tsform`: An R function in string to transform the expression matrix (i.e take log).
	`filter`: An R function in string to filter the expression data.
	`plot`  : Which plot to do? Default: `Box(boxplot = True, histogram = True, qqplot = True)`
	`ggs`   : The ggs for each plot. Default:
		- `boxplot   = Box(ylab = {0: "Expression"})`,
		- `histogram = Box(labs = {'x': 'Expression', 'y': '# Genes'})`,
		- `qqplot    = Box()`
	`params` : The params for each ggplot function.
	`devpars`: Parameters for png. Default: `{'res': 300, 'width': 2000, 'height': 2000}`
"""
pExprStats             = Proc(desc = 'Plot the expression values out.')
pExprStats.input       = 'infile:file, gfile:file'
pExprStats.output      = 'outdir:dir:{{i.infile | fn2}}.plots'
pExprStats.args.inopts = Box(cnames = True, rnames = True)
pExprStats.args.tsform = None
pExprStats.args.filter = None
pExprStats.args.plot   = Box(boxplot = True, histogram = True, qqplot = True)
pExprStats.args.ggs    = Box(
	boxplot   = Box(ylab = {0: "Expression"}),
	histogram = Box(labs = {'x': 'Expression', 'y': '# Genes'}),
	qqplot    = Box()
)
pExprStats.args.params   = Box(
	boxplot   = Box(),
	histogram = Box(),
	qqplot    = Box()
)
pExprStats.args.devpars = Box(res = 300, width = 2000, height = 2000)
pExprStats.envs.rimport = rimport
pExprStats.lang         = params.Rscript.value
pExprStats.script       = "file:scripts/rnaseq/pExprStats.r"

"""
@name:
	pBatchEffect
@description:
	Remove batch effect with sva-combat.
@input:
	`expr:file`:  The expression file, generated by pExprDir2Matrix
	`batch:file`: The batch file defines samples and batches.
@output:
	`outfile:file`: the expression matrix file
	`outdir:dir`:   the directory containing expr file and plots
@args:
	`tool`    : The tool used to remove batch effect. Default `'combat'`
	`hmrows`  : How many rows to be used to plot heatmap
	`plot`: Whether to plot
		- `boxplot`   : Whether to plot a boxplot. Default: False
		- `heatmap`   : Whether to plot a heatmap. Default: False
		- `histogram` : Whether to plot a histgram. Default: False
	`devpars`    : Parameters for png. Default: `{'res': 300, 'width': 2000, 'height': 2000}`
	`ggs`: The ggplot parameters
		- `boxplot`  : The ggplot parameters for boxplot. Default: `Box(ylab = {0: "Log2 Intensity"})`
		- `heatmap`  : The ggplot parameters for heatmap. Default: `Box(theme = {'axis.text.y': 'r:element_blank()'})`
		- `histogram`: The ggplot parameters for histgram. Default: `Box(labs = {'x': "Log2 Intensity", "y": "Density"})`
"""
pBatchEffect              = Proc(desc = 'Try to remove batch effect of expression data.')
pBatchEffect.input        = "expr:file, batch:file"
pBatchEffect.output       = "outfile:file:{{i.expr | fn2}}/{{i.expr | fn2}}.expr.txt, outdir:dir:{{i.expr | fn2}}"
pBatchEffect.args.tool    = 'combat'
pBatchEffect.args.plot    = Box(boxplot = False, heatmap = False, histogram = False)
pBatchEffect.args.hmrows  = 500
pBatchEffect.args.devpars = Box(res = 300, width = 2000, height = 2000)
pBatchEffect.args.ggs     = Box(
	boxplot   = Box(ylab = {0: "Expression"}),
	heatmap   = Box(theme = {'axis.text.y': 'r:element_blank()'}),
	histogram = Box(labs  = {'x': "Expression", "y": "Frequency"})
)
pBatchEffect.envs.rimport = rimport
pBatchEffect.lang   = params.Rscript.value
pBatchEffect.script = "file:scripts/rnaseq/pBatchEffect.r"

"""
@name:
	pUnitConversion
@description:
	Convert expression between units  
	See here: https://haroldpimentel.wordpress.com/2014/05/08/what-the-fpkm-a-review-rna-seq-expression-units/ and  
	https://docs.gdc.cancer.gov/Data/Bioinformatics_Pipelines/Expression_mRNA_Pipeline/#fpkm  
	Available converstions:
	- `count -> cpm, fpkm/rpkm, fpkm-uq/rpkm-rq, tpm, tmm`
	- `fpkm/rpkm -> count, tpm, cpm`
	- `tpm -> count, fpkm/rpkm, cpm`
	- `cpm -> count, fpkm/rpkm, tpm`
	NOTE that during some conversions, `sum(counts/effLen)` is approximated to `sum(counts)/sum(effLen) * length(effLen))`
@input:
	`infile:file`: the expression matrix
		- rows are genes, columns are samples
@output:
	`outfile:file`: the converted expression matrix
@args:
	`inunit`:    The unit of input expression values. Default: `count`
	`outunit`:   The unit of output expression values. Default: `tpm`
	`meanfl`:    A file containing the mean fragment length for each sample by rows, without header.
		- Or a fixed universal estimated number. Default: `1` (used by TCGA)
	`nreads`:    The estimatied total number of reads for each sample. Default: `30000000`
		- Or you can pass a file with the number for each sample by rows, without header.
		- In converting `fpkm/rpkm -> count`: it should be total reads of that sample
		- In converting `cpm -> count`: it should be total reads of that sample
		- In converting `tpm -> count`: it should be total reads of that sample
		- In converting `tpm -> cpm`: it should be total reads of that sample
		- In converting `tpm -> fpkm/rpkm`: it should be `sum(fpkm)` of that sample
	`inform`:    Transform the input to the unit specified. (sometimes the values are log transformed)
		- For example, if the `inunit` is `tpm`, but it's actually `log2(expr+1)` transformed,
		- Then this should be `function(expr) 2^(expr - 1)`.
		- Default: `None` (No transformation has been done)
	`outform`:   Transform to be done on the output expression values. Default: `None`
	`refexon`:   the exome gff file, for RPKM/FPKM
		- `gene_id` is required for gene names
@requires:
	[edgeR](https://bioconductor.org/packages/release/bioc/html/edger.html) if cpm or rpkm is chosen
	[coseq](https://rdrr.io/rforge/coseq/man/transform_RNAseq.html) if tmm is chosen
"""
pUnitConversion              = Proc(desc = 'Convert raw counts to another unit.')
pUnitConversion.input        = "infile:file"
pUnitConversion.output       = "outfile:file:{{i.infile | fn2}}.{{args.outunit}}{{args.outform | lambda x: '_t' if x else ''}}.txt"
pUnitConversion.args.inunit  = 'count'
pUnitConversion.args.outunit = 'tpm'
pUnitConversion.args.meanfl  = 1
pUnitConversion.args.nreads  = 30000000
pUnitConversion.args.refexon = params.refexon.value
pUnitConversion.args.inform  = None
pUnitConversion.args.outform = None
pUnitConversion.envs.rimport = rimport
pUnitConversion.lang         = params.Rscript.value
pUnitConversion.script       = "file:scripts/rnaseq/pUnitConversion.r"

"""
@name:
	pRNASeqDEG
@description:
	Detect DEGs for RNA-seq data
@input:
	`efile:file`: The expression matrix
	`gfile:file`: The group information
		- Like:
		```
		Sample	[Patient	]Group
		sample1	[patient1	]group1
		sample2	[patient1	]group1
		sample3	[patient2	]group1
		sample4	[patient2	]group2
		sample5	[patient3	]group2
		sample6	[patient3	]group2
		```
@output:
	`outfile:file`: The DEG list
	`outdir:file`:  The output directory containing deg list and plots
@args:
	`tool`  : The tool used to detect DEGs. Default: 'deseq2' (edger is also available).
	`inopts`: Options to read `infile`. Default: `Box(cnames = True, rnames = True)`
	`cutoff`: The cutoff used to filter the results. Default: `0.05`
		- `0.05` implies `{"by": "p", "value": "0.05", "sign": "<"}`
	`plot`  : The plots to do. Default: 
		- `mdsplot`: True, MDS plot
		- `volplot`: True, volcano plot
		- `maplot `: True, MA plot
		- `heatmap`: True, heatmap for DEGs
		- `qqplot `: True, The QQplot for pvalues
	`ggs`   : The ggs for each plot. Default:
		- `heatmap`: `Box(theme = {'axis.text.y': 'r:element_blank()'})`
		- Not available for `mdsplot`.
		- Others are empty `Box()`s
	`params`: Parameters for each plot. Default: 
		- `volplot`: `Box(pcut = 0.05, fccut = 2)`
		- `maplot` : `Box(pcut = 0.05)`
	`devpars`: Parameters for png. Default: `{'res': 300, 'width': 2000, 'height': 2000}`
	`mapfile`: Probe to gene mapping file. If not provided, assume genes are used as rownames.
"""
pRNASeqDEG        = Proc(desc = 'Detect DEGs by RNA-seq data.')
pRNASeqDEG.input  = "efile:file, gfile:file"
pRNASeqDEG.output = [
	"outfile:file:{{i.efile | fn2}}-{{i.gfile | fn2}}.DEGs/{{i.efile | fn2}}-{{i.gfile | fn2}}.degs.txt",
	"outdir:dir:{{i.efile | fn2}}-{{i.gfile | fn2}}.DEGs"
]
pRNASeqDEG.args.tool    = 'deseq2' # edger
pRNASeqDEG.args.inopts  = Box(cnames = True, rnames = True)
pRNASeqDEG.args.mapfile = ""
pRNASeqDEG.args.cutoff  = 0.05
pRNASeqDEG.args.plot    = Box(
	mdsplot = True,
	volplot = True,
	maplot  = True,
	heatmap = True,
	qqplot  = True
)
pRNASeqDEG.args.ggs = Box(
	maplot  = Box(),
	heatmap = Box(theme = {'axis.text.y': 'r:element_blank()'}),
	volplot = Box(),
	qqplot  = Box(labs = {'x': 'Expected(-log10(p-value))', 'y': 'Observed(-log10(p-value))'})
)
pRNASeqDEG.args.params = Box(
	volplot = Box(fccut = 2),
	maplot  = Box()
)
pRNASeqDEG.args.devpars = Box(res = 300, width = 2000, height = 2000)
pRNASeqDEG.envs.rimport = rimport
pRNASeqDEG.lang         = params.Rscript.value
pRNASeqDEG.script       = "file:scripts/rnaseq/pRNASeqDEG.r"

"""
@name:
	pCoexp
@description:
	Get co-expression of gene pairs in the expression matrix.
"""
pCoexp             = Proc(desc = "Get co-expression of gene pairs in the expression matrix.")
pCoexp.input       = "infile:file"
pCoexp.output      = "outfile:file:{{i.infile | fn}}.coexp, outpval:file:{{i.infile | fn}}.pval"
pCoexp.args.method = 'pearson'
pCoexp.args.pval   = False
pCoexp.lang        = params.Rscript.value
pCoexp.script      = "file:scripts/rnaseq/pCoexp.r"
