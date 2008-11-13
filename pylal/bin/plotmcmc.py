#!/usr/bin/python
__author__ = "Romain Gouaty"
__version__ = "$Revision$"[11:-2]
__date__ = "$Date$"[7:-2]

import os
import sys
import commands

from optparse import *

usage = """ %prog [options]
"""

parser = OptionParser( usage )

parser.add_option("-v","--version",action="store_true",default=False,\
    help="display version information and exit")

parser.add_option("-f","--mcmc-file",action="store",type="string",\
    metavar=" FILE",help="list of .txt files (or list of path/files) generated by the MCMC code, used as input (there are several files because there are several chains running in parallel). The files in the list have to be separated by a coma.")

parser.add_option("-r","--plot-routine",action="store",type="string",\
    metavar=" FILE",help="path to the \"mcmcsummary.R\" script")

parser.add_option("-e","--executable",action="store",type="string",\
    metavar=" FILE",help="path to the R executable")

parser.add_option("-b","--burnin",action="store",type="string",\
    metavar=" VALUE",help="number of mcmc iterations to disregard")

parser.add_option("-t","--reference-time",action="store",type="string",\
    metavar=" GPS",help="GPS time to be used as reference")

parser.add_option("-C","--reference-mchirp",action="store",type="string",\
    metavar=" VALUE",help="VALUE chirp mass to be used as reference")

parser.add_option("-E","--reference-eta",action="store",type="string",\
    metavar=" VALUE",help="VALUE eta to be used as reference")

parser.add_option("-d","--reference-distance",action="store",type="string",\
    metavar=" VALUE",help="VALUE distance to be used as reference")

parser.add_option("-P","--reference-phi",action="store",type="string",\
    metavar=" VALUE",help="VALUE phi to be used as reference")

parser.add_option("-o","--output-path",action="store",type="string",\
    metavar=" PATH",help="use output path PATH")

parser.add_option("-i","--identity",action="store",type="string",\
    metavar=" STRING",help="job identity STRING")

command_line = sys.argv[1:]
(opts,args) = parser.parse_args()

#################################
# if --version flagged
if opts.version:
  print "$Id$"
  sys.exit(0)

#################################
# Sanity check of input arguments

if not opts.mcmc_file:
  print >> sys.stderr, "No mcmc file specified."
  print >> sys.stderr, "Use --mcmc-file FILE to specify location."
  sys.exit(1)

if not opts.plot_routine:
  print >> sys.stderr, "No R routine specified."
  print >> sys.stderr, "Use --plot-routine FILE to specify location."
  sys.exit(1)

if not opts.executable:
  print >> sys.stderr, "No R executable specified."
  print >> sys.stderr, "Use --executable FILE to specify location."
  sys.exit(1)

if not opts.burnin:
  print >> sys.stderr, "No burnin specified."
  print >> sys.stderr, "Use --burnin VALUE to specify it."
  sys.exit(1)

if not opts.reference_time:
  print >> sys.stderr, "No reference time specified."
  print >> sys.stderr, "Use --reference-time GPS to specify location."
  sys.exit(1)

if not opts.reference_mchirp:
  print >> sys.stderr, "No reference mchirp specified."
  print >> sys.stderr, "Use --reference-mchirp VALUE to specify location."
  sys.exit(1)

if not opts.reference_eta:
  print >> sys.stderr, "No reference eta specified."
  print >> sys.stderr, "Use --reference-eta VALUE to specify location."
  sys.exit(1)

if not opts.reference_distance:
  print >> sys.stderr, "No reference distance specified."
  print >> sys.stderr, "Use --reference-distance VALUE to specify location."
  sys.exit(1)

if not opts.reference_phi:
  print >> sys.stderr, "No reference phi specified."
  print >> sys.stderr, "Use --reference-phi VALUE to specify location."
  sys.exit(1)

