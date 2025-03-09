# Import the dependencies.
import numpy as np
import pandas as pd
import datetime as dt

# Python SQL toolkit and Object Relational Mapper
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, desc

from datetime import datetime, timedelta

from flask import Flask, jsonify

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(autoload_with=engine)

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)


#################################################
# Flask Routes
#################################################

@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/&lt;start&gt;<br/>"
        f"/api/v1.0/&lt;start&gt;/&lt;end&gt;"
    )

#Get last 12 months of data to a dictionary using date as the key and prcp as the value
@app.route("/api/v1.0/precipitation")
def precipitation():
    #Get 12 month dates
    recent_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()[0]
    recent_date_format = datetime.strptime(recent_date, "%Y-%m-%d")
    one_year_date = recent_date_format - timedelta(days=365)

    #Get precipitation data
    results = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= one_year_date).all()
    # Convert results to a  dictionaries
    precipitation_data = {date: prcp for date, prcp in results}

    return jsonify(precipitation_data)

#Get list of stations from the dataset
@app.route("/api/v1.0/stations")
def stations():
    results_sta = session.query(Station.station, Station.name).all()
    # Convert results to a list of dictionaries
    stations_data = [{station: name} for station, name in results_sta]

    return jsonify(stations_data)

#Query the dates and temperature observations of the most-active station for the previous year of data
@app.route("/api/v1.0/tobs")
def tobs():
    # Find active station
    active_station = session.query(Measurement.station).filter(Measurement.station == "USC00519281").first()[0]

    # Calculate dates for 12 months
    recent_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()[0]
    recent_date_format = datetime.strptime(recent_date, "%Y-%m-%d")
    one_year_date = recent_date_format - timedelta(days=365)

    # Get date and temperature
    results_temp = session.query(Measurement.date, Measurement.tobs).filter(Measurement.station == active_station)\
            .filter(Measurement.date >= one_year_date).all()
    # Convert results to a list of dictionaries
    temp_data = [{"date": date, "temperature": tobs} for date, tobs in results_temp]
    
    return jsonify(temp_data)


#Get min,max, average temp for start date
@app.route("/api/v1.0/<start>")
def temp(start):
    start_date = dt.datetime.strptime(start, "%Y-%m-%d")
    
    start_query = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs))\
        .filter(Measurement.date >= start_date).all()
    # Convert the result to a dictionary
    temp_data = {
        "min_temp": start_query[0][0],
        "avg_temp": start_query[0][1],
        "max_temp": start_query[0][2]
    }
    return jsonify(temp_data)


#Get min,max, average temp for start and end dates
@app.route("/api/v1.0/<start>/<end>")            #note need to enter query date as 127.0.0.1:5000/api/v1.0/2017-08-16/2017-08-23
def temp_range(start, end):
    try:
        start_date = dt.datetime.strptime(start, "%Y-%m-%d")
        end_date = dt.datetime.strptime(end, "%Y-%m-%d")
    except ValueError:
        return jsonify({"error": "Invalid date format. Please use YYYY-MM-DD."}), 400

    # Query to get min, avg, and max temperature
    range_query = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs))\
        .filter(Measurement.date >= start_date).filter(Measurement.date <= end_date).all()

    # Convert the result to a dictionary
    temp_data = {
        "min_temp": range_query[0][0],
        "avg_temp": range_query[0][1],
        "max_temp": range_query[0][2]
    }
    return jsonify(temp_data)
    


if __name__ == "__main__":
    app.run(debug=True)