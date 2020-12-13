import logging
import unittest

from athletics_event import AthleticsEventScheduler
import umm2019


logger = logging.getLogger("matplotlib")
logger.setLevel(logging.ERROR)
msg_parameter_for_solver = 1  # 0 (silent) or 1 (verbose)


wettkampf_budget_data = {
    "saturday": {
        # wettkampf: (start_time_unit, end_time_unit)
        "U12W_4K": (22, 49),
        "U16W_5K": (13, 42),
        "WOM_7K": (9, 35),
        "U12M_4K": (0, 27),
        "U16M_6K": (6, 45),
        "MAN_10K": (20, 53),
    },
    "sunday": {
        "U14W_5K": (18, 49),
        "WOM_7K": (23, 41),
        "WOM_5K": (10, 38),
        "U14M_5K": (0, 26),
        "MAN_10K": (14,53),
        "MAN_6K": (4, 45),
    },
}


def _getFirstDisziplinAsString(wettkampf_name, groups, disziplinen, wettkampf_budget_data):
    disziplin_name = disziplinen[0]["name"]
    disziplin_length = disziplinen[0]["kwargs"]["length"]
    disziplin_begin = wettkampf_budget_data[wettkampf_name][0]
    disziplin_end = disziplin_begin + disziplin_length
    return "({}_{}_to_{}_{}, {}, {}, {})".format(
        wettkampf_name,
        groups[0],
        groups[-1],
        disziplin_name,
        groups[0],
        disziplin_begin,
        disziplin_end,
    )


def _getLastDisziplinAsString(wettkampf_name, groups, disziplinen, wettkampf_budget_data):
    disziplin_name = disziplinen[-1]["name"]
    disziplin_length = disziplinen[-1]["kwargs"]["length"]
    disziplin_begin = wettkampf_budget_data[wettkampf_name][1]
    disziplin_end = disziplin_begin + disziplin_length
    return "({}_{}_to_{}_{}, {}, {}, {})".format(
        wettkampf_name,
        groups[0],
        groups[-1],
        disziplin_name,
        groups[0],
        disziplin_begin,
        disziplin_end,
    )


