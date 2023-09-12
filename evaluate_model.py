import json
from pickle import FALSE, TRUE
from re import I
import pandas as pd
import numpy as np
import math
import seaborn as sns
import matplotlib.pyplot as plt

def main():

    # Opening JSON file
    f = open('./materials/stimuli.json')
    
    # returns JSON object as
    # a dictionary
    stimuli = json.load(f)
    # easy = [ 1  for stimulus in stimuli if ((stimulus["nr_reds"]/stimulus["nr_total"]*100)>=50 and (stimulus["AI_conf"] >= 50)) ] + [ 1  for stimulus in stimuli if ((stimulus["nr_reds"]/stimulus["nr_total"]*100)<50 and (stimulus["AI_conf"] < 50)) ]
    # hard = [ ((stimulus["nr_reds"]/stimulus["nr_total"]*100), stimulus["AI_conf"])  for stimulus in stimuli if ((stimulus["nr_reds"]/stimulus["nr_total"]*100)>=50 and (stimulus["AI_conf"] < 50)) ] + [ ((stimulus["nr_reds"]/stimulus["nr_total"]*100), stimulus["AI_conf"])  for stimulus in stimuli if ((stimulus["nr_reds"]/stimulus["nr_total"]*100)<50 and (stimulus["AI_conf"] >= 50)) ]
    # easy = [ 1  for stimulus in stimuli if ((stimulus["nr_reds"]/stimulus["nr_total"]*100)>=70 and (stimulus["AI_conf"] >= 70)) ] + [ 1  for stimulus in stimuli if ((stimulus["nr_reds"]/stimulus["nr_total"]*100)<70 and (stimulus["AI_conf"] < 70)) ]
    # hard = [ ((stimulus["nr_reds"]/stimulus["nr_total"]*100), stimulus["AI_conf"])  for stimulus in stimuli if ((stimulus["nr_reds"]/stimulus["nr_total"]*100)>=70 and (stimulus["AI_conf"] < 70)) ] + [ ((stimulus["nr_reds"]/stimulus["nr_total"]*100), stimulus["AI_conf"])  for stimulus in stimuli if ((stimulus["nr_reds"]/stimulus["nr_total"]*100)<70 and (stimulus["AI_conf"] >= 70)) ]
    easy = [ 1  for stimulus in stimuli if ((stimulus["nr_reds"]/stimulus["nr_total"]*100)>=50 and (stimulus["AI_conf"] >= 50)) ] + [ 1  for stimulus in stimuli if ((stimulus["nr_reds"]/stimulus["nr_total"]*100)<50 and (stimulus["AI_conf"] < 50)) ]
    hard = [ ((stimulus["nr_reds"]/stimulus["nr_total"]*100), stimulus["AI_conf"])  for stimulus in stimuli if ((stimulus["nr_reds"]/stimulus["nr_total"]*100)>=50 and (stimulus["AI_conf"] < 50)) ] + [ ((stimulus["nr_reds"]/stimulus["nr_total"]*100), stimulus["AI_conf"])  for stimulus in stimuli if ((stimulus["nr_reds"]/stimulus["nr_total"]*100)<50 and (stimulus["AI_conf"] >= 50)) ]
    
    easy_total =  len(easy)
    hard_total = len(stimuli) - easy_total
    win_prob_list = [ stimulus["nr_reds"]/stimulus["nr_total"] for stimulus in stimuli if stimulus["AI_conf"] >= 50]
    win_prob_list += [ 1-(stimulus["nr_reds"]/stimulus["nr_total"]) for stimulus in stimuli if stimulus["AI_conf"] < 50]

    win_prob_list_perf = [ stimulus["nr_reds"]/stimulus["nr_total"] for stimulus in stimuli if stimulus["nr_reds"]/stimulus["nr_total"] >= 0.5]
    win_prob_list_perf += [ 1-(stimulus["nr_reds"]/stimulus["nr_total"]) for stimulus in stimuli if stimulus["nr_reds"]/stimulus["nr_total"] < 0.5]

    print("Expected accuracy: ", sum(win_prob_list)/len( win_prob_list))
    print("Expected accuracy perf: ", sum(win_prob_list_perf)/len( win_prob_list_perf))
    print("Easy stimuli: ", easy_total)
    print("Hard stimuli: ", hard_total)
    print("Hard stimuli: ", hard)

    true_prob = [ stimulus["nr_reds"]/stimulus["nr_total"] for stimulus in stimuli] 
    model_conf = [ stimulus["AI_conf"] for stimulus in stimuli]  
    df = pd.DataFrame({'true_prob': true_prob, 'model_conf':model_conf })
    sns.histplot(df, x="true_prob", y="model_conf", cbar=TRUE )
    plt.show()

    alpha= 0.1
    gamma = 1/5
    human_conf_val = 5.0
    eta = 0.1
    nr_datapoints = lambda x: human_conf_val/(alpha*alpha*x*gamma) * math.log(human_conf_val/(x*eta))
    nr_bins = np.arange(1,26)
    nr_stimuli = 24
    data =[nr_datapoints(1/x) for x in nr_bins]
    people =[round(nr_datapoints(1/x)/nr_stimuli) for x in nr_bins]
    df_bins = pd.DataFrame({'nr_bins': nr_bins, 'participants':people })
    sns.relplot(df_bins, x='nr_bins', y='participants')
    plt.show()

if __name__ == "__main__":
    main()