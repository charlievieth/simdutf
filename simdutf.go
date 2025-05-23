// Package simdutf is a Go wrapper around the [simdutf] Unicode validation and
// transcoding library.
//
// [simdutf]: https://github.com/simdutf/simdutf/
package simdutf

// #cgo CFLAGS: -O2 -g
//
// #cgo noescape validate_ascii
// #cgo nocallback validate_ascii
// #cgo noescape validate_utf8
// #cgo nocallback validate_utf8
//
// #include "simdutf_ext.h"
import "C"

import (
	"unicode/utf8"
	"unsafe"
)

// IsASCII reports whether p consists entirely of valid ASCII-encoded runes.
func IsASCII(p []byte) bool {
	if len(p) <= cutoffIsASCII {
		return isASCII(p)
	}
	return validateASCII(&p[0], len(p))
}

// IsASCIIString reports whether s consists entirely of valid ASCII-encoded runes.
func IsASCIIString(s string) bool {
	if len(s) <= cutoffIsASCII {
		return isASCIIString(s)
	}
	return validateASCII(unsafe.StringData(s), len(s))
}

// Valid reports whether p consists entirely of valid UTF-8-encoded runes.
func Valid(p []byte) bool {
	if len(p) <= cutoffValid {
		return utf8.Valid(p)
	}
	return validateUTF8(&p[0], len(p))
}

// ValidString reports whether s consists entirely of valid UTF-8-encoded runes.
func ValidString(s string) bool {
	if len(s) <= cutoffValid {
		return utf8.ValidString(s)
	}
	return validateUTF8(unsafe.StringData(s), len(s))
}

// isASCII is a pure Go implementation of IsASCII and is used when the input
// too small to justify the overhead of using the simdutf library.
func isASCII(p []byte) bool {
	// This optimization avoids the need to recompute the capacity
	// when generating code for p[8:], bringing it to parity with
	// ValidString, which was 20% faster on long ASCII strings.
	p = p[:len(p):len(p)]

	// Fast path. Check for and skip 8 bytes of ASCII characters per iteration.
	for len(p) >= 8 {
		// Combining two 32 bit loads allows the same code to be used
		// for 32 and 64 bit platforms.
		// The compiler can generate a 32bit load for first32 and second32
		// on many platforms. See test/codegen/memcombine.go.
		first32 := uint32(p[0]) | uint32(p[1])<<8 | uint32(p[2])<<16 | uint32(p[3])<<24
		second32 := uint32(p[4]) | uint32(p[5])<<8 | uint32(p[6])<<16 | uint32(p[7])<<24
		if (first32|second32)&0x80808080 != 0 {
			// Found a non ASCII byte (>= RuneSelf).
			break
		}
		p = p[8:]
	}
	for i := 0; i < len(p); i++ {
		if p[i]&utf8.RuneSelf != 0 {
			return false
		}
	}
	return true
}

// isASCIIString is a pure Go implementation of IsASCII and is used when the input
// too small to justify the overhead of using the simdutf library.
func isASCIIString(s string) bool {
	// Fast path. Check for and skip 8 bytes of ASCII characters per iteration.
	for len(s) >= 8 {
		// Combining two 32 bit loads allows the same code to be used
		// for 32 and 64 bit platforms.
		// The compiler can generate a 32bit load for first32 and second32
		// on many platforms. See test/codegen/memcombine.go.
		first32 := uint32(s[0]) | uint32(s[1])<<8 | uint32(s[2])<<16 | uint32(s[3])<<24
		second32 := uint32(s[4]) | uint32(s[5])<<8 | uint32(s[6])<<16 | uint32(s[7])<<24
		if (first32|second32)&0x80808080 != 0 {
			// Found a non ASCII byte (>= RuneSelf).
			return false
		}
		s = s[8:]
	}
	for i := 0; i < len(s); i++ {
		if s[i]&utf8.RuneSelf != 0 {
			return false
		}
	}
	return true
}

func validateASCII(p *byte, n int) bool {
	return bool(C.validate_ascii((*C.char)(unsafe.Pointer(p)), C.size_t(n)))
}

func validateUTF8(p *byte, n int) bool {
	return bool(C.validate_utf8((*C.char)(unsafe.Pointer(p)), C.size_t(n)))
}
