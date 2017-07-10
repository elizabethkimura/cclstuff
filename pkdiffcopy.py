from flask import Flask, render_template, request
import pandas as pd
from bokeh.embed import components

from bokeh.layouts import column, widgetbox
from bokeh.models import Button, HoverTool
from bokeh.models.widgets import Slider
from bokeh.plotting import figure, curdoc, show

app = Flask(__name__)
print("first print")
feature_names = ["Matter Power Spectrum", "test"]

#creates hover tool so that more information about data point is displayed when mouse hovers over data point
hover = HoverTool(tooltips=[
    ("index", "$index"),
    ("(x,y)", "($x, $y)"),
    ("desc", "@desc"),
    ])

def create_figure(current_feature_name, bins):
    print("create_figure")
    # load the data
    i = 2
    fname = "../CCL/mpk_lin_%05d.dat" % (i)
    ccl_data = pd.read_table(fname,
        names=["k", "pk_lin"], skiprows = 1, delim_whitespace = True)
    print(ccl_data['k'].values)

    # create a plot and style its properties
    p = figure(toolbar_location="right", title = "CCL Validation", x_axis_type = "log", y_axis_type = "log", tools = "hover, pan, wheel_zoom, box_zoom, reset")

    p.outline_line_color = None
    p.grid.grid_line_color = None

    # plot the data
    p.circle(ccl_data['k'].values, ccl_data['pk_lin'].values, size = 5)
    # Set the x axis label
    p.xaxis.axis_label = current_feature_name
    # Set the y axis label
    p.yaxis.axis_label = 'Count (log)'
    return p
def createFigure2(current_feature_name, bins):
    # load the data
    #i = 2
    #fname = "../CCL/mpk_lin_%05d.dat" % (i)
    fname = "../CLASS/lin/trial_lin_00000z1_pk.dat"
    classData = pd.read_table(fname,
        names=["k", "P"], skiprows = 4, delim_whitespace = True)
    print(classData['k'].values)

    # create a plot and style its properties
    p2 = figure(toolbar_location="right", title = "CLASS Validation", x_axis_type = "log", y_axis_type = "log", tools = "hover, pan, wheel_zoom, box_zoom, reset")

    p2.outline_line_color = None
    p2.grid.grid_line_color = None

    # plot the data
    p2.circle(classData['k'].values, classData['P'].values, size = 5)
    # Set the x axis label
    p2.xaxis.axis_label = current_feature_name
    # Set the y axis label
    p2.yaxis.axis_label = 'Count (log)'
    return p2

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
    plot = create_figure(current_feature_name, 10)
    # Embed plot into HTML via Flask Render
    script, div = components(plot)
    return render_template("kCCL.html", script=script, div=div,
	   feature_names=feature_names, current_feature_name=current_feature_name)

@app.route('/kpCLASS')
def index2():
    # Determine the selected feature
    current_feature_name = request.args.get("feature_name")
    if current_feature_name == None:
        current_feature_name = "Matter Power Spectrum"

    # Create the plot
    plot2 = createFigure2(current_feature_name, 10)
    print("finished plotxs")
    # Embed plot into HTML via Flask Render
    script, div = components(plot2)
    return render_template("kpCLASS.html", script=script, div=div,
        feature_names=feature_names, current_feature_name=current_feature_name)


# With debug=True, Flask server will auto-reload
# when there are code changes
if __name__ == '__main__':
    #set debug to false in a production envrionment
    app.run(port=5000, debug=True)
