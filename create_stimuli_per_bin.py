import json
import numpy as np
from pickle import FALSE, TRUE
import pandas as pd
from scipy.stats import hypergeom, nchypergeom_wallenius
from scipy.optimize import linprog
from helper import *

#parameters
rng = np.random.default_rng(42)
total_count = 156
total_red_count = 78
nr_total = 65
ai_total = 13
mult= 5
shape = (5,13)
shape_center = (3,7)
row = (shape[0]-shape_center[0])//2
col = (shape[1]-shape_center[1])//2
nr_center = 21
center_odds=1
center_odds_other= 5
total_stimuli = 1000

# stimuli with most instances in 4-9 bin
var_per_bin = {0:0, 1:5, 2:8, 3:9, 4:9, 5:10, 6:9, 7:9, 8:10, 9:9, 10:9, 11:8, 12:5, 13:0}

# returns AI confidence in terms of percentage
def get_AI_conf(ai_reds):
    return round(ai_reds/ai_total * 100)

# returns bias for sampling in terms of odds
def bias(nr_reds, nr_ai_reds, level):
    if level=="random" or ((nr_reds <= nr_ai_reds*mult+1) and (nr_reds >= nr_ai_reds*mult-1)):
        return 1
    elif nr_reds > nr_ai_reds*mult+1:
        if level=="hard":
            return center_odds/center_odds_other
        else:
            return center_odds_other/center_odds
    elif nr_reds < nr_ai_reds*mult-1:
        if level=="hard":
            return center_odds_other/center_odds
        else:
            return center_odds/center_odds_other

#returns utility of best decision (according to the true probability)
def get_utility_best(reds):
    util_red = reds /nr_total * int(reds>nr_total/2) 
    util_black = (1- reds /nr_total) * int(reds<=nr_total/2) 
    return util_red + util_black