class Basics(unittest.TestCase):
    _WETTKAMPF_DAY = "saturday"
    _anlagen_descriptors = [
        ("Läufe",),
        ("Weit", 2),
        ("Kugel", 2),
        ("Hoch", 2),
        ("Diskus",),
    ]
    _wettkampf_budget_data = {
        "U12M_4K": (0, 16),
    }
    _disziplinen_data = {
        "U12M_4K": [
            dict(name="60m", together=True, resource="Läufe", sequence_free=False, kwargs=dict(length=3, state=1, plot_color="yellow")),
            dict(name="Pause_1", together=False, resource=None, sequence_free=False, kwargs=dict(length=1, state=-1, plot_color='white')),
            dict(name="Weit", together=False, resource="Weit", sequence_free=True, kwargs=dict(length=3, state=1, plot_color="yellow")),
            dict(name="Pause_2", together=False, resource=None, sequence_free=False, kwargs=dict(length=1, state=-1, plot_color='white')),
            dict(name="Kugel", together=False, resource="Kugel", sequence_free=True, kwargs=dict(length=2, state=1, plot_color="yellow")),
            dict(name="Pause_3", together=False, resource=None, sequence_free=False, kwargs=dict(length=1, state=-1, plot_color='white')),
            dict(name="600m", together=True, resource="Läufe", sequence_free=False, kwargs=dict(length=3, state=1, plot_color="yellow")),
        ],
    }

    def test_instance(self):
        AthleticsEventScheduler(name="test", duration_in_units=1)

    def test_create_anlagen(self):
        event = AthleticsEventScheduler(name="test", duration_in_units=1)
        event.create_anlagen(self._anlagen_descriptors)
        self.assertEqual(str(event.scenario.resources()), "[Läufe, Weit1, Weit2, Kugel1, Kugel2, Hoch1, Hoch2, Diskus]")

    def test_scenario(self):
        event = AthleticsEventScheduler(name="test", duration_in_units=1)
        event.create_anlagen(self._anlagen_descriptors)
        teilnehmer_data = {
            "U12M_4K": {
                "Gr30": 12,
            },
        }
        event.create_disziplinen(umm2019.disziplinen_data[self._WETTKAMPF_DAY], teilnehmer_data)
        event.create_anlagen_pausen()
        event.set_wettkampf_start_times(umm2019.wettkampf_start_times[self._WETTKAMPF_DAY])
        event.ensure_pausen_for_gruppen_and_anlagen()
        scenario_as_string = str(event.scenario)
        expected_scenario_as_string = """
SCENARIO: test / horizon: 1

OBJECTIVE: U12M_4K_Gr30_to_Gr30_60m*-1+U12M_4K_Gr30_to_Gr30_600m*2

RESOURCES:
Läufe
Weit1
Weit2
Kugel1
Kugel2
Hoch1
Hoch2
Diskus
Gr30

TASKS:
U12M_4K_Gr30_to_Gr30_60m : Läufe,Gr30
U12M_4K_Gr30_Pause_1 : Gr30
U12M_4K_Gr30_Weit : Weit1|Weit2,Gr30
U12M_4K_Gr30_Pause_2 : Gr30
U12M_4K_Gr30_Kugel : Kugel1|Kugel2,Gr30
U12M_4K_Gr30_Pause_3 : Gr30
U12M_4K_Gr30_to_Gr30_600m : Läufe,Gr30
Läufe_Pause_1 : Läufe
Läufe_Pause_2 : Läufe
Weit1_Pause_1 : Weit1
Weit2_Pause_1 : Weit2
Kugel1_Pause_1 : Kugel1
Kugel2_Pause_1 : Kugel2

JOINT RESOURCES:
Weit1|Weit2 : U12M_4K_Gr30_Weit
Kugel1|Kugel2 : U12M_4K_Gr30_Kugel

LAX PRECEDENCES:
U12M_4K_Gr30_to_Gr30_60m < U12M_4K_Gr30_Weit
U12M_4K_Gr30_to_Gr30_60m < U12M_4K_Gr30_Kugel
U12M_4K_Gr30_Weit < U12M_4K_Gr30_to_Gr30_600m
U12M_4K_Gr30_Kugel < U12M_4K_Gr30_to_Gr30_600m

CAPACITY BOUNDS:
Gr30['state'][:0] <= 1
-1*Gr30['state'][:0] <= 0
Läufe['state'][:0] <= 1
-1*Läufe['state'][:0] <= 0
Weit1['state'][:0] <= 1
-1*Weit1['state'][:0] <= 0
Weit2['state'][:0] <= 1
-1*Weit2['state'][:0] <= 0
Kugel1['state'][:0] <= 1
-1*Kugel1['state'][:0] <= 0
Kugel2['state'][:0] <= 1
-1*Kugel2['state'][:0] <= 0
Hoch1['state'][:0] <= 1
-1*Hoch1['state'][:0] <= 0
Hoch2['state'][:0] <= 1
-1*Hoch2['state'][:0] <= 0
Diskus['state'][:0] <= 1
-1*Diskus['state'][:0] <= 0
"""
        self.assertIn(expected_scenario_as_string, scenario_as_string)

    def test_solution_and_objective(self):
        event = AthleticsEventScheduler(name="test", duration_in_units=40)
        event.create_anlagen(self._anlagen_descriptors)
        teilnehmer_data = {
            "U12M_4K": {
                "Gr30": 12,
            },
        }
        event.create_disziplinen(self._disziplinen_data, teilnehmer_data)
        event.create_anlagen_pausen()
        event.set_wettkampf_start_times(umm2019.wettkampf_start_times[self._WETTKAMPF_DAY])
        event.ensure_pausen_for_gruppen_and_anlagen()
        event.solve(time_limit=60, msg=msg_parameter_for_solver)
        self.assertEqual(event.scenario.objective_value(), 25)
        objective_as_string = str(event.scenario.objective())
        self.assertEqual("U12M_4K_Gr30_to_Gr30_60m*-1+U12M_4K_Gr30_to_Gr30_600m*2", objective_as_string)
        solution_as_string = str(event.scenario.solution())
        self.assertIn("(U12M_4K_Gr30_to_Gr30_60m, Gr30, 0, 3)", solution_as_string)
        self.assertIn("(U12M_4K_Gr30_to_Gr30_60m, Läufe, 0, 3)", solution_as_string)
        self.assertIn("(U12M_4K_Gr30_to_Gr30_600m, Gr30, 11, 14)", solution_as_string)
        self.assertIn("(U12M_4K_Gr30_to_Gr30_600m, Läufe, 11, 14)", solution_as_string)

    def test_solution_and_objective_in_event_with_two_groups(self):
        event = AthleticsEventScheduler(name="test", duration_in_units=40)
        event.create_anlagen(self._anlagen_descriptors)
        teilnehmer_data = {
            "U12M_4K": {
                "Gr30": 12,
                "Gr31": 12,
            },
        }
        event.create_disziplinen(self._disziplinen_data, teilnehmer_data)
        event.create_anlagen_pausen()
        event.set_wettkampf_start_times(umm2019.wettkampf_start_times[self._WETTKAMPF_DAY])
        event.ensure_pausen_for_gruppen_and_anlagen()
        event.solve(time_limit=60, msg=msg_parameter_for_solver)
        self.assertEqual(event.scenario.objective_value(), 25)
        objective_as_string = str(event.scenario.objective())
        self.assertEqual("U12M_4K_Gr30_to_Gr31_60m*-1+U12M_4K_Gr30_to_Gr31_600m*2", objective_as_string)
        solution_as_string = str(event.scenario.solution())
        self.assertIn("(U12M_4K_Gr30_to_Gr31_60m, Gr30, 0, 3)", solution_as_string)
        self.assertIn("(U12M_4K_Gr30_to_Gr31_60m, Gr31, 0, 3)", solution_as_string)
        self.assertIn("(U12M_4K_Gr30_to_Gr31_60m, Läufe, 0, 3)", solution_as_string)
        self.assertIn("(U12M_4K_Gr30_to_Gr31_600m, Gr30, 11, 14)", solution_as_string)
        self.assertIn("(U12M_4K_Gr30_to_Gr31_600m, Gr31, 11, 14)", solution_as_string)
        self.assertIn("(U12M_4K_Gr30_to_Gr31_600m, Läufe, 11, 14)", solution_as_string)

    def test_solution_and_objective_in_event_with_four_groups(self):
        event = AthleticsEventScheduler(name="test", duration_in_units=40)
        event.create_anlagen(self._anlagen_descriptors)
        teilnehmer_data = {
            "U12M_4K": {
                "Gr30": 12,
                "Gr31": 12,
                "Gr32": 12,
                "Gr33": 12,
            },
        }
        event.create_disziplinen(self._disziplinen_data, teilnehmer_data)
        event.create_anlagen_pausen()
        event.set_wettkampf_start_times(umm2019.wettkampf_start_times[self._WETTKAMPF_DAY])
        event.ensure_pausen_for_gruppen_and_anlagen()
        event.solve(time_limit=60, msg=msg_parameter_for_solver)
        self.assertEqual(event.scenario.objective_value(), 27)
        objective_as_string = str(event.scenario.objective())
        self.assertEqual("U12M_4K_Gr30_to_Gr33_60m*-1+U12M_4K_Gr30_to_Gr33_600m*2", objective_as_string)
        solution_as_string = str(event.scenario.solution())
        self.assertIn("(U12M_4K_Gr30_to_Gr33_60m, Gr30, 0, 3)", solution_as_string)
        self.assertIn("(U12M_4K_Gr30_to_Gr33_60m, Gr31, 0, 3)", solution_as_string)
        self.assertIn("(U12M_4K_Gr30_to_Gr33_60m, Gr32, 0, 3)", solution_as_string)
        self.assertIn("(U12M_4K_Gr30_to_Gr33_60m, Gr33, 0, 3)", solution_as_string)
        self.assertIn("(U12M_4K_Gr30_to_Gr33_60m, Läufe, 0, 3)", solution_as_string)
        self.assertIn("(U12M_4K_Gr30_to_Gr33_600m, Gr30, 12, 15)", solution_as_string)
        self.assertIn("(U12M_4K_Gr30_to_Gr33_600m, Gr31, 12, 15)", solution_as_string)
        self.assertIn("(U12M_4K_Gr30_to_Gr33_600m, Gr32, 12, 15)", solution_as_string)
        self.assertIn("(U12M_4K_Gr30_to_Gr33_600m, Gr33, 12, 15)", solution_as_string)
        self.assertIn("(U12M_4K_Gr30_to_Gr33_600m, Läufe, 12, 15)", solution_as_string)

    def test_solution_and_objective_in_event_with_six_groups(self):
        event = AthleticsEventScheduler(name="test", duration_in_units=40)
        event.create_anlagen(self._anlagen_descriptors)
        teilnehmer_data = {
            "U12M_4K": {
                "Gr30": 12,
                "Gr31": 12,
                "Gr32": 12,
                "Gr33": 12,
                "Gr34": 12,
                "Gr35": 12,
            },
        }
        event.create_disziplinen(self._disziplinen_data, teilnehmer_data)
        event.create_anlagen_pausen()
        event.set_wettkampf_start_times(umm2019.wettkampf_start_times[self._WETTKAMPF_DAY])
        event.ensure_pausen_for_gruppen_and_anlagen()
        event.solve(time_limit=60, msg=msg_parameter_for_solver)
        self.assertEqual(event.scenario.objective_value(), 46)
        objective_as_string = str(event.scenario.objective())
        self.assertEqual("U12M_4K_Gr30_to_Gr35_60m*-1+U12M_4K_Gr30_to_Gr35_600m*2", objective_as_string)
        solution_as_string = str(event.scenario.solution())
        self.assertIn("(U12M_4K_Gr30_to_Gr35_60m, Gr30, 0, 3)", solution_as_string)
        self.assertIn("(U12M_4K_Gr30_to_Gr35_60m, Gr31, 0, 3)", solution_as_string)
        self.assertIn("(U12M_4K_Gr30_to_Gr35_60m, Gr32, 0, 3)", solution_as_string)
        self.assertIn("(U12M_4K_Gr30_to_Gr35_60m, Gr33, 0, 3)", solution_as_string)
        self.assertIn("(U12M_4K_Gr30_to_Gr35_60m, Gr34, 0, 3)", solution_as_string)
        self.assertIn("(U12M_4K_Gr30_to_Gr35_60m, Gr35, 0, 3)", solution_as_string)
        self.assertIn("(U12M_4K_Gr30_to_Gr35_60m, Läufe, 0, 3)", solution_as_string)
        self.assertIn("(U12M_4K_Gr30_to_Gr35_600m, Gr30, 28, 31)", solution_as_string)
        self.assertIn("(U12M_4K_Gr30_to_Gr35_600m, Gr31, 28, 31)", solution_as_string)
        self.assertIn("(U12M_4K_Gr30_to_Gr35_600m, Gr32, 28, 31)", solution_as_string)
        self.assertIn("(U12M_4K_Gr30_to_Gr35_600m, Gr33, 28, 31)", solution_as_string)
        self.assertIn("(U12M_4K_Gr30_to_Gr35_600m, Gr34, 28, 31)", solution_as_string)
        self.assertIn("(U12M_4K_Gr30_to_Gr35_600m, Gr35, 28, 31)", solution_as_string)
        self.assertIn("(U12M_4K_Gr30_to_Gr35_600m, Läufe, 28, 31)", solution_as_string)

    def test_solution_and_objective_in_event_with_seven_groups(self):
        event = AthleticsEventScheduler(name="test", duration_in_units=60)
        event.create_anlagen(self._anlagen_descriptors)
        teilnehmer_data = {
            "U12M_4K": {
                "Gr30": 12,
                "Gr31": 12,
                "Gr32": 12,
                "Gr33": 12,
                "Gr34": 12,
                "Gr35": 12,
                "Gr36": 12,
            },
        }
        event.create_disziplinen(self._disziplinen_data, teilnehmer_data)
        event.create_anlagen_pausen()
        event.set_wettkampf_start_times(umm2019.wettkampf_start_times[self._WETTKAMPF_DAY])
        event.ensure_pausen_for_gruppen_and_anlagen()
        event.solve(time_limit=120, msg=msg_parameter_for_solver)
        self.assertEqual(event.scenario.objective_value(), 26)
        objective_as_string = str(event.scenario.objective())
        self.assertEqual("U12M_4K_Gr30_to_Gr36_60m*-1+U12M_4K_Gr30_to_Gr36_600m*2", objective_as_string)
        solution_as_string = str(event.scenario.solution())
        self.assertIn("(U12M_4K_Gr30_to_Gr36_60m, Gr30, 0, 3)", solution_as_string)
        self.assertIn("(U12M_4K_Gr30_to_Gr36_60m, Gr31, 0, 3)", solution_as_string)
        self.assertIn("(U12M_4K_Gr30_to_Gr36_60m, Gr32, 0, 3)", solution_as_string)
        self.assertIn("(U12M_4K_Gr30_to_Gr36_60m, Gr33, 0, 3)", solution_as_string)
        self.assertIn("(U12M_4K_Gr30_to_Gr36_60m, Gr34, 0, 3)", solution_as_string)
        self.assertIn("(U12M_4K_Gr30_to_Gr36_60m, Gr35, 0, 3)", solution_as_string)
        self.assertIn("(U12M_4K_Gr30_to_Gr36_60m, Gr36, 0, 3)", solution_as_string)
        self.assertIn("(U12M_4K_Gr30_to_Gr36_60m, Läufe, 0, 3)", solution_as_string)
        self.assertIn("(U12M_4K_Gr30_to_Gr36_600m, Gr30, 20, 23)", solution_as_string)
        self.assertIn("(U12M_4K_Gr30_to_Gr36_600m, Gr31, 20, 23)", solution_as_string)
        self.assertIn("(U12M_4K_Gr30_to_Gr36_600m, Gr32, 20, 23)", solution_as_string)
        self.assertIn("(U12M_4K_Gr30_to_Gr36_600m, Gr33, 20, 23)", solution_as_string)
        self.assertIn("(U12M_4K_Gr30_to_Gr36_600m, Gr34, 20, 23)", solution_as_string)
        self.assertIn("(U12M_4K_Gr30_to_Gr36_600m, Gr35, 20, 23)", solution_as_string)
        self.assertIn("(U12M_4K_Gr30_to_Gr36_600m, Gr36, 20, 23)", solution_as_string)
        self.assertIn("(U12M_4K_Gr30_to_Gr36_600m, Läufe, 20, 23)", solution_as_string)


