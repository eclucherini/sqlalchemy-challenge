# Import the dependencies.
import datetime as dt
import numpy as np
import pandas as pd
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask, jsonify


#################################################
# Database Setup
#################################################

# Reflect an existing database into a new model
engine = create_engine("sqlite:///Resources/hawaii.sqlite")
Base = automap_base()

# Reflect the tables
Base.prepare(autoload_with=engine)

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station


#################################################
# Flask Setup
#################################################

app = Flask(__name__)

#################################################
# Flask Routes
#################################################

@app.route("/")
def welcome():
    return(
    f"Welcome to Elena Lucherini's Hawaii climate analysis API!<br/><br/>"
    f"Available Routes:<br/><br/>"
    f"A list of percipitation data for the dates between 8/23/2016 and 8/23/2017:<br/>/api/v1.0/precipitation<br/><br/>"
    f"A list of all weather observation stations:<br/>/api/v1.0/stations<br/><br/>"
    f"A list of the previous year's temperature observations from the most-active weather station:<br/>/api/v1.0/tobs<br/><br/>"
    f"A list of the minimum, maximum, and average temperature for all dates greater than or equal to the start date.<br/>Format:yyyy-mm-dd. Earliest date is 1/1/2010, and latest date is 8/23/2017:<br/>/api/v1.0/date_search/2010-01-01<br/><br/>"
    f"A list of the minimum, maximum, and average temperature from the start date through the end date.<br/>Format:yyyy-mm-dd/yyyy-mm-dd. Earliest date is 1/1/2010, and latest date is 8/23/2017:<br/>/api/v1.0/date_search/2010-01-01/2017-08-23<br/><br/>"
    )


@app.route("/api/v1.0/precipitation")
def precipitation():
   session = Session(engine)
   past_year = dt.date(2017, 8, 23) - dt.timedelta(days=365)
   precipitation = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= past_year).all()
   session.close()
   prcp_dict = {date: prcp for date, prcp in precipitation}
   return jsonify(prcp_dict)


@app.route("/api/v1.0/stations")
def stations():
    session = Session(engine)
    results = session.query(Station.station).all()
    session.close()
    stations = list(np.ravel(results))
    return jsonify(stations=stations)


@app.route("/api/v1.0/tobs")
def temp_monthly():
    session = Session(engine)
    past_year = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    results = session.query(Measurement.tobs).filter(Measurement.station == 'USC00519281').filter(Measurement.date >= past_year).all()
    session.close()
    temps = list(np.ravel(results))
    return jsonify(temps=temps)


@app.route("/api/v1.0/date_search/<StartDate>")
def start(StartDate):
    session = Session(engine)
    sel = [Measurement.date, func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs)]
    startdate_results = session.query(*sel).filter(Measurement.date >= StartDate).group_by(Measurement.date).all()
    session.close()

    dates = []                       
    for result in startdate_results:
        date_dict = {}
        date_dict["Date"] = result[0]
        date_dict["Low Temp"] = result[1]
        date_dict["High Temp"] = result[2]
        date_dict["Avg Temp"] = result[3]
        dates.append(date_dict)
    return jsonify(dates)


@app.route("/api/v1.0/date_search/<StartDate>/<EndDate>")
def StartDateEndDate(StartDate,EndDate):
    session = Session(engine)
    sel = [Measurement.date, func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs)]
    startenddate_results = session.query(*sel).filter(Measurement.date >= StartDate).filter(Measurement.date <= EndDate).group_by(Measurement.date).all()
    session.close()

    dates = []                       
    for result in startenddate_results:
        date_dict = {}
        date_dict["Date"] = result[0]
        date_dict["Low Temp"] = result[1]
        date_dict["High Temp"] = result[2]
        date_dict["Avg Temp"] = result[3]
        dates.append(date_dict)
    return jsonify(dates)


if __name__ == '__main__':
    app.run(debug=True)

