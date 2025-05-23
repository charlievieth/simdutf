//go:build arm || wasm

package simdutf

const (
	// Duplicate the MaxInt logic from the math package
	// to avoid the dependency.
	intSize = 32 << (^uint(0) >> 63) // 32 or 64
	maxInt  = 1<<(intSize-1) - 1     // MaxInt32 or MaxInt64 depending on intSize.
)

// This essentially disables use of the simdutf library on platforms it does
// not natively support since the Go implementation will be just as fast.
const (
	cutoffIsASCII = maxInt
	cutoffValid   = maxInt
)
