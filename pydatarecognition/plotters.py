import sys
import matplotlib.pyplot as plt
import matplotlib as mpl
from matplotlib.backends.backend_pdf import PdfPages
import numpy as np
from copy import copy

from bg_mpl_stylesheet.bg_mpl_stylesheet import bg_mpl_style

from pydatarecognition.utils import plotting_min_max

def iq_plot(q, i):
    plt.style.use(bg_mpl_style)
    iq_plot = plt.figure()
    plt.plot(q, i, lw=0.5)
    plt.xlim(np.amin(q), np.amax(q))
    plt.xlabel(r'$Q$ $[\mathrm{\AA}^{-1}]$')
    plt.ylabel(r'$I$ $[\mathrm{counts}]$')
    plt.ticklabel_format(style='sci', axis='y', scilimits=(0, 0))
    plt.tight_layout()
    plt.close()

    return iq_plot


def itt_plot(tt, i):
    plt.style.use(bg_mpl_style)
    itt_plot = plt.figure()
    plt.plot(tt, i, lw=0.5)
    plt.xlim(np.amin(tt), np.amax(tt))
    plt.xlabel(r'$2\theta$ $[^{\circ}]$')
    plt.ylabel(r'$I$ $[\mathrm{counts}]$')
    plt.ticklabel_format(style='sci', axis='y', scilimits=(0, 0))
    plt.tight_layout()
    plt.close()

    return itt_plot


def iinvd_plot(inv_d, i):
    plt.style.use(bg_mpl_style)
    id_plot = plt.figure()
    plt.plot(inv_d, i, lw=0.5)
    plt.xlim(np.amin(inv_d), np.amax(inv_d))
    plt.xlabel(r'$d^{-1}$ $[\mathrm{\AA}^{-1}]$')
    plt.ylabel(r'$I$ $[\mathrm{counts}]$')
    plt.ticklabel_format(style='sci', axis='y', scilimits=(0, 0))
    plt.tight_layout()
    plt.close()

    return id_plot



@mpl.rc_context({'lines.linewidth': 1, 'axes.linewidth': 0.7, 'xtick.major.size': 0.7,
                 'xtick.major.width': 0.7,  'xtick.labelsize': 5, 'legend.frameon': False,
                 'legend.loc': 'best', 'font.size': 5, 'axes.labelsize': 5,
                 'ytick.left': False, 'ytick.labelleft': False, 'ytick.right': False
                 })
