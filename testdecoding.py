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
CHROMTOBETESTED = str(%%%%%SELECTYOURFAVORITECHROMOSOME%%%%%) ####value replaced py the script generate scripts
#####################################################################################################

if LOGGING==True :
	old_stdout = sys.stdout
	log_file = open("./logtestdecode{}.log".format(CHROMTOBETESTED),"w")
	sys.stdout = log_file

print("Program started at {}".format(str(datetime.datetime.now())))

errors_file = []
errors_sup_pos = []
errors_real_pos = []
errors_type = []
errors_prev_pos = []
errors_next_pos = []

_meta = pd.read_csv(PATHORIGIN+"/"+CHROMTOBETESTED+"/_meta.txt.gz", sep = "\t", index_col=False).drop(["#CHROM","ID","QUAL", "FILTER", "INFO", "FORMAT"], 1)

files = list_elements(PATHENCODED + CHROMTOBETESTED + "/", extension = ".txt.gz")


for j in range(min(nbfilesmax, len(files))) :
	random.seed()
	testfile = random.choice(files)
	name = testfile.split("/")[-1].split(".")[0]


	_meta["originaldata"] = pd.read_csv(PATHORIGIN+"/"+CHROMTOBETESTED+"/"+name +"_"+ name + ".txt.gz", index_col=None, header=None)

	_meta["totest"] = pd.read_csv(testfile,  index_col = None, header = None)

	for i in range(nbtests):
		totest = random.choice(_meta.totest.tolist())
		A1, A2, position = decode_position(totest, LN)


		if position == -1 :
			index = _meta.loc[(_meta.totest == totest),:].index.tolist()[0]
			errors_file.append(testfile)
			errors_sup_pos.append(position)
			errors_real_pos.append(_meta.iloc[max(index,0), 0])
			errors_type.append("Impossible to decode")
			errors_prev_pos.append(_meta.iloc[max(index-1,0), 0])
			errors_next_pos.append(_meta.iloc[min(index+1, _meta.shape[0]), 0])

			if not LOGGING :
				printProgress(j*nbtests+i,nbtests*min(nbfilesmax, len(files))-1, decimals = 3)
			if VERBOSE == True :
				print("{0}/{1} files tested. Date : {2}".format(i, nbtests, str(datetime.datetime.now())))
			continue

		originalalleles = _meta.loc[(_meta.totest == totest), :]["originaldata"].tolist()[0].split("/")
		originalpos = _meta.loc[(_meta.totest == totest), :]["POS"].tolist()[0]
		ref =  _meta.loc[(_meta.totest == totest), :]["REF"].tolist()[0]
		alt =  _meta.loc[(_meta.totest == totest), :]["ALT"].tolist()[0]

		if position != originalpos:
			index = _meta.loc[(_meta.totest == totest),:].index.tolist()[0]
			errors_file.append(testfile)
			errors_sup_pos.append(position)
			errors_real_pos.append(_meta.iloc[max(index,0), 0])
			errors_type.append("Position")
			errors_prev_pos.append(_meta.iloc[max(index-1,0), 0])
			errors_next_pos.append(_meta.iloc[min(index+1, _meta.shape[0]), 0])

		if ((originalalleles[0] == 0) and (A1 != ref)) or ((originalalleles[0] == 1) and (A1 != alt)) :
			index = _meta.loc[(_meta.totest == totest),:].index.tolist()[0]
			errors_file.append(testfile)
			errors_sup_pos.append(position)
			errors_real_pos.append(_meta.iloc[max(index,0), 0])
			errors_type.append("Allele 1")
			errors_prev_pos.append(_meta.iloc[max(index-1,0), 0])
			errors_next_pos.append(_meta.iloc[min(index+1, _meta.shape[0]), 0])

		if ((originalalleles[-1] == 0) and (A1 != alt)) or ((originalalleles[-1] == 1) and (A1 != alt)) :
			index = _meta.loc[(_meta.totest == totest),:].index.tolist()[0]
			errors_file.append(testfile)
			errors_sup_pos.append(position)
			errors_real_pos.append(_meta.iloc[max(index,0), 0])
			errors_type.append("Allele 2")
			errors_prev_pos.append(_meta.iloc[max(index-1,0), 0])
			errors_next_pos.append(_meta.iloc[min(index+1, _meta.shape[0]), 0])

		if not LOGGING :
			printProgress(j*nbtests+i,nbtests*min(nbfilesmax, len(files))-1, decimals = 3)
		if VERBOSE == True :
			print("{0}/{1} files tested. Date : {2}".format(i, nbtests, str(datetime.datetime.now())))


errors = pd.DataFrame({"File" : errors_file,
	"Supposed_position" : errors_sup_pos,
	"Real_position" : errors_real_pos,
	"Error_type" : errors_type,
	"Previous_positions" : errors_prev_pos,
	"Next_position" : errors_next_pos})

if not errors.empty :
	errorsal1 = errors.loc[(errors.Error_type == "Allele 1"),:].shape[0]
	errorsal2 = errors.loc[(errors.Error_type == "Allele 2"),:].shape[0]
	errorspos = errors.loc[(errors.Error_type == "Position"),:].shape[0]
	Impossibletodecode = errors.loc[(errors.Error_type == "Impossible to decode"),:].shape[0]
	totalerror = errors.shape[0]

	print("\nAllele 1 errors : {0}\nAllele 2 errors : {1}\nPosition errors : {2}\nImpossible to decode : {3}\nTotal errors : {4}".format(errorsal1, errorsal2, errorspos, Impossibletodecode, totalerror))
	print("In total : {}% errors !\n".format(100*(totalerror)/(nbtests*min(nbfilesmax, len(files)))))
	print("Date : {}".format(str(datetime.datetime.now())))
	errors.to_csv("Errorsfoundin{}.csv".format(CHROMTOBETESTED), sep = "\t")
else :
	print("No error found !")


if LOGGING==True :
	sys.stdout = old_stdout
	log_file.close()

