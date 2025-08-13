#ifndef SIMDUTF_EXT_H
#define SIMDUTF_EXT_H
#ifdef __cplusplus
extern "C" {
#endif // __cplusplus

#include <stdbool.h>
#include <stddef.h>

/**
 * Validate the ASCII string.
 *
 * Overridden by each implementation.
 *
 * @param buf the ASCII string to validate.
 * @param len the length of the string in bytes.
 * @return true if and only if the string is valid ASCII.
 */
bool validate_ascii(const char *buf, size_t len);

/**
 * Validate the UTF-8 string. This function may be best when you expect
 * the input to be almost always valid. Otherwise, consider using
 * validate_utf8_with_errors.
 *
 * Overridden by each implementation.
 *
 * @param buf the UTF-8 string to validate.
 * @param len the length of the string in bytes.
 * @return true if and only if the string is valid UTF-8.
 */
bool validate_utf8(const char *buf, size_t len);

/**
 * Return the version of the linked simdutf library.
 *
 * @return the version of the simdutf library.
 */
const char *simdutf_version(void);

#ifdef __cplusplus
}
#endif // __cplusplus
#endif // SIMDUTF_EXT_H
