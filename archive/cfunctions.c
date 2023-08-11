#include <stdint.h>

/* Only valid input should be passed in. 
 * All the checking should be done in the Python file. */

/* Returns 1 if n is prime, 0 otherwise. */
int prime(uint64_t n) {
    if (n == 2 || n == 3) return 1;
    if (n % 2 == 0 || n % 3 == 0) return 0;
    for (uint64_t i = 5; i*i <= n; i+=6) {
        if (n % i == 0 || n % (i + 2) == 0) {
            return 0;
        }
    }
    return 1;
}

/* Returns the nth number in the Fibonocci sequence. */
// fib(95) > UINT64_MAX
uint64_t fib(int n) {
    if (n == 1) return 0;
    if (n == 2) return 1;
    uint64_t prev = 0, curr = 1;
    for (int i = 2; i < n; i++) {
        curr += prev;
        prev = curr - prev;
    }
    return curr;
}