# Import the dependencies.

import numpy as np
import datetime as dt

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, text

from flask import Flask, jsonify

#################################################
# Database Setup
#################################################


# reflect an existing database into a new model
engine = create_engine(r'sqlite:///C:\Users\Republic XIV\Documents\BootCamp\Module 10\Challange\sqlalchemy-challange\Resources\hawaii.sqlite')


# reflect the tables
Base = automap_base()
Base.prepare(engine)

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station


# Create our session (link) from Python to the DB
with Session(engine) as session:

    #################################################
    # Flask Setup
    #################################################
    app = Flask(__name__)

    #Determine the most recent date in de DB and calculate the date of one year ago for future use
    most_recent = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    most_recent = most_recent._mapping['date']
    rdate = dt.datetime.strptime(most_recent, '%Y-%m-%d').date()
    year_ago = rdate - dt.timedelta(days=365)

    #Determine the most active station in the DB and store it for future use
    st_activity= session.query(Measurement.station, func.count(Measurement.station)).\
                    group_by(Measurement.station).\
                    order_by(func.count(Measurement.station).desc()).all()

    most_active_station = st_activity[0]._mapping['station']


    #################################################
    # Flask Routes
    #################################################


    @app.route("/")
    def welcome():
        """List all available api routes."""
        return (
            f"Available Routes:<br/>"
            f"Precipitation: /api/v1.0/precipitation<br/>"
            f"List of Stations: /api/v1.0/stations<br/>"
            f"Temperature for one year: /api/v1.0/tobs<br/>"
            f"Temperature statistics from the date: /api/v1.0/yyyy-mm-dd<br/>"
            f"Temperature statatistics for a period: /api/v1.0/yyyy-mm-dd/yyyy-mm-dd"
        )



    @app.route("/api/v1.0/precipitation")
    def precipitation():
        last_year_pr = session.query(Measurement.date,Measurement.prcp).\
                            filter(Measurement.date >= year_ago).\
                            order_by(Measurement.date).all()
        
    #This will be a list of dictionaries
        precipitations=[]

        for date , prcp in last_year_pr:
                #Create a dictionary for each iteration
                prcp_dict={date:prcp} 
                precipitations.append(prcp_dict)

        return jsonify(precipitations)


    @app.route('/api/v1.0/stations')
    def stations():
        stations_it=session.query(Station.station, Station.name).all()

        stations_name=[]

        for s,n in stations_it:
            stations_dict={s:n}
            stations_name.append(stations_dict)
        
        station_jlist={'Stations':stations_name}

        return jsonify(station_jlist)

    @app.route("/api/v1.0/tobs")
    def tobs():
        temperture_station = session.query(Measurement.date, Measurement.tobs).\
                                filter(Measurement.date >= year_ago).\
                                filter(Measurement.station == most_active_station).all()
        tobs_list=[]
        for date, t in temperture_station:
            tobs_dict={date:t}
            tobs_list.append(tobs_dict)

        return jsonify(tobs_list)

    @app.route("/api/v1.0/<start>")
    def from_date(start):

        temp_info = session.query(
                    func.min(Measurement.tobs),
                    func.max(Measurement.tobs),
                    func.avg(Measurement.tobs)).\
                    filter(Measurement.date >= start).all()
        
        
        info = {'T_min':temp_info[0][0],
                'T_max':temp_info[0][1],
                'avg_Temp':temp_info[0][2]} 
        
        return jsonify(info)

    @app.route("/api/v1.0/<start>/<end>")
    def period(start,end):
        temp_info = session.query(
                    func.min(Measurement.tobs),
                    func.max(Measurement.tobs),
                    func.avg(Measurement.tobs)).\
                    filter(Measurement.date.between(start, end)).all()
        
        info = {'T_min':temp_info[0][0],
                'T_max':temp_info[0][1],
                'avg_Temp':temp_info[0][2]} 
        
        return jsonify(info)



    if __name__ == "__main__":
        app.run(debug=True)

#Close the session
session.close()