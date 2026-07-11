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

class Player:
    # Class attribute
    # The system constant, which constrains
    # the change in volatility over time.
    _tau = 0.5

    def getRating(self):
        return (self.__rating * 173.7178) + 1500 

    def setRating(self, rating):
        self.__rating = (rating - 1500) / 173.7178

    rating = property(getRating, setRating)

    def getRd(self):
        return self.__rd * 173.7178

    def setRd(self, rd):
        self.__rd = rd / 173.7178

    rd = property(getRd, setRd)
     
    def __init__(self, rating = 1500, rd = 350, vol = 0.06, tau = None):
        """Create a player.

        tau is the Glicko-2 system constant. Callers should use the same
        value for every player in a rating system.
        """
        # For testing purposes, preload the values
        # assigned to an unrated player.
        self.setRating(rating)
        self.setRd(rd)
        self.vol = vol
        if tau is not None:
            if not math.isfinite(tau) or tau <= 0:
                raise ValueError("tau must be a positive finite number")
            self._tau = tau
            
    def _preRatingRD(self):
        """ Calculates and updates the player's rating deviation for the
        beginning of a rating period.
        
        preRatingRD() -> None
        
        """
        self.__rd = math.sqrt(math.pow(self.__rd, 2) + math.pow(self.vol, 2))
        
    def update_player(self, rating_list, RD_list, outcome_list):
        """ Calculates the new rating and rating deviation of the player.

        Outcomes are 1 for a win, 0.5 for a draw and 0 for a loss.
        An empty game list is treated as not competing (Step 6 only).

        update_player(list[float], list[float], list[float]) -> None

        """
        if not len(rating_list) == len(RD_list) == len(outcome_list):
            raise ValueError("rating_list, RD_list and outcome_list "
                             "must have the same length")
        if not rating_list:
            self.did_not_compete()
            return

        # Convert the rating and rating deviation values for internal use.
        rating_list = [(x - 1500) / 173.7178 for x in rating_list]
        RD_list = [x / 173.7178 for x in RD_list]

        v = self._v(rating_list, RD_list)
        self.vol = self._newVol(rating_list, RD_list, outcome_list, v)
        self._preRatingRD()
        
        self.__rd = 1 / math.sqrt((1 / math.pow(self.__rd, 2)) + (1 / v))
        
        tempSum = 0
        for i in range(len(rating_list)):
            tempSum += self._g(RD_list[i]) * \
                       (outcome_list[i] - self._E(rating_list[i], RD_list[i]))
        self.__rating += math.pow(self.__rd, 2) * tempSum
        
        
    def _newVol(self, rating_list, RD_list, outcome_list, v):
        """ Calculating the new volatility as per the Glicko2 system.

        Uses the Illinois algorithm from the February 22, 2012 revision
        of the algorithm (Step 5 of http://www.glicko.net/glicko/glicko2.pdf),
        which replaced the unstable Newton-Raphson iteration.

        _newVol(list, list, list, float) -> float

        """
        delta = self._delta(rating_list, RD_list, outcome_list, v)
        phi = self.__rd
        tau = self._tau
        a = math.log(math.pow(self.vol, 2))
        eps = 0.000001

        def f(x):
            ex = math.exp(x)
            return (ex * (math.pow(delta, 2) - math.pow(phi, 2) - v - ex)) \
                   / (2 * math.pow(math.pow(phi, 2) + v + ex, 2)) \
                   - (x - a) / math.pow(tau, 2)

        # Set the initial values A and B so that they bracket ln(vol'^2).
        A = a
        if math.pow(delta, 2) > math.pow(phi, 2) + v:
            B = math.log(math.pow(delta, 2) - math.pow(phi, 2) - v)
        else:
            k = 1
            while f(a - k * tau) < 0:
                k += 1
            B = a - k * tau

        # Iteratively narrow the bracket until it is smaller than eps.
        fA = f(A)
        fB = f(B)
        while math.fabs(B - A) > eps:
            C = A + (A - B) * fA / (fB - fA)
            fC = f(C)
            if fC * fB <= 0:
                A = B
                fA = fB
            else:
                fA = fA / 2
            B = C
            fB = fC

        return math.exp(A / 2)

    def _delta(self, rating_list, RD_list, outcome_list, v):
        """ The delta function of the Glicko2 system.
        
        _delta(list, list, list) -> float
        
        """
        tempSum = 0
        for i in range(len(rating_list)):
            tempSum += self._g(RD_list[i]) * (outcome_list[i] - self._E(rating_list[i], RD_list[i]))
        return v * tempSum
        
    def _v(self, rating_list, RD_list):
        """ The v function of the Glicko2 system.

        _v(list[float], list[float]) -> float

        """
        tempSum = 0
        for i in range(len(rating_list)):
            tempE = self._E(rating_list[i], RD_list[i])
            tempSum += math.pow(self._g(RD_list[i]), 2) * tempE * (1 - tempE)
        return 1 / tempSum
        
    def _E(self, p2rating, p2RD):
        """ The Glicko E function.

        _E(float, float) -> float

        """
        return 1 / (1 + math.exp(-1 * self._g(p2RD) * \
                                 (self.__rating - p2rating)))
        
    def _g(self, RD):
        """ The Glicko2 g(RD) function.
        
        _g() -> float
        
        """
        return 1 / math.sqrt(1 + 3 * math.pow(RD, 2) / math.pow(math.pi, 2))
        
    def did_not_compete(self):
        """ Applies Step 6 of the algorithm. Use this for
        players who did not compete in the rating period.

        did_not_compete() -> None
        
        """
        self._preRatingRD()
