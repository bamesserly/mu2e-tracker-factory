import numpy
import scipy.optimize


def lin_fit(x, y):
    """Fits a linear fit of the form mx+b to the data"""
    fitfunc = lambda params, x: params[0] * x  # create fitting function of form mx+b
    errfunc = (
        lambda p, x, y: fitfunc(p, x) - y
    )  # create error function for least squares fit

    init_a = 0.5  # find initial value for a (gradient)
    init_p = numpy.array((init_a))  # bundle initial values in initial parameters

    # calculate best fitting parameters (i.e. m and b) using the error function
    p1, success = scipy.optimize.leastsq(errfunc, init_p.copy(), args=(x, y))
    f = fitfunc(p1, x)  # create a fit with those parameters
    return p1, f


def main():
    L = [0, 24, 36]
    dL = [0, 24, 36]
    m = lin_fit(L, dL)
    print("m: " + str(m))


main()
