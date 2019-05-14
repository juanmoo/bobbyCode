#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Mar 21 22:56:12 2019

@author: Bobby
"""

import pandas
import numpy as np
import operator
import time
import json


##################################################################################
#Match Along new dimensions
##################################################################################  

def gen_branch_pref(dict_cadet, branches):
    """
    Input:  dict_cadet: Dictionary where key is cadet, value is list with first element favorite
            branches:   List of branches all strings
    Output: dict_branchpref:  Dictionary where key is branch, value is another dict
               with key 'pref' is preference order of cadet and 'capacity' is
               capacity of branch.
    """
    branch_scores = {}
    for branch in branches:
        branch_scores[str(branch)+"_score"] = {}
    
    
    for cadet in dict_cadet.keys():
        #AD 1,2
        branch_scores['AD_score'][cadet] =  1/2*dict_cadet[cadet]['a1_uncor'] + 1/2*dict_cadet[cadet]['a2_uncor']
        #AG 1,3
        branch_scores['AG_score'][cadet] =  1/2*dict_cadet[cadet]['a1_uncor'] + 1/2*dict_cadet[cadet]['a3_uncor']
        #AR 1,4
        branch_scores['AR_score'][cadet] =  1/2*dict_cadet[cadet]['a1_uncor'] + 1/2*dict_cadet[cadet]['a4_uncor']
        #AV 1,5
        branch_scores['AV_score'][cadet] =  1/2*dict_cadet[cadet]['a1_uncor'] + 1/2*dict_cadet[cadet]['a5_uncor']
        #CM 2,2
        branch_scores['CM_score'][cadet] = 1/2*dict_cadet[cadet]['a2_uncor'] + 1/2*dict_cadet[cadet]['a2_uncor']
        #EN 1,1
        branch_scores['EN_score'][cadet] =  1/2*dict_cadet[cadet]['a1_uncor'] + 1/2*dict_cadet[cadet]['a1_uncor']
        #FA 2,3'
        branch_scores['FA_score'][cadet] = 1/2*dict_cadet[cadet]['a2_uncor'] + 1/2*dict_cadet[cadet]['a3_uncor']
        #FI 2,4
        branch_scores['FI_score'][cadet] =  1/2*dict_cadet[cadet]['a2_uncor'] + 1/2*dict_cadet[cadet]['a4_uncor']
        #IN 2,5
        branch_scores['IN_score'][cadet] =  1/2*dict_cadet[cadet]['a2_uncor'] + 1/2*dict_cadet[cadet]['a5_uncor']
        #MI 3,3
        branch_scores['MI_score'][cadet] =  1/2*dict_cadet[cadet]['a3_uncor'] + 1/2*dict_cadet[cadet]['a3_uncor']
        #MP 3,4
        branch_scores['MP_score'][cadet] =  1/2*dict_cadet[cadet]['a3_uncor'] + 1/2*dict_cadet[cadet]['a4_uncor']
        #MS 3
        branch_scores['MS_score'][cadet] =  1/2*dict_cadet[cadet]['a3_uncor'] + 1/2*dict_cadet[cadet]['a3_uncor']
        #OD 4,4
        branch_scores['OD_score'][cadet] =  1/2*dict_cadet[cadet]['a4_uncor'] + 1/2*dict_cadet[cadet]['a4_uncor']
        #QM 4,5
        branch_scores['QM_score'][cadet] =  1/2*dict_cadet[cadet]['a4_uncor'] + 1/2*dict_cadet[cadet]['a5_uncor']
        #SC 5,5
        branch_scores['SC_score'][cadet] =  1/2*dict_cadet[cadet]['a5_uncor'] + 1/2*dict_cadet[cadet]['a5_uncor']
        #SP 1
        branch_scores['SP_score'][cadet] =  1/2*dict_cadet[cadet]['a1_uncor'] + 1/2*dict_cadet[cadet]['a1_uncor']
        #TC 3,5
        branch_scores['TC_score'][cadet] =  1/2*dict_cadet[cadet]['a3_uncor'] + 1/2*dict_cadet[cadet]['a5_uncor']
    
    dict_branchpref = {}
    for branch in branches:
        sorted_list = sorted(branch_scores[str(branch) + '_score'].items(), key=operator.itemgetter(1), reverse = True)
        dict_branchpref[branch] = {}
        dict_branchpref[branch]['pref'] = []
        for tupe in sorted_list:
            dict_branchpref[branch]['pref'].append(tupe[0])
    dict_branchpref['AD']['capacity'] = 82
    dict_branchpref['AG']['capacity'] = 144
    dict_branchpref['AR']['capacity'] = 128
    dict_branchpref['AV']['capacity'] = 146
    dict_branchpref['CM']['capacity'] = 67
    dict_branchpref['EN']['capacity'] = 189
    dict_branchpref['FA']['capacity'] = 233
    dict_branchpref['FI']['capacity'] = 35
    dict_branchpref['IN']['capacity'] = 282
    dict_branchpref['MI']['capacity'] = 362
    dict_branchpref['MP']['capacity'] = 100
    dict_branchpref['MS']['capacity'] = 0
    dict_branchpref['OD']['capacity'] = 208
    dict_branchpref['QM']['capacity'] = 164
    dict_branchpref['SC']['capacity'] = 255
    dict_branchpref['TC']['capacity'] = 150
    dict_branchpref['SP']['capacity'] = 4
      
    return dict_branchpref


##################################################################################
#Deferred Acceptance Algorithm
##################################################################################  
def cadet_prop_deferred(cadet_prefs,branch_prefs):
    """
    Input: cadet_prefs: Dictionary where key is cadet, value is list with first element favorite
           branch_pref: Dictionary where key is branch, value is another dict
               with key 'pref' is preference order of cadet and 'capacity' is
               capacity of branch.
    Output: cadet_matches: Dictionary with key as cadet and value as match
            branch_matches: Dictionary with key branch and value as set of cadet matches.
    
    """
    cadet_matches = {}
    branch_matches = {}
    branch_minority_match = {}
    cadets_unmatched = cadet_prefs.keys()
    
    for branch in branch_prefs.keys():
        branch_matches[branch] = []
    for cadet in cadet_prefs.keys():
        cadet_matches[cadet] = []
    #A trigger to let us know when we finish
    finish = 1
    step = 1
    while finish:  
        
        #A trigger to let us know when the step is finished
        step_comp = 1
        while step_comp:
            
            #Choose the index
            index = step - 1
            #track cadets pushed aside
            cadets_unmatched_after = []
            rejected_cadets = []
            #For cadets not matched or rejected
            for cadet in cadets_unmatched:
                #Figure out who cadet is proposing to
                propose_to = cadet_prefs[cadet][index]
               
                #Number of cadets in branch
                num_filled = len(branch_matches[propose_to])
                
                capacity = branch_prefs[propose_to]['capacity']
                
                #Discover if better than worst cadet in branch
                not_worst_rank_in_branch = 0
                brnch_pref_list = branch_prefs[propose_to]['pref']
                brnch_matches = branch_matches[propose_to]
                cdt_br_rnk = brnch_pref_list.index(cadet)
                #Worst cadet
                worst_cadet = cadet
                #For each match in our proposed branch
                for match in brnch_matches:
    
                    #Check if any are worse ranked than our cadet
                    if brnch_pref_list.index(match) > cdt_br_rnk:
                        not_worst_rank_in_branch = 1
                        #If so, see if worse than the worst
                        if brnch_pref_list.index(match) > brnch_pref_list.index(worst_cadet):
                            worst_cadet = match
                
                #Now we go through different possibilites.
                #If branch is not filled add cadet
                if num_filled < capacity:
                    cadet_matches[cadet] = propose_to
                    branch_matches[propose_to].append(cadet)
                    
                #Else if not the worst choice
                elif not_worst_rank_in_branch:
                    
                    branch_matches[propose_to].remove(worst_cadet)
                    cadets_unmatched_after.append(worst_cadet)
                    cadet_matches[worst_cadet] = ""
                    #Add our cadet in
                    branch_matches[propose_to].append(cadet)
                    cadet_matches[cadet] = propose_to
                        
                #Finally add cadet to list of rejected if not matched
                else:
                    rejected_cadets.append(cadet)
                    
            #Updated list of cadets who need to attempt to match
            cadets_unmatched = cadets_unmatched_after
            
            #If no cadets need to be attempted to update
            if cadets_unmatched_after == []:
                step_comp = 0
                step = 1 + step
                cadets_unmatched = rejected_cadets
        if step == 5:
            finish = 0
    return (cadet_matches, branch_matches)

##################################################################################
#Generate Fake Score
##################################################################################  
#for each cadet uncorrelated
def gen_partition(dict_cadet):
    """
    Input: dict_cadet: Dictionary where key is cadet, value is list with first element favorite
    Output: partition: Dictionary with key as cadet and value as list with first value
                       with first value equal to upper bound and second value lower bound.
    """
    #intialize dict of partitions
    partition = {}
    
    #pull the list of cadets
    list_cadet = list(dict_cadet.keys())
    
    #for each cadet in the list of cadets
    for index in range(len(list_cadet)):
        
        #iniditialize the cadet we are looking at and their oms
        cadet = list_cadet[index]
        cadet_oms = dict_cadet[cadet]['oms_score']
        
        #if they are first
        if index == 0:
            #look at the next cadet and take their oms then average with current cadet
            cadet_after = list_cadet[index + 1]
            cadet_after_oms = dict_cadet[cadet_after]['oms_score']
            average_after = (cadet_oms + cadet_after_oms)/2
            
            #partition for this cadet is .01 above and the below bound
            partition[cadet] = [cadet_oms +.01, average_after]
            
        #if they are last
        elif index == len(list_cadet)-1:
            #look at cadet before and do same steps as before
            cadet_before = list_cadet[index - 1]
            cadet_before_oms = dict_cadet[cadet_before]['oms_score']
            average_before = (cadet_oms + cadet_before_oms)/2
            partition[cadet] = [average_before, cadet_oms-.01]
            
        #Otherwise
        else:
            #Oms of next cadet
            cadet_after = list_cadet[index + 1]
            cadet_after_oms = dict_cadet[cadet_after]['oms_score']
            #Oms ov cadet before
            cadet_before = list_cadet[index - 1]
            cadet_before_oms = dict_cadet[cadet_before]['oms_score']
            #average between after and current
            average_after = (cadet_oms + cadet_after_oms)/2
            #average between before and current
            average_before = (cadet_oms + cadet_before_oms)/2
            #use to create bounds
            partition[cadet] = [average_before, average_after]
    return partition
def gen_cadet_uncor(dict_cadet):
    """
    Input: dict_cadet:  Dictionary where key is cadet, value is full info of cadet.
                        make sure oms is under key 'oms_score'
    Output: dict_cadet: Dictionary with key as cadet and value as match generated
                        subscore with uncorrelated subscores.
    """
    start = time.time()
    partition = gen_partition(dict_cadet)
    
    toofar = 1
    #while the generated is too far away
    while toofar:
        a1_uncor = np.random.uniform(75,85) + np.random.normal(0,10)
        a2_uncor = np.random.uniform(75,85) + np.random.normal(0,10)
        a3_uncor = np.random.uniform(75,85) + np.random.normal(0,10)
        a4_uncor = np.random.uniform(75,85) + np.random.normal(0,10)
        a5_uncor = np.random.uniform(75,85) + np.random.normal(0,10)
        oms_gen = 1/5*a1_uncor +1/5*a2_uncor + 1/5*a3_uncor + 1/5*a4_uncor + 1/5*a5_uncor
        
        #Check if value fall in partition
        for cadet in list(partition.keys()):
            if oms_gen <= partition[cadet][0] and oms_gen >= partition[cadet][1]:
                dict_cadet[cadet]['oms_uncor'] = oms_gen
                dict_cadet[cadet]['a5_uncor'] = a5_uncor
                dict_cadet[cadet]['a4_uncor'] = a4_uncor
                dict_cadet[cadet]['a3_uncor'] = a3_uncor
                dict_cadet[cadet]['a2_uncor'] = a2_uncor
                dict_cadet[cadet]['a1_uncor'] = a1_uncor
                del partition[cadet]
                break

        if len(list(partition.keys())) == 0:
            toofar = 0
    end = time.time()
    print(end-start)
    return dict_cadet

def gen_cadet_cor(dict_cadet):  
    """
    Input: dict_cadet:  Dictionary where key is cadet, value is full info of cadet.
                        make sure oms is under key 'oms_score'
    Output: dict_cadet: Dictionary with key as cadet and value as match generated
                        subscore with correlated subscores.
    """      
    start = time.time()
    partition = gen_partition(dict_cadet)
    
    
    toofar = 1
    #while the generated is too far away
    while toofar:
        ability = np.random.uniform(75,85)
        a1_cor = ability + np.random.normal(0,10)
        a2_cor = ability + np.random.normal(0,10)
        a3_cor = ability + np.random.normal(0,10)
        a4_cor = ability + np.random.normal(0,10)
        a5_cor = ability + np.random.normal(0,10)
        oms_gen = 1/5*a1_cor +1/5*a2_cor + 1/5*a3_cor + 1/5*a4_cor + 1/5*a5_cor
        
        #Check if value fall in partition
        for cadet in list(partition.keys()):
            if oms_gen <= partition[cadet][0] and oms_gen >= partition[cadet][1]:
                dict_cadet[cadet]['oms_cor'] = oms_gen
                dict_cadet[cadet]['a5_cor'] = a5_cor
                dict_cadet[cadet]['a4_cor'] = a4_cor
                dict_cadet[cadet]['a3_cor'] = a3_cor
                dict_cadet[cadet]['a2_cor'] = a2_cor
                dict_cadet[cadet]['a1_cor'] = a1_cor
                del partition[cadet]
                break

        if len(list(partition.keys())) == 0:
            toofar = 0
    end = time.time()
    print(end-start)
    return dict_cadet
"""
cadet_data_gen = pandas.DataFrame(dict_cadet.items())
cadet_data_gen.to_csv("/Users/Bobby/Desktop/14125Final/Datagen.csv")
"""


##################################################################################
#Importing in cadet preferences
##################################################################################  
#load in data and turn it into a dictionary where the keys are their respective rank as a string
cadetrank = pandas.read_csv('./cadet_clean.csv')
dict_cadet = cadetrank.to_dict('index')
#dict_cadet = {}
#for key in dict_cadet_num.keys():
#    dict_cadet[str(key)] = dict_cadet_num[key]
list_cadet = list(dict_cadet.keys())
branchpref = list(dict_cadet.keys())

#generate a dictionary of cadet preferences where key is cadet rank and object is list of pref with
#first item most preferred then second then third
cadetpref = {}
for cadet in list_cadet:
    cadetpref[cadet] = []
    for prefnum in ['p1','p2','p3','p4','p5',]:
        cadetpref[cadet].append(dict_cadet[cadet][prefnum])

#Create branch preferences where key is branch and object is rank order list of cadets
branches = ['AD','AG','AR','AV','CM','EN','FA','FI','IN','MI','MP','MS',
            'OD','QM','SC','SP','TC']
final_branchpref = {}

for branch in branches:
    dict_branchpref = {}
    dict_branchpref['pref'] = branchpref
    final_branchpref[branch] = dict_branchpref
    
final_branchpref['AD']['capacity'] = 82
final_branchpref['AG']['capacity'] = 144
final_branchpref['AR']['capacity'] = 128
final_branchpref['AV']['capacity'] = 146
final_branchpref['CM']['capacity'] = 67
final_branchpref['EN']['capacity'] = 189
final_branchpref['FA']['capacity'] = 233
final_branchpref['FI']['capacity'] = 35
final_branchpref['IN']['capacity'] = 282
final_branchpref['MI']['capacity'] = 362
final_branchpref['MP']['capacity'] = 100
final_branchpref['MS']['capacity'] = 0
final_branchpref['OD']['capacity'] = 208
final_branchpref['QM']['capacity'] = 164
final_branchpref['SC']['capacity'] = 255
final_branchpref['TC']['capacity'] = 150
final_branchpref['SP']['capacity'] = 4

##################################################################################
#DA matching
##################################################################################  
"""
cadet_matches, branch_matches = cadet_prop_deferred(cadetpref, final_branchpref)

