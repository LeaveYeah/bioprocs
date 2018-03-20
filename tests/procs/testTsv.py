import unittest
from os import path
from pyppl import PyPPL
from bioprocs.tsv import pMatrixR, pCbind, pRbind, pCsplit, pRsplit, pTxtFilter, pTxtTransform, pSimRead, pTsv
from helpers import getfile, procOK, config

class testMatrix (unittest.TestCase):
	
	def testMatrix(self):
		name               = 'matrix.txt'
		pMatrixR1           = pMatrixR.copy()
		pMatrixR1.input     = [getfile(name)]
		pMatrixR1.args.code = "mat = log(mat + 1, 2)"
		PyPPL(config).start(pMatrixR1).run()
		procOK(pMatrixR1, name, self)

	def testMatrixNoHead(self):
		name                 = 'matrix-nohead.txt'
		pMatrixR2             = pMatrixR.copy()
		pMatrixR2.input       = [getfile(name)]
		pMatrixR2.args.code   = "mat = log(mat + 1, 2)"
		pMatrixR2.args.cnames = False
		PyPPL(config).start(pMatrixR2).run()
		procOK(pMatrixR2, name, self)

	def testMatrixNoRn(self):
		name                 = 'matrix-norn.txt'
		pMatrixR3             = pMatrixR.copy()
		pMatrixR3.input       = [getfile(name)]
		pMatrixR3.args.code   = "mat = log(mat + 1, 2)"
		pMatrixR3.args.rnames = False
		PyPPL(config).start(pMatrixR3).run()
		procOK(pMatrixR3, name, self)

	def testCbind(self):
		name1 = 'matrix-cbind-1.txt'
		name2 = 'matrix-cbind-2.txt'
		name0 = 'matrix-cbind.txt'
		pCbind1 = pCbind.copy()
		pCbind1.input = [[getfile(name1), getfile(name2)]]
		PyPPL(config).start(pCbind1).run()
		procOK(pCbind1, name0, self)

	def testRbind(self):
		name1 = 'matrix-rbind-1.txt'
		name2 = 'matrix-rbind-2.txt'
		name0 = 'matrix-rbind.txt'
		pRbind1 = pRbind.copy()
		pRbind1.input = [[getfile(name1), getfile(name2)]]
		PyPPL(config).start(pRbind1).run()
		procOK(pRbind1, name0, self)

	def testCsplit(self):
		name1 = 'matrix-rbind-1.txt'
		pCsplit.input = [getfile(name1)]
		PyPPL(config).start(pCsplit).run()
		procOK(pCsplit, 'matrix-rbind-1.splits', self)

	def testRsplit(self):
		name1 = 'matrix-rbind-2.txt'
		pRsplit.input = [getfile(name1)]
		PyPPL(config).start(pRsplit).run()
		procOK(pRsplit, 'matrix-rbind-2.rsplits', self)

	def testRsplitN(self):
		name1 = 'matrix-rsplit.txt'
		pRsplitN = pRsplit.copy()
		pRsplitN.input = [getfile(name1)]
		pRsplitN.args.n = 3
		PyPPL(config).start(pRsplitN).run()
		procOK(pRsplitN, 'matrix-rsplit.rsplits', self)

	def testCsplitN(self):
		name1 = 'matrix-csplit.txt'
		pCsplitN = pCsplit.copy()
		pCsplitN.input = [getfile(name1)]
		pCsplitN.args.n = 3
		PyPPL(config).start(pCsplitN).run()
		procOK(pCsplitN, 'matrix-csplit.csplits', self)

	def testTxtFilter(self):
		pTxtFilter.input        = [getfile('txtfilter.txt')]
		pTxtFilter.args.cols    = [0, 2, "V4"]
		pTxtFilter.args.rfilter = 'lambda row: float(row[1]) > 2 and float(row[2]) > 2'
		pTxtFilter.args.skip    = 2
		pTxtFilter.args.delimit = '|'
		pTxtFilter.args.outdelimit = '|'
		PyPPL(config).start(pTxtFilter).run()
		procOK(pTxtFilter, 'txtfilter.txt', self)

	def testTxtTransform(self):
		pTxtTransform.input          = [getfile('txtfilter.txt')]
		pTxtTransform.args.cols      = [0, 2, "V4"]
		pTxtTransform.args.transform = 'lambda row: [str(float(r) + 1) if i == 1 else r for i, r in enumerate(row)]'
		pTxtTransform.args.skip      = 2
		pTxtTransform.args.delimit   = '|'
		pTxtTransform.args.outdelimit   = '|'
		PyPPL(config).start(pTxtTransform).run()
		procOK(pTxtTransform, 'txttransform.txt', self)

	def testSimRead(self):
		pSimRead.input        = [[getfile('simread1.txt.gz'), getfile('simread2.txt')]]
		pSimRead.args.skip    = [3]
		pSimRead.args.usehead = 0
		pSimRead.args.match   = 'lambda r1, r2: compare(r1[0], r2[1])'
		pSimRead.args.do      = 'lambda r1, r2: writelist(r1)'
		pSimRead.args.delimit = ["\t", "|"]
		PyPPL(config).start(pSimRead).run()
		procOK(pSimRead, 'simread.txt', self)

	def testpTsv(self):
		pTsvInmeta = pTsv.copy()
		pTsvInmeta.input = [getfile('matrix-nohead.txt')]
		pTsvInmeta.args.inmeta = [('NAME', 'Row name'), ('COL1', 'Column 1'), ('COL2', 'Column 2'), ('COL3', 'Column 3')]
		PyPPL(config).start(pTsvInmeta).run()
		procOK(pTsvInmeta, 'matrix-nohead.tsv', self)

	def testpTsvFilter(self):
		pTsvFilter = pTsv.copy()
		pTsvFilter.input = [getfile('matrix-nohead.txt')]
		pTsvFilter.output = "outfile:file:{{in.infile | fn}}.filtered"
		pTsvFilter.args.inmeta = [('NAME', 'Row name'), ('COL1', 'Column 1'), ('COL2', 'Column 2'), ('COL3', 'Column 3')]
		pTsvFilter.args.outmeta = ['NAME', 'COL2']
		pTsvFilter.args.writemeta = False
		pTsvFilter.args.ops = 'lambda r: None if int(r.COL1) >=7 else r'
		PyPPL(config).start(pTsvFilter).run()
		procOK(pTsvFilter, 'matrix-nohead.filtered', self)

	# TODO:
	# test predefined read/write classes for pTsv

if __name__ == '__main__':
	unittest.main()
		