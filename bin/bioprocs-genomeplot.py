#!/usr/bin/env python
# Plot genomic elements.
import json, sys
from os import path
from pyppl import PyPPL, utils, Box
from bioprocs import params
from bioprocs.genomeplot import pInteractionTrack, pAnnoTrack, pDataTrack, pUcscTrack, pGenomePlot

#params.prefix('-')

params.ideo       = 'True'
params.ideo.desc  = 'Show ideogram track?'
params.genes      = params.refgene.value
params.genes.desc = 'Show gene track?'
params.axis       = True
params.axis.desc  = 'Show axis?'

params.genome.show     = True
params.outdir.required = True
params.outdir.desc     = 'Output directory.'

params.region.required = True
params.region.desc     = 'The region to plot. E.g. chr1:1000000-1200000'
params.tracks.required = True
params.tracks.type     = list
params.tracks.desc     = 'The track types. Could be data, anno, interaction or ucsc, or multiple of them.'
params.names.required  = True
params.names.type      = list
params.names.desc      = 'The corresponding names of the tracks.'
params.inputs.required = True
params.inputs.type     = list
params.inputs.desc     = 'The input of the tracks.\n"<ucscTrack>:<gvizTrack>" for ucsc track;\n"<infile>:<intype>" for interaction tracks;\nfiles for other tracks.'
params.params.type     = list
params.params.desc     = 'The params for each track'
params.plotparams.desc = 'The params for pGenomePlot.'
params.devpars         = '{"res": 300, "height": 300, "width": 2000}'
params.devpars.desc    = 'The device parameters for plotting.'
params.splitlen        = 5000000
params.splitlen.desc   = 'Split the plot into 2 if the region is longer then splitlen.'
params.forks           = 2
params.forks.desc      = 'Number of cores used to plot if split.'

# highlist
params.highlights      = []
params.highlights.desc = 'The highlight regions in format of "start-end"'

params = params.parse()

chrom, startend  = params.region.split(':')
start, end       = startend.split('-')
start      = int(start)
end        = int(end)
trackProcs = []
#uuid       = utils.uid(str(sys.argv))
for i, tt in enumerate(params.tracks):
	if tt == 'data':
		datatrackproc = pDataTrack.copy(tag = params.names[i])
		datatrackproc.input = (params.names[i], params.inputs[i], chrom)
		if params.params:
			datatrackproc.args.params.update(json.loads(params.params[i]))
		trackProcs.append(datatrackproc)
	elif tt == 'anno':
		annotrackproc = pAnnoTrack.copy(tag = params.names[i])
		annotrackproc.input = (params.names[i], params.inputs[i], chrom)
		if params.params:
			annotrackproc.args.params.update(json.loads(params.params[i]))
		trackProcs.append(annotrackproc)
	elif tt == 'ucsc':
		ucsctrackproc = pUcscTrack.copy(tag = params.names[i])
		ucsctrack, gviztrack = params.inputs[i].split(':')
		ucsctrackproc.input = (params.names[i], ucsctrack, gviztrack, params.region)
		if params.params:
			ucsctrackproc.args.params.update(json.loads(params.params[i]))
		trackProcs.append(ucsctrackproc)
	else:
		intertrackproc = pInteractionTrack.copy(tag = params.names[i])
		infile, intype = params.inputs[i].split(':')
		intertrackproc.input = (params.names[i], infile, params.region)
		intertrackproc.args.intype = intype
		if params.params:
			intertrackproc.args.params.update(json.loads(params.params[i]))
		trackProcs.append(intertrackproc)

if end - start > params.splitlen:
	pGenomePlot.depends        = trackProcs
	#pGenomePlot.tag            = uuid
	pGenomePlot.forks          = params.forks
	pGenomePlot.exdir          = params.outdir
	pGenomePlot.args.ideoTrack = params.ideo
	pGenomePlot.args.axisTrack = params.axis
	pGenomePlot.args.geneTrack = params.genes
	if params.devpars:
		pGenomePlot.args.devpars.update(json.loads(params.devpars))
	if params.plotparams:
		pGenomePlot.args.params.update(json.loads(params.plotparams))
	if len(params.highlights) == 2 and '-' not in params.highlist[0]:
		h1 = params.highlights[0]
		h2 = params.highlights[1]
	else:
		h1 = ';'.join(params.highlights)
		h2 = h1
	pGenomePlot.input   = lambda *chs: [
		([ch.get() for ch in chs], "%s:%s-%s" % (chrom, start, start + 10000), h1),
		([ch.get() for ch in chs], "%s:%s-%s" % (chrom, end - 100000, end), h2),
	]

else:
	pGenomePlot.depends        = trackProcs
	#pGenomePlot.tag            = uuid
	pGenomePlot.exdir          = params.outdir
	pGenomePlot.args.ideoTrack = params.ideo
	pGenomePlot.args.axisTrack = params.axis
	pGenomePlot.args.geneTrack = params.genes
	if params.devpars:
		pGenomePlot.args.devpars.update(json.loads(params.devpars))
	if params.plotparams:
		pGenomePlot.args.params.update(json.loads(params.plotparams))
	pGenomePlot.input   = lambda *chs: [([ch.get() for ch in chs], params.region, ';'.join(params.highlights))]
	
config = {'proc': {'file': None}}
PyPPL(config).start(trackProcs).run()
