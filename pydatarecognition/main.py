import sys
import os
from pathlib import Path
from pydatarecognition.cif_io import cif_read, rank_write, user_input_read, \
    cif_read_ext, json_dump, print_story
from pydatarecognition.utils import xy_resample, correlate, get_iucr_doi, \
    get_formatted_crossref_reference, rank_returns, validate_args, XCHOICES, \
    XUNITS, SIMILARITY_METRICS, process_args, create_q_int_arrays
from pydatarecognition.plotters import rank_plot, all_plot
import argparse


def create_parser(**kwargs):
    parser = argparse.ArgumentParser()
    parser.add_argument('-i','--input', required=True, help="path to the input data-file. Path can be relative from the"
                                             " current location, e.g., ./my_data_dir/my_data_filename.xy")
    parser.add_argument('--xquantity', required=True, choices=XCHOICES,
                        help=f"Independent variable quantity of the input data, from {*XCHOICES,}. By default units "
                             f"are {*XUNITS,}, respectively")
    parser.add_argument('--xunit', required=True, choices=XUNITS,
                        help=f"Units for the independent variable quantity of the input data if different from the "
                             f"default, from {*XUNITS,}")
    parser.add_argument('-o', '--output', help="Path to output files. Path can be relative from the current "
                                             "location, e.g., ./my_data_dir/")
    parser.add_argument('-w', '--wavelength', help="wavelength of the radiation in angstrom units. Required if "
                                                  "xquantity is twotheta")
    parser.add_argument('--similarity-metric', help=f"The similarity metric to use, from {*SIMILARITY_METRICS,}",
                        default='pearson')
    parser.add_argument('--similarity-threshold', help="The similarity threshold above which we will keep the result."
                                                       "default = 0.8",
                        default=0.8)
    parser.add_argument('--qgrid-interval', help="The step-size/interval of the regular q-grid of the output",
                        default=0.001)
    parser.add_argument('--returns-min-max', help=f"Minimumum and maximum number of results to return. Provide"
                                                          f"two (space separated) integers.",
                        default=[5, 20], nargs=2)
    parser.add_argument('--plot-all', help=f"Plots all the patterns from the cifs, not just the selected ones."
                                                          f", if specified.  Used for testing",
                        action='store_true')
    parser.add_argument('--jsonify', action='store_true', help="dumps cifs into jsons")
    return parser



