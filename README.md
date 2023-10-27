# Omnes pro uno

Unofficial implementation of [_Omnes pro uno: Practical multi-writer encrypted database_][Omnes pro uno]

[Omnes pro uno]: https://www.usenix.org/conference/usenixsecurity22/presentation/wang-jiafan

## Dependencies

In addition to [Poetry], you also need to install [Charm-Crypto].
Charm-Crypto installation can be difficult nowadays since many dependencies are outdated.
We provide a Docker image [myl7/charm-crypto] with Charm-Crypto installed for your convenience.
This Docker image is released on Docker Hub.
The original Dockerfile is available at [docker/charm.dockerfile](docker/charm.dockerfile).
In that case you need to run `poetry config virtualenvs.create false` to reuse the system dependencies.

[Poetry]: https://python-poetry.org/
[Charm-Crypto]: https://jhuisi.github.io/charm/
[myl7/charm-crypto]: https://hub.docker.com/r/myl7/charm-crypto

## License

Copyright (C) myl7

SPDX-License-Identifier: Apache-2.0