class BaseEventWithWettkampfHelper(unittest.TestCase):
    _SATURDAY = "saturday"
    _SUNDAY = "sunday"

    def wettkampf_helper(self, wettkampf_budget_data, wettkampf_day, last_wettkampf_of_the_day=None, time_limit=120, objective_override_disziplinen_factors=None):
        event = AthleticsEventScheduler(name="test", duration_in_units=60)
        teilnehmer_data = { wettkampf_name: umm2019.teilnehmer_data[wettkampf_name] for wettkampf_name in wettkampf_budget_data }
        event.prepare(
            anlagen_descriptors=umm2019.anlagen_descriptors[wettkampf_day],
            disziplinen_data=umm2019.disziplinen_data[wettkampf_day],
            teilnehmer_data=teilnehmer_data,
            wettkampf_start_times=umm2019.wettkampf_start_times[wettkampf_day])
        if objective_override_disziplinen_factors:
            event.set_objective(objective_override_disziplinen_factors)
        logging.debug("objective: {}".format(event.scenario.objective()))

        if last_wettkampf_of_the_day:
            event.ensure_last_wettkampf_of_the_day(last_wettkampf_of_the_day)
        event.solve(time_limit=time_limit, msg=msg_parameter_for_solver)
        logging.debug("objective_value: {}".format(event.scenario.objective_value()))

        solution_as_string = str(event.scenario.solution())
        for wettkampf_name in wettkampf_budget_data:
            groups = event.getGroups(wettkampf_name)
            disziplinen = event.getDisziplinen(wettkampf_name)
            expected_first_disziplin_as_string = _getFirstDisziplinAsString(wettkampf_name, groups, disziplinen, wettkampf_budget_data)
            self.assertIn(expected_first_disziplin_as_string, solution_as_string)
            expected_last_disziplin_as_string = _getLastDisziplinAsString(wettkampf_name, groups, disziplinen, wettkampf_budget_data)
            self.assertIn(expected_last_disziplin_as_string, solution_as_string)
        self.event = event


