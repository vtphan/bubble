'''
Author: Vinhthuy Phan, 2013

Bubble plots are similar to scatter plot, with an additional dimension
that is captured by the circular area of a data point.  Multiple categories
can be captured using different colors.

When to use: 3 dimensional data, where the third dimension is somewhat
qualitative.
'''
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.pyplot import Rectangle, Circle, Line2D, gcf
import tsv
import argparse
import sys
import math

LEGEND_RATIO = 0.1
MARGIN = 0.05
XMIN, XMAX, YMIN, YMAX = None, None, None, None
ALPHA = 0.6
LEGEND_FONT_SIZE = "medium"
LEGEND_TOP_PADDING, LEGEND_LEFT_PADDING = 0, 0
FIG_SIZE = (8,6)

X_var, Y_var, Z_var, Z_is_radius, Category_var, Group_var, Label_var = \
   None, None, None, None, None, None, None

# 1. Linear, 2. Power, 3. Log, 4. Exponential
Z_transform = None

def transform_select(t_type, t_var):
   if t_type is None:
      return lambda(x): x
   if t_type == 1:
      return lambda(x): t_var * x
   if t_type == 2:
      return lambda(x): x**t_var
   if t_type == 3:
      return lambda(x): math.log(x)/math.log(b)
   if t_type == 4:
      return lambda(x): t_var**x

# Maximally distinct colors
# Ref: http://stackoverflow.com/questions/470690/how-to-automatically-generate-n-distinct-colors
COLORS = [('#f3c300', 'Vivid Yellow'), ('#875692', 'Strong Purple'), ('#f38400', 'Vivid Orange'), ('#a1caf1', 'Very Light Blue'), ('#be0032', 'Vivid Red'), ('#c2b280', 'Grayish Yellow'), ('#848482', 'Medium Gray'), ('#008856', 'Vivid Green'), ('#e68fac', 'Strong Purplish Pink'), ('#0067a5', 'Strong Blue'), ('#f99379', 'Strong Yellowish Pink'), ('#604e97', 'Strong Violet'), ('#f6a600', 'Vivid Orange Yellow'), ('#b3446c', 'Strong Purplish Red'), ('#dcd300', 'Vivid Greenish Yellow'), ('#882d17', 'Strong Reddish Brown'), ('#27a64c', 'Vivid Yellowish Green'), ('#654522', 'Deep Yellowish Brown'), ('#e25822', 'Vivid Reddish Orange'), ('#2b3d26', 'Dark Olive Green')]

Categories = []

##-------------------------------------------------------------------
class Subplot:
   def __init__(self, data):
      self.options = {'alpha':ALPHA, 'linewidths':0}
      self.x = []
      self.y = []
      self.label = []
      if Z_var is not None:
         self.options['s'] = []
      if Category_var is not None:
         self.options['c'] = []

   def add(self, r):
      self.x.append(float(r[X_var]))
      self.y.append(float(r[Y_var]))
      if Z_var is not None:
         self.options['s'].append( float(r[Z_var]) )
         if Z_is_radius:
            self.options['s'][-1] = np.pi * self.options['s'][-1]**2
         if Z_transform is not None:
            print Z_transform
            self.options['s'][-1] = Z_transform( self.options['s'][-1] )

      if Category_var is not None:
         if r[Category_var] not in Categories:
            Categories.append(r[Category_var])
            try:
               color = COLORS[len(Categories)-1][0]
            except:
               print ("Error: exceed maximum number of categories (%d)." % len(Categories))
               sys.exit(0)
         else:
            color = COLORS[Categories.index(r[Category_var])][0]
         self.options['c'].append(color)
      if Label_var is not None:
         self.label.append(r[Label_var])

##-------------------------------------------------------------------
## n = rows * cols; rows >= cols
def compute_rows_cols(n):
   for c in range(int(math.floor(math.sqrt(n))), 0, -1):
      r = n/c
      if n == r*c:
         return r,c

##-------------------------------------------------------------------
def check_column(var, data):
   if var is not None and var not in data:
      print "Unknown column %s" % var
      sys.exit(0)

def check_for_column_names(data):
   check_column(X_var,data)
   check_column(Y_var,data)
   check_column(Z_var,data)
   check_column(Category_var,data)
   check_column(Group_var,data)
   check_column(Label_var,data)

# def check_for_range(range):
#    if range is not None:
#       try:
#          (a,b) = (float(i) for i in range.split(" "))
#          return (a,b)
#       except:
#          print("Invalid range: %s.  Valid example: \"0 1\"" % range)
#          sys.exit(0)
#    return None

