[![GoDoc](https://img.shields.io/badge/godoc-reference-blue.svg)](https://pkg.go.dev/github.com/charlievieth/simdutf@master)

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
