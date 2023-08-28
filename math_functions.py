import math

def square(x):
    return x**2

def decreasing_square(x):
    return (1-x)**2

def root(x):
    return math.sqrt(x)

def decreasing_root(x):
    return math.sqrt(1-x)

def cube(x):
    return x ** 3

def decreasing_cube(x):
    return (1 - x) ** 3

def mid_square(x):
    return (2 * x - 1) ** 2

def inverse_mid_square(x):
    return 1 - mid_square(x)

def mid_root(x):
    return math.sqrt(abs(2 * x - 1))
def inverse_mid_root(x):
    return 1 - mid_root(x)

def gamma(x):
    epsilon_dec = 0.001
    arranged_x = min(max(x, epsilon_dec), 1 - epsilon_dec)
    return math.gamma(arranged_x) / math.gamma(epsilon_dec)

def log(x):
    epsilon_dec = 0.0001
    arranged_x = min(max(x, epsilon_dec), 1 - epsilon_dec)
    return math.log(arranged_x) / math.log(epsilon_dec)

def exp(x):
    return math.exp(x)


def ql(x):
    if x <= 1/4:
        return root(4 * x)
    else:
        return decreasing_square((x - 1/4) * 4 / 3)

def print_graph(fun):
    from matplotlib import pyplot as plt
    import numpy

    X = numpy.linspace(0,1,1000)
    Y = [fun(x) for x in X]
    plt.plot(X,Y)
    plt.show()

#print_graph(ql)