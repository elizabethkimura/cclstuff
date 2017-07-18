from flask import Flask, render_template, request
import pandas as pd
from bokeh.embed import components
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from bokeh.layouts import column, widgetbox
from bokeh.models import Button, HoverTool
from bokeh.models.widgets import Slider
from bokeh.plotting import figure, curdoc, show
from bokeh.charts import HeatMap
import numpy as np
import pdb

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
    j = 1
    fname = "../CCL/lhs/lin/non_pre/lhs_mpk_lin_%05d" % (i)
    fname += "z%d_pk.dat" % (j)
    #ccl_data = pd.read_table(fname,
        #names=["k", "pk_lin"], skiprows = 1, delim_whitespace = True)
    cclData = np.loadtxt(fname, skiprows = 1)
    cclKLinNonPre = cclData[:, 0]
    cclPkLinNonpre = cclData[:, 1]
    data = np.loadtxt('../parameters/par_stan.txt', skiprows = 1)


    k = 0
    l = 1
    fname = "../CLASS/lhs/lin/non_pre/lhs_lin_%05d" % (k)
    fname += "z%d_pk.dat" % (l)
    #classData = pd.read_table(fname,
        #names=["k", "P"], skiprows = 4, delim_whitespace = True)
    classData = np.loadtxt(fname, skiprows = 4);
    classKLinNonPre = classData[:, 0]
    classPLinNonPre = classData[:, 1]

    #Multiply by factors
    #multiply k by some factor of h, CLASS and CCL use different units, ugh
    h = float(data[i,1])

    classKLinNonPre *= h
    classPLinNonPre /= h**3

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
    p.line(cclKLinNonPre, cclPkLinNonpre, line_width = 2)
    p.circle(cclKLinNonPre, cclPkLinNonpre, size = 5, legend = "ccl data", fill_color = "white", fill_alpha = 0.5)

    #p.circle(classData['k'].values, classData['P'].values, size = 5, color = "red", legend = "class data")
    p.line(classKLinNonPre, classPLinNonPre, line_width = 2)
    p.circle(classKLinNonPre, classPLinNonPre, size = 5, color = "red", legend = "class data", fill_color = "white", fill_alpha = 0.5)

    # Set the x axis label
    p.xaxis.axis_label = current_feature_name
    # Set the y axis label
    p.yaxis.axis_label = 'Count (log)'
    p2.line(classKLinNonPre, abs(cclPkLinNonpre - classPLinNonPre), line_width = 2)
    p2.circle(classKLinNonPre, abs(cclPkLinNonpre - classPLinNonPre), size = 5, fill_color = "white")

    return p, p2
def create_figure2():#current_feature_name):



#This program's aim is to look at each trial and find the places where the validity fails
#We are going to have 3 colors, corresponding to how badly it failed
#These will be based on the condition for clustering
#Clustering values  only affect those in the range of [1.e-2,0.2]
#So we're going to bin our k values according to
#Ultra-large scales:[1e-4, 1e-2]
#Linear scales:[1e-2, 0.1]
#Quasi-linear:[0.1,1.0]
#Each bin we're going to assign a number for how many points failed to reach 1e-4 threshold for each bin
#Then we will have a number as a threshold, accounting for how many times we will allow it to fail
#RED = it failed to reach 1e-4 more than the threshold
#ORANGE = it failed to reach 1e-4 less than the threshold
#GREEN = it reaches 1e-4 everywhere

#Also the number for failures can either include clustering regime only or not
    thres = 10 #Threshold for number of failures
    clustering_only = False #Only counts failures if inside the clustering regime

    ultra_scale_min = 1e-4 #Minimum for the ultra-large scales
    ultra_scale_max = 1e-2 #Maximum for the ultra-large scales
    lin_scale_min = 1e-2 #Min for the linear scales
    lin_scale_max = 1e-1 #Max for the linear scales
    quasi_scale_min = 1e-1 #Min for the quasi-lin scales
    quasi_scale_max = 1.0 #Max for the quasi-lin scales


    cluster_reg_min = 1e-2 #Min for the cluster regime
    cluster_reg_max = 0.2 # Max for the cluster regime


