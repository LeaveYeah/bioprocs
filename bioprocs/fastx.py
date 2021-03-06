"""
A set of processes to generate/process fastq/fasta files
"""

from os import path
from pyppl import Proc, Box
from . import params, bashimport

def _getFastqFn(fastq):
	ret = path.basename(fastq)
	if ret.endswith('.gz')   : ret = ret[:-3]
	if ret.endswith('.fastq'): ret = ret[:-6]
	if ret.endswith('.fq')   : ret = ret[:-3]
	if ret.endswith('.clean'): ret = ret[:-6]
	if ret.endswith('_clean'): ret = ret[:-6]
	return ret

def _getCommonName(f1, f2):
	ret = path.basename(path.commonprefix([f1, f2]))
	while not ret[-1].isalnum(): ret = ret[:-1]
	return ret

"""
@name:
	pFastq2Expr
@description:
	Use Kallisto to get gene expression from pair-end fastq files.
@input:
	`fqfile1:file`: The fastq file1.
	`fqfile2:file`: The fastq file2.
@output:
	`outfile:file`: The expression file
	`outdir:dir`  : Output direcotry with expression and other output files
@args:
	`params`  : Other parameters for `kallisto quant`. Default: `Box()`
	`idxfile` : The kallisto index file. Default: `params.kallistoIdx`
	`kallisto`: The path to `kallisto`. Default: `params.kallisto`
	`nthread` : # threads to use. Default: `1`
"""
pFastq2Expr        = Proc(desc = 'Use Kallisto to get gene expression from pair-end fastq files.')
pFastq2Expr.input  = "fqfile1:file, fqfile2:file"
pFastq2Expr.output = [
	"outfile:file:{{i.fqfile1, i.fqfile2 | *commonname}}/{{i.fqfile1, i.fqfile2 | *commonname}}.expr.txt",
	"outdir:dir:{{i.fqfile1, i.fqfile2 | *commonname}}"
]
pFastq2Expr.args.params     = Box()
pFastq2Expr.args.idxfile    = params.kallistoIdx.value
pFastq2Expr.args.kallisto   = params.kallisto.value
pFastq2Expr.args.nthread    = 1
pFastq2Expr.envs.commonname = lambda f1, f2, path = __import__('os').path: path.basename(path.commonprefix([f1, f2])).rstrip('_. ,[]')
pFastq2Expr.envs.bashimport = bashimport
pFastq2Expr.preCmd          = """
{{bashimport}} reference.bash
reference kallisto {{args.idxfile | squote}}
"""
pFastq2Expr.lang   = params.python.value
pFastq2Expr.script = "file:scripts/fastx/pFastq2Expr.py"

"""
@name:
	pFastqSim
@description:
	Simulate reads
@input:
	`seed`: The seed to generate simulation file
		- None: use current timestamp.
@output:
	`fq1:file`: The first pair read file
	`fq2:file`: The second pair read file
@args:
	`tool`:  The tool used for simulation. Default: wgsim (dwgsim)
	`len1`:  The length of first pair read. Default: 100
	`len2`:  The length of second pair read. Default: 100
	`num`:   The number of read PAIRs. Default: 1000000
	`gz`:    Whether generate gzipped read file. Default: True
	`wgsim`: The path of wgsim. Default: wgsim
	`dwgsim`:The path of wgsim. Default: dwgsim
	`ref`:   The reference genome. Required
	`params`:Other params for `tool`. Default: ""
@requires:
	[`wgsim`](https://github.com/lh3/wgsim)
"""
pFastqSim             = Proc(desc = 'Simulate pair-end reads.')
pFastqSim.input       = "seed"
pFastqSim.output      = "fq1:file:read{{i.seed}}_1.fastq{% if args.gz %}.gz{% endif %}, fq2:file:read{{i.seed}}_2.fastq{% if args.gz %}.gz{% endif %}"
pFastqSim.args.tool   = 'wgsim'
pFastqSim.args.wgsim  = params.wgsim.value
pFastqSim.args.dwgsim = params.dwgsim.value
pFastqSim.args.len1   = 100
pFastqSim.args.len2   = 100
pFastqSim.args.num    = 1000000
pFastqSim.args.gz     = False
pFastqSim.args.params = Box()
pFastqSim.args.ref    = params.ref.value
pFastqSim.lang        = params.python.value
pFastqSim.script      = "file:scripts/fastx/pFastqSim.py"

