import matplotlib.pyplot as plt
import numpy as np
from bg_mpl_stylesheet.bg_mpl_stylesheet import bg_mpl_style

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


def rank_plot(q_reg, userdata_resampled_int, cif_rank_pearson_list, cif_dict, png_path=None):
    cifdata_q_reg, cifdata_resampled_intensity = [], []
    for i in range(0, 5):
        file = cif_rank_pearson_list[i][0]
        for key in cif_dict:
            if key == file:
                cifdata_resampled_intensity.append(cif_dict[key]['intensity_resampled'])
                cifdata_q_reg.append(cif_dict[key]['q_reg'])
    fig, axs = plt.subplots(6, 1, sharex=True, figsize=(8,4), dpi=300)
    plt.xlim(np.amin(q_reg), np.amax(q_reg))
    plt.yticks([])
    fig.add_subplot(111, frameon=False)
    plt.tick_params(labelcolor='none', which='both',
                    top=False, bottom=False, left=False, right=False)
    plt.xlabel(r"$Q$ $[\mathrm{nm}^{-1}]$", fontsize=16)
    plt.ylabel(r"$I$ $[\mathrm{arb.u.}]$", fontsize=16, labelpad=-10)
    plt.style.use(bg_mpl_style)
    colors = ["#0B3C5D", "#B82601", "#1c6b0a", "#328CC1", "#062F4F", "#D9B310",
              "#984B43", "#76323F", "#626E60", "#AB987A", "#C09F80"]
    x_min, x_max = np.amin(q_reg), np.amax(q_reg)
    y_min, y_max = np.amin(userdata_resampled_int), np.amax(userdata_resampled_int)
    y_range = y_max - y_min
    axs[0].plot(q_reg, userdata_resampled_int, lw=0.5, c=colors[0])
    axs[0].text(0.875 * x_max, 0.65 * y_max, 'User data')
    axs[0].set_yticks([])
    axs[0].set_ylim(y_min - 0.1*y_range, y_max + 0.1*y_range)
    for i in range(1, 6):
        y_min, y_max = np.amin(cifdata_resampled_intensity[i-1]), np.amax(cifdata_resampled_intensity[i-1])
        y_range = y_max - y_min
        axs[i].plot(cifdata_q_reg[i-1], cifdata_resampled_intensity[i-1], lw=0.5, c=colors[i])
        axs[i].text(0.875 * x_max, 0.65 * y_max, f'Rank: {i}')
        axs[i].set_yticks([])
        axs[i].set_ylim(y_min - 0.1*y_range, y_max + 0.1*y_range)
    if png_path:
        plt.savefig(png_path / 'rank_plot.png', bbox_inches='tight')
    else:
        return fig
    return None
