import random
import functools
import copy

import engine

# the maximum amount an adjustment can be
ADJUST_MAX = 0.1
# the size of a generation
GEN_SIZE = 1000
# the number of steps of evolution done in total
GENERATIONS = 100

def break_unit(size):
    "Returns a list of `size` floats that sum to 1."
    floats = [0, *(random.random() for _ in range(size)), 1]
    floats.sort()
    float_diffs = []
    functools.reduce(lambda x, y: (float_diffs.append(y - x), y)[1], floats)
    return float_diffs

def pick_2(n):
    """Returns two random numbers a and b between
       0 and n-1, where a != b."""
    a = random.randrange(n)
    b = random.randrange(n - 1)
    return a, b + (b >= a)

def triangular(n):
    """Returns a random number from 0 to n-1, chosen from a triangular
       distribution (the lowest numbers are more common)"""
    return random.randrange(random.randrange(n) + 1)

class SetLayer():
    "Represents a layer with the values already known."
    def __init__(self, values):
        self.values = values
    def __iter__(self):
        return iter(self.values)
    
class UnsetLayer():
    """Represents a layer in which the values are not set,
       but depend on weights."""
    def __init__(self, node_weights):
        self.node_weights = node_weights
    def __iter__(self):
        return iter(self.node_weights)
    
def compute_weights(set_, unset):
    """Returns a new SetLayer based on the current values
       and the weights of the given UnsetLayer."""
    return SetLayer([
        sum(val * weight for val, weight in zip(set_, node)) for node in unset
    ])

class Net():
    """Represents a neural net.
       It contains size information and weight information
       (for the UnsetLayers)."""
    def __init__(self, input_size, unset_layers):
        self.input_size = input_size
        self.unset_layers = unset_layers
    def compute(self, inputs):
        assert self.input_size == len(inputs)
        input_layer = SetLayer(inputs)
        return functools.reduce(compute_weights, [input_layer, *self.unset_layers])

def random_layer(prev_size, curr_size):
    "Creates a random UnsetLayer."
    return UnsetLayer([break_unit(prev_size) for _ in range(curr_size)])

def random_net(input_size, unset_sizes):
    "Creates a random Net()."
    layers = [input_size, *unset_sizes]
    return Net(input_size, [random_layer(prev_size=layers[i],
                                         curr_size=layers[i + 1])
                            for i in range(len(unset_sizes))])

def adjust(net):
    """Adjusts the weights on each layer of the net."""
    for layer in net.unset_layers:
        for weights in layer:
            # generate two random increment and decrement indices
            inc_idx, dec_idx = pick_2(len(weights))
            adjust_amount = random.random() * ADJUST_MAX
            if weights[dec_idx] < adjust_amount:
                weights[inc_idx] += weights[dec_idx]
                weights[dec_idx] = 0
            else:
                weights[inc_idx] += adjust_amount
                weights[dec_idx] -= adjust_amount

def play_game(net):
    """Plays one game controlled by the given network.
       Returns the score the network achieved."""
    engine.init()
    # Play until the net tries to make the same move twice.
    # If this happens, it will be fed with the same input again,
    # so there will be an infinite loop.
    # This has the added advantage that if it is impossible to make a move
    # the loop will exit as well, so I don't have to call engine.can_move(),
    # which is inefficient.
    prev = None
    while engine.board != prev:
        prev = engine.copy_board()
        max_item = max(map(max, engine.board))
        inputs = []
        for row in engine.board:
            for item in row:
                # Each number is fed to the neural network as a fraction
                # of the maximum.
                inputs.append(item / max_item)
        outputs = net.compute(inputs)
        # find the index of the highest output
        move_index = outputs.values.index(max(outputs))
        engine.move(move_index)
    return engine.score
    
def fitness(net):
    "Returns the total score of the net across 10 games."
    return sum(play_game(net) for _ in range(10))

def do_generation(nets):
    """Kills half of the nets and adjusts the rest.
       Better nets are more likely (but not guaranteed) to survive."""
    sorted_nets = sorted(nets, key=fitness)
    for i in range(GEN_SIZE // 2):
        kill_index = triangular(GEN_SIZE - i)
        del sorted_nets[kill_index]
    adjusted_nets = []
    for net in sorted_nets:
        child = copy.deepcopy(net)
        adjust(child)
        adjusted_nets.append(child)
    # return the ones that passed selection and their children
    return sorted_nets + adjusted_nets

def evolve():
    """Goes through the evolution process, starting from random nets.
       Returns the ending population."""
    population = [random_net(16, [4, 4, 4]) for _ in range(GEN_SIZE)]
    for _ in range(GENERATIONS):
        population = do_generation(population)
    return population

def init(rng_state):
    # If I was smart, the dependency injection would have been on the random
    # module itself, not on the seed, but that's too late to change now.
    engine.init(rng_state)
    random.setstate(rng_state)

def run(fg_iter=[None]):
    "Yields one member of the final population every time it is called."
    # Evil; takes advantage of parse-time evaluation of arg defaults
    if fg_iter[0] is None:
        fg_iter[0] = iter(evolve())
    return fitness(next(fg_iter[0]))

if __name__ == "__main__":
    print([run() for i in range(GEN_SIZE)])