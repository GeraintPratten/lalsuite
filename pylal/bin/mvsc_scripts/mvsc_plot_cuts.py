#!/usr/bin/python
"""Plots the cuts made on any two dimensions by SprBaggerDecisionTreeApp."""

__author__ = 'Tristan Miller <tmiller@caltech.edu>'
__date__ = '$Date$'
__version__ = '$Revision$'
__prog__ = 'mvsc_plot_cuts'

##############################################################################
# import modules
import math, re, sys
from optparse import OptionParser
from mvsc_plots import patread
from matplotlib import pyplot

##############################################################################
# parse arguments

parser = OptionParser()
parser.add_option("-f","--filepath",help="The filepath of the test results")
parser.add_option("-z","--zeropath",default=False, \
                  help="The filepath of zero-lag test results (optional)")
parser.add_option("-t","--treepath",help="The filepath of the decision trees")
parser.add_option("-x",help="Name of the x dimension")
parser.add_option("-y",help="Name of the y dimension")
parser.add_option("-p",default=False,action="store_true",\
                  help="Print out the choices of dimensions and quit")
parser.add_option("","--xlin",action="store_true",default=False, \
                  help="Make linear in x dimension (log by default)")
parser.add_option("","--ylin",action="store_true",default=False, \
                  help="Make linear in y dimension (log by default)")

opts,args = parser.parse_args()

##############################################################################
# The main function: plot_cuts

def plot_cuts(data,cols,dim1_header,dim2_header,dim1log,dim2log,filename=None,\
              zerodata=None):
    """Attempts to plot the decision tree cuts in two dimensions.

    Filename is the path to decision tree file.  If not given, will not plot
    any cuts."""

    if not (cols.has_key(dim1_header) & cols.has_key(dim2_header)):
        print 'Invalid dimensions given to plot-cuts option'
        return
        
    dim1 = cols[dim1_header]
    dim2 = cols[dim2_header]

    injdim1 = []
    tsdim1 = []
    injdim2 = []
    tsdim2 = []

    #separate into timeslides and injections
    for i in range(len(data[0])):
        if data[1][i] == 0:
            tsdim1.append( data[dim1][i] )
            tsdim2.append( data[dim2][i] )
        else:
            injdim1.append( data[dim1][i] )
            injdim2.append( data[dim2][i] )

    #Plot injections and timeslides
    pyplot.figure()
    pyplot.plot(tsdim1,tsdim2,'xk',label='Timeslides')
    pyplot.plot(injdim1,injdim2,'+r',mec='r', \
                label='Injections')

    if zerodata:
        zerodim1 = []
        zerodim2 = []
        for i in range(len(zerodata[0])):
            zerodim1.append( zerodata[dim1][i])
            zerodim2.append( zerodata[dim2][i])

        pyplot.plot(zerodim1,zerodim2,'.g',mec='g', \
            label='Zero lag')
    
    #pyplot.legend(loc='lower right')
    pyplot.xlabel(dim1_header)
    pyplot.ylabel(dim2_header)
    
    if dim1log & dim2log:
        pyplot.loglog()
    elif dim1log:
        pyplot.semilogx()
    elif dim2log:
        pyplot.semilogy()

    if filename:
        #Find all cuts made
        try:
            f = open(filename)
        except IOError:
            print '***Error!*** Trouble opening file', filename
            return

        p = re.compile(r'Id: \S+ Score: \S+ Dim: (\S+) Cut: (\S+)')
        p2 = re.compile(r'Dimensions:')
        p3 = re.compile(r'\s+(\S+)\s+(\S+)')

        dim1cuts = []
        dim2cuts = []
        cuts = []
        cutcols = {}
        
        while True:
            n = f.readline()
            m = p.match(n)
            if m:
                cuts.append( ( m.group(1), m.group(2) ) )
            elif p2.match(n):
                break
            elif not n:
                print '***Error!*** Unexpected format in',filename
                return

        while True:
            n = f.readline()
            m = p3.match(n)
            if m:
                cutcols[m.group(2)] = m.group(1)
            else:
                break
        
        f.close()

        if cutcols.has_key(dim1_header):
            for i in range(len(cuts)):
                if cuts[i][0] == cutcols[dim1_header]:
                    dim1cuts.append(float(cuts[i][1]))

        if cutcols.has_key(dim2_header):
            for i in range(len(cuts)):
                if cuts[i][0] == cutcols[dim2_header]:
                    dim2cuts.append(float(cuts[i][1]))
        
        xmin,xmax = pyplot.xlim()
        ymin,ymax = pyplot.ylim()
    
        #Plot cuts
        for i in range(len(dim1cuts)):
            pyplot.plot([dim1cuts[i],dim1cuts[i]],[ymin,ymax],'b',alpha=0.2)
        for i in range(len(dim2cuts)):
            pyplot.plot([xmin,xmax],[dim2cuts[i],dim2cuts[i]],'b',alpha=0.2)

        pyplot.xlim(xmin,xmax)
        pyplot.ylim(ymin,ymax)
        pyplot.title('Decision tree cuts on "'+dim1_header+'" and "' \
                 +dim2_header+'" dimensions' )
        
    else:
        pyplot.title('Triggers in the "'+dim1_header+'" and "' \
                 +dim2_header+'" dimensions' )

##############################################################################
# execute plot_cuts

if not opts.filepath:
    print 'Filepath option (-f) required'
    sys.exit()

if opts.p:
    header = patread( opts.filepath,headeronly=True )
    print 'Dimensions available:'
    for i in range(len(header)):
        print header[i]
    sys.exit()

if not opts.treepath:
    print 'Treepath option (-t) required'
elif not opts.x:
    print 'X dimension option (-x) required'
elif not opts.y:
    print 'Y dimension option (-y) required'

data,cols = patread( opts.filepath )

if opts.zeropath:
    zerodata,temp1 = patread( opts.zeropath )
else:
    zerodata = None

plot_cuts(data,cols,opts.x,opts.y,not opts.xlin,not opts.ylin, \
                  opts.treepath,zerodata)

pyplot.show()
