//go:build arm64

package simdutf

// These values were empirically discovered using the Calibration tests
// which can be invoked by running `make calibrate`.
const (
	cutoffIsASCII = 1024
	cutoffValid   = 64
)
