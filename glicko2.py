import math

class Player:
    def __init__(self, rating = 0, rd = (200/173.7178), vol = 0.06):
        # For testing purposes, preload the values
        # assigned to an unrated player.
        self.__rating = rating
        self.__rd = rd
        self.__vol = vol
        # The system constant, which constrains
        # the change in volatility over time.
        self.__tau = 0.5
             
    def __preRatingRD(self):
        """ Calculates and updates the player's rating deviation for the
        beginning of a rating period.
        
        preRatingRD() -> None
        
        """
        self.__rd = math.sqrt(math.pow(self.__rd, 2) + math.pow(self.__vol, 2))
        
    def update_player(self, rating_list, RD_list, outcome_list):
        """ Calculates the new rating and rating deviation of the player.
        
        update_player(list[int], list[int], list[bool]) -> None
        
        """
        v = self.__v(rating_list, RD_list)
        self.__vol = self.__newVol(rating_list, RD_list, outcome_list, v)
        self.__preRatingRD()
        
        self.__rd = 1 / math.sqrt((1 / math.pow(self.__rd, 2)) + (1 / v))
        
        tempSum = 0
        for i in range(len(rating_list)):
            tempSum += self.__g(RD_list[i]) * \
                       (outcome_list[i] - self.__E(rating_list[i], RD_list[i]))
        self.__rating += math.pow(self.__rd, 2) * tempSum
        
        
    def __newVol(self, rating_list, RD_list, outcome_list, v):
        """ Calculating the new volatility as per the Glicko2 system.
        
        __newVol(list, list, list) -> float
        
        """
        i = 0
        delta = self.__delta(rating_list, RD_list, outcome_list, v)
        a = math.log(math.pow(self.__vol, 2))
        tau = self.__tau
        x0 = a
        x1 = 0
        
        while x0 != x1:
            # New iteration, so x(i) becomes x(i-1)
            x0 = x1
            d = math.pow(self.__rating, 2) + v + math.exp(x0)
            h1 = -(x0 - a) / math.pow(tau, 2) - 0.5 * math.exp(x0) \
            / d + 0.5 * math.exp(x0) * math.pow(delta / d, 2)
            h2 = -1 / math.pow(tau, 2) - 0.5 * math.exp(x0) * \
            (math.pow(self.__rating, 2) + v) \
            / math.pow(d, 2) + 0.5 * math.pow(delta, 2) * math.exp(x0) \
            * (math.pow(self.__rating, 2) + v - math.exp(x0)) / math.pow(d, 3)
            x1 = x0 - (h1 / h2)

        return math.exp(x1 / 2)
        
    def __delta(self, rating_list, RD_list, outcome_list, v):
        """ The delta function of the Glicko2 system.
        
        __delta(list, list, list) -> float
        
        """
        tempSum = 0
        for i in range(len(rating_list)):
            tempSum += self.__g(RD_list[i]) * (outcome_list[i] - self.__E(rating_list[i], RD_list[i]))
        return v * tempSum
        
    def __v(self, rating_list, RD_list):
        """ The v function of the Glicko2 system.
        
        __v(list[int], list[int]) -> float
        
        """
        tempSum = 0
        for i in range(len(rating_list)):
            tempE = self.__E(rating_list[i], RD_list[i])
            tempSum += math.pow(self.__g(RD_list[i]), 2) * tempE * (1 - tempE)
        return 1 / tempSum
        
    def __E(self, p2rating, p2RD):
        """ The Glicko E function.
        
        __E(int) -> float
        
        """
        return 1 / (1 + math.exp(-1 * self.__g(p2RD) * \
                                 (self.__rating - p2rating)))
        
    def __g(self, RD):
        """ The Glicko2 g(RD) function.
        
        __g() -> float
        
        """
        return 1 / math.sqrt(1 + 3 * math.pow(RD, 2) / math.pow(math.pi, 2))
        
    # The following functions are just getters, which I was using for debugging.
        
    def E(self, p2rating, p2RD):
        return self.__E(p2rating, p2RD)
        
    def v(self, rating_list = [], RD_list = []):
        return self.__d2(rating_list, RD_list)
        
    def rating(self):
        """ Returns rating.
        
        rating() -> int
        
        """
        return self.__rating * 173.7178 + 1500
        
    def rd(self):
        """ Returns the Rating Deviation.
        
        rd() -> int
        
        """
        return self.__rd * 173.7178
        
    def vol(self):
        """ Returns the volatility.
        
        vol() -> float
        
        """
        return self.__vol

    def did_not_compete(self):
        """ Applies Step 6 of the algorithm. Use this for
        players who did not compete in the rating period.

        did_not_compete() -> None
        
        """
        self.__preRatingRD()