def all_plot(user_dict, cif_dict, output_dir):
    n_subplots = 12 # number of subplots in a column.  Two will have user data plotted
                    # in them in each column.  The others will have cif data plotted.

    cifs = copy(cif_dict)
    gs = mpl.gridspec.GridSpec(n_subplots, 2)
    gs.update(wspace=0., hspace=0.)
    qrange = [user_dict["q"][0], user_dict["q"][-1]]
    n_cifs = len(cifs)
    n_pages = 1 + n_cifs // ((n_subplots-2) * 2)

    # plot the user data at the top of each column
    with PdfPages(output_dir / 'all_cifs.pdf') as pdf:
        for p in range(n_pages):
            done_keys = []
            for i in range(2):
                for j in [0,n_subplots//2]:
                    ax = plt.subplot(gs[j, i])
                    ax.set_xlim(qrange[0], qrange[1])
                    ax.set_ylim(plotting_min_max(user_dict["intensity"])[0],
                                plotting_min_max(user_dict["intensity"])[1])
                    ax.plot(user_dict["q"], user_dict["intensity"],
                            label=f"User Data", c='#B82601')
                    ax.legend()

            # then plot the cif data below
            i, j = 1, 0
            for key, cifdata in cifs.items():
                if i == n_subplots//2:
                    i += 1
                ax = plt.subplot(gs[i,j])
                ax.set_xlim(qrange[0], qrange[1])
                ax.set_ylim(plotting_min_max(cifdata["intensity_resampled"])[0],
                                  plotting_min_max(cifdata["intensity_resampled"])[1])
                ax.plot(cifdata["q_reg"], cifdata["intensity_resampled"],
                              label=f"{cifdata['cifname']}")
                ax.legend()
                i += 1

                if i == n_subplots and j == 1:
                    done_keys.append(key)
                    break
                elif i == n_subplots:
                    j = 1
                    i = 1
                done_keys.append(key)
            for key in done_keys:
                del cifs[key]
            pdf.savefig(bbox_inches='tight')
            plt.close()

        return None

def rank_plot(user_dict, cif_dict, cif_rank_coeff, output_dir, ranktype, plot_all=False):
    x_user, y_user = user_dict["q"], user_dict["intensity"]
    x_min_user, x_max_user = np.amin(x_user), np.amax(x_user)
    y_min_user, y_max_user = np.amin(y_user), np.amax(y_user)
    x_range_user, y_range_user = x_max_user - x_min_user, y_max_user - y_min_user
    cifdata_q, cifdata_q_reg, cifdata_intensity, cifdata_intensity_resampled, cifdata_cifname = [], [], [], [], []
    for i in range(0, 5):
        file = cif_rank_coeff[i][0]
        for key in cif_dict:
            if key == file:
                cifdata_q.append(cif_dict[key]['q'])
                cifdata_q_reg.append(cif_dict[key]['q_reg'])
                cifdata_intensity.append(cif_dict[key]['intensity'])
                cifdata_intensity_resampled.append(cif_dict[key]['intensity_resampled'])
                cifdata_cifname.append(cif_dict[key]['cifname'])
    fontsize_labels, fontsize_ticks, fontsize_legend = 20, 16, 16
    legend_handle_lw, legend_frame_lw = 0, 2
    plt.style.use(bg_mpl_style)
    fig, axs = plt.subplots(6, 1, sharex='all', figsize=(8,10), dpi=300, gridspec_kw={'hspace':0})
    fig.add_subplot(111, frameon=False)
    plt.tick_params(labelcolor='none', which='both',
                    top=False, bottom=False, left=False, right=False)
    plt.xlabel(r"$Q$ $[\mathrm{nm}^{-1}]$", fontsize=fontsize_labels)
    plt.ylabel(r"$I$ $[\mathrm{arb.u.}]$", fontsize=fontsize_labels, labelpad=-10)
    # colors = plt.rcParams['axes.prop_cycle'].by_key()['color']
    # axs[0].plot(x_user, y_user, c=colors[0], label="User Data")
    axs[0].plot(x_user, y_user, label="User Data", c='#B82601')
    legend = axs[0].legend(loc="upper right", fontsize=fontsize_legend, handletextpad=0, handlelength=0)
    legend.get_frame().set_linewidth(legend_frame_lw)
    for line in legend.get_lines():
        line.set_linewidth(legend_handle_lw)
    axs[0].set_xlim(x_min_user, x_max_user)
    axs[0].set_ylim(y_min_user - 0.1*y_range_user, y_max_user + 0.1*y_range_user)
    axs[0].set_yticks([])
    for i in range(1, 6):
        x, y = cifdata_q_reg[i-1], cifdata_intensity_resampled[i-1]
        y_min, y_max = np.amin(y), np.amax(y)
        y_range = y_max - y_min
        # axs[i].plot(x, y, c=colors[i], label=f"Rank {i}: {cifdata_cifname[i-1]}")
        if plot_all:
            axs[i].plot(x, y, label=f"Rank {i}: {cifdata_cifname[i-1]}")
        else:
            axs[i].plot(x, y, label=f"Rank {i}")
        axs[i].set_ylim(y_min - 0.1 * y_range, y_max + 0.1 * y_range)
        axs[i].set_yticks([])
        legend = axs[i].legend(loc="upper right", fontsize=fontsize_legend, handletextpad=0, handlelength=0)
        legend.get_frame().set_linewidth(legend_frame_lw)
        for line in legend.get_lines():
            line.set_linewidth(legend_handle_lw)
    axs[-1].tick_params(axis="x", which="major", labelsize=fontsize_ticks)
    plt.savefig(output_dir / f'rank_plot_{ranktype}.png', bbox_inches='tight')
    plt.savefig(output_dir / f'rank_plot_{ranktype}.pdf', bbox_inches='tight')
    plt.close()

    return None
