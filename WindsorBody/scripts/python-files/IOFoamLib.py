#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Description:
------------
This is a python file contains a collection of little functions to handle OpenFOAM data,
write data in a consistent format and read case parameters from the custom caseDefinition file
in post processing scripts.

Functionality:
--------------
This file can be loaded as a python module in other python post processing scripts.

Script developer : Louis Fliessbach (louis.fliessbach@upstream-cfd.com)

Last updated : 04.01.2023
"""
import os
import re
import numpy as np
import yaml

#%% I/O functions
def read_data(inputFile):
    with open(inputFile,'r') as fileIn:
        rawContent = fileIn.readlines()
    return rawContent

def load_data(inputFile,Delimiter,Unpack=False):
    try:
        data        = np.loadtxt(inputFile,delimiter=Delimiter,unpack=Unpack)
    except ValueError:
        rawContent  = read_data(inputFile)
        data        = np.loadtxt(re.sub('\)','',re.sub('\(','',stripCommentedLines(''.join(rawContent),'#'))).split('\n'))
    return data

def write_data(dataSet,Header,pathToOutFile,fileNameOut,delimiter=",",fmt="%30.16e"):
    np.savetxt(os.path.join(pathToOutFile,fileNameOut), dataSet, delimiter=delimiter, header=Header, fmt=fmt)
    return

def find_line_of_string(strList, subStr):
    nLines          = len(strList)
    idxLines        = [iLine for iLine in range(nLines) if subStr in strList[iLine]]
    lineContent     = [strList[iLine] for iLine in idxLines]
    return idxLines, len(idxLines), lineContent

def find_header(inputFile):
    rawContent = read_data(inputFile)
    headerLineIdx, nHeaderLines, headerContent = find_line_of_string(rawContent,'#')
    return headerContent, nHeaderLines

def stripCommentedLines(string,commentMarker):
    return re.sub(r'(?m)^ *'+commentMarker+'.*\n?', '', string)

def remove_comments(line, commentMarker):
    for s in commentMarker:
        i = line.find(s)
        if i >= 0:
            line = line[:i]
    return line.strip()

def get_caseDefinition(inputFile):
    rawContent      = read_data(inputFile)
    stripContent    = []
    caseDict        = {}
    # remove all Comments from list of strings
    for line in rawContent:
        stripContent.append(remove_comments(line,'//'))
    # list all lines with character ';'
    idxLines, nLines, lineContent = find_line_of_string(stripContent, ';')
    for iLine in range(nLines):
        lineContent[iLine] = lineContent[iLine].replace(';', '').split()
        # create keyword value pairs
        try:
            caseDict[str(lineContent[iLine][0])] = int(lineContent[iLine][1])
        except:
            try:
                caseDict[str(lineContent[iLine][0])] = float(lineContent[iLine][1])
            except:
                caseDict[str(lineContent[iLine][0])] = str(lineContent[iLine][1])
    return caseDict

def mergeOFTimeSeries(fileIn=list):
    for iFile, file in zip(range(len(fileIn)), fileIn):
        #tmpData = load_data(file,'\t')
        tmpData = load_data(file,None)
        if iFile == 0:
            data = tmpData
        else:
            try:
                idxOverlap = np.where(data[:,0].astype(float)==float(tmpData[0,0]))[0][0]
                print('Time series %i is overlapping previous time series with %i timesteps'%(iFile,int(len(data[:,0])-idxOverlap)))
                data    = np.concatenate((data[:idxOverlap,:],tmpData),axis=0)
            except IndexError:
                print('No overlapping of time series!')
                data    = np.concatenate((data,tmpData),axis=0)
    return data