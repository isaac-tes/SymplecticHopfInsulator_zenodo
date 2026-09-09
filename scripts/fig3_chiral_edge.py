"""Figure 3: symplectic (BBdG) Hopf-insulator chiral edge states.

Standalone reproduction of the paper's Fig. 3 (label
``fig:hopf-bbdg-model-chiral-edge-modes``) from precomputed data only, with
no external physics dependencies: just numpy/matplotlib and the vendored
PyWatson helpers (https://github.com/isaac-tes/pywatson) for path/data
management. The only "derived" step left at plot time, the boundary
spectral weight rho(k_par, omega), is a standard Lorentzian
spectral-function formula (Furukawa & Ueda, New J. Phys. 17, 115014 (2015),
Eq. 64), reimplemented directly below rather than imported from anywhere.
Uses the shipped LaTeX-based publication style
(mplstyle/aps_math_new.mplstyle) when a LaTeX installation is available,
falling back to plain mathtext otherwise; see README.md.
"""
import shutil
from pathlib import Path

import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
import matplotlib.colors
import matplotlib.transforms as mtransforms
from matplotlib.collections import LineCollection

from symplectichopfinsulator_zenodo import plotsdir, load_data

MPLSTYLE = Path(__file__).resolve().parents[1] / "mplstyle" / "aps_math_new.mplstyle"
HAS_LATEX = shutil.which("latex") is not None
BM_K = r"\bm{k}" if HAS_LATEX else r"\mathbf{k}"
BM_K_PAR = r"\bm{k}_\parallel" if HAS_LATEX else r"\mathbf{k}_\parallel"

# ---- exact frozen params for the published figure ----
KX_FIXED = 0.9
OMEGA_FRAC = 0.35
ETA = 0.05
UN_MAP = 0.2


def _apply_style():
    if HAS_LATEX:
        plt.style.use(MPLSTYLE)
    else:
        print(f"Note: no LaTeX installation found. Falling back to matplotlib's "
              f"built-in mathtext instead of the shipped style ({MPLSTYLE.name}). "
              f"Install TeX Live/MacTeX/MiKTeX (or use Docker, which has LaTeX "
              f"preinstalled) for pixel-exact publication styling.")
        plt.rcParams.update({
            "font.size": 7, "axes.titlesize": 8, "axes.labelsize": 7,
            "xtick.labelsize": 6, "ytick.labelsize": 6, "legend.fontsize": 6,
        })


def surface_spectral_weight(E_pos, w_u, w_v_minus_k, omega, eta):
    r"""Boundary spectral weight rho(k_par, omega) of a bosonic BdG slab.

    Furukawa & Ueda Eq. (64): every positive-energy mode E_j contributes a
    particle peak at +E_j (residue w_u_j) and a hole peak at -E_j (residue
    w_v_j(-k_par)), each a normalized Lorentzian delta_eta(x) = (eta/pi)/(x^2+eta^2).
    """
    lor_particle = (eta / np.pi) / ((omega - E_pos) ** 2 + eta ** 2)
    lor_hole = (eta / np.pi) / ((omega + E_pos) ** 2 + eta ** 2)
    return np.sum(w_u * lor_particle + w_v_minus_k * lor_hole, axis=-1)


def edge_cmap(base="viridis_r"):
    cmap = plt.get_cmap(base)
    return mpl.colors.ListedColormap(cmap(np.linspace(0.25, 1.0, 256)), name="edge_localized")


def band_line_segments(x, Y, C):
    """Per-band line segments + per-segment color (midpoint average of C)."""
    n_bands = Y.shape[1]
    segs, cols = [], []
    for n in range(n_bands):
        y = Y[:, n]
        valid = np.isfinite(y)
        keep = valid[:-1] & valid[1:]
        if not np.any(keep):
            continue
        pts = np.column_stack([x, y])
        segs.append(np.stack([pts[:-1][keep], pts[1:][keep]], axis=1))
        cols.append(0.5 * (C[:-1, n][keep] + C[1:, n][keep]))
    if not segs:
        return np.empty((0, 2, 2)), np.empty((0,))
    return np.concatenate(segs, axis=0), np.concatenate(cols)


