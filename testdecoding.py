# -*- coding: utf-8 -*-
import math
import random
import pandas as pd
import time
import datetime
import subprocess
import os

if not os.path.isfile("./params.py") : #### If custom version of params doesn't exist, copy template
	subprocess.call("cp paramstemplate.py params.py", shell = True)
	from params import *
	from usefulfunctions import *
else :
	from params import *
	from usefulfunctions import *

#####################################################################################################
CHROMTOBETESTED = %%%%%SELECTYOURFAVORITECHROMOSOME%%%%% ####value replaced py the script generate scripts
#####################################################################################################


if LOGGING==True :
	old_stdout = sys.stdout
	log_file = open("./logtestdecode{}.log".format(CHROMTOBETESTED),"w")
	sys.stdout = log_file

print("Program started at {}".format(str(datetime.datetime.now())))

errorsal1 = 0
errorsal2 = 0
listpbal1 = []
listpbal2 = []


_meta = pd.read_csv(PATHORIGIN+"/"+CHROMTOBETESTED+"/_meta.txt.gz", sep = "\t", index_col=False).drop(["#CHROM","ID","QUAL", "FILTER", "INFO", "FORMAT"], 1)

files = list_elements(PATHENCODED + CHROMTOBETESTED + "/", extension = ".txt.gz")


for j in range(min(nbfilesmax, len(files))) :

	testfile = random.choice(files)
	name = testfile.split("/")[-1].split(".")[0]


	_meta["originaldata"] = pd.read_csv(PATHORIGIN+"/"+CHROMTOBETESTED+"/"+name +"_"+ name + ".txt.gz", index_col=None, header=None)

	_meta["totest"] = pd.read_csv(testfile,  index_col = None, header = None)

	for i in range(nbtests):
		totest = random.choice(_meta.totest.tolist())
		A1, A2, position = decode_position(totest, LN)
		#print(A1, A2, position)
		#print(_meta.loc[(_meta.POS == position), :])
		originalalleles = _meta.loc[(_meta.POS == position), :]["originaldata"].tolist()[0].split("/")
		ref =  _meta.loc[(_meta.POS == position), :]["REF"].tolist()[0]
		alt =  _meta.loc[(_meta.POS == position), :]["ALT"].tolist()[0]

		if (originalalleles[0] == 0) and (A1 != ref) :
			errorsal1 +=1
			listpbal1.append(position)
		if (originalalleles[0] == 1) and (A1 != alt) :
			errorsal1 += 1
			listpbal1.append(position)

		if (originalalleles[-1] == 0) and (A1 != alt) :
			errorsal2 +=1
			listpbal2.append(position)
		if (originalalleles[-1] == 1) and (A1 != alt) :
			errorsal2 +=1
			listpbal2.append(position)

		if not LOGGING :
			printProgress(j*nbtests+i,nbtests*min(nbfilesmax, len(files))-1, decimals = 3)
		if VERBOSE == True :
			print("{0}/{1} files tested. Date : {2}".format(i, nbtests, str(datetime.datetime.now())))


print("\nAllele 1 errors : {0}\nAllele 2 errors : {1}\ntotal errors : {2}".format(errorsal1, errorsal2, errorsal1+errorsal2))
print("In total : {}% errors !\n".format(100*(errorsal1+errorsal2)/(2*nbtests*min(nbfilesmax, len(files)))))
print("Date : {}".format(str(datetime.datetime.now())))

if LOGGING==True :
	sys.stdout = old_stdout
	log_file.close()