class OneEventWithStrictSequence(BaseEventWithWettkampfHelper):
    def test_scheduling_of_first_and_last_disziplin_for_wettkampf_WOM_7K_saturday(self):
        wettkampf_budget_data = {
           "WOM_7K" : (9, 27),
        }
        self.wettkampf_helper(wettkampf_budget_data=wettkampf_budget_data, wettkampf_day=self._SATURDAY)

    def test_scheduling_of_first_and_last_disziplin_for_wettkampf_WOM_7K_sunday(self):
        wettkampf_budget_data = {
            "WOM_7K": (23, 38),
        }
        wettkampf_day = self._SUNDAY
        self.wettkampf_helper(wettkampf_budget_data=wettkampf_budget_data, wettkampf_day=self._SUNDAY)

    def test_scheduling_of_first_and_last_disziplin_for_wettkampf_U16M_6K(self):
        wettkampf_budget_data = {
            "U16M_6K": (6, 37),
        }
        self.wettkampf_helper(wettkampf_budget_data=wettkampf_budget_data, wettkampf_day=self._SATURDAY)

    def test_scheduling_of_first_and_last_disziplin_for_wettkampf_MAN_10K_saturday(self):
        wettkampf_budget_data = {
            "MAN_10K": (20, 46),
        }
        self.wettkampf_helper(wettkampf_budget_data=wettkampf_budget_data, wettkampf_day=self._SATURDAY)

    def test_scheduling_of_first_and_last_disziplin_for_wettkampf_MAN_10K_sunday(self):
        wettkampf_budget_data = {
            "MAN_10K": (14, 46),
        }
        self.wettkampf_helper(wettkampf_budget_data=wettkampf_budget_data, wettkampf_day=self._SUNDAY)


