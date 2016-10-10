import os
import subprocess
import glob
import re
import pandas as pd
import math
import multiprocessing

###########################################################################################
####useful functions
###########################################################################################

####List elements in path, _type can be "files", "dir", "all"; exception can be any file you don't want to add in the list
def list_elements(PATH, _type="files", extension='', VERBOSE=False, sort=True, exception=[]):
	filelist = []
	####List all files
	if _type=="files" or _type=="all" :
		iteratorfiles = 0
		for files in glob.glob(PATH+'*'+extension):
			if os.path.isfile(files) and (files not in exception) :
				iteratorfiles+=1
				filelist.append(files)
				if VERBOSE :
					print("File found at {0} : {1}".format(PATH,files))

		print("Number of{0} files found in {1} : {2}".format(extension, PATH, iteratorfiles))


	####List all directories
	if _type=="dir" or _type=="all" :
		iteratordir = 0
		for files in glob.glob(PATH+'*'+extension):
			if os.path.isdir(files) and (files not in exception) :
				iteratordir+=1
				filelist.append(files)
				if VERBOSE :
					print("File found at {0} : {1}".format(PATH,files))

		print("Number of{0} directories found in {1} : {2}".format(extension, PATH, iteratordir))

	if _type=="all" :
		print("In total {0} elements found in {1}".format(iteratordir+iteratorfiles,PATHINPUT))


	####Naturally sort the files so that the chromosomes are processed in the roght order
	if sort :
		filelist = natural_sort(filelist)

	return filelist

def natural_sort(l): 
	convert = lambda text: int(text) if text.isdigit() else text.lower() 
	alphanum_key = lambda key: [ convert(c) for c in re.split('([0-9]+)', key) ] 
	return sorted(l, key = alphanum_key)


def wrightencodeoutput(PATH, dataframe, namedir="/floatfiles") :

	#PATH+namedir
	print("Je suis entrée dans wrightencodeoutput")


###########################################################################################
####useful variables and constants
###########################################################################################

####Constants
PATHINPUT='./'
VERBOSE=False
FILEBATCHSIZE=100
####Intermediate variables to make the encoding a bit more clear
FBP = int(math.pow(2,28)) #FIRST_ALLELE_BIT_POS
SBP = int(math.pow(2,30)) #SECOND_ALLELE_BIT_POS
NL = {"A":int(0), "T":int(1),"G":int(2), "C":int(3)} #NUCLEOTIDE_LABELS
SVE=[NL["A"]*FBP,NL["T"]*FBP,NL["G"]*FBP,NL["C"]*FBP,NL["A"]*SBP,NL["T"]*SBP,NL["G"]*SBP,NL["C"]*SBP] #SNPSVALUESENCODED



####Variables
listdir = []
listfiles = []


###########################################################################################
####It actually starts here
###########################################################################################

if (PATHINPUT[0] == "/") and (len(PATHINPUT)<=1):
	print("Wrong path to data, be careful...")
	quit()
else:
	os.system("rm {}/floatfiles/*".format(PATHINPUT))


listdir = list_elements(PATHINPUT+"/", _type="dir", VERBOSE=True, exception=[PATHINPUT+"floatfiles", PATHINPUT+"/floatfiles"])

print(listdir)

if not os.path.isdir(PATHINPUT+"/floatfiles") :
	os.mkdir(PATHINPUT+"/floatfiles")


for dirs in listdir:


	print("Processing {}".format(dirs))

	####load the meta data in a pandas data frame
	_meta = pd.read_csv(dirs+"/_meta.txt.gz", sep ="\t",index_col=False)


	listfiles = list_elements(dirs+"/", extension=".txt.gz", exception=[dirs+"/_meta.txt.gz", dirs+"_meta.txt.gz", dirs+"/_comments.txt.gz", dirs+"_comments.txt.gz"])

	batchiter = 0
	liste=[]
	df = _meta.drop(["#CHROM","ID","QUAL", "FILTER", "INFO", "FORMAT"], 1)


	for files in listfiles :

		samplename = files.split("_")[0].split("/")[-1]
		liste.append(samplename)

		df[samplename] = pd.read_csv(files)


		if (batchiter < FILEBATCHSIZE) and (files is not listfiles[-1]):
			batchiter += 1
		else :
			print("iter {}".format(batchiter))
			#print(len(liste))
			p = multiprocessing.Process(target=wrightencodeoutput, args=(PATHINPUT, df))
			####Reinitialize stuff
			batchiter = 0
			liste = []
			df = _meta.drop(["#CHROM","ID","QUAL", "FILTER", "INFO", "FORMAT"], 1)
			p.start()