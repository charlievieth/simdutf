package simdutf

import (
	"fmt"
	"sort"
	"strings"
	"testing"
	"unicode/utf8"
)

type ValidTest struct {
	in  string
	out bool
}

var validTests = []ValidTest{
	{"", true},
	{"a", true},
	{"abc", true},
	{"Ж", true},
	{"ЖЖ", true},
	{"брэд-ЛГТМ", true},
	{"☺☻☹", true},
	{"aa\xe2", false},
	{string([]byte{66, 250}), false},
	{string([]byte{66, 250, 67}), false},
	{"a\uFFFDb", true},
	{string("\xF4\x8F\xBF\xBF"), true},      // U+10FFFF
	{string("\xF4\x90\x80\x80"), false},     // U+10FFFF+1; out of range
	{string("\xF7\xBF\xBF\xBF"), false},     // 0x1FFFFF; out of range
	{string("\xFB\xBF\xBF\xBF\xBF"), false}, // 0x3FFFFFF; out of range
	{string("\xc0\x80"), false},             // U+0000 encoded in two bytes: incorrect
	{string("\xed\xa0\x80"), false},         // U+D800 high surrogate (sic)
	{string("\xed\xbf\xbf"), false},         // U+DFFF low surrogate (sic)
}

func TestValidUTF8(t *testing.T) {
	for _, tt := range validTests {
		if Valid([]byte(tt.in)) != tt.out {
			t.Errorf("Valid(%q) = %v; want %v", tt.in, !tt.out, tt.out)
		}
		if ValidString(tt.in) != tt.out {
			t.Errorf("ValidString(%q) = %v; want %v", tt.in, !tt.out, tt.out)
		}
	}
}

// Reference isValidASCII function
func isValidASCII(s string) bool {
	for _, r := range s {
		if r >= utf8.RuneSelf || r == utf8.RuneError {
			return false
		}
	}
	return true
}

func TestIsASCII8(t *testing.T) {
	for _, tt := range validTests {
		want := isValidASCII(tt.in)
		if IsASCII([]byte(tt.in)) != want {
			t.Errorf("IsASCII(%q) = %v; want %v", tt.in, !want, want)
		}
		if IsASCIIString(tt.in) != want {
			t.Errorf("IsASCIIString(%q) = %v; want %v", tt.in, !want, want)
		}
	}
}

func TestValidCalibration(t *testing.T) {
	bench := func(t *testing.T, name, prefix string) {
		t.Run(name, func(t *testing.T) {
			s := strings.Repeat(prefix, 2048)
			// Find the point where the simdutf library is 10% faster than
			// a pure Go implementation.
			n := sort.Search(len(s), func(n int) bool {
				if n == 0 {
					return true
				}
				s := s[:n]
				bmstdlib := testing.Benchmark(func(b *testing.B) {
					for i := 0; i < b.N; i++ {
						utf8.ValidString(s)
					}
				})
				bmsimd := testing.Benchmark(func(b *testing.B) {
					for i := 0; i < b.N; i++ {
						ValidString(s)
					}
				})
				fmt.Printf("  n=%d: stdlib=%d simdutf=%d\n", n, bmstdlib.NsPerOp(), bmsimd.NsPerOp())
				return bmstdlib.NsPerOp()*100 > bmsimd.NsPerOp()*110
			})
			fmt.Printf("calibration: %s brute-force cutoff = %d\n", name, n)
		})
	}
	// TODO: use a mixed string
	bench(t, "Unicode", "α")
	bench(t, "ASCII", "a")
}

func isASCII(s string) bool {
	for i := 0; i < len(s); i++ {
		if s[i] >= utf8.RuneSelf {
			return false
		}
	}
	return true
}

func TestIsASCIICalibration(t *testing.T) {
	t.Skip("FIXME: place non-ASCII rune at the end of search string")
	bench := func(t *testing.T, name, prefix string) {
		t.Run(name, func(t *testing.T) {
			s := strings.Repeat(prefix, 2048)
			// Find the point where the simdutf library is 10% faster than
			// a pure Go implementation.
			n := sort.Search(2048, func(n int) bool {
				if n == 0 {
					return true
				}
				s := s[:n]
				bmstdlib := testing.Benchmark(func(b *testing.B) {
					for i := 0; i < b.N; i++ {
						isASCII(s)
					}
				})
				bmsimd := testing.Benchmark(func(b *testing.B) {
					for i := 0; i < b.N; i++ {
						IsASCIIString(s)
					}
				})
				fmt.Printf("  n=%d: stdlib=%d simdutf=%d\n", n, bmstdlib.NsPerOp(), bmsimd.NsPerOp())
				return bmstdlib.NsPerOp()*100 > bmsimd.NsPerOp()*110
			})
			fmt.Printf("calibration: brute-force cutoff = %d\n", n)
		})
	}
	// WARN: need to put the unicode rune at the end
	// otherwise it succeeds immediately.
	bench(t, "Unicode", "α")
	bench(t, "ASCII", "a")
}

func BenchmarkValidUTF8(b *testing.B) {
	s := strings.Repeat("#", 2048)
	b.SetBytes(int64(len(s)))
	for i := 0; i < b.N; i++ {
		if !ValidString(s) {
			b.Fatal("FAIL")
		}
	}
}

func BenchmarkIsASCII(b *testing.B) {
	s := strings.Repeat("#", 2048*16)
	b.SetBytes(int64(len(s)))
	for i := 0; i < b.N; i++ {
		if !IsASCIIString(s) {
			b.Fatal("FAIL")
		}
	}
}