##-------------------------------------------------------------------
def plot(input_file):
   data = tsv.Read(input_file, ",")
   check_for_column_names(data)

   # Read in data
   if Group_var is not None and Group_var in data:
      subplots = {}
   else:
      subplots = {1:Subplot(data)}
   for r in data:
      group_id = 1
      if Group_var is not None and Group_var in data:
         group_id = r[Group_var]
      if group_id not in subplots:
         subplots[group_id] = Subplot(data)
      subplots[group_id].add(r)

   rows, cols = (1,1) if len(subplots)==1 else compute_rows_cols(len(subplots))
   xlim, ylim = None, None

   figure = plt.figure(figsize=FIG_SIZE)

   # Add plots to figure
   if not Categories:
      plot_width = (1.0-2*MARGIN)/cols
   else:
      plot_width = (1.0-LEGEND_RATIO-2*MARGIN)/cols
   plot_height = (1.0-2*MARGIN)/rows
   for k,group_id in enumerate(subplots):
      plot = subplots[group_id]
      x, y = (k%cols)*plot_width + MARGIN, (k/cols)*plot_height + MARGIN
      axis = figure.add_axes( [x,y,plot_width,plot_height] )
      axis.scatter(plot.x, plot.y, **plot.options)

      if Label_var is not None:
         for i in range(len(plot.x)):
            axis.text(plot.x[i], plot.y[i], plot.label[i],size=11,horizontalalignment='center')

      if len(subplots)>1:
         axis.text(0.05, 0.95, group_id, transform=axis.transAxes, fontsize=16, va='top')
      if xlim is None and ylim is None:
         xlim, ylim = axis.get_xbound(), axis.get_ybound()
      else:
         xlim=min(xlim[0],axis.get_xbound()[0]),max(xlim[1],axis.get_xbound()[1])
         ylim=min(ylim[0],axis.get_ybound()[0]),max(ylim[1],axis.get_ybound()[1])

   # Adjust limits of all axes to the same ranges, plus some extra padding
   x_int, y_int = (xlim[1]-xlim[0])*0.2, (ylim[1]-ylim[0])*0.2
   xlim = (xlim[0]-x_int if XMIN is None else XMIN, xlim[1]+x_int if XMAX is None else XMAX)
   ylim = (ylim[0]-y_int if YMIN is None else YMIN, ylim[1]+y_int if YMAX is None else YMAX)

   for i, axis in enumerate(figure.axes):
      if i%cols != 0:
         axis.set_yticklabels(axis.get_yticklabels(), visible=False)
      if i/cols != 0:
         axis.set_xticklabels(axis.get_xticklabels(), visible=False)
      axis.set_xlim(*xlim)
      axis.set_ylim(*ylim)

   # Build legend
   if Categories:
      x, y = cols*plot_width + MARGIN, MARGIN
      axis = figure.add_axes( [x,y,LEGEND_RATIO,1-2*MARGIN], frameon=False )
      axis.get_xaxis().set_visible(False)
      axis.get_yaxis().set_visible(False)
      markers, labels = [], []
      for i, c in enumerate(Categories):
         color = COLORS[i][0]
         markers.append(Line2D([],[],marker="o",alpha=ALPHA,linewidth=0,mfc=color,mec=color,ms=10))
         labels.append(c)
      figure.axes[-1].legend(markers, labels, loc="upper left", bbox_to_anchor=(0+LEGEND_LEFT_PADDING,1+LEGEND_TOP_PADDING), numpoints=1, fontsize=LEGEND_FONT_SIZE)

   plt.savefig("test.pdf")
   plt.show()

##----------------------------------------------------------------------------
if __name__ == '__main__':
   parser = argparse.ArgumentParser()
   parser.add_argument("input_file", help="comma-separated-values (csv) input file; columns are named in the header.")
   parser.add_argument("X", help="name of column representing the X variable.")
   parser.add_argument("Y", help="name of column representing the Y variable.")
   parser.add_argument("Z", default=None, nargs='?', help="optional name of column representing a third variable. Values equated to areas of bubbles.")
   parser.add_argument("--Z_is_radius", action="store_true", help="indicates that Z values are radii, not areas of bubbles.")
   parser.add_argument("-c", help="optional name of column representing categories. Colors are assigned to categories automatically.")
   parser.add_argument("-g", help="optional name of column representing groups. Each group is represented by a plot.")
   parser.add_argument("-l", help="optional name of column representing data point labels.")
   parser.add_argument("--ranges", nargs=4, type=float, metavar=('xmin','xmax','ymin','ymax'))
   parser.add_argument("--alpha", type=float, default=ALPHA, help="bubble transparency; between 0 and 1. Default: %s" % ALPHA)
   parser.add_argument("--margin", type=float, default=MARGIN, help="plot margin; should be between 0 and 1. Default: %s." % MARGIN)
   parser.add_argument("--legend_ratio", type=float, default=LEGEND_RATIO, help="number between 0 and 1, indicating the fraction of width the legend takes.  Default: %s" % LEGEND_RATIO)
   parser.add_argument("--legend_top_padding", type=float, default=LEGEND_TOP_PADDING, help="Default: %s." % LEGEND_TOP_PADDING)
   parser.add_argument("--legend_left_padding", type=float, default=LEGEND_LEFT_PADDING, help="Default: %s." % LEGEND_LEFT_PADDING)
   parser.add_argument("--figsize", help='Width and height of figure in inches.  Example: "16,12".  Default: %s,%s.' % (FIG_SIZE[0], FIG_SIZE[1]))

   args = parser.parse_args()
   X_var, Y_var, Z_var, Z_is_radius, Category_var, Group_var, Label_var = \
      args.X, args.Y, args.Z, args.Z_is_radius, args.c, args.g, args.l

   if args.ranges:
      XMIN, XMAX, YMIN, YMAX = args.ranges

   # Z_transform = args.Z_transform
   LEGEND_RATIO = args.legend_ratio

   if 0 < args.alpha <= 1:
      ALPHA = args.alpha
   else:
      print ("Invalid alpha.  Must be in (0, 1].")
      sys.exit(0)
   LEGEND_TOP_PADDING = args.legend_top_padding
   LEGEND_LEFT_PADDING = args.legend_left_padding
   MARGIN = args.margin

   if args.figsize is not None:
      try:
         w, h = (float(i) for i in args.figsize.split(","))
         FIG_SIZE = (w, h)
      except:
         print("Invalid figure size %s.  Example --figsize 8,6" % args.figsize)
         sys.exit(0)

   print args
   plot( args.input_file )

