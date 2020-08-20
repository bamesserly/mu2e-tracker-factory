def sum_div(num_lst,den_lst):
    total = 0
    for count in range(0,len(num_lst)):
        #print "Count is at %f" % count
        #print "Num is at %f" % num_lst[count]
        #print "den is at %f" % den_lst[count]
        total = total + float(num_lst[count])/float(den_lst[count])
        #print "total is at %f" % total
    return total

def mult_lists(x,y):
    lst = []
    for count in range(0,len(x)):
        lst.append(x[count]*y[count])
    return lst

def sqr_list(lst):
    new_lst = []
    for num in lst:
        new_lst.append(num**2)
    return new_lst

def inver_list(lst):
    new_lst = []
    for num in lst:
        new_lst.append(1.0/float(num))
    return new_lst

def get_slope(xi,yi,yi_err):
    slope = -100
    num1 = sum_div(xi,sqr_list(yi_err))*sum_div(yi,sqr_list(yi_err))
    num2 = sum_div(mult_lists(xi,yi),sqr_list(yi_err))*sum(sqr_list(inver_list(yi_err)))
    den1 = sum_div(xi,sqr_list(yi_err))**2
    den2 = sum_div(sqr_list(xi),sqr_list(yi_err))*sum(sqr_list(inver_list(yi_err)))
    if den1 != den2 :
        slope = float(num1 - num2)/float(den1-den2)
    return slope

def get_slope_err(xi,yi,yi_err):
    slope_err = -100
    #yi cancels out...weird
    num1 = sum(sqr_list(inver_list(yi_err)))
    den1 = sum_div(sqr_list(xi),sqr_list(yi_err))*num1 
    den2 = sum_div(xi,sqr_list(yi_err))**2
    if den1 != den2 :
        slope_err = (float(num1)/float(den1 - den2))**0.5
    return slope_err

def get_intercept(xi,yi,yi_err):
    intercept = -100
    num1 = sum_div(mult_lists(xi,yi),sqr_list(yi_err))
    num2 = get_slope(xi,yi,yi_err)*sum_div(sqr_list(xi),sqr_list(yi_err))
    den1 = sum_div(xi,sqr_list(yi_err))
    if den1 != 0 :
        intercept = float(num1 - num2)/float(den1)
    return intercept

def get_intercept_err(xi,yi,yi_err):
    intercept_err = -100
    num1 = sum_div(sqr_list(xi),sqr_list(yi_err))
    den1 = num1 * sum(sqr_list(inver_list(yi_err)))
    den2 = sum_div(xi,sqr_list(yi_err))**2
    if den1 != den2 :
        intercept_err = (float(num1)/float(den1 - den2))**0.5
    return intercept_err

def get_slope_zero_intercept(xi,yi,yi_err):
    num1 = sum_div(mult_lists(xi,yi),sqr_list(yi_err))
    den1 = sum_div(sqr_list(xi),sqr_list(yi_err))
    slope = float(num1)/float(den1)
    return slope

def sub_lists(xi,yi):
    result = []
    for count in range(0,len(xi)):
        result.append(xi[count]-yi[count])
    return result

def mult_list(xi,mult):
    result = []
    for num in xi:
        result.append(num*mult)
    return result

def get_slope_err_zero_intercept(xi,yi,yi_err):
    a = get_slope_zero_intercept(xi,yi,yi_err)
    s = (float(sum(sqr_list(sub_lists(yi,mult_list(xi,a)))))/float(len(xi)-1))**0.5
    slope_err = float(s)/float(sum_div(sqr_list(xi),sqr_list(yi_err))**0.5)
    return slope_err

#This method check jump for the lastest 10 mins. To modify the time, change the constant 40 and 20 in the code
def jump_check_average(PPM):
    Nsigma = 1
    #n_sigma is the number of sigma to determine the jump
    rms_1 = 0
    rms_2 = 0
    i = 0
    rms_list = sqr_list(PPM)
    for sqr_v in rms_list:
        i = i + 1
        if i > (len(PPM) - 60) and i <= (len(PPM) - 30):
            rms_1 = rms_1 + sqr_v
        elif i > (len(PPM) - 30) and i <= len(PPM):
            rms_2 = rms_2 + sqr_v
    rms_1 = (rms_1/30)**0.5
    rms_2 = (rms_2/30)**0.5
    #mean has been calculated

    #Next calculate the standard deviation
    sigma_1 = 0
    sigma_2 = 0
    i = 0
    for co2_ppm in PPM :
        i = i + 1
        if i > (len(PPM)-60) and i <= (len(PPM)-30):
            sigma_1 = sigma_1 + (co2_ppm - rms_1)**2
        elif i > (len(PPM)-60) and i <= len(PPM):
            sigma_2 = sigma_2 + (co2_ppm - rms_2)**2
    sigma_1 = (sigma_1/30)**0.5
    sigma_2 = (sigma_2/30)**0.5



    if abs(rms_1-rms_2)>sigma_1*Nsigma or abs(rms_1-rms_2)>sigma_2*Nsigma:
        return 1
    else:
        return 0

def jump_check_intercept(time, PPM, err):
    Nerr = 1.5
    #n_sigma is the number of sigma to determine the jump
    x0 = []
    x1 = []
    y0 = []
    y1 = []
    err0 = []
    err1 = []
    
    i = 0
    for temp in time:
        i = i + 1
        if i > (len(PPM) - 60) and i <= (len(PPM) - 30):
            x0 = x0 + [temp]
        elif i > (len(PPM) - 30) and i <= len(PPM):
            x1 = x1 + [temp]
    i = 0
    for temp in PPM:
        i = i + 1
        if i > (len(PPM) - 60) and i <= (len(PPM) - 30):
            y0 = y0 + [temp]
        elif i > (len(PPM) - 30) and i <= len(PPM):
            y1 = y1 + [temp]

    i = 0
    for temp in err:
        i = i + 1
        if i > (len(PPM) - 60) and i <= (len(PPM) - 30):
            err0 = err0 + [temp]
        elif i > (len(PPM) - 30) and i <= len(PPM):
            err1 = err1 + [temp]

    #Next calculate the standard deviation
    intercept_0 = get_intercept(x0,y0,err0)
    intercept_1 = get_intercept(x1,y1,err1)

    inter_err0 = get_intercept_err(x0,y0,err0)
    inter_err1 = get_intercept_err(x1,y1,err1)

    if abs(intercept_0-intercept_1)>inter_err0*Nerr or abs(intercept_0-intercept_1)>inter_err1*Nerr:
        return 1
    else:
        return 0
