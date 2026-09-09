"""Figure 2: symplectic Hopf-index / BdG-gap phase diagram vs. mass parameter
and interaction strength, plus 1D slices.

Standalone reproduction of the paper's Fig. 2 (label
``fig:phase-diagram-hopf-bdg``) from precomputed data only, with no
external physics dependencies: just numpy/matplotlib and the vendored
PyWatson helpers (https://github.com/isaac-tes/pywatson) for path/data
management. Uses the shipped LaTeX-based publication style
(mplstyle/aps_math_new.mplstyle) when a LaTeX installation is available,
falling back to plain mathtext otherwise; see README.md.
"""
import shutil
from pathlib import Path

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors

from symplectichopfinsulator_zenodo import plotsdir, load_data

MPLSTYLE = Path(__file__).resolve().parents[1] / "mplstyle" / "aps_math_new.mplstyle"
HAS_LATEX = shutil.which("latex") is not None


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


def main():
    d = load_data("fig2_phase_diagram/phase_diagram.h5")
    hopf_index_ar = d["hopf_index_ar"]      # (m, N, U, band)
    min_bdg_gap_ar = d["min_bdg_gap_ar"]    # (m, N, U)
    min_gap_ar = d["min_gap_ar"]            # (m, N, U)
    m_ar = d["m_ar"]
    N_ar = d["N_ar"]
    U_ar = d["U_ar"]

    U_max = U_ar.max()
    gap_threshold = 0.1
    band_index_combined = 0
    Nval_combined = 100
    N_idx_c = int(np.flatnonzero(np.isin(N_ar, Nval_combined))[0])
    uval_slice_left = 0.2
    mval_slice_right = 2
    lwd, mksz, mked_col, mkd_edwd = 1.0, 4.0, "black", 0.2
    fsz, fsz_leg = 8, 6
    wspace_top, wspace_bottom = 0.2, 0.1
    figszwidth = 3.52913
    figheight = 3.5
    shading = None
    cmapgap = "plasma"
    gap_scale = "linear"
    vmin, vmax = 0, 1
    gap_norm = mcolors.Normalize(vmin=vmin, vmax=vmax)
    hopf_levels = np.arange(-2.5, 3.0, 1.0)
    hopf_ticks = np.arange(-2, 3, 1)
    m_ticks = np.arange(-4, 5, 1)
    u_ticks = np.arange(0, U_max + 0.1, 0.1)
    ylab = r"Interaction strength $Un/J$"

    _apply_style()

    mass_grid, Un_grid = np.meshgrid(m_ar, U_ar, indexing="ij")

    gap_grid_c = min_bdg_gap_ar[:, N_idx_c, :]
    hopf_grid_c = hopf_index_ar[:, N_idx_c, :, band_index_combined]
    hopf_grid_c = np.where(gap_grid_c > gap_threshold, hopf_grid_c, 0.0)

    fig_comb = plt.figure(figsize=(figszwidth * 1.2, figheight), constrained_layout=False)
    outer_gs = fig_comb.add_gridspec(nrows=2, ncols=1, height_ratios=[1, 1], hspace=0.4)
    top_gs = outer_gs[0].subgridspec(1, 2, wspace=wspace_top, width_ratios=[1.0, 1])
    bottom_gs = outer_gs[1].subgridspec(1, 2, wspace=wspace_bottom)
    ax_hopf = fig_comb.add_subplot(top_gs[0, 0])
    ax_gap = fig_comb.add_subplot(top_gs[0, 1])
    ax_left = fig_comb.add_subplot(bottom_gs[0, 0])
    ax_right = fig_comb.add_subplot(bottom_gs[0, 1])

    # --- top-left: Hopf index ---
    im_c = ax_hopf.pcolormesh(mass_grid, Un_grid, hopf_grid_c, cmap="RdBu_r", shading=shading,
                               norm=mcolors.BoundaryNorm(hopf_levels, ncolors=plt.get_cmap("RdBu_r").N))
    cb_c = fig_comb.colorbar(im_c, ax=ax_hopf, ticks=hopf_ticks)
    cb_c.ax.set_title(r"$\chi$")
    cb_c.set_ticklabels([rf"${t}$" for t in hopf_ticks])
    cb_c.ax.tick_params(direction="out")
    ax_hopf.set_xlabel(r"Mass parameter $m/J$")
    ax_hopf.set_ylabel(ylab)
    ax_hopf.set_title("Hopf Index", fontsize=fsz)
    ax_hopf.grid(alpha=0.1)
    ax_hopf.tick_params(length=2)

    # --- top-right: BdG gap ---
    im2_c = ax_gap.pcolormesh(mass_grid, Un_grid, gap_grid_c, cmap=cmapgap, shading=shading,
                               norm=gap_norm)
    cb2_c = fig_comb.colorbar(im2_c, ax=ax_gap)
    cb2_c.ax.set_title(r"$\Delta E^{\mathrm{BdG}}_\mathrm{min}\!/J$", x=1.9, y=1.01, fontsize=fsz)
    if gap_scale in ("linear", "power"):
        cb2_c.formatter.set_scientific(True)
        cb2_c.formatter.set_useMathText(True)
        cb2_c.update_ticks()
    ax_gap.set_title("Mininum bandgap", fontsize=fsz)
    cb2_c.ax.tick_params(direction="out")

    col_slice, lwd_slice, alpha_slice, zorder_slice = "green", 0.5, 0.75, 1
    for axval in [ax_hopf, ax_gap]:
        axval.set_xlabel(r"Mass parameter $m/J$", labelpad=0.5)
        axval.set_xticks(m_ticks)
        axval.set_yticks(u_ticks)
        axval.grid(alpha=0.1)
        axval.tick_params(length=2)
        axval.axhline(y=uval_slice_left, color=col_slice, linestyle="--",
                      linewidth=lwd_slice, alpha=alpha_slice, zorder=zorder_slice)
        axval.axvline(x=mval_slice_right, color=col_slice, linestyle="--",
                      linewidth=lwd_slice, alpha=alpha_slice, zorder=zorder_slice)

    # --- bottom-left: Hopf index / gap vs m, at fixed Un ---
    def plot_hopf_m_slice(ax, uval, show_ylabel):
        uidx_c = int(np.flatnonzero(np.isin(U_ar, uval))[0])
        hopf_full_c = hopf_index_ar[:, :, uidx_c, band_index_combined]
        gap_full_c = min_bdg_gap_ar[:, :, uidx_c]
        hopf_full_c = np.where(gap_full_c > gap_threshold, hopf_full_c, 0.0)
        gap_bdg_c = min_bdg_gap_ar[:, N_idx_c, uidx_c]
        gap_bare_c = min_gap_ar[:, N_idx_c, 0]

        ax.plot(m_ar, hopf_full_c[:, 1], marker="o", linestyle="", color="blue",
                markeredgecolor=mked_col, markeredgewidth=mkd_edwd,
                linewidth=lwd, markersize=mksz, alpha=1, zorder=3, label="Hopf Index")
        ax.plot(m_ar, gap_bdg_c, marker="s", linestyle="--", color="darkorange",
                markersize=mksz - 1, linewidth=lwd, markeredgecolor=mked_col,
                markeredgewidth=mkd_edwd, label=r"$\Delta E^{\mathrm{BdG}}_\mathrm{min}$")
        ax.plot(m_ar, gap_bare_c, marker="^", linestyle=":", color="green",
                markersize=mksz, linewidth=lwd, markeredgecolor=mked_col,
                markeredgewidth=mkd_edwd, label="Non-int. gap")
        ax.set_xlabel(r"Mass parameter $m/J$", labelpad=0)
        ax.set_xticks(m_ticks)
        if show_ylabel:
            ax.set_ylabel("Energy / Hopf Index", labelpad=0.5)
        ax.set_title(rf"$Un/J={uval}$", pad=4, fontsize=fsz)
        ax.grid(True, which="both", ls="-", alpha=0.3)
        ax.tick_params(axis="both", length=2.5)
        ax.set_ylim(-2.2, 2.2)
        return ax

    def plot_hopf_U_slice(ax, mval, show_ylabel):
        m_idx_c = int(np.flatnonzero(np.isin(m_ar, mval))[0])
        hopf_full_c = hopf_index_ar[m_idx_c, :, :, band_index_combined]
        gap_full_c = min_bdg_gap_ar[m_idx_c, :, :]
        hopf_full_c = np.where(gap_full_c > gap_threshold, hopf_full_c, 0.0)
        gap_bdg_c = min_bdg_gap_ar[m_idx_c, N_idx_c, :]
        gap_bare_c = min_gap_ar[m_idx_c, N_idx_c, 0]

        ax.plot(U_ar, hopf_full_c[1, :], marker="o", linestyle="", color="blue",
                markeredgecolor=mked_col, markeredgewidth=mkd_edwd,
                linewidth=lwd, markersize=mksz, alpha=1, zorder=3, label="Hopf Index")
        ax.plot(U_ar, gap_bdg_c, marker="s", linestyle="--", color="darkorange",
                markersize=mksz - 1, linewidth=lwd, markeredgecolor=mked_col,
                markeredgewidth=mkd_edwd, label=r"$\Delta E^{\mathrm{BdG}}_\mathrm{min}\!/J$")
        ax.plot(U_ar, np.ones(len(U_ar)) * gap_bare_c, marker="^", linestyle=":",
                color="green", markersize=mksz, linewidth=lwd, markeredgecolor=mked_col,
                markeredgewidth=mkd_edwd, label="Non-int. gap")
        ax.set_xlabel(r"Interaction strength $Un/J$", labelpad=0)
        if show_ylabel:
            ax.set_ylabel("Energy / Hopf Index", labelpad=0.5)
        ax.tick_params(axis="y", left=True, right=True, labelright=True, labelleft=None)
        ax.tick_params(axis="both", length=2.5)
        ax.set_title(rf"$m/J={mval}$", pad=4, fontsize=fsz)
        ax.grid(True, which="both", ls="-", alpha=0.3)
        return ax

    plot_hopf_m_slice(ax_left, uval_slice_left, show_ylabel=True)
    axright = plot_hopf_U_slice(ax_right, mval_slice_right, show_ylabel=False)
    axright.legend(bbox_to_anchor=(0.48, 0.19), loc="center", bbox_transform=fig_comb.transFigure,
                   ncol=3, borderaxespad=0.0, fontsize=fsz_leg, framealpha=0.9,
                   handletextpad=0.4, columnspacing=0.6)

    # Row-flush position fix: colorbars shrink ax_hopf/ax_gap by different
    # amounts, so their boxes drift out of vertical alignment.
    fig_comb.canvas.draw()
    pos_hopf = ax_hopf.get_position()
    pos_left = ax_left.get_position()
    pos_right = ax_right.get_position()
    xshift = 0.015
    ax_left.set_position((pos_left.x0 - xshift, pos_left.y0, pos_left.width, pos_left.height))
    ax_right.set_position((pos_right.x0 - xshift, pos_left.y0, pos_right.width, pos_left.height))

    for i, (ax, lab) in enumerate(zip([ax_hopf, ax_gap, ax_left, ax_right],
                                       ["(a)", "(b)", "(c)", "(d)"])):
        ax.text(-0.15, 1.08, lab, transform=ax.transAxes, fontsize=9)

    out = plotsdir() / "fig2_phase_diagram"
    fig_comb.savefig(out.with_suffix(".pdf"), dpi=600, bbox_inches="tight")
    fig_comb.savefig(out.with_suffix(".png"), dpi=600, bbox_inches="tight")
    print(f"Saved {out.with_suffix('.pdf')}")
    return fig_comb


if __name__ == "__main__":
    main()
