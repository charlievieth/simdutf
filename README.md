[![Tests](https://github.com/charlievieth/simdutf/actions/workflows/test.yml/badge.svg)](https://github.com/charlievieth/simdutf/actions/workflows/test.yml)
[![GoDoc](https://img.shields.io/badge/godoc-reference-blue.svg)](https://pkg.go.dev/github.com/charlievieth/simdutf@master)
[![codecov](https://codecov.io/gh/charlievieth/simdutf/graph/badge.svg?token=66ZMOXC3F9)](https://codecov.io/gh/charlievieth/simdutf)

# simdutf

Package simdutf is a Go wrapper around the [simdutf](https://github.com/simdutf/simdutf/)
library.

**Note:** [CGO](https://go.dev/wiki/cgo) is required to build this library.
You can check if your Go installation supports CGO by running: `go env CGO_ENABLED`.

By default, the bundled simdutf library is used. To link to a system installed
simdutf library build this library with the `libsimdutf` build tag.

### simdutf version

This library bundles version 7.1.0 of [simdutf](https://github.com/simdutf/simdutf/).
The [SIMDUTF_VERSION](./SIMDUTF_VERSION) file contains the current version of
the bundled simdutf version.

## Benchmarks

<details>
<summary>Apple M4 Pro</summary>

```
goos: darwin
goarch: arm64
pkg: github.com/charlievieth/simdutf
cpu: Apple M4 Pro

BenchmarkValid/ASCII/10           3.448 ns/op      2900.58 MB/s
BenchmarkValid/ASCII/32           3.670 ns/op      8720.07 MB/s
BenchmarkValid/ASCII/64           4.555 ns/op      14049.86 MB/s
BenchmarkValid/ASCII/128          30.23 ns/op      4234.37 MB/s
BenchmarkValid/ASCII/256          30.84 ns/op      8301.91 MB/s
BenchmarkValid/ASCII/512          32.43 ns/op      15787.08 MB/s
BenchmarkValid/ASCII/4K           61.07 ns/op      67067.36 MB/s
BenchmarkValid/ASCII/16K          168.7 ns/op      97117.82 MB/s
BenchmarkValid/ASCII/4M           41620 ns/op      100776.48 MB/s
BenchmarkValid/ASCII/64M          818370 ns/op     82003.04 MB/s
BenchmarkValid/MostlyASCII/10     5.760 ns/op      1736.00 MB/s
BenchmarkValid/MostlyASCII/32     14.29 ns/op      2239.25 MB/s
BenchmarkValid/MostlyASCII/64     25.89 ns/op      2471.84 MB/s
BenchmarkValid/MostlyASCII/128    32.37 ns/op      3954.28 MB/s
BenchmarkValid/MostlyASCII/256    33.27 ns/op      7694.38 MB/s
BenchmarkValid/MostlyASCII/512    36.46 ns/op      14043.92 MB/s
BenchmarkValid/MostlyASCII/4K     84.97 ns/op      48203.90 MB/s
BenchmarkValid/MostlyASCII/16K    249.4 ns/op      65706.04 MB/s
BenchmarkValid/MostlyASCII/4M     62598 ns/op      67004.03 MB/s
BenchmarkValid/MostlyASCII/64M    988549 ns/op     67886.23 MB/s
BenchmarkValid/Japanese/10        5.830 ns/op      1715.19 MB/s
BenchmarkValid/Japanese/32        14.69 ns/op      2178.73 MB/s
BenchmarkValid/Japanese/64        26.63 ns/op      2403.41 MB/s
BenchmarkValid/Japanese/128       34.35 ns/op      3726.50 MB/s
BenchmarkValid/Japanese/256       40.39 ns/op      6338.72 MB/s
BenchmarkValid/Japanese/512       58.29 ns/op      8783.84 MB/s
BenchmarkValid/Japanese/4K        317.5 ns/op      12899.32 MB/s
BenchmarkValid/Japanese/16K       1204 ns/op       13603.54 MB/s
BenchmarkValid/Japanese/4M        305288 ns/op     13738.83 MB/s
BenchmarkValid/Japanese/64M       4842601 ns/op    13858.02 MB/s
BenchmarkIsASCII/10               2.483 ns/op      4027.34 MB/s
BenchmarkIsASCII/32               2.979 ns/op      10740.36 MB/s
BenchmarkIsASCII/64               3.859 ns/op      16585.18 MB/s
BenchmarkIsASCII/128              6.656 ns/op      19230.76 MB/s
BenchmarkIsASCII/256              11.96 ns/op      21408.87 MB/s
BenchmarkIsASCII/512              22.41 ns/op      22845.88 MB/s
BenchmarkIsASCII/4K               56.23 ns/op      72838.62 MB/s
BenchmarkIsASCII/16K              150.5 ns/op      108835.26 MB/s
BenchmarkIsASCII/4M               43032 ns/op      97468.37 MB/s
BenchmarkIsASCII/64M              766867 ns/op     87510.49 MB/s
```

</details>

<details>
<summary>AMD Ryzen 9 9950X</summary>

```
goos: linux
goarch: amd64
pkg: github.com/charlievieth/simdutf
cpu: AMD Ryzen 9 9950X 16-Core Processor

BenchmarkValid/ASCII/10           2.962 ns/op      3376.02 MB/s
BenchmarkValid/ASCII/32           3.294 ns/op      9715.53 MB/s
BenchmarkValid/ASCII/64           26.36 ns/op      2427.49 MB/s
BenchmarkValid/ASCII/128          27.18 ns/op      4708.65 MB/s
BenchmarkValid/ASCII/256          26.13 ns/op      9797.32 MB/s
BenchmarkValid/ASCII/512          28.50 ns/op      17966.39 MB/s
BenchmarkValid/ASCII/4K           44.88 ns/op      91274.24 MB/s
BenchmarkValid/ASCII/16K          112.0 ns/op      146231.88 MB/s
BenchmarkValid/ASCII/4M           29763 ns/op      140923.76 MB/s
BenchmarkValid/ASCII/64M          865934 ns/op     77498.81 MB/s
BenchmarkValid/MostlyASCII/10     5.511 ns/op      1814.40 MB/s
BenchmarkValid/MostlyASCII/32     17.52 ns/op      1826.35 MB/s
BenchmarkValid/MostlyASCII/64     28.83 ns/op      2220.09 MB/s
BenchmarkValid/MostlyASCII/128    25.99 ns/op      4925.02 MB/s
BenchmarkValid/MostlyASCII/256    28.39 ns/op      9016.97 MB/s
BenchmarkValid/MostlyASCII/512    30.72 ns/op      16664.88 MB/s
BenchmarkValid/MostlyASCII/4K     52.25 ns/op      78390.60 MB/s
BenchmarkValid/MostlyASCII/16K    144.3 ns/op      113534.30 MB/s
BenchmarkValid/MostlyASCII/4M     34517 ns/op      121512.83 MB/s
BenchmarkValid/MostlyASCII/64M    897078 ns/op     74808.30 MB/s
BenchmarkValid/Japanese/10        5.361 ns/op      1865.23 MB/s
BenchmarkValid/Japanese/32        17.81 ns/op      1796.73 MB/s
BenchmarkValid/Japanese/64        26.87 ns/op      2381.91 MB/s
BenchmarkValid/Japanese/128       27.53 ns/op      4648.68 MB/s
BenchmarkValid/Japanese/256       29.91 ns/op      8558.51 MB/s
BenchmarkValid/Japanese/512       33.82 ns/op      15139.06 MB/s
BenchmarkValid/Japanese/4K        111.3 ns/op      36799.37 MB/s
BenchmarkValid/Japanese/16K       388.8 ns/op      42140.47 MB/s
BenchmarkValid/Japanese/4M        92143 ns/op      45519.42 MB/s
BenchmarkValid/Japanese/64M       1661231 ns/op    40397.06 MB/s
BenchmarkIsASCII/10               2.272 ns/op      4402.11 MB/s
BenchmarkIsASCII/32               2.403 ns/op      13317.69 MB/s
BenchmarkIsASCII/64               3.452 ns/op      18542.17 MB/s
BenchmarkIsASCII/128              6.105 ns/op      20964.92 MB/s
BenchmarkIsASCII/256              10.90 ns/op      23491.01 MB/s
BenchmarkIsASCII/512              20.63 ns/op      24819.66 MB/s
BenchmarkIsASCII/4K               39.73 ns/op      103086.84 MB/s
BenchmarkIsASCII/16K              106.9 ns/op      153207.23 MB/s
BenchmarkIsASCII/4M               28989 ns/op      144686.87 MB/s
BenchmarkIsASCII/64M              805979 ns/op     83263.84 MB/s
```

</details>