def main():
    try:
        d = load_data("fig3_chiral_edge/chiral_edge.h5")
    except FileNotFoundError as e:
        raise FileNotFoundError(
            "Fig. 3's full dataset (~256MB) is hosted on Zenodo rather than in "
            "this repo (GitHub's 100MB file limit). Download it and place it at "
            "data/fig3_chiral_edge/chiral_edge.h5. See README.md for the link. "
            f"Underlying error: {e}"
        ) from e
    kx_list = d["kx_list"]              # (21,); full dataset spans a kx scan,
                                         # we only use the KX_FIXED slice below
    ikx = int(np.argmin(np.abs(kx_list - KX_FIXED)))
    if not np.isclose(kx_list[ikx], KX_FIXED, atol=1e-9):
        raise ValueError(f"KX_FIXED={KX_FIXED:g} not in stored kx_list {kx_list.tolist()}")

    E_band = d["E_band"][ikx]              # (2 m, 3 Un, 101 ky, 128)
    part_band = d["part_band"][ikx]
    unstable_band = d["unstable_band"][ikx]
    gap_bounds = d["gap_bounds"][ikx]        # (2 m, 3 Un, 2)
    surf_ev = d["surf_ev"]              # (2 m, 301, 301, 64) positive branch only
    surf_wu = d["surf_wu"]
    surf_wv = d["surf_wv"]
    surf_unstable = d["surf_unstable"]
    kx_grid = d["kx_grid"]
    ky_grid = d["ky_grid"]
    ky_band = d["ky_band"]
    m_values = d["m_values"]
    Un_values = d["Un_values"]

    nm, nUn = len(m_values), len(Un_values)
    n_surface_bz = len(kx_grid)
    iu_map = int(np.argmin(np.abs(Un_values - UN_MAP)))

    _apply_style()
    EDGE_CMAP = edge_cmap()

    # ---- column-4 surface map, one per m ----
    omega_ref = np.empty(nm)
    A_map = np.empty((nm, n_surface_bz, n_surface_bz))
    for im in range(nm):
        gap_lo, gap_hi = gap_bounds[im, iu_map]
        if np.isfinite(gap_lo):
            omega_ref[im] = gap_lo + OMEGA_FRAC * (gap_hi - gap_lo)
        else:
            omega_ref[im] = np.nanmedian(np.abs(E_band[im, iu_map]))
        wv_minus_k = surf_wv[im][::-1, ::-1, :]
        A = surface_spectral_weight(surf_ev[im], surf_wu[im], wv_minus_k, omega_ref[im], ETA)
        A_map[im] = np.where(surf_unstable[im], np.nan, A)
        print(f"m={m_values[im]:g}: omega*={omega_ref[im]:.2f}")

    # ---- figure layout ----
    lwd_edge, gridalpha, yloc_title = 1, 0.2, 0.98
    figszwidth = 2.5 * 3.52913
    figsize = (figszwidth, 3.75)
    width_ratios_outer = [3, 1.15]
    omega_ref_color, omega_ref_lw, omega_ref_ls = "crimson", 0.75, "--"
    cbar_ticklabel_fontsize, cbar_shared_fraction, cbar_shared_pad = 8, 0.025, 0.02
    spectral_cmap = "magma"
    gap_zoom_margin = 2

    fig = plt.figure(figsize=figsize)
    outer = fig.add_gridspec(1, 2, width_ratios=width_ratios_outer, wspace=0.11)
    gs_grid = outer[0].subgridspec(nm, nUn, wspace=0.175, hspace=0.35)
    gs_spec = outer[1].subgridspec(nm, 1, hspace=0.35)
    axes = np.empty((nm, 4), dtype=object)
    for im in range(nm):
        for iu in range(nUn):
            axes[im, iu] = fig.add_subplot(gs_grid[im, iu])
        axes[im, 3] = fig.add_subplot(gs_spec[im, 0])

    sc = None
    for im, m in enumerate(m_values):
        for iu, Un in enumerate(Un_values):
            ax = axes[im, iu]
            E = E_band[im, iu]
            part = part_band[im, iu]
            unstable = unstable_band[im, iu]
            smask = E > 0  # particle sector
            Eplot = np.where(unstable[:, None] | ~smask, np.nan, E)
            ky_over_pi = ky_band / np.pi

            segs, seg_colors = band_line_segments(ky_over_pi, Eplot, part)
            order = np.argsort(np.nan_to_num(seg_colors))
            sc = LineCollection(segs[order], cmap=EDGE_CMAP,
                                 norm=mpl.colors.Normalize(vmin=0, vmax=1),
                                 linewidths=lwd_edge, capstyle="round")
            sc.set_array(seg_colors[order])
            ax.add_collection(sc)
            ax.autoscale_view()
            ax.set_xlim(ky_over_pi.min(), ky_over_pi.max())

            gap_lo, gap_hi = gap_bounds[im, iu]
            if np.isfinite(gap_lo):
                mgn = gap_zoom_margin * (gap_hi - gap_lo)
                ax.set_ylim(gap_lo - mgn, gap_hi + mgn)
            if iu == iu_map:
                trans = mtransforms.blended_transform_factory(ax.transAxes, ax.transData)
                ax.axhline(omega_ref[im], color=omega_ref_color, lw=omega_ref_lw,
                           ls=omega_ref_ls, alpha=1, zorder=-5)
                x_loc, y_loc = (0.1, omega_ref[im] + 0.15) if im == 0 else (0.3, omega_ref[im] + 0.15)
                ax.text(x_loc, y_loc, r"$\omega^*$", transform=trans, color=omega_ref_color,
                        fontsize="small", ha="left", va="bottom", zorder=6,
                        bbox=dict(boxstyle="square, pad=0.1", fc="white", ec="none", alpha=0.75))
            ax.set_xlabel(r"$k_y/\pi$", labelpad=0)
            ax.set_xticks([-1, -0.5, 0, 0.5, 1])
            if iu == 0:
                ax.set_ylabel(rf"$m/J={m:g}$" + "\n" + rf"Quasiparticle energy $E({BM_K})/J$")
            if im == 0:
                ax.set_title(rf"$Un/J={Un:g}$" + rf", $k_{{x}}/\pi={KX_FIXED:.1f}$", y=yloc_title)
            ax.grid(alpha=gridalpha, zorder=-10)
            ax.tick_params(axis="both", length=2.5)

    for im, m in enumerate(m_values):
        ax = axes[im, 3]
        pcm = ax.pcolormesh(kx_grid / np.pi, ky_grid / np.pi, A_map[im].T,
                             shading="nearest", cmap=spectral_cmap, rasterized=True)
        ax.text(0.5, 0.35, rf"$Un/J={UN_MAP:g}$", transform=ax.transAxes, color="white",
                fontsize=7, ha="center", va="center", zorder=6)
        ax.text(0.485, 0.25, rf"$m/J={m:g}$", transform=ax.transAxes, color="white",
                fontsize=7, ha="center", va="center", zorder=6)
        ax.set_xticks([-1, -0.5, 0, 0.5, 1])
        ax.set_xlabel(r"$k_x/\pi$", labelpad=-3)
        ax.set_ylabel(r"$k_y/\pi$", labelpad=-5)
        ax.set_title(rf"$\omega^*/J={omega_ref[im]:.2f}$", y=yloc_title, x=0.45)
        ax.set_aspect("equal")
        ax.axvline(KX_FIXED, color=omega_ref_color, lw=omega_ref_lw, ls=omega_ref_ls, alpha=1, zorder=1)
        cb = fig.colorbar(pcm, ax=ax, shrink=1, fraction=0.1, pad=0.04)
        cb.ax.tick_params(direction="out", length=2.5, labelsize=cbar_ticklabel_fontsize)
        ax.tick_params(length=2.5)
        cb.ax.set_title(rf"$A({BM_K_PAR},\omega^*)$", y=0.99)

    for im in range(nm):
        cb = fig.colorbar(sc, ax=axes[im, :nUn].tolist(), fraction=cbar_shared_fraction, pad=cbar_shared_pad)
        cb.ax.tick_params(direction="out", length=2.5, labelsize=cbar_ticklabel_fontsize)
        cb.set_label(r"Edge participation", labelpad=1)

    for im, lab in enumerate(["(a)", "(b)"][:nm]):
        axes[im, 0].text(-0.35, 1.15, lab, transform=axes[im, 0].transAxes, fontsize=9)
    for im, lab in enumerate(["(c)", "(d)"][:nm]):
        axes[im, 3].text(-0.25, 1.15, lab, transform=axes[im, 3].transAxes, fontsize=9)

    out = plotsdir() / "fig3_chiral_edge"
    fig.savefig(out.with_suffix(".pdf"), bbox_inches="tight", dpi=600)
    fig.savefig(out.with_suffix(".png"), bbox_inches="tight", dpi=600)
    print(f"Saved {out.with_suffix('.pdf')}")
    return fig


if __name__ == "__main__":
    main()
