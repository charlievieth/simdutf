//go:build libsimdutf

package simdutf

// #cgo CFLAGS: -DUSE_LIBSIMDUTF
// #cgo pkg-config: simdutf
import "C"
