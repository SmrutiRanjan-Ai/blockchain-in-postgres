MODULE_big = lsm3
OBJS = lsm3.o
PGFILEDESC = "lsm3 - MVCC storage with undo log"

EXTENSION = lsm3
DATA = lsm3--1.0.sql

REGRESS = test
REGRESS_OPTS = --temp-config $(POSTGRES_SRCDIR)/contrib/lsm3/lsm3.conf


ifdef USE_PGXS
PG_CONFIG ?= pg_config
PGXS := $(shell $(PG_CONFIG) --pgxs)
include $(PGXS)
else
subdir = contrib/lsm3
top_builddir = $(POSTGRES_SRCDIR)
include $(POSTGRES_SRCDIR)/src/Makefile.global
include $(POSTGRES_SRCDIR)/contrib/contrib-global.mk
endif
