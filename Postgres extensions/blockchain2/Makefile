# contrib/blockchain2/Makefile

EXTENSION = blockchain2
DATA = blockchain2--1.0.sql
PGFILEDESC = "blockchain2"
REGRESS = blockchain2

ifdef USE_PGXS
PG_CONFIG = pg_config
PGXS := $(shell $(PG_CONFIG) --pgxs)
include $(PGXS)
else
subdir = contrib/blockchain2
top_builddir = ../..
include $(top_builddir)/src/Makefile.global
include $(top_srcdir)/contrib/contrib-global.mk
endif
