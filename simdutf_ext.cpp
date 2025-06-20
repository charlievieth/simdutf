#include "simdutf_ext.h"
#include "simdutf.h"

bool validate_ascii(const char *buf, size_t len) {
  return simdutf::validate_ascii(buf, len);
}

bool validate_utf8(const char *buf, size_t len) {
  return simdutf::validate_utf8(buf, len);
}

size_t utf16_length_from_utf8(const char *buf, size_t len) {
  return simdutf::utf16_length_from_utf8(buf, len);
}

size_t utf8_length_from_utf16(const char16_t *buf, size_t len) {
  return simdutf::utf8_length_from_utf16(buf, len);
}

size_t convert_utf8_to_utf16(const char *input, size_t length,
                             char16_t *utf16_output) {
  return simdutf::convert_utf8_to_utf16(input, length, utf16_output);
}

size_t convert_utf16_to_utf8(const char16_t *input, size_t length,
                             char *utf8_output) {
  return simdutf::convert_utf16_to_utf8(input, length, utf8_output);
}
