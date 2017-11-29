<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->
**Table of Contents**  *generated with [DocToc](https://github.com/thlorenz/doctoc)*

- [pRankProduct](#prankproduct)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->


## pRankProduct

### description
	Calculate the rank product of a set of ranks. Refer to [here](https://en.wikipedia.org/wiki/Rank_product)

### input
#### `infile:file`:
 The input file  
	- Format:
	```
				Case1	Case2	...
	Feature1	8.2  	10.1 	...
	Feature2	2.3  	8.0  	...
	...
	```
	- Or instead of values, you can also have ranks in the input file:
	```
				Rank1	Rank2	...
	Feature1	2    	1    	...
	Feature2	3    	2    	...
	...
	```

### output
#### `outfile:file`:
 The output file with original ranks, rank products and p-value if required  