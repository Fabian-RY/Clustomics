#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Feb  5 10:49:11 2020

@author: fabian

"""

import os
import random


def random_input_files(variables_num, variable_names, registre_num, writer):
    writer = open(writer, "w")
    #if (len(variable_names) != variables_num):
        #raise Exception("Different number of variable and names")
    #for i in range(variables_num):
        #print(variable_names[i])
        #writer.write("%s\t" %(variable_names[i])) 
    #writer.write("\n")
    for resgistre in range(registre_num):
        for _ in range(variables_num):
            writer.write("%f\t" % (random.random())) 
        writer.write("\n")
    writer.close()

random_input_files(100, ["altura", "anchura"], 50000, "../projects/1tfd.csv")
