<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->
**Table of Contents**  *generated with [DocToc](https://github.com/thlorenz/doctoc)*

- [pBedSort](#pbedsort)
- [pBedIntersect](#pbedintersect)
- [pBedCluster](#pbedcluster)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->


## pBedSort

### description
	Sort bed files

### input
#### `infile:file`:
 The input file  

### output
#### `outfile:file`:
 The output file  

### args
#### `tool`:
         The tool used to sort the file. Default: sort (bedtools, bedops)  
#### `bedtools`:
     The path to bedtools. Default: bedtools  
#### `bedops_sort`:
  The path to bedops' sort-bed. Default: sort-bed  
#### `mem`:
          The memory to use. Default: 8G  
#### `tmpdir`:
       The tmpdir to use. Default: `$TMPDIR`  
#### `unique`:
       Remove the dupliated records? Default: True  
#### `params`:
       Other params for `tool`. Default: {}  

## pBedIntersect

### description
	Find intersections of two bed files.
	Input files must be sorted.

### input
#### `infile1:file`:
 The 1st input bed file  
#### `infile2:file`:
 The 2nd input bed file  

### output
#### `outfile:file`:
 The output file  

### args
#### `tool`:
         The tool used to sort the file. Default: bedtools (bedops)  
#### `bedtools`:
     The path to bedtools. Default: bedtools  
#### `bedops`:
  The path to bedops. Default: bedops  
#### `params`:
       Other params for `tool`. Default: ''  

## pBedCluster

### description
	Assign cluster id to each record

### input
#### `infile:file`:
 The input bed file  

### output
#### `outfile:file`:
 The output file  

### args
#### `tool`:
         The tool used to sort the file. Default: bedtools  
#### `bedtools`:
     The path to bedtools. Default: bedtools  
#### `params`:
       Other params for `tool`. Default: ''  