def main(verbose=True):
    parser = create_parser()
    argsns = argparse.Namespace()
    args = vars(parser.parse_args(namespace=argsns))
    args = process_args(args)
    validate_args(args)
    # These need to be inside main for this to run from an IDE like PyCharm
    # and still find the example files.
    cifname_ranks, iucrid_ranks, corr_coeff_ranks, cif_dict, skipped_cifs, ciflog = [], [], [], {}, [], []
    parent_dir = Path.cwd()
    cif_dir = parent_dir
    user_input = Path(args['input']).resolve()
    ciffiles = cif_dir.glob("*.cif")
    if args['output'] is None:
        output_dir = Path.cwd() / '_output'
    else:
        output_dir = Path(args['output']).resolve()
    if not output_dir.exists():
        output_dir.mkdir()
    userdata = user_input_read(user_input)
    user_q, user_int = create_q_int_arrays(args, userdata)
    if args['jsonify']:
        for ciffile in ciffiles:
            print(ciffile.name)
            json_data = cif_read_ext(ciffile, 'json')
            pre = Path(ciffile).stem
            json_dump(json_data, str(output_dir/pre) + ".json")
    else:
        for ciffile in ciffiles:
            if verbose:
                ciflog.append(ciffile.name)
            pcd = cif_read(ciffile)
            try:
                user_resampled, target_resampled = xy_resample(user_q, user_int, pcd.q,
                                             pcd.intensity, x_step=args.get('qgrid_interval'))
                corr_coeff = correlate(user_resampled[1], target_resampled[1])
            except (AttributeError, ValueError) as e:
                skipped_cifs.append((ciffile.name, e))
                continue

            cifname_ranks.append(ciffile.stem)
            iucrid_ranks.append(ciffile.stem[0:6])
            corr_coeff_ranks.append(corr_coeff)
            cif_dict[str(ciffile.stem)] = dict([
                        ('cifname', str(ciffile.stem)),
                        ('iucrid', str(ciffile.stem)[0:6]),
                        ('intensity', pcd.intensity),
                        ('q', pcd.q),
                        ('qmin', pcd.q[0]),
                        ('qmax', pcd.q[-1]),
                        ('q_reg', user_resampled[0]),
                        ('intensity_resampled', target_resampled[1]),
                        ('corr_coeff', corr_coeff),
                    ])
        print_story(user_input, args, ciflog, skipped_cifs)

        user_dict= dict([
            ('intensity', userdata[1]),
            ('q', user_q),
            ('q_min', user_q[0]),
            ('q_max', user_q[-1]),
        ])

        cif_rank_coeff_all = sorted(list(zip(cifname_ranks, corr_coeff_ranks)), key = lambda x: x[1], reverse=True)
        cif_rank_dict, paper_rank_dict = {}, {}
        for i in range(len(cif_rank_coeff_all)):
            cif_rank_dict[i] = cif_dict[cif_rank_coeff_all[i][0]]
        cif_returns = rank_returns(cif_rank_dict, args.get('returns_min_max')[0], args.get('returns_min_max')[1], args['similarity_threshold'])
        for i in range(cif_returns):
            cif_rank_dict[i]['doi'] = get_iucr_doi(cif_rank_dict[i]['iucrid'])
            cif_rank_dict[i]['ref'] = get_formatted_crossref_reference(cif_rank_dict[i]['doi'])[0]
        cif_rank_coeff_requested = [[cif_rank_dict[i]['cifname'],
                                     cif_rank_dict[i]['corr_coeff'],
                                     cif_rank_dict[i]['doi'],
                                     cif_rank_dict[i]['ref'],
                                     ] for i in range(cif_returns)]
        paper_rank_counter, paper_all = 0, []
        for i in range(len(cif_rank_dict.keys())):
            if not cif_rank_dict[i]['iucrid'] in paper_all:
                paper_all.append(cif_rank_dict[i]['iucrid'])
                paper_rank_dict[paper_rank_counter] = cif_rank_dict[i]
                paper_rank_counter += 1
        paper_returns = rank_returns(paper_rank_dict, args.get('returns_min_max')[0], args.get('returns_min_max')[1], args['similarity_threshold'])
        for i in range(paper_returns):
            if verbose:
                print(f"\t{paper_rank_dict[i]['cifname']}")
            paper_rank_dict[i]['doi'] = get_iucr_doi(paper_rank_dict[i]['iucrid'])
            paper_rank_dict[i]['ref'] = get_formatted_crossref_reference(paper_rank_dict[i]['doi'])[0]
        paper_rank_coeff_requested = [[paper_rank_dict[i]['cifname'],
                                       paper_rank_dict[i]['corr_coeff'],
                                       paper_rank_dict[i]['doi'],
                                       paper_rank_dict[i]['ref']]
                                      for i in range(paper_returns)]
        cif_ranks = [{'IUCrCIF':cif_rank_dict[i]['cifname'],
                      'score':cif_rank_dict[i]['corr_coeff'],
                      'doi':cif_rank_dict[i]['doi'],
                      'ref':cif_rank_dict[i]['ref'],
                      } for i in range(cif_returns)]
        ranks_papers = [{'IUCrCIF':paper_rank_dict[i]['cifname'],
                         'score':paper_rank_dict[i]['corr_coeff'],
                         'doi':paper_rank_dict[i]['doi'],
                         'ref':paper_rank_dict[i]['ref']
                         } for i in range(paper_returns)]
        if verbose:
            print(f'Done getting references.')
        rank_txt = rank_write(cif_ranks, output_dir, "cifs")
        frame_dashchars = '-' * 80
        print(f'{frame_dashchars}\nCIF ranking\n{frame_dashchars}\n{rank_txt.encode("utf8")}')
        rank_papers_txt = rank_write(ranks_papers, output_dir, "papers")
        print(f'{frame_dashchars}\nPaper ranking\n{frame_dashchars}\n{rank_papers_txt.encode("utf8")}')
        if verbose:
            print(f'{frame_dashchars}\nPlotting...\n\tCIF rank plot')
        rank_plot(user_dict, cif_dict, cif_rank_coeff_requested, output_dir, "cifs", plot_all=args['plot_all'])
        if args['plot_all']:
            all_plot(user_dict, cif_dict, output_dir)
        if verbose:
            print('\tPaper rank plot')
        rank_plot(user_dict, cif_dict, paper_rank_coeff_requested, output_dir, "papers", plot_all=args['plot_all'])
        if verbose:
            print('Done plotting.')
        print(f'{frame_dashchars}\n.txt, .pdf, and .png files have been saved to the output '
              f'diretory.')
        # with open((output_dir / "pydatarecognition.log"), "w") as o:
        #     o.write(log)

    return None


if __name__ == "__main__":
    # in Pycharm (and probably other IDEs) it runs main in place, so if so
    # detect this and move to the examples folder where it can find the data
    cwd = Path().cwd()
    relpath = cwd / ".." / "docs" / "examples"
    if cwd.parent.name == "pydatarecognition" and cwd.parent.parent.name != "pydatarecognition":
        os.chdir(relpath)
    main()

# End of file.
