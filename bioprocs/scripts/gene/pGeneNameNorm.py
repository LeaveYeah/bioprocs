from os import path, symlink
{{ genenorm }}

_, cachefile = genenorm(
	{{in.infile | quote}}, 
	{{out.outfile | quote}}, 
	col      = {{args.col}},
	notfound = {{args.notfound | quote}},
	frm      = {{args.frm | quote}},
	to       = {{args.to | quote}},
	header   = {{args.header}},
	genome   = {{args.genome | quote}},
	skip     = {{args.skip}},
	delimit  = {{args.delimit | quote}},
	tmpdir   = {{args.tmpdir | quote}},
	comment  = {{args.comment | quote}}
)
symlink(cachefile, path.join({{job.outdir | quote}}, path.basename(cachefile)))