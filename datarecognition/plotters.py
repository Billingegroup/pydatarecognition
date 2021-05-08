from pathlib import Path
import matplotlib.pyplot as plt
# import matplotlib as mpl
# from bg_mpl_stylesheet.bg_mpl_stylesheet import bg_mpl_style

def cif_plot(cif_file_path, parent_path, png_path, cif_data):
    plot_file_name = str(cif_file_path.resolve().stem) + '.png'
    tt = cif_data[0]
    int_exp = cif_data[1]
    # mpl.rcParams.update(mpl.rcParamsDefault)
    # plt.style.use(os.path.join(parent_path, "utils","billinge.mplstyle"))
    plt.style.use(bg_mpl_style)
    fig, ax = plt.subplots(dpi=300, figsize=(12,4))
    ax.plot(tt, int_exp, linewidth=1)
    plt.ticklabel_format(style='sci', axis='y', scilimits=(0,0))
    ax.set_xlabel(r"2$\theta$ $[^{\circ}]$")#, labelpad=5)
    ax.set_ylabel(r"$I$ $[\mathrm{counts}]$")#, labelpad=5)
    plt.xlim(min(tt), max(tt))
    # plt.ylim(min(int), max(int))
    plt.savefig(png_path / plot_file_name, bbox_inches='tight')
    plt.close()

    return None
    # End fo function.


def rank_plot(user_data, cif_rank_pearson_list, data_dict, png_path):
    q, int_exp = [], []
    for i in range(0, 5):
        file = cif_rank_pearson_list[i][0]
        for key in data_dict:
            if key == file:
                q.append(data_dict[key]['q'])
                int_exp.append(data_dict[key]['int_exp'])
    fig, axs = plt.subplots(6, 1, sharex=True, figsize=(8,4), dpi=300)
    plt.xlim(min(user_data[1]), max(user_data[1]))
    plt.yticks([])
    fig.add_subplot(111, frameon=False)
    plt.tick_params(labelcolor='none', which='both',
                    top=False, bottom=False, left=False, right=False)
    plt.xlabel(r"$Q$ $[\mathrm{\AA}^{-1}]$", fontsize=16)
    plt.ylabel(r"$I$ $[\mathrm{arb.u.}]$", fontsize=16, labelpad=-10)
    # plt.style.use(bg_mpl_style)
    colors = ["#0B3C5D", "#B82601", "#1c6b0a", "#328CC1", "#062F4F", "#D9B310",
              "#984B43", "#76323F", "#626E60", "#AB987A", "#C09F80"]
    axs[0].plot(user_data[1], user_data[2], c=colors[0], lw=0.5)
    axs[0].text(0.89*max(user_data[1]), 0.7*max(user_data[2]), 'User data')
    axs[0].set_yticks([])
    y_min = min(user_data[2])
    y_max = max(user_data[2])
    y_range = y_max - y_min
    axs[0].set_ylim(y_min - 0.1*y_range, y_max + 0.1*y_range)
    for i in range(1, 6):
        axs[i].plot(q[i-1], int_exp[i-1], c=colors[i], lw=0.5)
        axs[i].text(0.89*max(q[i-1]), 0.7*max(int_exp[i-1]), 'Rank: ' + str(i))
        axs[i].set_yticks([])
        # axs[i].text(0.89*max(user_data[1]), 0.7, 'Rank: ' + str(i))
        # axs[i].set_xlim(min(q[i-1]), max(q[i-1]))
        y_min = min(int_exp[i-1])
        y_max = max(int_exp[i-1])
        y_range = y_max - y_min
        axs[i].set_ylim(y_min - 0.1*y_range, y_max + 0.1*y_range)
    plt.savefig(png_path / 'rank_plot.png', bbox_inches='tight')
    plt.close()

    return None
    # End of function.
