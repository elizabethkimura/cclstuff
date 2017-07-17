from flask import Flask, render_template, request
import pandas as pd
from bokeh.embed import components

from bokeh.layouts import column, widgetbox
from bokeh.models import Button, HoverTool
from bokeh.models.widgets import Slider
from bokeh.plotting import figure, curdoc, show

import numpy as np

app = Flask(__name__)

feature_names = ["Matter Power Spectrum", "test"]

#creates hover tool so that more information about data point is displayed when mouse hovers over data point
hover = HoverTool(tooltips=[
    ("index", "$index"),
    ("(x,y)", "($x, $y)"),
    ("desc", "@desc"),
    ])

def create_figure(current_feature_name):
    # load the data
    i = 0

    fname = "../CCL/mpk_lin_%05d.dat" % (i)
    #ccl_data = pd.read_table(fname,
        #names=["k", "pk_lin"], skiprows = 1, delim_whitespace = True)
    cclData = np.loadtxt(fname, skiprows = 1)
    cclK = cclData[:, 0]
    cclPk = cclData[:, 1]
    data = np.loadtxt('../par_var.txt', skiprows = 1)


    j = 0
    fname = "../CLASS/lin/trial_lin_%05dz1_pk.dat" % (j)
    #classData = pd.read_table(fname,
        #names=["k", "P"], skiprows = 4, delim_whitespace = True)
    classData = np.loadtxt(fname, skiprows = 4);
    classKLin = classData[:, 0]
    classPLin = classData[:, 1]

    #Multiply by factors
    #multiply k by some factor of h, CLASS and CCL use different units, ugh
    h = float(data[i,1])

    classKLin *= h
    classPLin /= h**3

    # create a plot and style its properties
    p = figure(toolbar_location="right", title = "CCL Validation", x_axis_type = "log", y_axis_type = "log",
        tools = "hover, pan, wheel_zoom, box_zoom, save, resize, reset")

    p2 = figure(toolbar_location="right", title = "CCL Validation", x_axis_type = "log", y_axis_type = "log",
        tools = "hover, pan, wheel_zoom, box_zoom, save, resize, reset")

    p.outline_line_color = None
    p.grid.grid_line_color = None

    p2.outline_line_color = None
    p2.grid.grid_line_color = None

    # plot the data
    #p.circle(ccl_data['k'].values, ccl_data['pk_lin'].values, size = 5, legend = "ccl data")
    p.line(cclK, cclPk, line_width = 2)
    p.circle(cclK, cclPk, size = 10, legend = "ccl data", fill_color = "white")

    #p.circle(classData['k'].values, classData['P'].values, size = 5, color = "red", legend = "class data")
    p.line(classKLin, classPLin, line_width = 2)
    p.circle(classKLin, classPLin, size = 5, color = "red", legend = "class data", fill_color = "white")

    # Set the x axis label
    p.xaxis.axis_label = current_feature_name
    # Set the y axis label
    p.yaxis.axis_label = 'Count (log)'
    comparisonValue = abs(cclPk - classPLin)
    p2.line(classKLin, comparisonValue, line_width = 2)
    p2.circle(classKLin, abs(cclPk - classPLin), size = 5, fill_color = "white")

    return p, p2

@app.route('/')
def home():
    return "Welcome to the Home Page!"

# Index page
@app.route('/kCCL')
def index():
    # Determine the selected feature
    current_feature_name = request.args.get("feature_name")
    if current_feature_name == None:
        current_feature_name = "Matter Power Spectrum"

    # Create the plot
    plot = create_figure(current_feature_name)

    # Embed plot into HTML via Flask Render
    script, div = components(plot)
    #print (script)
    #print(div)

    return render_template("kCCL.html", script=script, div=div,
	   feature_names=feature_names, current_feature_name=current_feature_name)

# With debug=True, Flask server will auto-reload
# when there are code changes
if __name__ == '__main__':
    #set debug to false in a production envrionment
    app.run(port=5000, debug=True)
