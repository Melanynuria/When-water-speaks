import pandas as pd
from xgboost import XGBRegressor

def euros_per_m3(liters, service_type):
    m3 = liters/1000
    price = 0
    if service_type == "D": 
        if 0 <= m3 <= 6: price = m3*0.8
        elif 6 < m3 <= 9: price = m3 * 1.6002
        elif 9 < m3 <= 15: price = m3 * 2.4894
        elif 15 < m3 <= 18: price = m3 * 3.3189
        elif 18 < m3: price= m3 * 4.1486

    elif service_type == "C":
        if 0 <= m3 <= 9: price = m3 * 1.2164
        elif m3 >= 9: price = m3 * 2.4328

    elif service_type == "A":       #mirar que es exactamente 
        price = m3 * 1.1173 
    return price


def get_next_month_bill(price):
    '''
    price is the water consumption price computed. 
    This function calculates the total amount of the next month bill. 
    '''
    #include IVA (10%)
    price = price * 1.1

    #canon aigua 
    price += 6.91

    #clavegueram 
    price += 3.09

    #tractament de residus
    price += 11.43

    #recollida de residus 
    price += 10.19

    return price 