"""
@name:
	pFastQC
@description:
	QC report for fastq file
@input:
	`fq:file`:    The fastq file (also fine with gzipped)
@output:
	`outdir:dir`: The output direcotry
@args:
	`tool`:    The tool used for simulation. Default: fastqc
	`fastqc`:  The path of fastqc. Default: fastqc
	`nthread`: Number of threads to use. Default: 1
	`params`:Other params for `tool`. Default: ""
@requires:
	[`fastqc`](https://www.bioinformatics.babraham.ac.uk/projects/fastqc/)
"""
pFastQC                 = Proc(desc = 'QC report for fastq file.')
pFastQC.input           = "fq:file"
pFastQC.output          = "outdir:dir:{{i.fq | getFastqFn}}.fastqc"
pFastQC.args.tool       = 'fastqc'
pFastQC.args.fastqc     = params.fastqc.value
pFastQC.args.nthread    = 1
pFastQC.args.params     = Box()
pFastQC.lang            = params.python.value
pFastQC.envs.getFastqFn = _getFastqFn
pFastQC.script          = "file:scripts/fastx/pFastQC.py"

"""
@name:
	pFastMC
@description:
	Multi-QC based on pFastQC
@input:
	`qcdir:file`:  The direcotry containing QC files
@output:
	`outdir:dir`: The output direcotry
@args:
	`tool`:    The tool used for simulation. Default: multiqc
	`multiqc`: The path of fastqc. Default: multiqc
	`params`:  Other params for `tool`. Default: ""
@requires:
	[`multiqc`](http://multiqc.info/)
"""
pFastMC              = Proc(desc = 'Multi-QC based on pFastQC.')
pFastMC.input        = "qcdir:file"
pFastMC.output       = "outdir:dir:{{i.qcdir | fn}}.multiqc"
pFastMC.args.tool    = 'multiqc'
pFastMC.args.multiqc = params.multiqc.value
pFastMC.args.params  = Box()
pFastMC.lang         = params.python.value
pFastMC.script       = "file:scripts/fastx/pFastMC.py"

"""
@name:
	pFastqTrim
@description:
	Trim pair-end FASTQ reads
@input:
	`fq1:file`:  The input fastq file
	`fq2:file`:  The input fastq file
@output:
	`outfq1:file`: The trimmed fastq file
	`outfq2:file`: The trimmed fastq file
@args:
	`tool`        : The tools used for trimming. Default: trimmomatic (cutadapt|skewer)
	`cutadapt`    : The path of seqtk. Default: cutadapt
	`skewer`      : The path of fastx toolkit trimmer. Default: skewer
	`trimmomatic` : The path of trimmomatic. Default: trimmomatic
	`params`      : Other params for `tool`. Default: ""
	`nthread`     : Number of threads to be used. Default: 1
	- Not for cutadapt
	`gz`          : Whether gzip output files. Default: True
	`mem`         : The memory to be used. Default: 4G
	- Only for trimmomatic
	`minlen`      : Discard trimmed reads that are shorter than `minlen`. Default: 18
	- For trimmomatic, the number will be `minlen`*2 for MINLEN, as it filters before trimming
	`minq`        : Minimal mean qulity for 4-base window or leading/tailing reads. Default: 3
	`cut5`        : Remove the 5'end reads if they are below qulity. Default: 3
	`cut3`        : Remove the 3'end reads if they are below qulity. Default: 3
	- Not for skewer
	`adapter1`    : The adapter for sequence. Default: AGATCGGAAGAGCACACGTCTGAACTCCAGTCAC
	`adapter2`    : The adapter for pair-end sequence. Default: AGATCGGAAGAGCGTCGTGTAGGGAAAGAGTGTA
@requires:
	[`cutadapt`](http://cutadapt.readthedocs.io/en/stable/guide.html)
	[`skewer`](https://github.com/relipmoc/skewer)
	[`trimmomatic`](https://github.com/timflutre/trimmomatic)
"""
pFastqTrim        = Proc(desc = 'Trim pair-end reads in fastq file.')
pFastqTrim.input  = "fq1:file, fq2:file"
pFastqTrim.output = [
	"outfq1:file:{{i.fq1 | getFastqFn}}.fastq{% if args.gz %}.gz{% endif %}",
	"outfq2:file:{{i.fq2 | getFastqFn}}.fastq{% if args.gz %}.gz{% endif %}"
]
pFastqTrim.lang             = params.python.value
pFastqTrim.args.tool        = 'skewer'
pFastqTrim.args.cutadapt    = params.cutadapt.value
pFastqTrim.args.skewer      = params.skewer.value
pFastqTrim.args.trimmomatic = params.trimmomatic.value
pFastqTrim.args.params      = Box()
pFastqTrim.args.nthread     = 1
pFastqTrim.args.gz          = False
pFastqTrim.args.mem         = params.mem4G.value
pFastqTrim.args.minlen      = 18
pFastqTrim.args.minq        = 3
pFastqTrim.args.cut5        = 3
pFastqTrim.args.cut3        = 3
pFastqTrim.args.adapter1    = 'AGATCGGAAGAGCACACGTCTGAACTCCAGTCAC'
pFastqTrim.args.adapter2    = 'AGATCGGAAGAGCGTCGTGTAGGGAAAGAGTGTA'
pFastqTrim.envs.getFastqFn  = _getFastqFn
pFastqTrim.script           = "file:scripts/fastx/pFastqTrim.py"