#Call the original par_var file, so we can get the trial # (easier in the long run, trust)

    data = np.genfromtxt('../parameters/par_stan.txt', dtype='str', skip_header=1)
    #data = np.loadtxt('../parameters/par_stan.txt', dtype='str', skiprows=1)

#Gets the trial number into an arr
    trial_arr = 1 #data[:,0]

#Iterates over the trial #
    i = trial_arr
    #trial = data[i,0]
    trial = "00001"
    #print ("Performing trial %s" %trial)

    z_vals = ['1','2','3','4','5','6']

	#Gonna generate an array of arrays, with each row corresponding to a different z value
	#Each column will correspond to a different bin of k_values
    sum_lin = []
	#For list of lists
    sum_lin_ll = []
    for j in range(len(z_vals)):
        #z_val = z_vals[j]
        z_val = 2
        z_path = '_z%s.dat' %z_val
        #print ("Performing z_val = " ), z_val
		#For ease in iterating over different z valus we use string manipulation
        stats_lin_path = '../stats/lhs/lin/non_pre/lhs_mpk_err_lin_%s' %trial
		#Adds the z_path
        stats_lin_path += z_path

		#calls the data
        stats_lin_data = np.loadtxt(stats_lin_path, skiprows=1)
        stats_lin_k = stats_lin_data[:,0]
        stats_lin_err = stats_lin_data[:,1]
		#Create arrays that will be used to fill the complete summary arrays
        sum_lin_z = []

		#For list of lists
        sum_lin_z_ll = []
		#We perform a loop that looks into the bins for k
		#Doing this for lin
		#Much easier than doing a for loop because of list comprehension ALSO FASTER
        fail_ultra = 0 #initial value for ultra large scales
        fail_lin = 0 #initialize for lin scales
        fail_quasi = 0 #initialize for quasi lin scales

		#k has to fall in the proper bins
        aux_k_ultra = (stats_lin_k > ultra_scale_min) & (stats_lin_k < ultra_scale_max)
        aux_k_lin = (stats_lin_k > lin_scale_min) & (stats_lin_k < lin_scale_max)
        aux_k_quasi = (stats_lin_k > quasi_scale_min) & (stats_lin_k < quasi_scale_max)

		#Looks at only the regime where clustering affects it
        if clustering_only == True:
            aux_cluster_ultra = (stats_lin_k[aux_k_ultra] > cluster_reg_min) & (stats_lin_k[aux_k_ultra] < cluster_reg_max)
            aux_cluster_lin = (stats_lin_k[aux_k_lin] > cluster_reg_min) & (stats_lin_k[aux_k_lin] < cluster_reg_max)
            aux_cluster_quasi = (stats_lin_k[aux_k_quasi] > cluster_reg_min) & (stats_lin_k[aux_k_quasi] < cluster_reg_max)
            aux_err_ultra = (stats_lin_err[aux_k_ultra])[aux_cluster_ultra] > 1e-4
            aux_err_lin = (stats_lin_err[aux_k_lin])[aux_cluster_lin] > 1e-4
            aux_err_quasi = (stats_lin_err[aux_k_quasi])[aux_cluster_quasi] > 1e-4

		#calculates imprecision in any regime
        if clustering_only == False:
            aux_err_ultra = stats_lin_err[aux_k_ultra] > 1e-4
            aux_err_lin = stats_lin_err[aux_k_lin] > 1e-4
            aux_err_quasi = stats_lin_err[aux_k_quasi] > 1e-4

		#Adds the number of times it fails and appends it to our summary statistic
		#If you want list of lists
            sum_lin_z_ll.append(np.sum(aux_err_ultra))
            sum_lin_z_ll.append(np.sum(aux_err_lin))
            sum_lin_z_ll.append(np.sum(aux_err_quasi))

		#Only interested in list
            sum_lin_z = np.append(sum_lin_z, np.sum(aux_err_ultra))
            sum_lin_z = np.append(sum_lin_z, np.sum(aux_err_lin))
            sum_lin_z = np.append(sum_lin_z, np.sum(aux_err_quasi))


		#If you want list of lists
            sum_lin_ll.append(sum_lin_z_ll)


		#Only if you want big list
            sum_lin = np.append(sum_lin, sum_lin_z)



            z_actual = range(len(z_vals))
            z_arr = np.float_(np.asarray(z_actual))
            z_arr *= 0.5
            z = []
            z_ll = []
	#Create a heat map, but makes it red, right now we just mark threshold on the heat map
    for j in range(len(z_actual)):
        z_full = np.full(len(sum_lin_ll[0]), z_arr[j])
        z = np.append(z,z_full)
        z_ll.append(z_full)
	#Generate an array of the midpoints of the bins
    ultra_scale_bin = (ultra_scale_max + ultra_scale_min)/2
    lin_scale_bin = (lin_scale_max + lin_scale_min)/2
    quasi_scale_bin = (quasi_scale_max + quasi_scale_min)/2

    k_bin = [ultra_scale_bin, lin_scale_bin, quasi_scale_bin]
    k_list = k_bin * len(z_vals)


	#Gonna try to plot it the pandas way
	#WORKS!!!! AND it fills the whole space. FUCKING LIT
    k_words = ['Ultra-large', 'Linear', 'Quasi Lin']
	#Use pandas to generate a data frame
    df = pd.DataFrame(sum_lin_ll, index=z_arr, columns=k_words)

	#Values greater than threshold will be red, values at 0 will be green
	#and values in between will be gradient of orange

	#Failed here
	#cmap, norm = mcolors.from_levels_and_colors([thres,100], ['red'])

