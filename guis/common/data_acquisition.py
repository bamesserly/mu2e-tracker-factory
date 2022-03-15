import sqlite3

def get_straw_tb(panel):
    # initialize connection with database
    con=sqlite3.connect('data/database.db')
    cursor=con.cursor()

    # acquire panel id
    cursor.execute("SELECT * FROM straw_location WHERE location_type='MN' AND number='"+str(panel[2:])+"'")
    panel_id=str(cursor.fetchall()[0][0])
    
    # acquire data
    cursor.execute("SELECT * FROM measurement_tensionbox WHERE panel='"+str(panel_id)+"' AND straw_wire='straw'")
    straw_tb=cursor.fetchall()
    
    return straw_tb
    
    
def get_wire_tb(panel):
    # initialize connection with database
    con=sqlite3.connect('data/database.db')
    cursor=con.cursor()
    
    # acquire panel id
    cursor.execute("SELECT * FROM straw_location WHERE location_type='MN' AND number='"+str(panel[2:])+"'")
    panel_id=str(cursor.fetchall()[0][0])
    
    # acquire data
    cursor.execute("SELECT * FROM measurement_tensionbox WHERE panel='"+str(panel_id)+"' AND straw_wire='wire'")
    wire_tb=cursor.fetchall()
    
    return wire_tb