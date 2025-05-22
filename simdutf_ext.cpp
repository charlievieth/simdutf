#include "simdutf_ext.h"
#include "simdutf/simdutf.h"

bool validate_ascii(const char *buf, size_t len) {
  return simdutf::validate_ascii(buf, len);
}

bool validate_utf8(const char *buf, size_t len) {
  return simdutf::validate_utf8(buf, len);
}