"""
@name:
	pFastqSETrim
@description:
	Trim single-end FASTQ reads
@input:
	`fq:file`:  The input fastq file
@output:
	`outfq:file`: The trimmed fastq file
@args:
	`tool`        : The tools used for trimming. Default: trimmomatic (cutadapt|skewer)
	`cutadapt`    : The path of seqtk. Default: cutadapt
	`skewer`      : The path of fastx toolkit trimmer. Default: skewer
	`trimmomatic` : The path of trimmomatic. Default: trimmomatic
	`params`      : Other params for `tool`. Default: ""
	`nthread`     : Number of threads to be used. Default: 1
	- Not for cutadapt
	`gz`          : Whether gzip output files. Default: True
	`mem`         : The memory to be used. Default: 4G
	- Only for trimmomatic
	`minlen`      : Discard trimmed reads that are shorter than `minlen`. Default: 18
	- For trimmomatic, the number will be `minlen`*2 for MINLEN, as it filters before trimming
	`minq`        : Minimal mean qulity for 4-base window or leading/tailing reads. Default: 3
	`cut5`        : Remove the 5'end reads if they are below qulity. Default: 3
	`cut3`        : Remove the 3'end reads if they are below qulity. Default: 3
	- Not for skewer
	`adapter`     : The adapter for sequence. Default: AGATCGGAAGAGCACACGTCTGAACTCCAGTCAC
@requires:
	[`cutadapt`](http://cutadapt.readthedocs.io/en/stable/guide.html)
	[`skewer`](https://github.com/relipmoc/skewer)
	[`trimmomatic`](https://github.com/timflutre/trimmomatic)
"""
pFastqSETrim                  = Proc(desc = 'Trim single-end reads in fastq file.')
pFastqSETrim.input            = "fq:file"
pFastqSETrim.output           = "outfq:file:{{i.fq | getFastqFn }}.fastq{% if args.gz %}.gz{% endif %}"
pFastqSETrim.lang             = params.python.value
pFastqSETrim.args.tool        = 'skewer'
pFastqSETrim.args.cutadapt    = params.cutadapt.value
pFastqSETrim.args.skewer      = params.skewer.value
pFastqSETrim.args.trimmomatic = params.trimmomatic.value
pFastqSETrim.args.params      = Box()
pFastqSETrim.args.nthread     = 1
pFastqSETrim.args.gz          = False
pFastqSETrim.args.mem         = params.mem4G.value
pFastqSETrim.args.minlen      = 18
pFastqSETrim.args.minq        = 3
pFastqSETrim.args.cut5        = 3
pFastqSETrim.args.cut3        = 3
pFastqSETrim.args.adapter     = 'AGATCGGAAGAGCACACGTCTGAACTCCAGTCAC'
pFastqSETrim.envs.getFastqFn  = _getFastqFn
pFastqSETrim.script           = "file:scripts/fastx/pFastqSETrim.py"


