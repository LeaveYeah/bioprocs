#!/usr/bin/env python
# Call mutations from sequencing data.
from os import path
from pyppl import PyPPL, Channel, Box
from bioprocs import params
from bioprocs.common import pFiles2Dir
from bioprocs.sambam import pBam2Gmut, pBamPair2Smut
from bioprocs.utils.tsvio import TsvReader
from bioaggrs.wxs import aEBam2Bam, aFastq2Bam, aBam2Mut

params.prefix('-')
params.intype         = 'bam' # ebam, fastq
params.intype.desc    = 'The input file types. Either bam, ebam or fastq.\nEbam means the bam files need to reformatted into fastq files.'
params.muts           = ['germ'] # or ['germ', 'soma'] cnv will be supported later
params.muts.desc      = 'What kind of mutations to call.\nNote: soma need paired information'
params.indir.required = True
params.indir.desc     = 'The input directory containing input files.'
params.saminfo.required = True
params.saminfo.desc = """The sample information file:
Column 1: the basename of the sample file in '-indir'
Column 2: Group if '-muts' includes 'soma', basically, 'TUMOR' and 'NORMAL'
Column 3: Patient if multiple samples belong to the same patient.
Example:
Sample	Group	Patient
A1.bam	TUMOR	A
A2.bam	NORMAL	A
B1.bam	TUMOR	A
B2.bam	NORMAL	A
"""

params.exdir.required = True
params.exdir.desc     = 'Where to export the result files.'
params.runner         = 'local'
params.runner.desc    = 'The runner to run the processes.'
params.forks          = 1
params.forks.desc     = 'How many jobs to run simultanuously.'
params.logfile        = ''
params.logfile.desc   = 'Where to save the logs.'
params.compress = True
params.compress.desc = 'Use gzip and bam file to save space.'

params = params.parse().toDict()

starts = []

reader  = TsvReader(params.saminfo, ftype = 'head')
samples = {r.Sample for r in reader}

aEBam2Bam.pFastq2Sam.args.tool    = 'bowtie2'

pBamDir         = pFiles2Dir
pBamDir.runner  = 'local'
if params.intype == 'ebam':
	#aEBam2Bam.input = [Channel.fromPattern(path.join(params.indir, '*.bam'))]
	aEBam2Bam.input = [[path.join(params.indir, sample) for sample in samples]]
	if params.compress:
		aEBam2Bam.args.gz = True
		aEBam2Bam.pFastq2Sam.args.outfmt = 'bam'

	pBamDir.depends = aEBam2Bam
	pBamDir.input   = lambda ch: [ch.flatten(0)]

	starts.append(aEBam2Bam)

elif params.intype == 'fastq':
	# *.fq, *.fq.gz *.fastq, *.fastq.gz
	# TODO: fix the input files with samples
	aFastq2Bam.input = [Channel.fromPairs(path.join(params.indir, '*.f*q*'))]

	pBamDir.depends = aEBam2Bam
	pBamDir.input   = lambda ch: [ch.flatten(0)]

	starts.append(aFastq2Bam)
else:
	# TODO: fix the input files with samples
	pBamDir.input = Channel.fromPattern(path.join(params.indir, '*.bam'))
	starts.append(pBamDir)

if 'germ' in params.muts and 'soma' in params.muts:
	aBam2Mut.pBamDir.depends     = pBamDir
	aBam2Mut.pSampleInfo.input   = [params.saminfo]
	aBam2Mut.pBam2Gmut.exdir     = path.join(params.exdir, 'germline')
	aBam2Mut.pBamPair2Smut.exdir = path.join(params.exdir, 'somatic')
	starts.append(aBam2Mut)
elif 'germ' in params.muts:
	pBam2Gmut.depends = pBamDir
	pBam2Gmut.input   = lambda ch: ch.expand(0, "*.bam")
elif 'soma' in params.muts:
	pBamPair2Smut.depends = pBamDir
	pBamPair2Smut.input = lambda ch1: [ \
		(path.join(ch1.get(), c1.get()), path.join(ch1.get(), c2.get())) for ch in \
		[Channel.fromFile(params.saminfo, header=True)] for p in \
		set(ch.Patient.flatten()) for c1, c2 in \
		[
			(Channel.fromChannels(ch.colAt(0), ch.Patient, ch.Group).filter(lambda x: x[1] == p and any([k in x[2].upper() for k in ['TUMOR', 'DISEASE', 'AFTER']])),
			Channel.fromChannels(ch.colAt(0), ch.Patient, ch.Group).filter(lambda x: x[1] == p and any([k in x[2].upper() for k in ['NORMAL', 'HEALTH', 'BEFORE', 'BLOOD']])))
		]
	]

PyPPL(Box(
	proc = Box(
		forks = params.forks
	),
	log = Box(
		file = params.logfile
	)
)).start(starts).run(params.runner)