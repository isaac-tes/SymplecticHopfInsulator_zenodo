# =============================================================================
# Dockerfile for SymplecticHopfInsulator_zenodo
# Adapted from a PyWatson-generated scaffold (https://github.com/isaac-tes/pywatson)
#
# Figs. 1-2 data ships inside the image (small). Fig. 3's full dataset
# (~256MB) is hosted on Zenodo (over GitHub's 100MB file limit) and must be
# bind-mounted at run time. See README.md for the download step and the
# exact `docker run`/`docker compose` invocations.
#
# Includes a LaTeX toolchain so the shipped publication style
# (mplstyle/aps_math_new.mplstyle, text.usetex=True with amsmath/amssymb/bm)
# renders exactly as in the paper, with no host LaTeX install required.
# This is the one path guaranteed to reproduce pixel-exact figures.
#
# Build:
#   docker build -t symplectic-hopf-figures .
# =============================================================================

# Pinned by digest, not just the "python3.12-bookworm-slim" tag: the tag is a
# moving pointer that Astral rebuilds over time (new Debian patches, new uv
# releases), so a `docker build` today and one in a few years could silently
# pull different base layers even from this same Dockerfile. The digest is
# immutable. To intentionally move to a newer base image later, re-resolve it
# with `docker pull ghcr.io/astral-sh/uv:python3.12-bookworm-slim` followed by
# `docker inspect --format='{{index .RepoDigests 0}}' ...` and update the line
# below.
FROM ghcr.io/astral-sh/uv@sha256:e5b65587bce7de595f299855d7385fe7fca39b8a74baa261ba1b7147afa78e58

RUN apt-get update && apt-get install -y --no-install-recommends \
        texlive-latex-recommended texlive-latex-extra texlive-fonts-recommended \
        cm-super dvipng \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY pyproject.toml uv.lock README.md ./
COPY src/ src/
RUN uv sync --frozen --no-dev

ENV UV_NO_SYNC=1

COPY scripts/ scripts/
COPY mplstyle/ mplstyle/
COPY data/fig1_hs_spectrum/ data/fig1_hs_spectrum/
COPY data/fig2_phase_diagram/ data/fig2_phase_diagram/

VOLUME ["/app/plots"]

CMD ["sh", "-c", "\
  uv run python scripts/fig1_hs_spectrum.py && \
  uv run python scripts/fig2_phase_diagram.py && \
  if [ -f data/fig3_chiral_edge/chiral_edge.h5 ]; then \
    uv run python scripts/fig3_chiral_edge.py; \
  else \
    echo 'Skipping Fig. 3: data/fig3_chiral_edge/chiral_edge.h5 not mounted (see README.md).'; \
  fi \
"]
