'''
Author: Vinhthuy Phan, 2013
'''
import numpy as np
import matplotlib.pyplot as plt
import tsv
import argparse
import sys
import math
import time

LEGEND_RATIO = 0.1
MARGIN = 0.1
XMIN, XMAX, YMIN, YMAX = None, None, None, None
ALPHA = 0.6
LEGEND_FONT_SIZE = "medium"
LEGEND_TOP_PADDING, LEGEND_LEFT_PADDING = 0, 0
FIG_SIZE = (8,6)
LABEL_AXES = False
LEGEND_BUBBLE_Y, LEGEND_BUBBLE_TABS = 3, 2
X_var, Y_var, Z_var, Category_var, Group_var, Label_var = None, None, None, None, None, None
Z_transform, Z_transform_label = None, lambda(x):x

OUTPUT_FORMAT = 'png'

##-------------------------------------------------------------------
## 21 out of Kelly's 22 colours of maximum mutual contrast
COLORS = [
   # ('#101010', 'Light Black',0),
   ('#848482', 'Medium Gray',7),
   ('#f3c300', 'Vivid Yellow',1),
   ('#875692', 'Strong Purple',2),
   ('#f38400', 'Vivid Orange',3),
   ('#a1caf1', 'Very Light Blue',4),
   ('#be0032', 'Vivid Red',5),
   ('#c2b280', 'Grayish Yellow',6),
   ('#848482', 'Medium Gray',7),
   ('#008856', 'Vivid Green',8),
   ('#e68fac', 'Strong Purplish Pink',9),
   ('#0067a5', 'Strong Blue',10),
   ('#f99379', 'Strong Yellowish Pink',11),
   ('#604e97', 'Strong Violet',12),
   ('#f6a600', 'Vivid Orange Yellow',13),
   ('#b3446c', 'Strong Purplish Red',14),
   ('#dcd300', 'Vivid Greenish Yellow',15),
   ('#882d17', 'Strong Reddish Brown',16),
   ('#27a64c', 'Vivid Yellowish Green',17),
   ('#654522', 'Deep Yellowish Brown',18),
   ('#e25822', 'Vivid Reddish Orange',19),
   ('#2b3d26', 'Dark Olive Green',20),
]

Categories = []
All_Z = []
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
         val = float(r[Z_var])
         if Z_transform is not None:
            val = Z_transform(val)
         self.options['s'].append(val)
         All_Z.append(val)

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

   # Estimate width and height
   plot_width = (1.0-2*MARGIN)/cols
   if Categories or (Z_var is not None):
      plot_width -= LEGEND_RATIO/cols
   plot_height = (1.0-2*MARGIN)/rows
   X_OFFSET = 0

   # Add plots to figure
   for k,group_id in enumerate(subplots):
      plot = subplots[group_id]
      x, y = (k%cols)*plot_width + MARGIN, (k/cols)*plot_height + MARGIN
      axis = figure.add_axes( [x,y,X_OFFSET+plot_width,plot_height] )
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
      elif LABEL_AXES:
         axis.set_ylabel(Y_var)
      if i/cols != 0:
         axis.set_xticklabels(axis.get_xticklabels(), visible=False)
      elif LABEL_AXES:
         axis.set_xlabel(X_var)

      axis.set_xlim(*xlim)
      axis.set_ylim(*ylim)

   # Build legend
   if Categories or (Z_var is not None):
      x, y = cols*plot_width + MARGIN, MARGIN
      axis = figure.add_axes( [X_OFFSET+x,y,LEGEND_RATIO,1-2*MARGIN], frameon=False )
      axis.get_xaxis().set_visible(False)
      axis.get_yaxis().set_visible(False)
      if All_Z:
         All_Z.sort()
         median_Z = All_Z[len(All_Z)/2]
         median_Z = int(median_Z) if median_Z > 10 else median_Z
         axis.set_ylim(0,10)
         axis.scatter([2],[LEGEND_BUBBLE_Y], s=median_Z, alpha=0.5, c='#786D5F', linewidths=0)
         axis.text(2,LEGEND_BUBBLE_Y, '%s%s%s' % (Z_transform_label(Z_var),LEGEND_BUBBLE_TABS*'\n',median_Z),
            size=9,horizontalalignment='center')

      if Categories:
         markers, labels = [], []
         for i, c in enumerate(Categories):
            color = COLORS[i][0]
            markers.append(plt.Line2D([],[],marker="o",alpha=ALPHA,linewidth=0,mfc=color,mec=color,ms=10))
            labels.append(c)
         figure.axes[-1].legend(markers, labels, loc="upper left", bbox_to_anchor=(0+LEGEND_LEFT_PADDING,1+LEGEND_TOP_PADDING), numpoints=1, fontsize=LEGEND_FONT_SIZE)


   # if Z_var is not None:
   #    figure.suptitle("%s, %s, and %s" % (X_var,Y_var,Z_transform_label(Z_var)), y=1-0.5*MARGIN)

   # Save
   t = time.localtime()
   output = 'output_%s_%s_%s_%s_%s_%s.%s' % \
      (t.tm_year, t.tm_mon, t.tm_mday, t.tm_hour, t.tm_min, t.tm_sec, OUTPUT_FORMAT)
   print "Save output to %s" % output
   plt.savefig(output)
   plt.show()

