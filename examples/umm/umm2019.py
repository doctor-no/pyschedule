import datetime
import logging
import os
import sys

import athletics_event


anlagen_descriptors = {
    'saturday': [
        ("Läufe",),
        ("Weit", 2),
        ("Kugel", 2),
        ("Hoch", 2),
        ("Diskus",),
    ],
    'sunday': [
        ("Läufe",),
        ("Weit", 2),
        ("Kugel", 2),
        ("Hoch", 2),
        ("Diskus",),
        ("Speer",),
        ("Stab",),
    ],
}

wettkampf_data = {
    'saturday': {
        "U12W_4K": {
            "disziplinen": [
                dict(name="60m", together=True, resource="Läufe", length=3),
                dict(name="Pause_1", length=1),
                dict(name="Weit", resource="Weit", length=3),
                dict(name="Pause_2", length=1),
                dict(name="Kugel", resource="Kugel", length=2),
                dict(name="Pause_3", length=1),
                dict(name="600m", together=True, resource="Läufe", length=3),
            ],
            "plot_color": "orange",
        },
        "U16W_5K": {
            "disziplinen": [
                dict(name="80m", together=True, resource="Läufe", length=3),
                dict(name="Pause_1", length=1),
                dict(name="Weit", resource="Weit", length=3),
                dict(name="Pause_2", length=1),
                dict(name="Kugel", resource="Kugel", length=2),
                dict(name="Pause_3", length=1),
                dict(name="Hoch", resource="Hoch", length=4),
                dict(name="Pause_4", length=1),
                dict(name="600m", together=True, resource="Läufe", length=3),
            ],
            "plot_color": "pink",
        },
        "WOM_7K": {
            "disziplinen": [
                dict(name="100mHü", together=True, resource="Läufe", length=3),
                dict(name="Pause_1", length=3),
                dict(name="Hoch", resource="Hoch", length=4),
                dict(name="Pause_2", length=3),
                dict(name="Kugel", resource="Kugel", length=2),
                dict(name="Pause_3", length=3),
                dict(name="200m", together=True, resource="Läufe", length=2),
            ],
            "is_wettkampf_with_strict_sequence": True,
            "plot_color": "lightgreen",
        },
        "U12M_4K": {
            "disziplinen": [
                dict(name="60m", together=True, resource="Läufe", length=3),
                dict(name="Pause_1", length=1),
                dict(name="Weit", resource="Weit", length=3),
                dict(name="Pause_2", length=1),
                dict(name="Kugel", resource="Kugel", length=2),
                dict(name="Pause_3", length=1),
                dict(name="600m", together=True, resource="Läufe", length=3),
            ],
            "plot_color": "yellow",
        },
        "U16M_6K": {
            "disziplinen": [
                dict(name="100mHü", together=True, resource="Läufe", length=2),
                dict(name="Pause_1", length=3),
                dict(name="Weit", resource="Weit", length=3),
                dict(name="Pause_2", length=3),
                dict(name="Kugel", resource="Kugel", length=2),
                dict(name="Pause_3", length=3),
                dict(name="Hoch", resource="Hoch", length=4),
                dict(name="Pause_4", length=3),
                dict(name="Diskus", together=True, resource="Diskus", length=5),
                dict(name="Pause_5", length=3),
                dict(name="1000m", together=True, resource="Läufe", length=2),
            ],
            "is_wettkampf_with_strict_sequence": True,
            "plot_color": "lightblue",
        },
        "MAN_10K": {
            "disziplinen": [
                dict(name="100m", together=True, resource="Läufe", length=1),
                dict(name="Pause_1", length=5),
                dict(name="Weit", resource="Weit1&Weit2", length=3),
                dict(name="Pause_2", length=3),
                dict(name="Kugel", resource="Kugel1&Kugel2", length=2),
                dict(name="Pause_3", length=4),
                dict(name="Hoch", resource="Hoch1&Hoch2", length=4),
                dict(name="Pause_4", length=4),
                dict(name="400m", together=True, resource="Läufe", length=2),
            ],
            "is_wettkampf_with_strict_sequence": True,
            "is_last_wettkampf_of_the_day": True,
            "plot_color": "red",
        },
    },
    "sunday": {
        "U14M_5K": {
            "disziplinen": [
                dict(name="60m", together=True, resource="Läufe", length=3),
                dict(name="Pause_1", length=1),
                dict(name="Weit", resource="Weit", length=3),
                dict(name="Pause_2", length=1),
                dict(name="Kugel", resource="Kugel", length=2),
                dict(name="Pause_3", length=1),
                dict(name="Hoch", resource="Hoch", length=3),
                dict(name="Pause_4", length=1),
                dict(name="600m", together=True, resource="Läufe", length=3),
            ],
            "plot_color": "orange",
        },
        "MAN_6K": {
            "disziplinen": [
                dict(name="100m", together=True, resource="Läufe", length=3),
                dict(name="Pause_1", length=1),
                dict(name="Weit", resource="Weit", length=3),
                dict(name="Pause_2", length=1),
                dict(name="Kugel", resource="Kugel1&Kugel2", length=2),
                dict(name="Pause_3", length=1),
                dict(name="Hoch", resource="Hoch", length=3),
                dict(name="Pause_4", length=1),
                dict(name="Speer", resource="Speer", length=3),
                dict(name="Pause_5", length=1),
                dict(name="1000m", together=True, resource="Läufe", length=3),
            ],
            "plot_color": "lightblue",
        },
        "WOM_5K": {
            "disziplinen": [
                dict(name="100m", together=True, resource="Läufe", length=2),
                dict(name="Pause_1", length=3),
                dict(name="Weit", resource="Weit", length=3),
                dict(name="Pause_2", length=3),
                dict(name="Kugel", resource="Kugel", length=2),
                dict(name="Pause_3", length=3),
                dict(name="Hoch", resource="Hoch", length=3),
                dict(name="Pause_4", length=3),
                dict(name="1000m", together=True, resource="Läufe", length=2),
            ],
            "plot_color": "olive",
        },
        "MAN_10K": {
            "disziplinen": [
                dict(name="110mHü", together=True, resource="Läufe", length=3),
                dict(name="Pause_1", length=3),
                dict(name="Diskus", resource="Diskus", length=2),
                dict(name="Pause_2", length=4),
                dict(name="Stab", resource="Stab", length=11),
                dict(name="Pause_3", length=3),
                dict(name="Speer", resource="Speer", length=3),
                dict(name="Pause_4", length=3),
                dict(name="1500m", together=True, resource="Läufe", length=1),
            ],
            "is_wettkampf_with_strict_sequence": True,
            "is_last_wettkampf_of_the_day": True,
            "plot_color": "red",

        },
        "U14W_5K": {
            "disziplinen": [
                dict(name="60m", together=True, resource="Läufe", length=3),  # FIXME: actual length should be 5
                dict(name="Pause_1", length=1),
                dict(name="Weit", resource="Weit", length=3),
                dict(name="Pause_2", length=1),
                dict(name="Kugel", resource="Kugel", length=2),
                dict(name="Pause_3", length=1),
                dict(name="Hoch", resource="Hoch", length=3),
                dict(name="Pause_4", length=1),
                dict(name="600m", together=True, resource="Läufe", length=3),
            ],
            "plot_color": "pink",
        },
        "WOM_7K": {
            "disziplinen": [
                dict(name="Weit", together=True, resource="Weit1&Weit2", length=3),
                dict(name="Pause_1", length=3),
                dict(name="Speer", together=True, resource="Speer", length=6),
                dict(name="Pause_2", length=3),
                dict(name="800m", together=True, resource="Läufe", length=2),
            ],
            "is_wettkampf_with_strict_sequence": True,
            "plot_color": "lightgreen",
        },
    }
}

