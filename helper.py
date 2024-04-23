import pandas as pd
import numpy as np

#count number of red cards in array
def is_red(name):
    return any(substring in name for substring in ["hearts","diamonds"])

vec_is_red = np.vectorize(is_red)

#discretize human confidence levels
def discretize_confidence(df_center_responses_level, conf_levels):
    divider = 100/(len(conf_levels)-1)
    df_center_responses_level["dm_conf"] = np.array([conf_levels[int(i)] for i in np.floor(df_center_responses_level["center_prob"]/divider)])
    #set dm_conf to "high" with prob. 0.5 if center_conf is 50
    df_center_responses_level.loc[(df_center_responses_level["center_prob"]==50),"dm_conf"] = np.random.choice(["high", "low"],len(df_center_responses_level.loc[(df_center_responses_level["center_prob"]==50),"dm_conf"]))

    # print("number of 50/50 instances: ", len(df_center_responses_level.loc[(df_center_responses_level["center_prob"]==50)]))
    # print((df_center_responses_level[["center_prob","dm_conf"]]))
    return df_center_responses_level

# read stimuli and estimate perceived probability of human DM (number of red cards shown)
def get_responses(stimuli, attention_tests, row, col, shape_center, nr_center):

    stimuli = pd.read_json(stimuli)
    stimuli["stimulus"]= stimuli["stimulus"].apply(lambda x: vec_is_red(np.array(x)).astype(int))
    # stimuli["center_stimulus"] = stimuli["stimulus"].apply(lambda x: np.hsplit(x,np.array([4,9]))[1])
    stimuli["center_prob"] = stimuli["stimulus"].apply(lambda x: x[row:row+shape_center[0],col:col+shape_center[1]].sum()/nr_center *100)

    stimuli_attention = pd.read_json(attention_tests)
    stimuli_attention["stimulus"]= stimuli_attention["stimulus"].apply(lambda x: vec_is_red(np.array(x)).astype(int))
    # stimuli_attention["center_stimulus"] = stimuli_attention["stimulus"].apply(lambda x: np.hsplit(x,np.array([4,9]))[1])
    stimuli_attention["center_prob"] = stimuli_attention["stimulus"].apply(lambda x: x[row:row+shape_center[0],col:col+shape_center[1]].sum()/nr_center *100)

    stimuli = pd.concat([stimuli,stimuli_attention])    
    
    return stimuli


# estimate empirical utility of each agent in each level
def compute_utility(df_utility, decision_maker, prob_name, sample, compute_prob=False):
    if compute_prob:
        df_helper = df_utility.pivot_table(
                        columns=[prob_name,'AI_conf'], aggfunc='mean', values="true_prob",dropna=False).unstack().reset_index().fillna(value=0).rename(columns={0:'Prob '+decision_maker})
        #drop column level_2
        df_helper.drop("level_2", inplace=True, axis=1)
        # print(df_humanAI)
        df_utility = df_utility.join(df_helper.set_index([prob_name,"AI_conf"]), on=[prob_name,"AI_conf"])
        prob_name = "Prob "+decision_maker
        
    df_utility["Decision "+ decision_maker] = df_utility[prob_name]>50
    
    df_utility["Utility "+ decision_maker] = df_utility["Decision "+ decision_maker]*df_utility["true_prob"] + (1-df_utility["Decision "+ decision_maker])*(100-df_utility["true_prob"])
    
    print("Utility "+ decision_maker+": ", df_utility["Utility "+ decision_maker].mean())
    print("Utility "+ decision_maker+" sample: ", df_utility.loc[sample,"Utility "+ decision_maker].mean())

    if compute_prob:
        df_utility["Decision "+ decision_maker+" max"] = df_utility.apply(lambda x: df_utility[ df_utility["AI_conf"]==x["AI_conf"]]["Decision "+ decision_maker ].max() , axis=1)
        df_utility["Decision "+ decision_maker+" min"] = df_utility.apply(lambda x: df_utility[ (df_utility["AI_conf"]==x["AI_conf"]) & (df_utility[prob_name]!=0)]["Decision "+ decision_maker ].min() , axis=1)

        df_utility["Utility "+ decision_maker +" max"] = df_utility["Decision "+ decision_maker+" max"]*df_utility["true_prob"] + (1-df_utility["Decision "+ decision_maker+" max"])*(100-df_utility["true_prob"])
        df_utility["Utility "+ decision_maker + " min"] = df_utility["Decision "+ decision_maker+" min"]*df_utility["true_prob"] + (1-df_utility["Decision "+ decision_maker+" min"])*(100-df_utility["true_prob"])

        print("Utility "+ decision_maker+" max: ", df_utility["Utility "+ decision_maker+" max"].mean())
        print("Utility "+ decision_maker+" min: ", df_utility["Utility "+ decision_maker+" min"].mean())
        print("Utility "+ decision_maker+" sample max: ", df_utility.loc[sample,"Utility "+ decision_maker+" max"].mean())
        print("Utility "+ decision_maker+" sample min: ", df_utility.loc[sample,"Utility "+ decision_maker+" min"].mean())

def estimated_utility(stimuli):
    df_utility = stimuli[["dm_conf","AI_conf","center_prob","true_prob"]].copy()
    
    sample = np.random.choice(df_utility.index, 17)
    for i in range(100):
        sample = np.concatenate((sample, np.random.choice(df_utility.index, 17)))

    compute_utility(df_utility, "Best", "true_prob", sample, compute_prob=False)
    compute_utility(df_utility, "AI", "AI_conf", sample, compute_prob=False)
    compute_utility(df_utility, "Human", "center_prob", sample, compute_prob=False)
    compute_utility(df_utility, "Human+AI", "dm_conf", sample, compute_prob=True)
    # compute_utility(df_utility, "Human+AI nondiscrete", "center_prob", sample, compute_prob=True)