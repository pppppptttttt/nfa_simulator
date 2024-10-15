import unittest
from nfa import NFA


class TestNFA(unittest.TestCase):
    def setUp(self):
        self._nfa = NFA(
            states_size=3,
            alphabet_size=2,
            start_states={0},
            accept_states={2},
            transitions={
                0: {0: {0}, 1: {0, 1}},
                1: {0: {2}, 1: {0}},
                2: {}
            }
        )

        # as in lecture example
        self._nfa2dfa = NFA(
            states_size=3,
            alphabet_size=2,
            start_states={0},
            accept_states={2},
            transitions={
                0: {0: {0, 1}, 1: {0}},
                1: {1: {2}},
            }
        )

        # as in lecture example
        self._dfa2min = NFA(
            states_size=3,
            alphabet_size=2,
            start_states={0},
            accept_states={1, 2},
            transitions={
                0: {0: {2}, 1: {1}},
                1: {0: {1}, 1: {2}},
                2: {0: {2}, 1: {2}}
            }
        )

    def test_accepts_empty_string(self):
        result = self._nfa.accepts("")
        self.assertFalse(result, "NFA should not accept empty string")

    def test_accepts_invalid_string(self):
        result = self._nfa.accepts("00")
        self.assertFalse(result, "NFA should not accept string '00'")

    def test_accepts_another_invalid_string(self):
        result = self._nfa.accepts("01")
        self.assertFalse(result, "NFA should not accept string '01'")

    def test_accepts_with_multiple_paths(self):
        result = self._nfa.accepts("10")
        self.assertTrue(result, "NFA should accept string '10'")

    def test_accepts_another_valid_string(self):
        result = self._nfa.accepts("110")
        self.assertTrue(result, "NFA should accept string '110'")

    def test_implicates_non_accepted_strings(self):
        result = self._nfa.accepts("111")
        self.assertFalse(result, "NFA should not accept string '111'")

    def test_state_range_validation(self):
        with self.assertRaises(ValueError):
            # Invalid states
            NFA(-1, 2, {3}, {2}, {})

        with self.assertRaises(ValueError):
            # Invalid alphabet
            NFA(3, -1, {0}, {2}, {})

        with self.assertRaises(ValueError):
            self._nfa.accepts("input string must contain integers only!")

    def test_transitions_structure(self):
        self.assertIn(0, self._nfa._transitions)
        self.assertIn(1, self._nfa._transitions)
        self.assertIn(2, self._nfa._transitions)
        self.assertEqual(len(self._nfa._transitions[0]), 2)
        self.assertEqual(len(self._nfa._transitions[1]), 2)
        self.assertEqual(len(self._nfa._transitions[2]), 0)

    def test_nfa2dfa_conversion(self):
        self.assertTrue(self._nfa2dfa.accepts("01"))
        self.assertFalse(self._nfa2dfa.accepts("00"))
        self.assertTrue(self._nfa2dfa.accepts("01101"))
        self.assertFalse(self._nfa2dfa.accepts("010"))

        self._nfa2dfa.to_DFA()

        # as in lecture example
        start_states = frozenset({0})
        accept_states = {frozenset({0, 2})}
        transitions = {
            frozenset({0}): {0: frozenset({0, 1}), 1: frozenset({0})},
            frozenset({0, 1}): {0: frozenset({0, 1}), 1: frozenset({0, 2})},
            frozenset({0, 2}): {0: frozenset({0, 1}), 1: frozenset({0})}
        }

        self.assertEqual(start_states, self._nfa2dfa._start_states)
        self.assertEqual(accept_states, self._nfa2dfa._accept_states)
        self.assertEqual(transitions, self._nfa2dfa._transitions)

        # after this, {0} will be `refactored` to state 2,
        # {0, 1} to state 0, and {0, 2} to state 1.
        self._nfa2dfa.normalize()

        self.assertEqual({2}, self._nfa2dfa._start_states)
        self.assertEqual({1}, self._nfa2dfa._accept_states)

        self.assertTrue(self._nfa2dfa.accepts("01"))
        self.assertFalse(self._nfa2dfa.accepts("00"))
        self.assertTrue(self._nfa2dfa.accepts("01101"))
        self.assertFalse(self._nfa2dfa.accepts("010"))

        self._nfa2dfa.write_to_file("out_dfa.txt")
        with open("out_dfa.txt") as f:
            self._ndfa2dfa = NFA().read_from_file(f)

        self.assertTrue(self._nfa2dfa.accepts("01"))
        self.assertFalse(self._nfa2dfa.accepts("00"))
        self.assertTrue(self._nfa2dfa.accepts("01101"))
        self.assertFalse(self._nfa2dfa.accepts("010"))

    def test_minimizing_dfa(self):
        # test lecture example
        self._dfa2min.minimize()
        self.assertEquals({0}, self._dfa2min._start_states)
        self.assertEquals({1}, self._dfa2min._accept_states)
        self.assertEquals(
            {0: {0: {1}, 1: {1}},
             1: {0: {1}, 1: {1}}},
            self._dfa2min._transitions)
        # self._dfa2min.write_to_file("minimized_dfa.txt")


if __name__ == "__main__":
    unittest.main()
