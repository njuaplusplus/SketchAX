# Sketch_notes
This repo keeps our official implementation of SketchAX and benchmarks used in our POPL 2020 paper "Augmented Example-Based Synthesis using Relational Perturbation Properties".

# Demo
The following video shows the execution of Sketch AXI for [`my_max3`](sketch-test/benchmarks/15_X/my_max3) benchmark.
It uses the 0th pre-generated random examples and user-provided properties.
[![asciicast](https://asciinema.org/a/SIQKijV1xC9JX9YlfabuupbxQ.svg)](https://asciinema.org/a/SIQKijV1xC9JX9YlfabuupbxQ)

# Benchmarks
We mainly use benchmarks from four sources:
1. int benchmarks from Sketch repo in [`sketch-test/benchmarks/int_ben`](sketch-test/benchmarks/int_ben)
2. int benchmarks from Sketch repo in [`sketch-test/benchmarks/bit_ben`](sketch-test/benchmarks/bit_ben)
3. SyGuS benchmarks from CLIA Track in [`sketch-test/benchmarks/15_X`](sketch-test/benchmarks/15_X)
4. handcrafted benchmarks in [`sketch-test/benchmarks/15_X`](sketch-test/benchmarks/15_X)

There corresponding properties are stored in `properties.conf`.

# Codes
Codes are located in [`sketch-test/python`](sketch-test/python).

# Usage

Most options could be found in the codes as well as their explanations.

```bash
# run SketchAX I on all int benchmarks with 10 sets of 3 user-provided exampels and properties
python3 python/test.py -d int_ben -t hard --load-example --repeat 10 --load-prop --example-nums 3 --random +
```

# BibTex

```
@article{An.Synthesis.POPL.2020,
  author = {An, Shengwei and Singh, Rishabh and Misailovic, Sasa and Samanta, Roopsha},
  title = {Augmented Example-Based Synthesis Using Relational Perturbation Properties},
  year = {2019},
  issue_date = {January 2020},
  publisher = {Association for Computing Machinery},
  address = {New York, NY, USA},
  volume = {4},
  number = {POPL},
  url = {https://doi.org/10.1145/3371124},
  doi = {10.1145/3371124},
  journal = {Proc. ACM Program. Lang.},
  month = {Dec},
  articleno = {56},
  numpages = {24},
}
```
