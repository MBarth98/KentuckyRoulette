
from random import Random
import time 
from multiprocessing import Pool

# ###############################################################
# #                                                             #
# #     Tweakable parameters for both the game rules            #
# #     and the simulation parameters.                          #
# #                                                             #
# ###############################################################

# simulation parameters

simulations = 20    # number of parallel simulations        (distributed over the CPU cores)
steps = 100000      # number of steps per simulation        (more gives better results)
options = 6         # number of 'chambers' in the revolver  (6 is the standard)
actors = 3          # number of 'players' in the game       (must be less than or equal to the number of options)

# game rules

reSpin = True       # if true, the revolver will be spinned after every shot.
continuous = False  # if false, the first player will always be the first to shoot.


# ###############################################################
# #                                                             #
# #     Implementation of the game and the simulation           #
# #                         BELOW                               #
# #                                                             #                          
# ###############################################################

class Chamber:
    bullet: bool
    def __init__(self, bullet = False):
        self.bullet = bullet
    
    def load(self):
        self.bullet = True
        
    def unload(self):
        self.bullet = False
        
    def hasBullet(self):
        return self.bullet
    
class Revolver:
    chamberIndex: int
    chambers: list 
    
    def __init__(self, size = 6):
        self.chambers = []
        for _ in range(size):
            self.chambers.append(Chamber())
        self.chamberIndex = 0
        self.random = Random()
    
    
    def load(self):
        self.chambers[self.chamberIndex].load()
        
    def turn(self):
        self.chamberIndex = (self.chamberIndex + 1) % len(self.chambers)
        
    def unload(self):
        self.chambers[self.chamberIndex].unload()
        
    def spin(self):
        self.chamberIndex = self.random.randint(0, len(self.chambers) - 1)
        
    def fire(self):
        if self.chambers[self.chamberIndex].hasBullet():
            self.unload()
            self.turn()
            return True
        else:
            self.turn()
            return False


class Game:
    def __init__(self, players, rounds, chambers, ruleContinuous = False, ruleAlwaysSpin = False):
        self.players = []
        for _ in range(players):
            self.players.append(0)
        self.rounds = rounds
        self.ruleContinuous = ruleContinuous
        self.ruleAlwaysSpin = ruleAlwaysSpin
        self.chambers = chambers

    def simulate(self):
        playerIndex = 0
        for _ in range(self.rounds):
            gun = Revolver(self.chambers)
            gun.load()
            gun.spin()
            if self.ruleContinuous is False:
                playerIndex = 0
            
            while gun.fire() is False:
                # advance and wrap to the next player
                playerIndex = (playerIndex + 1) % len(self.players)
                if self.ruleAlwaysSpin is True:
                    gun.spin()
                    
            # add a point to the player who fired
            self.players[playerIndex] += 1

        return self.players
    
    def getResults(self):
        return self.players
    
    def printResults(self):
        for p in self.players:
            print(p)

if __name__ == "__main__":

    games = [Game(actors, steps, options, continuous, reSpin)] * simulations
    result = [0] * actors

    print("Info:")
    print(f"    Steps: {steps} | Simulations: {simulations} | Actors: {actors}")
    print(f"    Total steps: {steps * simulations} (excl. substeps)")
    
    start_t = time.perf_counter_ns()

    with Pool() as pool: 
        # run the simulations in parallel
        results = pool.map(Game.simulate, games)        
        for r in results:
            # add the results of the simulations together
            result = [sum(x) for x in zip(result, r)]   

    end_t = time.perf_counter_ns()

    duration_ns = end_t - start_t
    duration_ms = duration_ns / 1000000
    duration_s = duration_ms / 1000

    print(f"Timing:")
    print(f"    Total: {duration_ms:.0f}ms ({duration_s:.1f}s)")
    print(f"    Each step: {(duration_ns / (steps * simulations)):.0f}ns")

    print("Results:")
    for i in range(len(result)):
        percentage = result[i] / (steps * simulations) * 100
        print(f"    Actor {i+1}: {percentage:.8f} % - ({round(percentage)} %) delta chance: {round(percentage) - round(100/ actors):=+3d} %")
    
