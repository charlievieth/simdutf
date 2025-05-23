//go:build !amd64 && !arm64 && !arm && !wasm

package simdutf

// FIXME: The below cutoffs are for CPU architectures that may be supported by
// simdutf and which I do not have access to. Therefore, the values here are
// complete guesses.
//
// If anyone reading this has access to any of the CPU architectures included
// here please run the calibration tests (`make calibrate`) and create a pull
// request with the results.

const (
	cutoffIsASCII = 1024
	cutoffValid   = 64
)
