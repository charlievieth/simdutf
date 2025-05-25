package simdutf

import (
	"bytes"
	"flag"
	"fmt"
	"slices"
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

func init() {
	// Increase the length of test cases so that the input
	// surpasses the pure-go/simdutf cutover.
	prefix := strings.Repeat("#", 4096)
	for _, t := range validTests {
		validTests = append(validTests, ValidTest{
			in:  prefix + t.in,
			out: t.out,
		})
	}
}

func TestValid(t *testing.T) {
	for _, tt := range validTests {
		if Valid([]byte(tt.in)) != tt.out {
			t.Errorf("Valid(%q) = %v; want %v", tt.in, !tt.out, tt.out)
		}
		if ValidString(tt.in) != tt.out {
			t.Errorf("ValidString(%q) = %v; want %v", tt.in, !tt.out, tt.out)
		}
	}
}

func TestValidAllocations(t *testing.T) {
	t.Run("IsASCII", func(t *testing.T) {
		p := []byte("你好世界, hello world. 你好世界, hello world. 你好世界, hello world.")
		testing.AllocsPerRun(100, func() {
			Valid(p)
		})
	})
	t.Run("IsASCIIString", func(t *testing.T) {
		testing.AllocsPerRun(100, func() {
			ValidString("你好世界, hello world. 你好世界, hello world. 你好世界, hello world.")
		})
	})
}

func TestIsASCII(t *testing.T) {
	tests := validTests
	s := strings.Repeat(" ", 18*1024)
	for i := range 18 * 1024 {
		tests = append(tests, ValidTest{in: s[i:], out: true})
	}
	for _, tt := range tests {
		want := isASCIIString(tt.in)
		if IsASCII([]byte(tt.in)) != want {
			t.Errorf("IsASCII(%q) = %v; want %v", tt.in, !want, want)
		}
		if IsASCIIString(tt.in) != want {
			t.Errorf("IsASCIIString(%q) = %v; want %v", tt.in, !want, want)
		}
	}
}

func TestIsASCIIAllocations(t *testing.T) {
	t.Run("IsASCII", func(t *testing.T) {
		p := []byte("你好世界, hello world. 你好世界, hello world. 你好世界, hello world.")
		testing.AllocsPerRun(100, func() {
			IsASCII(p)
		})
	})
	t.Run("IsASCIIString", func(t *testing.T) {
		testing.AllocsPerRun(100, func() {
			IsASCIIString("你好世界, hello world. 你好世界, hello world. 你好世界, hello world.")
		})
	})
}

var calibrate = flag.Bool("calibrate", false, "Run calibration tests to "+
	"determine the optimal go/simdutf cutoff")

func TestValidCalibration(t *testing.T) {
	if !*calibrate {
		t.Skip("The -calibrate flag needs to be provided to run this test.")
	}
	bench := func(t *testing.T, name, prefix string) {
		t.Run(name, func(t *testing.T) {
			s := bytes.Repeat([]byte(prefix), 2048)
			// Find the point where the simdutf library is 10% faster than
			// a pure Go implementation.
			n := sort.Search(len(s), func(n int) bool {
				if n == 0 {
					return true
				}
				s := s[:n]
				bmStdLib := testing.Benchmark(func(b *testing.B) {
					for i := 0; i < b.N; i++ {
						utf8.Valid(s)
					}
				})
				bmSimd := testing.Benchmark(func(b *testing.B) {
					for i := 0; i < b.N; i++ {
						validateUTF8(&s[0], len(s))
					}
				})
				fmt.Printf("  n=%d: stdlib=%d simdutf=%d\n", n, bmStdLib.NsPerOp(), bmSimd.NsPerOp())
				return bmStdLib.NsPerOp()*100 > bmSimd.NsPerOp()*110
			})
			fmt.Printf("calibration: %s brute-force cutoff = %d\n", name, n)
		})
	}
	// TODO: use a mixed string
	bench(t, "Unicode", "α")
	bench(t, "ASCII", "a")
}

func TestIsASCIICalibration(t *testing.T) {
	if !*calibrate {
		t.Skip("The -calibrate flag needs to be provided to run this test.")
	}

	// Instead of just setting a single bit to >=128 use a valid
	// UTF-8 sequence since that is more realistic and setting a
	// single ivalid bit really hits the simdutf libs performance.
	s := bytes.Repeat([]byte{'#'}, 16*1024)
	copy(s[len(s)-len("α"):], "α")

	// Use a binary search to find the point where the simdutf library is 10%
	// faster than a pure Go implementation.
	n := sort.Search(len(s), func(n int) bool {
		if n == 0 {
			return true
		}
		s := s[len(s)-n:]
		if !utf8.Valid(s) {
			t.Fatal("invalid utf8")
		}
		bmStdLib := testing.Benchmark(func(b *testing.B) {
			for i := 0; i < b.N; i++ {
				isASCII(s)
			}
		})
		bmSimd := testing.Benchmark(func(b *testing.B) {
			for i := 0; i < b.N; i++ {
				validateASCII(&s[0], len(s))
			}
		})
		fmt.Printf("  n=%d: stdlib=%d simdutf=%d\n", n, bmStdLib.NsPerOp(), bmSimd.NsPerOp())
		return bmStdLib.NsPerOp()*100 > bmSimd.NsPerOp()*110
	})
	fmt.Printf("calibration: IsASCII cutoff = %d\n", n)
}

var longStringMostlyASCII string // ~100KB, ~97% ASCII
var longStringJapanese string    // ~100KB, non-ASCII

func init() {
	const japanese = "日本語日本語日本語日"
	var b strings.Builder
	b.Grow(100_000)
	for i := 0; b.Len() < 100_000; i++ {
		if i%100 == 0 {
			b.WriteString(japanese)
		} else {
			b.WriteString("0123456789")
		}
	}
	longStringMostlyASCII = b.String()
	longStringJapanese = strings.Repeat(japanese, 100_000/len(japanese))
}

var benchSizes = []int{10, 32, 64, 128, 256, 512, 4 << 10, 16 << 10, 4 << 20, 64 << 20}

func valName(x int) string {
	if s := x >> 20; s<<20 == x {
		return fmt.Sprintf("%dM", s)
	}
	if s := x >> 10; s<<10 == x {
		return fmt.Sprintf("%dK", s)
	}
	return fmt.Sprint(x)
}

var bmbuf []byte

func benchBytes(b *testing.B, fn func(b *testing.B, buf []byte)) {
	for _, n := range benchSizes {
		b.Run(valName(n), func(b *testing.B) {
			defer func() {
				clear(bmbuf)
				bmbuf = bmbuf[:cap(bmbuf)]
			}()
			if len(bmbuf) < n {
				bmbuf = slices.Grow(bmbuf, n)
			}
			b.SetBytes(int64(n))
			fn(b, bmbuf[:n:n])
		})
	}
}

func BenchmarkValid(b *testing.B) {
	fillBuffer := func(p []byte, src string) {
		for n := 0; n < len(p); {
			n += copy(p[n:], src)
		}
		// Since we may have copied only part of a UTF-8 encoded
		// sequence we zero out the end of the buffer until it is
		// valid.
		for i := len(p) - 1; i >= 0 && !Valid(p); i-- {
			p[i] = 0
		}
	}
	bench := func(name, src string) {
		b.Run(name, func(b *testing.B) {
			benchBytes(b, func(b *testing.B, p []byte) {
				if src != "" {
					fillBuffer(p, src)
				}
				if !Valid(p) {
					b.Fatal("bench buffer not valid")
				}
				for b.Loop() {
					_ = Valid(p)
				}
			})
		})
	}
	bench("ASCII", "")
	bench("MostlyASCII", longStringMostlyASCII)
	bench("Japanese", longStringJapanese)
}

func BenchmarkIsASCII(b *testing.B) {
	benchBytes(b, func(b *testing.B, p []byte) {
		if !IsASCII(p) {
			b.Fatalf("bench buffer not valid: %q", bmbuf)
		}
		for b.Loop() {
			_ = IsASCII(p)
		}
	})
}