##----------------------------------------------------------------------------

def select_transform(L):
   def compose(fs):
      return (lambda(x): compose(fs[1:])( fs[0](x) )) if len(fs) > 1 else fs[0]

   def transform(key, val):
      functions = dict(
         add = lambda(x): val+x,
         mul = lambda(x): val*x,
         pow = lambda(x): x**val,
         log = lambda(x): math.log(x)/math.log(val),
         exp = lambda(x): val**x,
      )
      return functions.get(key)

   def transform_rep(key, val):
      functions = dict(
         add = lambda(x): '%s+%s' % (x, val),
         mul = lambda(x): '(%s)$\cdot$%s' % (x, val),
         pow = lambda(x): '(%s)$^{%s}$' % (x, val),
         log = lambda(x): '$log_{%s}$(%s)' % (val, x),
         exp = lambda(x): '%s^(%s)' % (val, x),
      )
      return functions.get(key)

   L2, L3 = [], []
   for key, val in L:
      try:
         val = float(val)
      except:
         raise argparse.ArgumentTypeError("Transform value %s is not a float" % val)

      f = transform(key, val)
      if f is None:
         raise argparse.ArgumentTypeError("%s is not a valid transform" % key)
      else:
         L2.append(f)
      L3.append(transform_rep(key,val))

   return compose(L2), compose(L3)

##----------------------------------------------------------------------------
if __name__ == '__main__':
   parser = argparse.ArgumentParser(description="Names of X, Y, Z, Category, Group, and Label must match with information specified in the header of the input file.")
   parser.add_argument("input_file", metavar="data.csv", help="header must contain names of X, Y and optionally Z, Category, Group, and Label.")
   parser.add_argument("X")
   parser.add_argument("Y")
   parser.add_argument("Z", default=None, nargs='?', help="optional, transformable, proportional to bubble areas.")
   parser.add_argument("-c", metavar="Category")
   parser.add_argument("-g", metavar="Group")
   parser.add_argument("-l", metavar="Label")
   parser.add_argument("-t", nargs=2, metavar=('transform', 'value'), action='append',
      help="transform Z variable.  Transform is one of {add, mul, pow, log, exp}.  Value is a float.")
   parser.add_argument("--ranges", nargs=4, type=float, metavar=('xmin','xmax','ymin','ymax'))
   parser.add_argument("--legend", type=float, nargs=3, metavar=('p', 'left', 'top'),
      help="p: figure portion given to legend; default is 0.1.  \
            left: spacing between plot and legend; default: 0.  \
            top: spacing between figure top & legend; default: 0.")
   parser.add_argument("--legend_bubble", type=float, nargs=2, metavar=('y', 'spacing'),
      help="y: position of vertical bubble placement; default: 3.  \
            spacing: no. of lines between annotations; default: 2.")
   parser.add_argument("--label_axes", default=LABEL_AXES, action="store_true", help="Turn on axes labels.")
   parser.add_argument("--figsize", type=float, nargs=2, metavar=('w', 'h'),
      help='figure width and height in inches; default: %s %s.' % (FIG_SIZE[0], FIG_SIZE[1]))
   parser.add_argument("--alpha", type=float, default=ALPHA, metavar='a',
      help="bubble transparency; default: %s" % ALPHA)
   parser.add_argument("--margin", type=float, metavar='m', help="plot margin; default: %s." % MARGIN)
   parser.add_argument("--output", choices=["png","pdf"], default=OUTPUT_FORMAT,
      help="format of output file; default: %s" % OUTPUT_FORMAT, )
   args = parser.parse_args()
   X_var, Y_var, Z_var, Category_var, Group_var, Label_var = args.X, args.Y, args.Z, args.c, args.g, args.l

   if args.t:
      Z_transform, Z_transform_label = select_transform(args.t)

   LABEL_AXES = args.label_axes
   ALPHA = args.alpha
   if args.margin:
      MARGIN = args.margin

   if args.ranges:
      XMIN, XMAX, YMIN, YMAX = args.ranges

   if args.legend:
      LEGEND_RATIO, LEGEND_LEFT_PADDING, LEGEND_TOP_PADDING = args.legend

   if args.legend_bubble:
      LEGEND_BUBBLE_Y = args.legend_bubble[0]
      LEGEND_BUBBLE_TABS = int(args.legend_bubble[1])

   if args.figsize:
      FIG_SIZE = args.figsize

   OUTPUT_FORMAT = args.output

   plot( args.input_file )

