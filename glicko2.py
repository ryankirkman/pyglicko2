import math

class Player:
    def __init__(self, rating = 0, rd = (200/173.7178), vol = 0.06):
        # For testing purposes, preload the values assigned to an unrated player.
        self.__rating = rating
        self.__rd = rd
        self.__vol = vol
        #The system constant, which constrains the change in volatility over time.
        self.__tau = 0.5
        
        # The constant used to convert between the glicko and glicko2 scales
        #self.__glicko2const = 173.7178
        
        # Convert to the glicko2 scale.
        #self.__g2rating = (self.__rating - 1500) / self.__glicko2const
        #self.__g2rd = self.__rd / self.__glicko2const
        
        
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
            tempSum += self.__g(RD_list[i]) * (outcome_list[i] - self.__E(rating_list[i], RD_list[i]))
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
        print a
        
        while round(x0, 5) != round(x1, 5):
            # New iteration, so x(i) becomes x(i-1)
            x0 = x1
            d = math.pow(self.__rating, 2) + v + math.exp(x0)
            h1 = -(x0 - a) / math.pow(tau, 2) - 0.5 * math.exp(x0) \
            / d + 0.5 * math.exp(x0) * math.pow(delta / d, 2)
            h2 = -1 / tau - 0.5 * math.exp(x0) * (math.pow(self.__rating, 2) + v) \
            / math.pow(d, 2) + 0.5 * math.pow(delta, 2) * math.exp(x0) \
            * (math.pow(self.__rating, 2) + v - math.exp(x0)) / math.pow(d, 3)
            x1 = x0 - (h1 / h2)
            i += 1
        
        print i
        print x0, x1
        print round(x0, 5), round(x1, 5)
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
        return 1 / (1 + math.exp(-1 * self.__g(p2RD) * (self.__rating - p2rating)))
        
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


##########
# The test area. #
##########

# Create a player called Ryan
Ryan = Player()

# Following the example at: http://math.bu.edu/people/mg/glicko/glicko2.doc/example.html
# Pretend Ryan (of rating 1500 and rating deviation 200)
# plays players of ratings 1400, 1550 and 1700
# and rating deviations 30, 100 and 300 respectively
# with outcomes 1, 0 and 0.
print "Old Rating: " + str(Ryan.rating())
print "Old Rating Deviation: " + str(Ryan.rd())
print "Old Volatility: " + str(Ryan.vol())
Ryan.update_player([(x - 1500) / 173.7178 for x in [1400, 1550, 1700]],
    [x / 173.7178 for x in [30, 100, 300]], [1, 0, 0])
print "New Rating: " + str(Ryan.rating())
print "New Rating Deviation: " + str(Ryan.rd())
print "New Volatility: " + str(Ryan.vol())