import math

class Player:
    def __init__(self):
        # For testing purposes, preload the values assigned to an unrated player.
        self.__rating = 1500
        self.__rd = 200
        
    def __preRatingRD(self, t = 1, c = 63.2):
        """ Calculates and updates the player's rating deviation for the
        beginning of a rating period.
        
        preRatingRD(int, float) -> None
        """
        
        # Calculate the new rating deviation.
        self.__rd = math.sqrt( math.pow ( self.__rd, 2 ) + 
            ( math.pow ( c, 2 ) * t ) )
        # Ensure RD doesn't rise above that of an unrated player.
        self.__rd = min( self.__rd, 350 )
        # Ensure RD doesn't drop too low so rating can still change appreciably.
        self.__rd = max( self.__rd, 30 )
        
    def update_player(self, rating_list, RD_list, outcome_list):
        """ Calculates the new rating and rating deviation of the player.
        
        update_player(list[int], list[int], list[bool]) -> None
        """
        # Calculate pre - rating period rating deviation.
        # This can be done either before or after updating ratings and 
        # deviations, as even if all players are unrated, the rating deviation
        # won't rise above 350.
        self.__preRatingRD()
        
        # Update rating.
        d2 = self.__d2(rating_list, RD_list)
        rPrime = (self.__q() / ((1 / math.pow(self.__rd, 2)) + 
            (1 / d2)))
        
        tempSum = 0
        for i in range(len(rating_list)):
            tempSum += self.__g(RD_list[i]) * (outcome_list[i] - self.__E(rating_list[i], RD_list[i]))
        
        rPrime *= tempSum
        rPrime += self.__rating
        self.__rating = rPrime
        
        # Update rating deviation.
        self.__rd = math.sqrt(1 / ((1 / math.pow(self.__rd, 2)) + (1 / d2)))
        
    def __d2(self, rating_list, RD_list):
        """ The d^2 function of the Glicko system.
        
        __d2(list[int], list[int]) -> float
        """
        tempSum = 0
        for i in range(len(rating_list)):
            tempE = self.__E(rating_list[i], RD_list[i])
            tempSum += math.pow(self.__g(RD_list[i]), 2) * tempE * (1 - tempE)
        return 1 / (math.pow(self.__q(), 2) * tempSum)
        
    def __E(self, p2rating, p2RD):
        """ The Glicko E function.
        
        __E(int) -> float
        """
        return 1 / (1 + math.pow(10, (-1 * self.__g(p2RD) * (self.__rating - p2rating) / 400)))
        
    def __g(self, RD):
        """ The Glicko g(RD) function.
        
        __gRD() -> float
        """
        return 1 / math.sqrt(1 + 3 * math.pow(self.__q(), 2) 
            * math.pow(RD, 2) / math.pow(math.pi, 2))
        
    def __q(self):
        """ The q constant of the Glicko system. 
        This could be made constant if a speed boost is necessary.
        
        __q() -> float
        """
        return math.log(10)/400
        
    # The following functions are just getters, which I was using for debugging.
        
    def E(self, p2rating, p2RD):
        return self.__E(p2rating, p2RD)
        
    def d2(self, rating_list = [], RD_list = []):
        return self.__d2(rating_list, RD_list)
        
    def rating(self):
        """ Returns rating.
        
        rating() -> int
        """
        return self.__rating
        
    def rd(self):
        """ Returns the Rating Deviation.
        
        rd() -> int
        """
        return self.__rd


##########
# The test area. #
##########

# Create a player called Ryan
Ryan = Player()

# Following the example at: http://math.bu.edu/people/mg/glicko/glicko.doc/glicko.html
# Pretend Ryan plays players of ratings 1400, ,1550 and 1700
# and rating deviations 30, 100 and 300 respectively
# with outcomes 1, 0 and 0.
print "Old Rating: " + str(Ryan.rating())
print "Old Rating Deviation: " + str(Ryan.rd())
Ryan.update_player([1400, 1550, 1700], [30, 100, 300], [1, 0, 0])
print "New Rating: " + str(Ryan.rating())
print "New Rating Deviation: " + str(Ryan.rd())