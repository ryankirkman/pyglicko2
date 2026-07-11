"""
Copyright (c) 2009 Ryan Kirkman

Permission is hereby granted, free of charge, to any person
obtaining a copy of this software and associated documentation
files (the "Software"), to deal in the Software without
restriction, including without limitation the rights to use,
copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the
Software is furnished to do so, subject to the following
conditions:

The above copyright notice and this permission notice shall be
included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES
OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
OTHER DEALINGS IN THE SOFTWARE.
"""

import math
import unittest

import glicko2


class PaperExampleTest(unittest.TestCase):
    """ The worked example from http://www.glicko.net/glicko/glicko2.pdf:
    a 1500-rated player with RD 200 and volatility 0.06 plays opponents
    rated 1400, 1550 and 1700 (RDs 30, 100 and 300), winning the first
    game and losing the other two. The paper rounds intermediate values,
    so expected results carry a small tolerance. """

    def test_paper_example(self):
        player = glicko2.Player(rating = 1500, rd = 200, vol = 0.06)
        player.update_player([1400, 1550, 1700], [30, 100, 300], [1, 0, 0])
        self.assertAlmostEqual(player.rating, 1464.06, delta = 0.01)
        self.assertAlmostEqual(player.rd, 151.52, delta = 0.01)
        self.assertAlmostEqual(player.vol, 0.05999, delta = 0.0001)


class SurprisingOutcomesTest(unittest.TestCase):
    """ Regression tests for the volatility update (Step 5). The old
    Newton-Raphson iteration produced wildly wrong results on these
    inputs (rating errors of hundreds of points). Expected values come
    from an independent implementation of the Illinois algorithm in the
    February 22, 2012 revision of the Glicko-2 paper. """

    def test_stable_player_sweeps_stronger_field(self):
        player = glicko2.Player(rating = 1500, rd = 30, vol = 0.06)
        player.update_player([2000] * 12, [40] * 12, [1] * 12)
        self.assertAlmostEqual(player.rating, 1564.4601, delta = 0.001)
        self.assertAlmostEqual(player.rd, 31.5399, delta = 0.001)
        self.assertAlmostEqual(player.vol, 0.0617572, delta = 0.00001)

    def test_stable_player_loses_to_weaker_field(self):
        player = glicko2.Player(rating = 2700, rd = 60, vol = 0.06)
        player.update_player([1500] * 20, [60] * 20, [0] * 20)
        self.assertAlmostEqual(player.rating, 2279.2508, delta = 0.001)
        self.assertAlmostEqual(player.rd, 61.0283, delta = 0.001)
        self.assertAlmostEqual(player.vol, 0.0667549, delta = 0.00001)

    def test_moderate_upset_series(self):
        player = glicko2.Player(rating = 2200, rd = 40, vol = 0.06)
        player.update_player([1600] * 15, [50] * 15, [0] * 15)
        self.assertAlmostEqual(player.rating, 2061.6009, delta = 0.001)
        self.assertAlmostEqual(player.rd, 40.9443, delta = 0.001)
        self.assertAlmostEqual(player.vol, 0.0629712, delta = 0.00001)

    def test_terminates_on_previously_hanging_input(self):
        # This input made the old exact-equality convergence test loop
        # forever. The Illinois algorithm must terminate and match the
        # independently verified result.
        player = glicko2.Player(rating = 2710.0078, rd = 301.9688, vol = 0.2)
        player.update_player(
            [926.7, 1679.0, 1264.7, 1135.9, 800.0, 747.6],
            [25.1, 186.7, 62.5, 307.1, 191.8, 56.9],
            [0, 0, 0, 0, 0.5, 0])
        self.assertAlmostEqual(player.rating, 112.2757, delta = 0.001)
        self.assertAlmostEqual(player.rd, 301.6729, delta = 0.001)
        self.assertAlmostEqual(player.vol, 0.2140866, delta = 0.000001)


class DidNotCompeteTest(unittest.TestCase):
    def test_rd_increases_rating_and_vol_unchanged(self):
        player = glicko2.Player(rating = 1850, rd = 50, vol = 0.06)
        player.did_not_compete()
        phi = 50 / 173.7178
        expected_rd = math.sqrt(phi ** 2 + 0.06 ** 2) * 173.7178
        self.assertAlmostEqual(player.rd, expected_rd, delta = 1e-9)
        self.assertAlmostEqual(player.rating, 1850, delta = 1e-9)
        self.assertEqual(player.vol, 0.06)

    def test_empty_game_list_treated_as_not_competing(self):
        player = glicko2.Player(rating = 1850, rd = 50, vol = 0.06)
        expected = glicko2.Player(rating = 1850, rd = 50, vol = 0.06)
        expected.did_not_compete()
        player.update_player([], [], [])
        self.assertAlmostEqual(player.rating, expected.rating, delta = 1e-9)
        self.assertAlmostEqual(player.rd, expected.rd, delta = 1e-9)
        self.assertEqual(player.vol, expected.vol)


class InputValidationTest(unittest.TestCase):
    def test_mismatched_list_lengths_raise(self):
        player = glicko2.Player()
        with self.assertRaises(ValueError):
            player.update_player([1400, 1550], [30], [1, 0])

    def test_invalid_tau_raises(self):
        for tau in [0, -0.5, float("inf"), float("-inf"), float("nan")]:
            with self.assertRaises(ValueError):
                glicko2.Player(tau = tau)


class PropertyTest(unittest.TestCase):
    def test_draw_between_identical_players_keeps_rating(self):
        player = glicko2.Player(rating = 1850, rd = 120, vol = 0.06)
        player.update_player([1850], [120], [0.5])
        self.assertAlmostEqual(player.rating, 1850, delta = 1e-6)
        self.assertLess(player.rd, 120)

    def test_win_raises_and_loss_lowers_rating(self):
        winner = glicko2.Player(rating = 1500, rd = 200, vol = 0.06)
        loser = glicko2.Player(rating = 1500, rd = 200, vol = 0.06)
        winner.update_player([1500], [200], [1])
        loser.update_player([1500], [200], [0])
        self.assertGreater(winner.rating, 1500)
        self.assertLess(loser.rating, 1500)

    def test_custom_tau(self):
        default_tau = glicko2.Player(rating = 2200, rd = 40, vol = 0.06)
        small_tau = glicko2.Player(rating = 2200, rd = 40, vol = 0.06,
                                   tau = 0.2)
        default_tau.update_player([1600] * 15, [50] * 15, [0] * 15)
        small_tau.update_player([1600] * 15, [50] * 15, [0] * 15)
        # A smaller tau constrains how much the volatility can grow
        # after surprising results.
        self.assertLess(small_tau.vol, default_tau.vol)


if __name__ == "__main__":
    unittest.main()