wettkampf_start_times = {
    "saturday": {
        "WOM_7K_Gr1_to_Gr2_100mHü": 12,
        "MAN_10K_Gr23_to_Gr23_100m": 12,
    },
    "sunday": {
        "MAN_10K_Gr23_to_Gr23_110mHü": 12,
        "WOM_7K_Gr1_to_Gr2_Weit": 12,
    },
}

teilnehmer_data = {
    "U12W_4K": {
        "Gr14": 13,
        "Gr15": 12,
        "Gr16": 12,
        "Gr17": 12,
        "Gr18": 12,
        "Gr19": 12,
        "Gr20": 12,
    },
    "U14W_5K": {
        "Gr7": 13,
        "Gr8": 13,
        "Gr9": 13,
        "Gr10": 13,
        "Gr11": 13,
        "Gr12": 13,
        "Gr13": 13,
    },
    "U16W_5K": {
        "Gr3": 10,
        "Gr4": 10,
        "Gr5": 11,
        "Gr6": 11,
    },
    "WOM_7K": {
        "Gr1": 11,
        "Gr2": 14,
    },
    "WOM_5K": {
        "Gr21": 8,
        "Gr22": 14,
    },
    "U12M_4K": {
        "Gr30": 12,
        "Gr31": 13,
        "Gr32": 11,
        "Gr33": 12,
        "Gr34": 11,
    },
    "U14M_5K": {
        "Gr26": 12,
        "Gr27": 12,
        "Gr28": 12,
        "Gr29": 12,
    },
    "U16M_6K": {
        "Gr24": 11,
        "Gr25": 10,
    },
    "MAN_10K": {
        "Gr23": 9,
    },
    "MAN_6K": {
        "Gr35": 12,
        "Gr36": 13,
        "Gr37": 17,
    },
}