#returns utility of AI 
def get_utility_AI(ai_reds, reds):
    util_red = reds /nr_total * int(ai_reds>=ai_total//2+1) 
    util_black = (1- reds /nr_total) * int(ai_reds<=ai_total//2) 
    return util_red + util_black

# returns perceived utility of human decision maker according to a (wallenius) hypergeometric distribution
def get_utility_human(reds, odds):
    util_red = reds /nr_total * (1-nchypergeom_wallenius.cdf(nr_center//2, nr_total, reds, nr_center, odds=odds)) 
    util_black = (1- reds /nr_total) * (nchypergeom_wallenius.cdf(nr_center//2, nr_total, reds, nr_center,odds=odds))

    return util_red + util_black
    
#compute the proportion of each cell in each level under the given constraints
def get_proportions(df_bins):

    #Equality constraints

    #compute bias for each bin in each level
    df_bins["bias_hard"] = df_bins.apply(lambda x: bias(x['true_reds'], x["AI_reds"], "hard"), axis=1)
    df_bins["bias_easy"] = df_bins.apply(lambda x: bias(x["true_reds"], x["AI_reds"], "easy"), axis=1)

    #compute utility for each agent in each level
    df_utility = df_bins.copy()
    df_utility["best_all"] = df_bins[["true_reds"]].apply(lambda x: get_utility_best(x["true_reds"]),axis=1)
    df_utility["AI_all"] = df_bins[["true_reds","AI_reds"]].apply(lambda x: get_utility_AI(x["AI_reds"],x["true_reds"]),axis=1)

    df_utility["Human_random"] = df_bins[["true_reds","bias_hard"]].apply(lambda x: get_utility_human(x["true_reds"], 1), axis =1) 
    df_utility["Human_hard"] = df_bins[["true_reds","bias_hard"]].apply(lambda x: get_utility_human(x["true_reds"], x["bias_hard"]), axis =1)
    df_utility["Human_easy"] = df_bins[["true_reds","bias_easy"]].apply(lambda x: get_utility_human(x["true_reds"], x["bias_easy"]), axis =1)

    #construct utility constraint matrix
    Best_util = df_utility["best_all"].to_numpy()
    AI_util =df_utility["AI_all"].to_numpy()

    DM_hard_util = df_utility["Human_hard"].to_numpy()
    DM_random_util = df_utility["Human_random"].to_numpy()
    DM_easy_util = df_utility["Human_easy"].to_numpy()
    Zero = np.zeros(Best_util.size)
    

    Util_A_eq = np.array([np.concatenate((Best_util,Zero,-Best_util)),
                        np.concatenate((Best_util,-Best_util,Zero)), 
                        np.concatenate((AI_util,Zero,-AI_util)),
                        np.concatenate((AI_util,-AI_util,Zero)), 
                        np.concatenate((DM_hard_util,Zero,-DM_easy_util))])    


    #construct symmetry constraint matrix
    pad_front = 0
    length = 3*Zero.size - 9
    new_array = [] 
    for _ in range(0,36): 
        pad_back = length - pad_front
        new_array += [np.concatenate((np.zeros(pad_front), np.array([1,0,0,0,0,0,0,0,-1]), np.zeros(pad_back)))]
        new_array += [np.concatenate((np.zeros(pad_front), np.array([0,1,0,0,0,0,0,-1,0]), np.zeros(pad_back)))]
        new_array += [np.concatenate((np.zeros(pad_front), np.array([0,0,1,0,0,0,-1,0,0]), np.zeros(pad_back)))]
        new_array += [np.concatenate((np.zeros(pad_front), np.array([0,0,0,1,0,-1,0,0,0]), np.zeros(pad_back)))]
        pad_front += 9
        
    Symmetry_A_eq = np.array(new_array)

    # #construct calibration constraint matrix
    # pad_front = 0
    # length = 3*Zero.size - 9
    # new_array = []
    # new_y = []
    # for i in range(0,12): 
    #     ind = i*9
    #     pad_front = ind
    #     pad_back = length - pad_front
    #     new_array += [np.concatenate((np.zeros(pad_front), df_bins.loc[ind:(ind+8)]["true_reds"].to_numpy(), np.zeros(pad_back)))]
    #     new_array += [np.concatenate((np.zeros(108+pad_front), df_bins.loc[ind:(ind+8)]["true_reds"].to_numpy(), np.zeros(pad_back-108)))]
    #     new_array += [np.concatenate((np.zeros(2*108+pad_front), df_bins.loc[ind:(ind+8)]["true_reds"].to_numpy(), np.zeros(pad_back-2*108)))]
    #     new_y += [df_bins.loc[ind]["AI_reds"]/13, df_bins.loc[ind]["AI_reds"]/13, df_bins.loc[ind]["AI_reds"]/13]
    
    # Calibration_A_eq = np.array(new_array)
    # Cal_y_eq = np.array(new_y)

    #construct Sum = 1 constraint matrix
    Sum_hard_A_eq = np.concatenate((np.ones(12*9), np.zeros(df_utility["Human_random"].size + df_utility["Human_easy"].size )))
    Sum_random_A_eq = np.concatenate((np.zeros(df_utility["Human_hard"].size),np.ones(12*9),np.zeros(df_utility["Human_easy"].size )))
    Sum_easy_A_eq = np.concatenate((np.zeros(df_utility["Human_hard"].size + df_utility["Human_random"].size ),np.ones(12*9) ))

    #concatenate equality constraint matrix and vector
    constraints = np.concatenate((Util_A_eq, Symmetry_A_eq, Sum_hard_A_eq.reshape(1,-1), Sum_random_A_eq.reshape(1,-1), Sum_easy_A_eq.reshape(1,-1)), axis=0)
    y = np.concatenate((np.zeros(5+4*36), np.array([1,1,1])))

    #Inequality constraint
    #constrain the minimum and maximum size of bins
    pad_front = 18
    length = Zero.size - 9
    new_array = [] 
    for _ in range(18,90,9): 
        pad_back = length - pad_front
        new_array += [np.concatenate((np.zeros(pad_front), np.array([1,1,1,0,0,0,1,1,1]), np.zeros(pad_back)))]
        new_array += [np.concatenate((np.zeros(pad_front), np.array([0,0,0,-1,-1,-1,0,0,0]), np.zeros(pad_back)))]
        pad_front += 9

    min_size = np.array(new_array)
    Min_size_hard_A_ub = np.concatenate((min_size, np.zeros((2*8, 2*df_utility["Human_hard"].size))), axis=1)
    Min_size_random_A_ub = np.concatenate(( np.zeros((2*8, df_utility["Human_hard"].size)),min_size, np.zeros((2*8,df_utility["Human_hard"].size))), axis=1)
    Min_size_easy_A_ub = np.concatenate(( np.zeros((2*8, 2*df_utility["Human_hard"].size)), min_size), axis=1)

    #concatenate inequality constraint matrix and vector
    ub_constraints = np.concatenate((Min_size_hard_A_ub, Min_size_random_A_ub, Min_size_easy_A_ub), axis=0)
    y_ub = np.tile([0.1,-0.03],3*8)

    #construct objective vector, maximizing the difference between utilitz of agents
    c = np.concatenate((AI_util-DM_hard_util, AI_util-DM_random_util, Best_util-AI_util))

    #solve linear program
    solve=linprog(-c, A_eq=constraints, b_eq=y, A_ub=-ub_constraints, b_ub = -y_ub, bounds=(0.0,1))

    print("Get bins probabilities successful: ", solve.success)


    df_weights = pd.DataFrame({"hard": solve.x[0:108], "random": solve.x[108:216], "easy": solve.x[216:324]}) 
    
    # print expected utilities of each agent in each level
    print("Best hard", df_weights["hard"]@Best_util)
    print("AI hard", df_weights["hard"]@AI_util)
    print("Human hard", df_weights["hard"]@DM_hard_util)
    print()
    print("Best random", df_weights["random"]@Best_util)
    print("AI random", df_weights["random"]@AI_util)
    print("Human random", df_weights["random"]@DM_random_util)
    print()
    print("Best easy", df_weights["easy"]@Best_util)
    print("AI easy", df_weights["easy"]@AI_util)
    print("Human easy", df_weights["easy"]@DM_easy_util)
    print()

    return df_weights

#sample shown cards and create a grid with hidden and shown cards
#input array: array of cards, reds: number of red cards, odds: bias for sampling
def get_grid(array, reds, odds):
    #sample number of reds in shown cards according to a (wallenius) hypergeometric distribution
    r_center = nchypergeom_wallenius.rvs(nr_total, reds, nr_center, odds=odds, size=1)[0]
    #get red cards from the front of array
    center_array = array[:r_center]
    #get black cards from the back of array
    if center_array.size != nr_center:
        center_array = np.concatenate((center_array, array[(-nr_center+r_center):]))
    #permute shown cards and create grid
    center_grid = rng.permutation(center_array).reshape(shape_center) 
    #add hidden cards around shown cards
    full_grid = np.repeat('img/img_card_back.png', nr_total).reshape(shape).astype('<U40')
    full_grid[row:row+shape_center[0], col:col+shape_center[1]] = center_grid
    #check if the number of red cards in the grid is correct
    if (vec_is_red(full_grid).sum()!=r_center):
        print("Error")

    return full_grid

#create stimulus dictionary for json file
def create_stimulus_dict(id, batch, grid, array, nr_reds, nr_ai_reds):
    return {
        "id": id,
        "batch": batch,
        "stimulus": grid.tolist(),
        "cards": array.tolist(),
        "nr_reds": nr_reds,
        "nr_total": nr_total,
        "AI_reds": nr_ai_reds,
        "AI_total": ai_total,
        "AI_conf": get_AI_conf(nr_ai_reds)
    }

# create a stimulus for given number of reds and level
def create_stimulus(id, batch, nr_reds, nr_ai_reds, reds, blacks, shuffle=TRUE, level="hard"):
    
    #get red and black cards according to number of reds in stimulus
    array_red = rng.choice(reds, nr_reds, replace = False) 
    array_black = rng.choice(blacks, nr_total-nr_reds, replace = False)

    #array of stimulus cards' name
    array = np.concatenate([array_red, array_black])

    #grid for attention stimulus
    if (nr_reds in [0, nr_total]): shuffle=False
    if shuffle==FALSE:
        full_grid = np.repeat('img/img_card_back.png', nr_total).reshape(shape).astype('<U40')
        full_grid[row:row+shape_center[0], col:col+shape_center[1] ] = array.reshape(shape)[row:row+shape_center[0], col:col+shape_center[1]]
        return create_stimulus_dict(id, batch,full_grid, array, nr_reds, nr_ai_reds)

    #generate grid for level sampling shown cards according to odds
    if level=="easy":
        if (nr_reds <= nr_ai_reds*mult+1) and (nr_reds >= nr_ai_reds*mult-1):
            grid_easy = get_grid(array, nr_reds, odds= 1)
        elif nr_reds > nr_ai_reds*mult+1:
            grid_easy = get_grid(array, nr_reds, odds=center_odds_other/center_odds)
        elif nr_reds < nr_ai_reds*mult-1:
            grid_easy = get_grid(array, nr_reds, odds=center_odds/center_odds_other)
        return create_stimulus_dict(id, batch, grid_easy, array, nr_reds, nr_ai_reds)
    elif level=="hard":
        if (nr_reds <= nr_ai_reds*mult+1) and (nr_reds >= nr_ai_reds*mult-1):
            grid_hard = get_grid(array, nr_reds, odds= 1)
        elif nr_reds > nr_ai_reds*mult+1:
            grid_hard = get_grid(array, nr_reds, odds=center_odds/center_odds_other)
        elif nr_reds < nr_ai_reds*mult-1:
            grid_hard = get_grid(array, nr_reds, odds=center_odds_other/center_odds)
        return create_stimulus_dict(id, batch, grid_hard, array, nr_reds, nr_ai_reds)
    else:
        grid_random = get_grid(array, nr_reds, odds=1)
        return create_stimulus_dict(id, batch, grid_random, array, nr_reds, nr_ai_reds)

# create a list of stimuli for each bin
def create_stimulus_per_bin(reds, blacks):

    ai_bin = []
    true_bin = []
    #for each AI bin create nine cells, three around the given AI confidence, six around the given AI confidence +- variance of AI bin
    for nr_ai_reds in range(1,13):
        # max variance per bin
        max_var = (mult-1)*min(nr_ai_reds,13-nr_ai_reds)
        # minimum of max and given variance
        var = min(var_per_bin[nr_ai_reds], max_var)

        # compute center of the three kinds of cells
        rexp =mult*nr_ai_reds
        rmin =mult*nr_ai_reds-var
        rmax =mult*nr_ai_reds+var

        #create three cells around each center, nine cells in total
        low_choices = np.arange(rmin,rmin+3)
        mid_choices = np.arange(rexp-1,rexp+2)
        high_choices = np.arange(rmax-3+1,rmax+1)

        #add created cells in this bin to the list of cells
        ai_bin += np.full(9,nr_ai_reds).tolist()
        true_bin += np.concatenate((low_choices, mid_choices, high_choices), axis=None).tolist()

    #get cells probabilities for each level
    df_bins = pd.DataFrame({'AI_reds': ai_bin, "true_reds": true_bin})
    df_weights = get_proportions(df_bins)
    
    #generate stimuli in each cell proportional to cell probabilities
    stimuli_list ={"hard": [], "random": [], "easy": []}
    id_offset={"hard": 0, "random": 0, "easy": 0}

    for level in ["hard", "random", "easy"]:
        bin_stimuli=[]
        choices = df_bins
        weights = df_weights[level].values

        #sample cell and generate stimulus according to cell properties
        for id, index in enumerate(rng.choice(np.arange(0,108), total_stimuli, replace = True, p=weights/weights.sum())):
            stimuli = create_stimulus(id_offset[level] + id, "game", int(choices.loc[index]["true_reds"]),choices.loc[index]["AI_reds"], reds, blacks, level=level)
            bin_stimuli.append(stimuli)

        id_offset[level] +=len(bin_stimuli)
        stimuli_list[level] += bin_stimuli

    return (stimuli_list["hard"], stimuli_list["random"], stimuli_list["easy"])

#writes stimuli to json file
def write_json_to_file(json_object, filename):
    with open(filename, "w") as outfile:
        outfile.write(json_object)

def create_all_stimuli():

    # Opening JSON file
    f = open('./materials/cards.json')
    
    # returns JSON object as a dictionary
    cards = json.load(f)
    # triple the amount of cards (three standard decks)
    cards = cards + cards + cards
    # filter red and black cards
    reds = [ card for card in cards if any(substring in card for substring in ["hearts","diamonds"])]
    blacks = [ card for card in cards if any(substring in card for substring in ["clubs","spades"])]

    # create attention stimuli
    red_grid = create_stimulus(-1,"attention",nr_total, ai_total, reds, blacks, shuffle=FALSE)
    black_grid = create_stimulus(-2,"attention",0, 0, reds, blacks, shuffle=FALSE)
    quarter_grid = create_stimulus(-3,"attention",int((mult-2) * nr_total/5),round((mult-2) * ai_total/5 + rng.integers(-1, 1)), reds, blacks, shuffle=FALSE)
    half_grid = create_stimulus(-4,"attention",round(nr_total/2),round(ai_total/2), reds, blacks, shuffle=FALSE)

    # create level stimuli
    stimuli_hard, stimuli_random, stimuli_easy = create_stimulus_per_bin(reds, blacks)

    # create json from dictionary
    stimuli_easy = json.dumps(stimuli_easy, indent=4)
    stimuli_hard = json.dumps(stimuli_hard, indent=4) 
    stimuli_random = json.dumps(stimuli_random, indent=4)
    attention = json.dumps([red_grid, black_grid, quarter_grid, half_grid], indent=4)

    # print estimated utilities
    conf_levels = ["very low", "low", "high", "very high","very high"]

    df_center_responses_hard = get_responses(stimuli_hard, attention,row, col, shape_center, nr_center )  
    df_center_responses_hard = discretize_confidence(df_center_responses_hard, conf_levels) 
    df_center_responses_hard["true_prob"] = df_center_responses_hard["nr_reds"]/df_center_responses_hard["nr_total"]*100

    df_center_responses_random = get_responses(stimuli_random, attention,row, col, shape_center, nr_center )  
    df_center_responses_random = discretize_confidence(df_center_responses_random, conf_levels) 
    df_center_responses_random["true_prob"] = df_center_responses_random["nr_reds"]/df_center_responses_random["nr_total"]*100

    df_center_responses_easy = get_responses(stimuli_easy, attention,row, col, shape_center, nr_center )  
    df_center_responses_easy = discretize_confidence(df_center_responses_easy, conf_levels) 
    df_center_responses_easy["true_prob"] = df_center_responses_easy["nr_reds"]/df_center_responses_easy["nr_total"]*100

    print("Level Hard")
    estimated_utility(df_center_responses_hard)

    print("Level Random")
    estimated_utility(df_center_responses_random)

    print("Level Easy")
    estimated_utility(df_center_responses_easy)

    # write stimuli to json files
    write_json_to_file(stimuli_hard, "./materials/stimuli_hard.json")
    write_json_to_file(stimuli_random, "./materials/stimuli_random.json")
    write_json_to_file(stimuli_easy, "./materials/stimuli_easy.json")
    write_json_to_file(attention, "./materials/attention_tests.json")

    return stimuli_hard, stimuli_random, stimuli_easy, attention

def main():
    create_all_stimuli()

if __name__ == "__main__":
    main()