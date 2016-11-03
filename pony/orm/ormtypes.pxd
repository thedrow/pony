cimport cython

@cython.locals(pos=cython.uint)
cpdef tuple parse_raw_sql(const char *sql)
