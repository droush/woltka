# Woltka

[![License](https://img.shields.io/badge/License-BSD%203--Clause-blue.svg)](https://opensource.org/licenses/BSD-3-Clause)
[![CI Status](https://github.com/qiyunzhu/woltka/actions/workflows/main.yml/badge.svg)](https://github.com/qiyunzhu/woltka/actions)
[![Coverage Status](https://coveralls.io/repos/github/qiyunzhu/woltka/badge.svg?branch=master)](https://coveralls.io/github/qiyunzhu/woltka?branch=master)

**Woltka** (Web of Life Toolkit App), is a bioinformatics package for shotgun metagenome data analysis. It takes full advantage of, and is not limited by, the [WoL](https://biocore.github.io/wol/) reference phylogeny. It bridges first-pass sequence aligners with advanced analytical platforms (such as QIIME 2). Highlights of this program include:

- OGU: fine-grained community ecology.
- Tree-based, rank-free classification.
- Combined taxonomic & functional analysis.

Woltka ships with a **QIIME 2 plugin**. [See here for instructions](woltka/q2).

## Contents

- [Overview](#overview)
- [Installation](#installation)
- [Example usage](#example-usage)
- Main workflow
  - [Input files](doc/input.md)
  - [Output files](doc/output.md)
  - [Classification systems](doc/hierarchy.md)
  - [Classification methods](doc/classify.md)
  - [Coordinates matching](doc/ordinal.md)
  - [Stratification](doc/stratify.md)
- Profile tools
  - [Collapse](doc/collapse.md), [Coverage](doc/coverage.md), [Normalize](doc/normalize.md), [Filter](doc/filter.md), [Merge](doc/merge.md)
- Tutorials
  - [Working with WoL](doc/wol.md)
  - [OGU analysis](doc/ogu.md)
- For users of
  - [QIIME 2](woltka/q2), [Qiita](doc/qiita.md), [SHOGUN](doc/wol.md#sequence-alignment), [GTDB](doc/gtdb.md), [MetaCyc](doc/metacyc.md), [KEGG](doc/kegg.md)
- References
  - [Command-line interface](doc/cli.md)
  - [Computational efficiency](doc/perform.md)
- [FAQs](#doc/faq.md)
- [Citation](#citation)
- [Contact](#contact)


## Overview

### Where does Woltka fit in a pipeline

Woltka is a **classifier**. It serves as a middle layer between sequence alignment and community ecology analyses.

### What does Woltka do

Woltka processes **alignments** -- the mappings of query sequences against reference sequences (such as microbial genomes or genes), and infers the best placement of the queries in a hierarchical classification system. One query could have simultaneous matches in multiple references. Woltka finds the most suitable classification unit(s) to describe the query accordingly the criteria specified by the researcher. Woltka generates **profiles** (feature tables) -- the frequencies (counts) of classification units which describe the composition of samples.

### What else does Woltka do

Woltka provides several utilities for handling feature tables, including collapsing a table to higher-level features, calculating feature group coverage, filtering features based on per-sample abundance, and  merging tables.

### What does Woltka not do

Woltka does NOT **align** sequences. You need to align your FastQ (or Fast5, etc.) files against a reference database (we recommend [WoL](https://biocore.github.io/wol/)) use an aligner of your choice (BLAST, Bowtie2, etc.). The resulting alignment files can be fed into Woltka.

Woltka does NOT **analyze** profiles. We recommend using [QIIME 2](https://qiime2.org/) for robust downstream analyses of the profiles to decode the relationships among micobial communities and with their environments.


## Installation

Requirement: [Python](https://www.python.org/) 3.6 or above, with Python package [biom-format](http://biom-format.org/) installed.

```bash
pip install woltka
```

After installation, launch the program by executing:

```bash
woltka
```

[More details about installation](doc/install.md) are provided here.

## Example usage

Woltka provides several small test datasets under [woltka/tests/data](woltka/tests/data). To access them, [download](https://github.com/qiyunzhu/woltka/archive/master.zip) this GitHub repo, unzip, and navigate to this directory.

One can execute the following commands to make sure that Woltka functions correctly, and to get an impression of the basic usage of Woltka.

(Note: a more complete list of commands at provided [here](woltka/tests/data). Alternatively, you can skip this test dataset check out the [instructions](doc/wol.md) for working with WoL.)

1\. OGU table generation ([details](doc/ogu.md)):

```bash
woltka classify -i align/bowtie2 -o ogu.biom
```

The input path, [`align/bowtie2`](woltka/tests/data/align/bowtie2), is a directory containing five Bowtie2 alignment files (`S01.sam.xz`, `S02.sam.xz`,... `S05.sam.xz`) (SAM format, xzipped), each representing the mapping of shotgun metagenomic sequences per sample against a reference genome database.

The output file, `table.biom`, is a feature table in BIOM format, which can then be analyzed using various bioformatics programs such as [QIIME 2](https://qiime2.org/).

2\. Taxonomic profiling at the ranks of phylum, genus and species ([details](doc/hierarchy.md)):

```bash
woltka classify \
  -i align/bowtie2 \
  --map taxonomy/taxid.map \
  --nodes taxonomy/nodes.dmp \
  --names taxonomy/names.dmp \
  --rank phylum,genus,species \
  -o output_dir
```

The mapping file (`taxid.map`) translates genome IDs to taxonomic IDs, which then allows Woltka to classify query sequences based on the NCBI taxonomy (`nodes.dmp` and `names.dmp`).

The output directory (`output_dir`) will contain three feature tables: `phylum.biom`, `genus.biom` and `species.biom`, each representing a taxonomic profile at one of the three ranks.

3\. Functional profiling by UniRef entries then by GO terms (molecular process):

```bash
woltka classify \
  -i align/bowtie2 \
  --coords function/coords.txt.xz \
  --map function/uniref.map.xz \
  --map function/go/process.tsv.xz \
  --rank uniref,process \
  -o output_dir
```

Here, the input files are still read-to-genome alignments, instead of read-to-gene ones, but Woltka matches reads to genes based on their coordinates on the genomes (as indicated by the file `coords.txt`). This ensures consistency between taxonomic and functional classifications.

Subsequently, Woltka is able to assign query sequences to functional units, as defined in mapping files (`uniref.map` and `go/process.tsv`). As you can see, compressed files are supported and auto-detected.

Similarly, the output files are two functional profiles: `uniref.biom` and `process.biom`.

One can also combine taxonomic and functional profilings in a **stratification** analysis. See [details](doc/stratify.md).


## Citation

The first manuscript describing Woltka has been preprinted at:

- Zhu Q, Huang S, Gonzalez A, McGrath I, McDonald D, Haiminen N, et al. [OGUs enable effective, phylogeny-aware analysis of even shallow metagenome community structures.](https://www.biorxiv.org/content/10.1101/2021.04.04.438427v1) _bioRxiv_. 2021. doi: https://doi.org/10.1101/2021.04.04.438427.

Note: This manuscript focuses on the [OGU analysis](doc/ogu.md). Although it does not discuss other functions of Woltka, it is so far the only citable article if you use Woltka in your studies.


## Contact

Please forward any questions to the project leader: Dr. Qiyun Zhu (qiyunzhu@gmail.com) or the senior PI: Dr. Rob Knight (robknight@ucsd.edu).
