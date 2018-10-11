{{rimport}}('__init__.r', 'plot.r')

infile  = {{i.infile | quote}}
inmodel = {{i.model | quote}}
outdir  = {{o.outdir | quote}}
outprob = {{args.outprob | R}}
inopts  = {{args.inopts | R}}
outauc  = {{args.outauc | R}}
params  = {{args.params | R}}
devpars = {{args.devpars | R}}
ggs     = {{args.ggs | R}}
prefix  = file.path(outdir, {{i.infile | stem | quote}})

indata = read.table.nodup(
	infile, 
	header      = {{args.inopts.get('cnames', True) | R}},
	row.names   = {{args.inopts.get('rnames', True) | :1 if a else None | R}},
	sep         = {{args.inopts.get('delimit', '\t') | R}},
	check.names = {{args.inopts.get('check.names', False) | R}}
)

cnames = colnames(indata)
if (is.null(cnames)) {
	colnames(indata) = c(paste('X', 1:(ncol(indata)-1)), 'Y')
	cnames = colnames(indata)
}

model = readRDS(inmodel)
prob  = predict.lm(model, indata, type="response")

if (model$yval == 'categ') {
	ymin  = model$ymin
	ymax  = model$ymax
	index = round(prob * (ymax - ymin) + ymin)
	if (outprob) {
		out = cbind(indata, Predict.Result = model$ylabs[index], Predict.Prob = round(prob, 3))
	} else {
		out = cbind(indata, Predict.Result = model$ylabs[index])
	}
} else if (model$yval == 'numeric') {
	ymin  = model$ymin
	ymax  = model$ymax
	value = prob * (ymax - ymin) + ymin
	if (outprob) {
		out = cbind(indata, Predict.Result = value, Predict.Prob = round(prob, 3))
	} else {
		out = cbind(indata, Predict.Result = value)
	}
}

ycol = model$ycol
if (outauc) {
	if (!ycol %in% cnames) {
		stop('No Y values found in input data, unable to plot ROC or output AUC.')
	}
	if (model$yval == 'prob' || model$yval == 'numeric') {
		stop('ROC/AUC is only available for categorical Y values, unable to plot ROC or output AUC.')
	}
	aucdata = data.frame(D = indata[, ycol] == out$Predict.Result, M = prob)
	auc = plot.roc(aucdata, paste0(prefix, '.roc.png'), params = params, ggs = ggs, devpars = devpars)
	out = cbind(out, AUC = auc)
}

write.table(out, paste0(prefix, '.result.txt'), row.names = {{args.inopts.get('rnames', True) | R}}, col.names = T, sep = "\t", quote = F)