cadet_match_dataframe = pandas.DataFrame(cadet_matches.items(), columns=['id', 'Match'])

cadet_match_dataframe.to_csv("/Users/Bobby/Desktop/14125Final/DA.csv")
"""

##################################################################################
#Match Along new dimensions
##################################################################################  
all_matches_uncor = {}
all_matches_cor = {}

start_iteration = 900

iteration_num = 100
iteration = start_iteration

#Load Current Version of Files

try:
    with open("./uncor_output.json", "r") as uncor_file:
        uncor_input = uncor_file.read()
        if len(uncor_input) > 0:
            all_matches_uncor = json.loads(uncor_input)
    
    with open("./cor_output.json", "r") as cor_file:
        cor_input = cor_file.read()
        if len(cor_input) > 0:
            all_matches_cor = json.loads(cor_input)
    
    assert(len(all_matches_uncor) == len(all_matches_cor))

except:
    pass

if len(all_matches_uncor) > 0:
    iteration = max(max([int(k) for k in all_matches_uncor.keys()]) + 1, iteration)
    print("Skipped to iteration {}".format(iteration))


while iteration < iteration_num + start_iteration:
    uncor_dict_cadet = gen_cadet_uncor(dict_cadet)
    print("uncor datagen finish")
    uncor_cadetpref = {}
    for cadet in list_cadet:
        uncor_cadetpref[cadet] = []
        for prefnum in ['p1','p2','p3','p4','p5',]:
            uncor_cadetpref[cadet].append(uncor_dict_cadet[cadet][prefnum])

    uncor_branch_pref = gen_branch_pref(uncor_dict_cadet, branches)
    
    print("uncor branchpref gen finish")
    uncor_cadet_matches = cadet_prop_deferred(uncor_cadetpref,uncor_branch_pref)[0]
    print("uncor match finish")
    all_matches_uncor[iteration] = uncor_cadet_matches
    
    
    
    cor_dict_cadet = gen_cadet_uncor(dict_cadet)
    print("cor datagen finish")
    cor_cadetpref = {}
    for cadet in list_cadet:
        cor_cadetpref[cadet] = []
        for prefnum in ['p1','p2','p3','p4','p5',]:
            cor_cadetpref[cadet].append(cor_dict_cadet[cadet][prefnum])
    
    cor_branch_pref = gen_branch_pref(cor_dict_cadet, branches)
    print("cor branchpref gen finish")
    cor_cadet_matches = cadet_prop_deferred(cor_cadetpref,cor_branch_pref)[0]
    print("cor match finish")
    all_matches_cor[iteration] = cor_cadet_matches
    
    print(iteration)
    iteration += 1

    # Update File State
    with open('./uncor_output.json', 'w+') as f:
        f.write(json.dumps(all_matches_uncor, indent=4))

    with open('./cor_output.json', 'w+') as f:
        f.write(json.dumps(all_matches_cor, indent=4))
