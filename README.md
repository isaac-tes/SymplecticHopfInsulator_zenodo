# Symplectic Hopf Insulator: figure data and reproduction scripts

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.22686505.svg)](https://doi.org/10.5281/zenodo.22686505)
[![arXiv](https://img.shields.io/badge/arXiv-2609.10541-b31b1b.svg)](https://arxiv.org/abs/2609.10541)


Data and self-contained plotting scripts that reproduce Figures 1-3 of the
paper on the symplectic (bosonic Bogoliubov-de Gennes) Hopf insulator. This
repository holds only what's needed to regenerate those three published
figures from already-computed numerical results.

| Figure | Script | Data | What it shows |
|---|---|---|---|
| Fig. 1 | `scripts/fig1_hs_spectrum.py` | `data/fig1_hs_spectrum/hs_spectrum.h5` (in repo, 80KB) | BBdG quasiparticle spectrum along a high-symmetry path, for mass parameters $m/J \in \{0.05, 1, 2\}$ and interaction strengths $Un/J \in \{0, 0.2, 0.4\}$ |
| Fig. 2 | `scripts/fig2_phase_diagram.py` | `data/fig2_phase_diagram/phase_diagram.h5` (in repo, 52KB) | Symplectic Hopf index $\chi$ and minimum BdG gap phase diagram vs. $m$ and $Un$, plus 1D slices |
| Fig. 3 | `scripts/fig3_chiral_edge.py` | `data/fig3_chiral_edge/chiral_edge.h5` (on Zenodo, ~268MB, see below) | Chiral edge-state spectra and boundary spectral function $A(\mathbf{k}_\parallel,\omega)$ for an open-boundary slab |

## Getting Fig. 3's data

Figs. 1-2's data ships directly in this repository. Fig. 3's full,
untrimmed dataset is about 268MB, over GitHub's 100MB per-file limit, so
it's hosted as its own file on the Zenodo record for this repository:

- Zenodo DOI: https://doi.org/10.5281/zenodo.22686505
- Download [`chiral_edge.h5`](https://zenodo.org/records/22691589/files/chiral_edge.h5?download=1)
  (268 MB, md5: `05cfb7fb64e0e3101aa1c26723f7e198`) from that record and place it at
  `data/fig3_chiral_edge/chiral_edge.h5` in your local checkout (or Docker bind-mount, see below).

Figs. 1-2 reproduce with no extra steps. Fig. 3 needs this download first.

## Publication styling (LaTeX)

The exact paper styling (Computer Modern font, bold-italic $\bm{k}$ vectors,
tick/label sizing) comes from a shipped matplotlib style file,
[`mplstyle/aps_math_new.mplstyle`](mplstyle/aps_math_new.mplstyle), which
uses `text.usetex=True` with the `amsmath`/`amssymb`/`bm` LaTeX packages.
Each script uses this style automatically if a `latex` executable is found
on `PATH`, and otherwise falls back to matplotlib's built-in mathtext
(still fully readable, just not pixel-identical to the paper: sans-serif
font, upright $\mathbf{k}$ instead of bold-italic $\bm{k}$), printing a
note when it does so.

Docker has a full LaTeX toolchain preinstalled
(`texlive-latex-recommended`, `texlive-latex-extra`,
`texlive-fonts-recommended`, `cm-super`, `dvipng`), so it's the only path
that guarantees pixel-exact styling regardless of your machine. For local
`uv`/`pip` runs to get the same result, install a LaTeX distribution with
those packages: [TeX Live](https://www.tug.org/texlive/) (Linux),
[MacTeX](https://www.tug.org/mactex/) (macOS), or
[MiKTeX](https://miktex.org/) (Windows).

## Long-term reproducibility (Docker image archive)

The `Dockerfile`'s base image is pinned by digest
(`ghcr.io/astral-sh/uv@sha256:...`), not the mutable
`python3.12-bookworm-slim` tag, so a from-scratch rebuild always starts from
the exact same base layer rather than whatever that tag has since been
rebuilt to. Python dependencies are pinned the same way, via `uv.lock`. The
`apt-get install`ed LaTeX toolchain isn't pinned this precisely, since Debian
doesn't offer per-package digests the way container registries offer image
digests, so a rebuild years from now could still pick up a slightly
different TeX Live point release.

For a guarantee independent of any registry or package mirror, this
repository's Zenodo record also archives the fully built image as a
`.tar.gz`, separate from the Dockerfile recipe above:

- Docker image archive: [`symplectic-hopf-figures-image.tar.gz`](https://zenodo.org/records/22691589/files/symplectic-hopf-figures-image.tar.gz?download=1) (407 MB, md5: `58b54e69b618b3af1e528a3bdf29c883`)

Loading that file reproduces the exact image byte-for-byte, with no build
step and no network access required at all:

```bash
docker load < symplectic-hopf-figures-image.tar.gz
docker run --rm --network none \
  -v "$PWD/plots:/app/plots" \
  -v "$PWD/data/fig3_chiral_edge:/app/data/fig3_chiral_edge:ro" \
  symplectic-hopf-figures:latest
```

(`--network none` is only there to demonstrate that no internet access is
needed once the image is loaded, it isn't required.)

## How to reproduce

### Option A: Docker (no local Python needed)

Requires [Docker Desktop](https://docs.docker.com/get-started/get-docker/)
(macOS/Windows) or `docker` + the `docker compose` plugin (Linux).

1. Get the code:
```bash
git clone <this-repo-url>
cd SymplecticHopfInsulator_zenodo
```

2. Download Fig. 3's data (optional):
```bash
mkdir -p data/fig3_chiral_edge
# download chiral_edge.h5 from the Zenodo DOI above into that directory
```

3. Build and run:
```bash
docker compose run reproduce
```
This builds the image (first run only, about 1-2 min) and runs all three
scripts. Figures land in `./plots/` on your host machine. If Fig. 3's data
wasn't downloaded, Figs. 1-2 still run and Fig. 3 is skipped with a clear
message rather than failing.

Equivalent manual (non-compose) form:
```bash
docker build -t symplectic-hopf-figures .
docker run --rm \
  -v "$PWD/plots:/app/plots" \
  -v "$PWD/data/fig3_chiral_edge:/app/data/fig3_chiral_edge:ro" \
  symplectic-hopf-figures
```

Interactive debugging shell (drops you into the container with the repo
mounted, for poking around or re-running one script at a time):
```bash
docker compose run shell
# inside the container:
uv run python scripts/fig1_hs_spectrum.py
```

Rebuilding after a change (e.g. you edited a script or pulled a new
commit): `docker compose run` reuses an existing `symplectic-hopf-figures`
image if one is already present locally, so it won't pick up code changes
on its own. Rebuild explicitly first:
```bash
docker compose build --no-cache
docker compose run reproduce
```

Instead of building from the `Dockerfile`, you can also load the exact image
archived on Zenodo (see "Long-term reproducibility" above) and skip the
build step entirely:
```bash
docker load < symplectic-hopf-figures-image.tar.gz
docker run --rm \
  -v "$PWD/plots:/app/plots" \
  -v "$PWD/data/fig3_chiral_edge:/app/data/fig3_chiral_edge:ro" \
  symplectic-hopf-figures:latest
```
This is the strongest reproducibility guarantee: the same image bytes
regardless of what happens to the base image tag, Debian's package mirrors,
or PyPI in the future.

### Option B: local Python with `uv` (recommended for local runs)

[`uv`](https://docs.astral.sh/uv/) is a fast Python package/project manager;
`pyproject.toml`/`uv.lock` pin every dependency to an exact version.

```bash
# install uv if you don't have it:  curl -LsSf https://astral.sh/uv/install.sh | sh
git clone <this-repo-url>
cd SymplecticHopfInsulator_zenodo
uv sync                                   # creates .venv, installs exact pinned versions
uv run python scripts/fig1_hs_spectrum.py
uv run python scripts/fig2_phase_diagram.py
uv run python scripts/fig3_chiral_edge.py  # after downloading its data, see above
```

### Option C: local Python with `pip` / `venv`

No `uv` required: a standard virtual environment works too.

```bash
git clone <this-repo-url>
cd SymplecticHopfInsulator_zenodo
python3 -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install --upgrade pip
pip install -e .                 # installs numpy/matplotlib/h5py + this repo's package
python scripts/fig1_hs_spectrum.py
python scripts/fig2_phase_diagram.py
python scripts/fig3_chiral_edge.py
```

`pip install -e .` reads the same `pyproject.toml` as `uv` (dependencies:
`numpy`, `matplotlib`, `h5py`), but it won't reproduce the exact pinned
patch versions in `uv.lock`. Either way, run the scripts from the repo
root: they locate `data/` and write `plots/` relative to the directory
containing `pyproject.toml`.

### What you get

Each script writes a `.pdf` and `.png` to `plots/` (e.g.
`plots/fig1_hs_spectrum.pdf`).

## Data provenance

The `.h5` files in `data/` are derived, reduced products of larger internal
simulation runs (a full $(m, N, U)$ parameter sweep for Fig. 2, a full
surface-Brillouin-zone slab diagonalization for Fig. 3, and a one-off
high-symmetry-path spectrum computation for Fig. 1). Figs. 1-2's files are
trimmed to exactly the arrays and parameter slices the published figures
use. Fig. 3's file is kept in full (no trimming).

## License

- Code (`scripts/`, `src/`, `Dockerfile`, `pyproject.toml`): [MIT](LICENSE)
- Data (`data/`, and the Zenodo-hosted Fig. 3 file): [CC-BY-4.0](LICENSE-DATA)

## Citation

If you use this data or code, please cite both the paper and this repository's
Zenodo record:

- Paper: I. Tesfaye and G. Palumbo, "Symplectic Hopf Insulator: Delicate Topology in Bosonic Bogoliubov-de Gennes Systems," (2026) [arXiv:2609.10541](http://arxiv.org/abs/2609.10541).

- Software/data: https://doi.org/10.5281/zenodo.22686506
