import math

class Player:
    def __init__(self):
        self.rating = 1500
        self.rd = 200
        
    def calcRD(self, t, c):
        """ Calculates and updates the player's rating deviation.
        
        calcRD(int, float) -> None
        """
        # Calculate the new rating deviation.
        self.rd = math.sqrt( math.pow ( self.rd, 2 ) + ( math.pow ( c, 2 ) * t ) )
        # Ensure RD doesn't rise above that of an unrated player.
        self.rd = min( self.rd, 350 )
        # Ensure RD doesn't drop too low so rating can still change appreciably.
        self.rd = max( self.rd, 30 )
    
    def rating(self):
        return self.rating
        
    def rd(self):
        return self.rd
        
ryan = Player()
ryan.calcRD(1, 63.2)
#print ryan.rating
print ryan.rd