"""
@name:
	pFastqSE2Sam
@description:
	Cleaned paired fastq (.fq, .fq.gz, .fastq, .fastq.gz file to mapped sam/bam file
@args:
	`tool`:   The tool used for alignment. Default: bwa (bowtie2|ngm)
	`bwa`:    Path of bwa, default: bwa
	`ngm`:    Path of ngm, default: ngm
	`bowtie2`:Path of bowtie2, default: bowtie2
	`rg`:     The read group. Default: {'id': '', 'pl': 'Illumina', 'pu': 'unit1', 'lb': 'lib1', 'sm': ''}
	- `id` will be parsed from filename with "_LX_" in it if not given
	- `sm` will be parsed from filename
	`ref`:    Path of reference file
	`params`: Other params for tool, default: ''
"""
pFastqSE2Sam                    = Proc(desc = 'Map cleaned single-end fastq file to reference genome.')
pFastqSE2Sam.input              = "fq:file"
pFastqSE2Sam.output             = "outfile:file:{{i.fq | getFastqFn }}.{{args.outfmt}}"
pFastqSE2Sam.args.outfmt        = "sam"
pFastqSE2Sam.args.tool          = 'bwa'
pFastqSE2Sam.args.bwa           = params.bwa.value
pFastqSE2Sam.args.ngm           = params.ngm.value
pFastqSE2Sam.args.star          = params.star.value
pFastqSE2Sam.args.samtools      = params.samtools.value
pFastqSE2Sam.args.bowtie2       = params.bowtie2.value
pFastqSE2Sam.args.bowtie2_build = params.bowtie2.value + '-build'
pFastqSE2Sam.args.rg            = Box(id = '', pl = 'Illumina', pu = 'unit1', lb = 'lib1', sm = '')
pFastqSE2Sam.args.ref           = params.ref.value
pFastqSE2Sam.args.refgene       = params.refgene.value
pFastqSE2Sam.args.nthread       = 1
pFastqSE2Sam.args.params        = Box()
pFastqSE2Sam.envs.getFastqFn    = _getFastqFn
pFastqSE2Sam.lang               = params.python.value
pFastqSE2Sam.script             = "file:scripts/fastx/pFastqSE2Sam.py"

"""
@name:
	pFastq2Sam
@description:
	Cleaned paired fastq (.fq, .fq.gz, .fastq, .fastq.gz file to mapped sam/bam file
@args:
	`tool`   : The tool used for alignment. Default: bwa (bowtie2, ngm, star)
	`bwa`    : Path of bwa, default: bwa
	`ngm`    : Path of ngm, default: ngm
	`star`   : Path of ngm, default: STAR
	`bowtie2`: Path of bowtie2, default: bowtie2
	`rg`:     The read group. Default: {'id': '', 'pl': 'Illumina', 'pu': 'unit1', 'lb': 'lib1', 'sm': ''}
	- `id` will be parsed from filename with "_LX_" in it if not given
	- `sm` will be parsed from filename
	`ref`    : Path of reference file
	`refgene`: The GTF file for STAR to build index. It's not neccessary if index is already been built. Default: ''
	`params` : Other params for tool, default: ''
"""
pFastq2Sam                 = Proc(desc = 'Map cleaned paired fastq file to reference genome.')
pFastq2Sam.input           = "fq1:file, fq2:file"
pFastq2Sam.output          = "outfile:file:{{i.fq1, i.fq2 | path.commonprefix | path.basename | .rstrip: '_. ,[]' }}.sam"
pFastq2Sam.args.tool       = 'bwa'
pFastq2Sam.args.bwa        = params.bwa.value
pFastq2Sam.args.ngm        = params.ngm.value
pFastq2Sam.args.star       = params.star.value
pFastq2Sam.args.samtools   = params.samtools.value
pFastq2Sam.args.bowtie2    = params.bowtie2.value
pFastq2Sam.args.rg         = Box(id = '', pl = 'Illumina', pu = 'unit1', lb = 'lib1', sm = '')
pFastq2Sam.args.ref        = params.ref.value
pFastq2Sam.args.refgene    = params.refgene.value
pFastq2Sam.args.nthread    = 1
pFastq2Sam.args.params     = Box()
pFastq2Sam.envs.path       = path
pFastq2Sam.envs.bashimport = bashimport
pFastq2Sam.preCmd          = """
{{bashimport}} reference.bash
export bwa={{args.bwa | squote}}
export ngm={{args.ngm | squote}}
export star={{args.star | squote}}
export samtools={{args.samtools | squote}}
export bowtie2={{args.bowtie2 | squote}}
export nthread={{args.nthread}}
export refgene={{args.refgene | squote}}
reference {{args.tool | squote}} {{args.ref | squote}}
"""
pFastq2Sam.lang               = 'python'
pFastq2Sam.script             = "file:scripts/fastx/pFastq2Sam.py"
