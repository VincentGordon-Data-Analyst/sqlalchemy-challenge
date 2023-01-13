import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

import datetime as dt



from flask import Flask, jsonify
##############################
# Database Setup 
##############################

# Correctly generate the engine to the correct sqlite file 
engine = create_engine("sqlite:///Resources/hawaii.sqlite")


# Use automap_base() and reflect the database schema
Base = automap_base()

# Correctly save references to the tables in the sqlite file (measurement and station)
Base.prepare(autoload_with=engine)
Base.classes.keys()

# Correctly create and binds the session between the python app and database 
Measurement = Base.classes.measurement
Station = Base.classes.station

# Display the available routes on the landing page
#################################################
# Flask Setup
#################################################
app = Flask(__name__)


################################################
# Flask Routes
################################################

@app.route("/")
def home():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        
    )
# Convert the query results from your precipitation analysis to a dictionary using date as the key and prcp as the value.

# Return the JSON representation of your dictionary.
@app.route("/api/v1.0/precipitation")
def precipitation():
    # Create our session (link) from Python to the DB
    session = Session(engine)
    
    """Get dates and precipitation values"""
    results = session.query(Measurement.date, Measurement.prcp).all()
    
    session.close()
    
    # Create a dictionary from the row data and append to a list
    prcp_data = []
    
    for date, prcp in results:
        prcp_dict = {}
        prcp_dict["date"] = date,
        prcp_dict["prcp"] = prcp
    
        prcp_data.append(prcp_dict)
    
    return jsonify(prcp_data)


    

# Return a JSON list of stations from the dataset
@app.route("/api/v1.0/stations")
def stations():
    # Create our session (link) from Python to the DB
    session = Session(engine)
    
    results = session.query(Station.id, Station.station).all()
    
    session.close()
    
    station_data = []
    for id, station in results:
        station_dict = {}
        station_dict["id"] = id
        station_dict["station"] = station
        
        station_data.append(station_dict)
    
    return jsonify(station_data)
        
        
# Query the dates and temperature observations of the most-active station for the previous year of data.

# Return a JSON list of temperature observations for the previous year.

@app.route("/api/v1.0/tobs")
def tobs():
    # Create our session (link) from Python to the DB
    session = Session(engine)
    
    # Calculate the date one year from the last date in data set.
    recent_date_data = session.query(Measurement.date).\
        order_by(Measurement.date.desc()).first()
    
    start_date = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    
    # Find the most active station in the database
    most_active = session.query(Measurement.station, func.count(Measurement.station)).\
        order_by(func.count(Measurement.station).desc()).\
        group_by(Measurement.station).first()
        
    most_active_station = most_active[0]
    
    station_temp_results = session.query(Measurement.date, Measurement.tobs, Measurement.station).\
        filter(Measurement.station == most_active_station).\
        filter(Measurement.date >= '2016-08-18').\
        filter(Measurement.date < '2017-08-19')
    
    session.close()
    
    station_temp_data = []
    for date, tobs, station in station_temp_results:
        station_temp_dict = {}
        station_temp_dict["date"] = date
        station_temp_dict["tobs"] = tobs
        station_temp_dict["station"] = station
        station_temp_data.append(station_temp_dict)
    
    return jsonify(station_temp_data)

if __name__ == "__main__":
    app.run(debug=True)

