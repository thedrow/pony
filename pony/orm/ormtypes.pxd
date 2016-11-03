cimport cython

@cython.locals(pos=cython.uint)
cpdef tuple parse_raw_sql(const char *sql)

cdef class RawSQL(object):
  cpdef public char *sql
  cpdef public tuple items
  cpdef public tuple codes
  cpdef public tuple values
  cpdef public tuple types
  cpdef public object result_type