#Trying to brute force colors for me
    cmap = mcolors.ListedColormap(['limegreen', 'greenyellow', 'yellow', 'gold', 'orange','red'])
    bounds = [0,int(thres / 4.), int(thres / 3.), int(thres / 2.), int(thres), int(len(stats_lin_k))]
    norm = mcolors.BoundaryNorm(bounds, cmap.N)

    fig = plt.subplots()
	#Plots the colors
        #pc = plt.pcolor(df, cmap = cmap, norm=norm)
    pc = plt.pcolor(df, cmap = cmap, norm=norm)
    #hm = HeatMap(df.values.tolist(), x)

    plt.yticks(np.arange(0.5, len(df.index),1), df.index)
    plt.xticks(np.arange(0.5, len(df.columns),1), df.columns)
    plt.xlabel('Scales')
    plt.ylabel('$z$')

    #Generate the color bar
    cb = plt.colorbar(pc)
    cb.set_label('Num of Failures')
    plt.title('Scales vs $z$, Threshold = %d' %thres)

    plt.savefig(pc)
    pc.seek(0)
    #Generates ap(df)
    return #send_file(pc, mimety)



@app.route('/')
def home():
    return "Welcome to the Home Page!"

# Index page
@app.route('/kCCL')
def index():
    # Determine the selected feature
    #current_feature_name = request.args.get("feature_name")
    #if current_feature_name == None:
     #   current_feature_name = "Matter Power Spectrum"

    # Create the plot
    plot = create_figure2()

    # Embed plot into HTML via Flask Render
    script, div = components(plot)
    #print (script)
    #print(div)

    return render_template("kCCL.html", script=script, div=div)#,
	   #feature_names=feature_names, current_feature_name=current_feature_name)

# With debug=True, Flask server will auto-reload
# when there are code changes
if __name__ == '__main__':
    #set debug to false in a production envrionment
    app.run(port=5000, debug=True)
