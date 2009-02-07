import glicko2
import timeit

def exampleCase():
    # Create a player called Ryan
    Ryan = glicko2.Player()
    # Following the example at:
    # http://math.bu.edu/people/mg/glicko/glicko2.doc/example.html
    # Pretend Ryan (of rating 1500 and rating deviation 200)
    # plays players of ratings 1400, 1550 and 1700
    # and rating deviations 30, 100 and 300 respectively
    # with outcomes 1, 0 and 0.
    #sprint "Old Rating: " + str(Ryan.rating())
    print("Old Rating Deviation: " + str(Ryan.rd()))
    print("Old Volatility: " + str(Ryan.vol()))
    Ryan.update_player([(x - 1500) / 173.7178 for x in [1400, 1550, 1700]],
        [x / 173.7178 for x in [30, 100, 300]], [1, 0, 0])
    print("New Rating: " + str(Ryan.rating()))
    print("New Rating Deviation: " + str(Ryan.rd()))
    print("New Volatility: " + str(Ryan.vol()))

def timingExample(runs = 10000):
    print("\nThe time taken to perform " + str(runs))
    print("separate calculations (in seconds) was:")
    timeTaken = timeit.Timer("Ryan = glicko2.Player(); \
                             Ryan.update_player([(x - 1500) / 173.7178 \
    for x in [1400, 1550, 1700]], \
    [x / 173.7178 for x in [30, 100, 300]], [1, 0, 0])", \
        "import glicko2").repeat(1, 10000)
    print(round(timeTaken[0], 4))

if __name__ == "__main__":
    exampleCase()
    timingExample()