def setup_logging(verbose, event_name):
    log_level = logging.INFO
    if verbose:
        log_level=logging.DEBUG
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)
    fh = logging.FileHandler('{}.log'.format(event_name))
    fh.setLevel(logging.DEBUG)
    ch = logging.StreamHandler()
    ch.setLevel(log_level)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    fh.setFormatter(formatter)
    root_logger.addHandler(ch)
    root_logger.addHandler(fh)
    matplotlib_logger = logging.getLogger("matplotlib")
    matplotlib_logger.setLevel(logging.INFO)


def main(args):
    start_time = datetime.datetime.now()
    event_name = "{}_{}".format(os.path.splitext(__file__)[0], args.day)
    output_folder_name = "{}_{}".format(start_time.isoformat(timespec="seconds"), event_name)
    output_folder_path = os.path.join("results", output_folder_name)
    os.makedirs(output_folder_path, exist_ok=True)
    link_path = os.path.join("results", "latest")
    if os.path.lexists(link_path):
        os.remove(link_path)
    os.symlink(output_folder_name, link_path)
    os.chdir(output_folder_path)

    setup_logging(args.verbose, event_name)

    logging.debug("arguments: {}".format(args))
    logging.debug('output folder: {!r}'.format(output_folder_name))

    event = athletics_event.AthleticsEventScheduler(
        name=event_name, duration_in_units=args.horizon, alternative_objective=args.alternative_objective)
    event.create_anlagen(anlagen_descriptors[args.day])
    event.create_disziplinen(wettkampf_data[args.day], teilnehmer_data)
    if not args.dont_set_start_time:
        event.set_wettkampf_start_times(wettkampf_start_times[args.day])
    event.ensure_last_wettkampf_of_the_day()
    scenario_as_string = str(event.scenario)
    scenario_filename = '{}_scenario.txt'.format(event_name)
    with open(scenario_filename, 'w') as f:
        f.write(scenario_as_string)
    if args.print_scenario_and_exit:
        logging.info("scenario: {}".format(scenario_as_string))
        sys.exit()
    logging.debug("scenario: {}".format(scenario_as_string))
    try:
        event.solve(time_limit=args.time_limit, ratio_gap=args.ratio_gap, random_seed=args.random_seed, threads=args.threads)
    except athletics_event.NoSolutionError as e:
        logging.error("Exception caught: {}".format(e.__class__.__name__))
    logging.debug("done")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description='calculate event timetable')
    parser.add_argument('--print-scenario-and-exit', action="store_true",
                        help='print scenario and exit')
    default_arguments = {
        "time_limit": "10m",
        "ratio_gap": 0.0,
        "random_seed": None,
        "threads": None,
        "horizon": 54,
    }
    parser.add_argument('-v', '--verbose', action="store_true", help="be verbose")
    help_text = 'time limit, e.g. 30s, 10m, 1h (default: {})'.format(default_arguments["time_limit"])
    parser.add_argument('--time-limit', default=default_arguments["time_limit"], help=help_text)
    help_text = 'ratio gap, e.g. 0.3 (default: {})'.format(default_arguments["ratio_gap"])
    parser.add_argument('--ratio-gap', type=float, default=default_arguments["ratio_gap"], help=help_text)
    help_text = 'random seed, e.g. 42 (default: {})'.format(default_arguments["random_seed"])
    parser.add_argument('--random-seed', type=int, default=default_arguments["random_seed"], help=help_text)
    help_text = 'threads, e.g. 4 (default: {})'.format(default_arguments["threads"])
    parser.add_argument('--threads', type=int, default=default_arguments["threads"], help=help_text)
    parser.add_argument('--dont-set-start-time', action="store_true", help="don't set start time")
    help_text = 'horizon, (default: {})'.format(default_arguments["horizon"])
    parser.add_argument('--horizon', type=int, default=default_arguments["horizon"], help=help_text)
    parser.add_argument('--alternative-objective', action="store_true")
    valid_wettkampf_days = ['saturday', 'sunday']
    parser.add_argument('day', type=str.lower, choices=valid_wettkampf_days, help='wettkampf day')
    args = parser.parse_args()
    if args.time_limit.endswith('s'):
        args.time_limit = float(args.time_limit[:-1])
    elif args.time_limit.endswith('m'):
        args.time_limit = float(args.time_limit[:-1]) * 60
    elif args.time_limit.endswith('h'):
        args.time_limit = float(args.time_limit[:-1]) * 3600
    else:
        args.time_limit = float(args.time_limit)

    main(args)