if not opts.output_path:
  print >> sys.stderr, "No output path specified."
  print >> sys.stderr, "Use --output-path PATH to specify location."
  sys.exit(1)

if not opts.identity:
  print >> sys.stderr, "No identity specified."
  print >> sys.stderr, "Use --identity STRING to specify it."
  sys.exit(1)

#################################
# Main program

file = open(opts.output_path + "/" + opts.identity + ".R",'w')

file.write("# load the \"mcmcsummary\" code:\n")
file.write("source(\"" + opts.plot_routine + "\")\n\n")

file.write("# load the data written in the MCMC txt file\n")
inputlist = opts.mcmc_file.split(',')
for k,inputfile in enumerate(inputlist):
  file.write("input" + str(k+1) + " <- read.table(\"" + inputfile + "\",header=TRUE)\n")

file.write("\n# keep only the tens of seconds for the GPS time. This will allow to display the decimal part of the gps time with a precision of 1.e-5 seconds.\n")
nb_chain = len(inputlist)
for k in range(nb_chain):
  file.write("input" + str(k+1) + "[,\"time\"] <- input" + str(k+1) + "[,\"time\"] %% 100\n")

file.write("\n# convert the logdistance into distance\n")
for k in range(nb_chain):
  file.write("input" + str(k+1) + "[,\"distance\"] <- exp(input" + str(k+1) + "[,\"logdistance\"])\n")

file.write("\n# Reorganize the input matrix with columns in the following order: chirpmass,massratio,time,pase,distance,loglikelihood\n")
for k in range(nb_chain):
  file.write("newinput" + str(k+1) + " <- cbind(input" + str(k+1) + "[,\"chirpmass\"],input" + str(k+1) + "[,\"massratio\"],input" + str(k+1) + "[,\"time\"],input" + str(k+1) + "[,\"phase\"],input" + str(k+1) + "[,\"distance\"],input" + str(k+1) + "[,\"logposterior\"],input" + str(k+1) + "[,\"loglikelihood\"])\n")

file.write("\n# prepare the input data for the plotting routine\n")
inputdatalist = ""
for k in range(nb_chain):
  inputdatalist += "as.vector(as.matrix(newinput" + str(k+1) + ")),"
file.write("post <- array(c(" + inputdatalist.strip(',') + "), dim=c(nrow(newinput" + str(1) + "),7," + str(nb_chain) + "))\n") #we assume that we are looking at 7 parameters as follows...
file.write("colnames(post) <- c(\"chirpmass\",\"massratio\",\"time\",\"phase\",\"distance\",\"logposterior\",\"loglikelihood\")\n")

file.write("\n# enter injected or inspiral parameters\n")
file.write("injpar <- c(\"chirpmass\"=" + opts.reference_mchirp + ",\"massratio\"=" + opts.reference_eta + ",\"tc\"=" + opts.reference_time + ",\"phi\"=" + opts.reference_phi + ",\"dl\"=" + opts.reference_distance + ",\"logpost\"= NA, \"loglikeli\"= NA" + ")\n")
file.write("injpar[\"tc\"] <- injpar[\"tc\"] %% 100\n\n")

file.write("# execute the \"mcmcsummary\" code:\n")
burninlist = ""
for k in range(nb_chain):
  burninlist += opts.burnin + ","

file.write("mcmcsummary(data=post,targetdirectory=\"" + opts.output_path + "/" + opts.identity + "\",iteration=input1[,1],burnin=c(" + burninlist.strip(',') + "),varnames=colnames(post),truevalue=injpar,graphicsformats = c(\"png\"), overwrite = T)")

file.close()

command = opts.executable + " --slave --vanilla --file=" + opts.output_path + "/" + opts.identity + ".R"

result = commands.getstatusoutput(command)
#result = commands.getoutput(command)

if not result[0] == 0:
  print >> sys.stderr, "status=" + str(result[0])
  print >> sys.stderr, result[1]
  sys.exit(1)

