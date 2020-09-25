## resistance.py
## Handles all resistance measurements for Mu2e Straw Lab

def verify_resistance_measurement(measurement,measurement_type):
    acceptable_range = {
            "inside-inside"     :   lambda ohms: (50.0 <= ohms <= 250.0),
            "ii"                :   lambda ohms: (50.0 <= ohms <= 250.0),
            "outside-outside"   :   lambda ohms: (50.0 <= ohms <= 250.0),
            "oo"                :   lambda ohms: (50.0 <= ohms <= 250.0),
            "inside-outside"    :   lambda ohms: (ohms > 1000),
            "io"                :   lambda ohms: (ohms > 1000),
            "outside-inside"    :   lambda ohms: (ohms > 1000),
            "oi"                :   lambda ohms: (ohms > 1000)
        }
    return acceptable_range[measurement_type](measurement)