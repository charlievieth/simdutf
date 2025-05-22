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
	return bool(C.validate_ascii((*C.char)(unsafe.Pointer(unsafe.SliceData(p))),
		C.size_t(len(p))))
}

// IsASCIIString reports whether s consists entirely of valid ASCII-encoded runes.
func IsASCIIString(s string) bool {
	return bool(C.validate_ascii((*C.char)(unsafe.Pointer(unsafe.StringData(s))),
		C.size_t(len(s))))
}

// Valid reports whether p consists entirely of valid UTF-8-encoded runes.
func Valid(p []byte) bool {
	if len(p) <= 64 {
		return utf8.Valid(p)
	}
	return bool(C.validate_utf8((*C.char)(unsafe.Pointer(unsafe.SliceData(p))),
		C.size_t(len(p))))
}

// ValidString reports whether s consists entirely of valid UTF-8-encoded runes.
func ValidString(s string) bool {
	if len(s) <= 64 {
		return utf8.ValidString(s)
	}
	return bool(C.validate_utf8((*C.char)(unsafe.Pointer(unsafe.StringData(s))),
		C.size_t(len(s))))
}
