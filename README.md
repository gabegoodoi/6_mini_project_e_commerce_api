This Repository is a mini-project for Coding Temple.

INSTALLATIONS:
    git clone https://github.com/gabegoodoi/6_mini_project_e_commerce_api.git
    
    you'll need to run the following in yout IDE of choice:

    cd directory_name
    code .
    python3 -m venv virtual_environment_name
    source virtual_environment_name/bin/activate
    pip install flask flask_sqlalchemy flask_marshmallow marshmallow
    
SQL TABLES
  Use MySQL and create a database (the program should make all the desired tables when run):

  CREATE DATABASE e_commerce_db;

'''

RUN APPLICATION
    
    cd 6_mini_project_e_commerce_api
    From your IDE of choice, select the run button from the app.py file.

TABLE OF CONTENTS:

    app.py
    password.py

APP.PY
The application runs through the app.py file. It does so by:

  1st: importing the following for the following purposes:

    from flask import Flask, jsonify, request
        Flask is a class instance that acts as the web application we're attempting to build here.
        jsonify is a function that converts python collections to JSON format (strings wrapped in curly braces) in a process called serialization
        request is an object of flask that can deserialize JSON formatted strings.

        
    from flask_sqlalchemy import SQLAlchemy
        SQLAlchemy is a class that creates database tables, handles data storage, and relationships

    from datetime import timedelta, datetime
        datetime is a class that allows us to access objects & classes that track and measure time including the exact time it is right now
        timedelta is a class used to tell the difference between two datetime objects
        
    from flask_marshmallow import Marshmallow, fields
        Marshmallow is a class that handles how the data stored by SQLAlchemy is presented and validated
        fields is a submodule that contains a bunch of predefined datatype classes that help Marshmallow handle the data of those datatypes in a formatted way

    from marshmallow import ValidationError
        ValidationError is an error class that handles data that doesn't meet the requirements set by the schemas
        
          
    from password import mypassword
        this is the password to your MySQLWorkbench connection. You'll need to change this yourself.

  2nd: initializing and running the Flask app, connecting to the database, creating an SQLAlchemy & Marshmallow object with the Flask app as it's argument, creating the defined tables that aren't already in the database.
  
  3rd: Defining the Model classes (tables) for Account, Customer, Product, order_product, & Order. With special importance given to setting primary keys, foreign keys, & relationships.
  
  4th: Defining the schema classes (data structure for marshmallow) for Accounts, Customers, Products, CustomerAccountDetail, OrderView, & OrderManip and their Metas
  
  5th: establishing the routes, their methods, and their endpoints
