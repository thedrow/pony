cimport cython

@cython.locals(z = cython.uint,
               start = cython.uint,
               i = cython.uint,
               counter = cython.uint)
cpdef tuple parse_expr(const char *s, unsigned int pos=?)
