"""Figure 1: symplectic (BBdG) Hopf-insulator quasiparticle spectrum along a
high-symmetry path, for three mass parameters and three interaction strengths.

Standalone reproduction of the paper's Fig. 1 (label
``fig:hopf-bbdg-model-spectrum``) from precomputed data only, with no
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
from mpl_toolkits.axes_grid1.inset_locator import mark_inset

from symplectichopfinsulator_zenodo import plotsdir, load_data

MPLSTYLE = Path(__file__).resolve().parents[1] / "mplstyle" / "aps_math_new.mplstyle"
HAS_LATEX = shutil.which("latex") is not None
BM_K = r"\bm{k}" if HAS_LATEX else r"\mathbf{k}"


def _apply_style():
    if HAS_LATEX:
        plt.style.use(MPLSTYLE)
    else:
        print(f"Note: no LaTeX installation found. Falling back to matplotlib's "
              f"built-in mathtext instead of the shipped style ({MPLSTYLE.name}). "
              f"Install TeX Live/MacTeX/MiKTeX (or use Docker, which has LaTeX "
              f"preinstalled) for pixel-exact publication styling.")
        plt.rcParams.update({
            "font.size": 8, "axes.titlesize": 9, "axes.labelsize": 8,
            "xtick.direction": "in", "ytick.direction": "in",
            "xtick.top": True, "ytick.right": True,
        })


def main():
    _apply_style()
    d = load_data("fig1_hs_spectrum/hs_spectrum.h5")
    spec_0 = d["spec_0"]      # (3, 501, 2)  Un/J=0 baseline
    spec_U1 = d["spec_U1"]    # (3, 501, 2)  Un/J=0.2
    spec_U2 = d["spec_U2"]    # (3, 501, 2)  Un/J=0.4
    m_values = d["m_values"]
    U1, U2 = d["Un_values"]
    ticks = d["ticks"]
    labels = list(d["labels"])

    inset_half_width = 5
    inset_hs_label = {m: "$T$" for m in m_values}

    col_U0, ls_U0, lw_U0 = "g", "-", 0.75
    col_U1, ls_U1, lw_U1 = "red", "-.", 1.0
    col_U2, ls_U2, lw_U2 = "blue", "-", 1.25
    fsz_labels, fsz_title = 8, 9
    grid_alpha = 0.3
    figszwidth_twocolumn = 2.0 * 3.52913
    figheight_multi_m = 1.75

    fig, axes = plt.subplots(1, 3, figsize=(figszwidth_twocolumn, figheight_multi_m))

    for i, m_val in enumerate(m_values):
        ax = axes[i]
        spec_0_m, spec_U1_m, spec_U2_m = spec_0[i], spec_U1[i], spec_U2[i]

        ax.plot(spec_0_m[:, 0], color=col_U0, lw=lw_U0, ls=ls_U0)
        ax.plot(spec_0_m[:, 1], color=col_U0, lw=lw_U0, ls=ls_U0)
        for band in range(2):
            ax.plot(spec_U1_m[:, band], color=col_U1, ls=ls_U1, lw=lw_U1)
            ax.plot(spec_U2_m[:, band], color=col_U2, ls=ls_U2, lw=lw_U2)

        ax.set_xticks(ticks)
        ax.set_xticklabels(labels, fontsize=fsz_labels)
        ax.set_title(rf"Mass parameter $m/J={m_val:g}$", fontsize=fsz_title, pad=4)
        if i == 0:
            ax.set_ylabel(rf"Quasiparticle energy $E({BM_K})/J$", fontsize=fsz_title)
        ax.grid(True, alpha=grid_alpha)
        ax.tick_params(length=2)

        # --- inset: zoom near the target HS point ---
        target_label = inset_hs_label[m_val]
        candidate_ticks = [t for t, lab in zip(ticks, labels) if lab == target_label]
        if len(candidate_ticks) > 1:
            gaps_at_candidates = [
                np.min(np.abs(np.diff(spec_0_m[max(0, t - 2):t + 3], axis=-1)))
                for t in candidate_ticks
            ]
            tick0 = candidate_ticks[int(np.argmin(gaps_at_candidates))]
        else:
            tick0 = candidate_ticks[0]

        x0, x1 = max(0, tick0 - inset_half_width), min(len(spec_0_m) - 1, tick0 + inset_half_width)
        y_window = np.concatenate([spec_0_m[x0:x1 + 1], spec_U1_m[x0:x1 + 1], spec_U2_m[x0:x1 + 1]])
        y0, y1 = y_window.min(), y_window.max()
        ins_pos = [0.65, 0.06, 0.2, 0.2] if i == 0 else [0.75, 0.06, 0.2, 0.2]
        axins = ax.inset_axes(ins_pos, xlim=(x0, x1), ylim=(y0, y1))
        axins.plot(spec_0_m[:, 0], color=col_U0, lw=lw_U0, ls=ls_U0)
        axins.plot(spec_0_m[:, 1], color=col_U0, lw=lw_U0, ls=ls_U0)
        for band in range(2):
            axins.plot(spec_U1_m[:, band], color=col_U1, ls=ls_U1, lw=lw_U1)
            axins.plot(spec_U2_m[:, band], color=col_U2, ls=ls_U2, lw=lw_U2)
        axins.set_xticks([])
        axins.tick_params(axis="y", which="major", pad=1.0)
        if i == 1:
            axins.set_yticks(axins.get_yticks()[1:4][::2])
        axins.tick_params(which="both", length=1.5)
        mark_inset(ax, axins, loc1=2, loc2=1, edgecolor="k", facecolor="none",
                   alpha=1, linewidth=0.75, zorder=5, linestyle="-")

    # single inset for the last panel around the Gamma point
    gam_index = labels.index(r"$\Gamma$")
    spec_0_last, spec_U1_last, spec_U2_last = spec_0[-1], spec_U1[-1], spec_U2[-1]
    pad_gam, ymax_gam = 0.1, 1
    t_gam = ticks[gam_index]
    ylim_gamma = (spec_0_last[t_gam - inset_half_width:t_gam + inset_half_width + 1].min() - pad_gam, ymax_gam)
    xlim_gamma = (t_gam - inset_half_width, t_gam + inset_half_width)
    axins_gamma = axes[-1].inset_axes([0.1, 0.085, 0.2, 0.2], xlim=xlim_gamma, ylim=ylim_gamma)
    axins_gamma.plot(spec_0_last[:, 0], color=col_U0, lw=lw_U0, ls=ls_U0)
    axins_gamma.plot(spec_0_last[:, 1], color=col_U0, lw=lw_U0, ls=ls_U0)
    for band in range(2):
        axins_gamma.plot(spec_U1_last[:, band], color=col_U1, ls=ls_U1, lw=lw_U1)
        axins_gamma.plot(spec_U2_last[:, band], color=col_U2, ls=ls_U2, lw=lw_U2)
    axins_gamma.set_xticks([])
    axins_gamma.tick_params(axis="y", which="major", pad=1.0)
    axins_gamma.tick_params(which="both", length=1.5)
    mark_inset(axes[-1], axins_gamma, loc1=1, loc2=4, edgecolor="k", facecolor="none",
               alpha=1, linewidth=0.75, zorder=5, linestyle="-")

    import matplotlib.lines as mlines
    legend_handles = [
        mlines.Line2D([0], [0], color=col_U0, ls=ls_U0, lw=lw_U0, label=r"$Un/J=0$"),
        mlines.Line2D([0], [0], color=col_U1, ls=ls_U1, lw=lw_U1, label=rf"$Un/J={U1:g}$"),
        mlines.Line2D([0], [0], color=col_U2, ls=ls_U2, lw=lw_U2, label=rf"$Un/J={U2:g}$"),
    ]
    fig.legend(handles=legend_handles, loc="lower center", ncol=3, fontsize=9,
               bbox_to_anchor=(0.5, -0.15), frameon=False)

    for i, ax in enumerate(axes):
        ax.text(-0.1, 1.04, ["(a)", "(b)", "(c)"][i], transform=ax.transAxes, fontsize=9)

    out = plotsdir() / "fig1_hs_spectrum"
    fig.savefig(out.with_suffix(".pdf"), dpi=600, bbox_inches="tight")
    fig.savefig(out.with_suffix(".png"), dpi=600, bbox_inches="tight")
    print(f"Saved {out.with_suffix('.pdf')}")
    return fig


if __name__ == "__main__":
    main()
