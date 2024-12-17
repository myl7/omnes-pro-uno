# syntax=docker/dockerfile:1
# GCC 14 does not work for GMP 5.x compilation
FROM gcc:13
WORKDIR /app

RUN apt-get update \
  && apt-get install -y --no-install-recommends flex bison git \
  && rm -rf /var/lib/apt/lists/*

ARG GMP_VER=5.1.3 \
  PBC_VER=0.5.14 \
  PYTHON_VER=3.10.13 \
  CHARM_COMMIT_HASH=bf9933fe843a0b78c07991452114fc4e4be2e71a
# Charm requires GMP 5.x, which is too old for most software sources
RUN curl -O https://gmplib.org/download/gmp/gmp-${GMP_VER}.tar.xz \
  && tar xf gmp-${GMP_VER}.tar.xz \
  && cd gmp-${GMP_VER} \
  && ./configure --prefix=/usr \
  && make -j $(nproc --all) \
  && make check -j $(nproc --all) \
  && make install \
  && rm -rf /app && mkdir /app && cd /app
# Latest PBC
RUN curl -O https://crypto.stanford.edu/pbc/files/pbc-${PBC_VER}.tar.gz \
  && tar xf pbc-${PBC_VER}.tar.gz \
  && cd pbc-${PBC_VER} \
  && ./configure --prefix=/usr \
  && make -j $(nproc --all) \
  && make install \
  && rm -rf /app && mkdir /app && cd /app
# Python 3.11 cannot work (`#include <longintrepr.h>` fails).
# It seems that Python 3.11 introduces some C ABI changes.
# Python 3.10 works fine.
RUN curl -O https://www.python.org/ftp/python/${PYTHON_VER}/Python-${PYTHON_VER}.tgz \
  && tar xf Python-${PYTHON_VER}.tgz \
  && cd Python-${PYTHON_VER} \
  && ./configure --enable-optimizations \
  && make -j $(nproc --all) \
  && make install \
  && rm -rf /app && mkdir /app && cd /app
# Latest Charm.
# OpenSSL 1.1 works fine (so no need for 1.0) but 3 seems not to work.
RUN git clone https://github.com/JHUISI/charm.git \
  && cd charm \
  && git checkout ${CHARM_COMMIT_HASH} \
  && ./configure.sh --prefix=/usr \
  && make -j $(nproc --all) \
  && make install \
  && rm -rf /app && mkdir /app && cd /app

# The `gcc` base image includes many development tools like `curl` and `xz`, which are helpful.
# If you want a slim image, copy libraries and headers from this one.