class OneEventWithRandomSequence(BaseEventWithWettkampfHelper):
    def test_scheduling_of_first_and_last_disziplin_for_wettkampf_U12W_4K(self):
        wettkampf_budget_data = {
            "U12W_4K": (22, 42),
        }
        disziplinen_factors={
            "U12W_4K_Gr14_to_Gr20_60m": -1,
            "U12W_4K_Gr14_to_Gr20_600m": 2,
        }
        self.wettkampf_helper(wettkampf_budget_data=wettkampf_budget_data, wettkampf_day=self._SATURDAY, objective_override_disziplinen_factors=disziplinen_factors)

    def test_scheduling_of_first_and_last_disziplin_for_wettkampf_U16W_5K(self):
        wettkampf_budget_data = {
            "U16W_5K": (13, 31),
        }
        self.wettkampf_helper(wettkampf_budget_data=wettkampf_budget_data, wettkampf_day=self._SATURDAY)

    def test_scheduling_of_first_and_last_disziplin_for_wettkampf_U12M_4K(self):
        wettkampf_budget_data = {
            "U12M_4K": (0, 16),
        }
        self.wettkampf_helper(wettkampf_budget_data=wettkampf_budget_data, wettkampf_day=self._SATURDAY)


class MoreEvents(BaseEventWithWettkampfHelper):
    def test_scheduling_of_first_and_last_disziplin_for_wettkampf_WOM_7K_and_U16M_6K_and_MAN_10K(self):
        wettkampf_budget_data = {
            "U16M_6K": (6, 37),
            "WOM_7K": (9, 27),
            "MAN_10K": (20, 46),
        }
        self.wettkampf_helper(wettkampf_budget_data=wettkampf_budget_data, wettkampf_day=self._SATURDAY)

    def test_scheduling_of_first_and_last_disziplin_for_wettkampf_U16W_5K_and_WOM_7K_and_U16M_6K_and_MAN_10K(self):
        wettkampf_budget_data = {
            "U16M_6K": (6, 37),
            "WOM_7K": (9, 27),
            "U16W_5K": (13, 42),  # much too late (should be 31)
            "MAN_10K": (20, 46),  # much too late (should be 46)
        }
        self.wettkampf_helper(wettkampf_budget_data=wettkampf_budget_data, wettkampf_day=self._SATURDAY, last_wettkampf_of_the_day="MAN_10K")

    def test_scheduling_of_first_and_last_disziplin_for_wettkampf_U12W_4K_and_U12M_4K_1(self):
        wettkampf_budget_data = {
            "U12M_4K": (0, 16),
            "U12W_4K": (22, 59),  # +17
        }
        disziplinen_factors={
            "U12W_4K_Gr14_to_Gr20_60m": -1,
            "U12W_4K_Gr14_to_Gr20_600m": 1,
            "U12M_4K_Gr30_to_Gr34_60m": -1,
            "U12M_4K_Gr30_to_Gr34_600m": 1,
        }
        self.wettkampf_helper(wettkampf_budget_data=wettkampf_budget_data, wettkampf_day=self._SATURDAY, objective_override_disziplinen_factors=disziplinen_factors)

    def test_scheduling_of_first_and_last_disziplin_for_wettkampf_U12W_4K_and_U12M_4K_2(self):
        wettkampf_budget_data = {
            "U12M_4K": (0, 16),
            "U12W_4K": (22, 47),  # +5
        }
        disziplinen_factors={
            "U12W_4K_Gr14_to_Gr20_60m": -1,
            "U12W_4K_Gr14_to_Gr20_600m": 2,
            "U12M_4K_Gr30_to_Gr34_60m": -1,
            "U12M_4K_Gr30_to_Gr34_600m": 2,
        }
        self.wettkampf_helper(wettkampf_budget_data=wettkampf_budget_data, wettkampf_day=self._SATURDAY, objective_override_disziplinen_factors=disziplinen_factors)


    def test_scheduling_of_first_and_last_disziplin_for_wettkampf_U12W_4K_and_U12M_4K_3(self):
        wettkampf_budget_data = {
            "U12M_4K": (0, 16),
            "U12W_4K": (22, 43),  # +1
        }
        disziplinen_factors={
            "U12W_4K_Gr14_to_Gr20_60m": -11,
            "U12W_4K_Gr14_Weit": 3,
            "U12W_4K_Gr14_Kugel": 2,
            "U12W_4K_Gr15_Weit": 3,
            "U12W_4K_Gr15_Kugel": 2,
            "U12W_4K_Gr16_Weit": 3,
            "U12W_4K_Gr16_Kugel": 2,
            "U12W_4K_Gr17_Weit": 3,
            "U12W_4K_Gr17_Kugel": 2,
            "U12W_4K_Gr18_Weit": 3,
            "U12W_4K_Gr18_Kugel": 2,
            "U12W_4K_Gr19_Weit": 3,
            "U12W_4K_Gr19_Kugel": 2,
            "U12W_4K_Gr20_Weit": 3,
            "U12W_4K_Gr20_Kugel": 2,
            "U12W_4K_Gr14_to_Gr20_600m": 6,
            "U12M_4K_Gr30_to_Gr34_60m": -11,
            "U12M_4K_Gr30_Weit": 3,
            "U12M_4K_Gr30_Kugel": 2,
            "U12M_4K_Gr31_Weit": 3,
            "U12M_4K_Gr31_Kugel": 2,
            "U12M_4K_Gr32_Weit": 3,
            "U12M_4K_Gr32_Kugel": 2,
            "U12M_4K_Gr33_Weit": 3,
            "U12M_4K_Gr33_Kugel": 2,
            "U12M_4K_Gr34_Weit": 3,
            "U12M_4K_Gr34_Kugel": 2,
            "U12M_4K_Gr30_to_Gr34_600m": 6,
        }
        self.wettkampf_helper(wettkampf_budget_data=wettkampf_budget_data, wettkampf_day=self._SATURDAY, objective_override_disziplinen_factors=disziplinen_factors)

    def test_scheduling_of_first_and_last_disziplin_for_wettkampf_U12W_4K_and_U12M_4K_4(self):
        wettkampf_budget_data = {
            "U12M_4K": (0, 16),
            "U12W_4K": (22, 42),
        }
        disziplinen_factors={
            "U12W_4K_Gr14_to_Gr20_60m": -13,
            "U12W_4K_Gr14_Weit": 6,
            "U12W_4K_Gr14_Kugel": 3,
            "U12W_4K_Gr15_Weit": 6,
            "U12W_4K_Gr15_Kugel": 3,
            "U12W_4K_Gr16_Weit": 6,
            "U12W_4K_Gr16_Kugel": 3,
            "U12W_4K_Gr17_Weit": 6,
            "U12W_4K_Gr17_Kugel": 3,
            "U12W_4K_Gr18_Weit": 6,
            "U12W_4K_Gr18_Kugel": 3,
            "U12W_4K_Gr19_Weit": 6,
            "U12W_4K_Gr19_Kugel": 3,
            "U12W_4K_Gr20_Weit": 6,
            "U12W_4K_Gr20_Kugel": 3,
            "U12W_4K_Gr14_to_Gr20_600m": 4,
            "U12M_4K_Gr30_to_Gr34_60m": -11,
            "U12M_4K_Gr30_Weit": 6,
            "U12M_4K_Gr30_Kugel": 3,
            "U12M_4K_Gr31_Weit": 6,
            "U12M_4K_Gr31_Kugel": 3,
            "U12M_4K_Gr32_Weit": 6,
            "U12M_4K_Gr32_Kugel": 3,
            "U12M_4K_Gr33_Weit": 6,
            "U12M_4K_Gr33_Kugel": 3,
            "U12M_4K_Gr34_Weit": 6,
            "U12M_4K_Gr34_Kugel": 3,
            "U12M_4K_Gr30_to_Gr34_600m": 2,
        }
        self.wettkampf_helper(wettkampf_budget_data=wettkampf_budget_data, wettkampf_day=self._SATURDAY, objective_override_disziplinen_factors=disziplinen_factors)

    def test_scheduling_of_first_and_last_disziplin_for_wettkampf_U12W_4K_and_U12M_4K_5(self):
        wettkampf_budget_data = {
            "U12M_4K": (0, 16),
            "U12W_4K": (22, 42),
        }
        disziplinen_factors={
            "U12W_4K_Gr14_to_Gr20_60m": -11,
            "U12W_4K_Gr14_Weit": 6,
            "U12W_4K_Gr14_Kugel": 3,
            "U12W_4K_Gr15_Weit": 6,
            "U12W_4K_Gr15_Kugel": 3,
            "U12W_4K_Gr16_Weit": 6,
            "U12W_4K_Gr16_Kugel": 3,
            "U12W_4K_Gr17_Weit": 6,
            "U12W_4K_Gr17_Kugel": 3,
            "U12W_4K_Gr18_Weit": 6,
            "U12W_4K_Gr18_Kugel": 3,
            "U12W_4K_Gr19_Weit": 6,
            "U12W_4K_Gr19_Kugel": 3,
            "U12W_4K_Gr20_Weit": 6,
            "U12W_4K_Gr20_Kugel": 3,
            "U12W_4K_Gr14_to_Gr20_600m": 2,
            "U12M_4K_Gr30_to_Gr34_60m": -11,
            "U12M_4K_Gr30_Weit": 6,
            "U12M_4K_Gr30_Kugel": 3,
            "U12M_4K_Gr31_Weit": 6,
            "U12M_4K_Gr31_Kugel": 3,
            "U12M_4K_Gr32_Weit": 6,
            "U12M_4K_Gr32_Kugel": 3,
            "U12M_4K_Gr33_Weit": 6,
            "U12M_4K_Gr33_Kugel": 3,
            "U12M_4K_Gr34_Weit": 6,
            "U12M_4K_Gr34_Kugel": 3,
            "U12M_4K_Gr30_to_Gr34_600m": 2,
        }
        self.wettkampf_helper(wettkampf_budget_data=wettkampf_budget_data, wettkampf_day=self._SATURDAY, objective_override_disziplinen_factors=disziplinen_factors)

    def test_scheduling_of_first_and_last_disziplin_for_wettkampf_U12W_4K_and_U12M_4K_6(self):
        wettkampf_budget_data = {
            "U12M_4K": (0, 16),
            "U12W_4K": (22, 42),
        }
        disziplinen_factors={
            "U12W_4K_Gr14_to_Gr20_60m": -77,
            "U12W_4K_Gr14_Weit": 1,
            "U12W_4K_Gr14_Kugel": 1,
            "U12W_4K_Gr15_Weit": 1,
            "U12W_4K_Gr15_Kugel": 1,
            "U12W_4K_Gr16_Weit": 1,
            "U12W_4K_Gr16_Kugel": 1,
            "U12W_4K_Gr17_Weit": 1,
            "U12W_4K_Gr17_Kugel": 1,
            "U12W_4K_Gr18_Weit": 1,
            "U12W_4K_Gr18_Kugel": 1,
            "U12W_4K_Gr19_Weit": 1,
            "U12W_4K_Gr19_Kugel": 1,
            "U12W_4K_Gr20_Weit": 1,
            "U12W_4K_Gr20_Kugel": 1,
            "U12W_4K_Gr14_to_Gr20_600m": 63,
            "U12M_4K_Gr30_to_Gr34_60m": -60,
            "U12M_4K_Gr30_Weit": 1,
            "U12M_4K_Gr30_Kugel": 1,
            "U12M_4K_Gr31_Weit": 1,
            "U12M_4K_Gr31_Kugel": 1,
            "U12M_4K_Gr32_Weit": 1,
            "U12M_4K_Gr32_Kugel": 1,
            "U12M_4K_Gr33_Weit": 1,
            "U12M_4K_Gr33_Kugel": 1,
            "U12M_4K_Gr34_Weit": 1,
            "U12M_4K_Gr34_Kugel": 1,
            "U12M_4K_Gr30_to_Gr34_600m": 50,
        }
        self.wettkampf_helper(wettkampf_budget_data=wettkampf_budget_data, wettkampf_day=self._SATURDAY, objective_override_disziplinen_factors=disziplinen_factors)


if __name__ == '__main__':
    unittest.main()