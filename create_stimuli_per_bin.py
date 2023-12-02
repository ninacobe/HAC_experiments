import json
from pickle import FALSE, TRUE
from re import I
import pandas as pd
import numpy as np
import math

np.random.seed(4203)
total_count = 104
total_red_count = 52
nr_total = 52
ai_total = 13
shape = (4,13)
nr_center = 20

def get_AI_conf(ai_reds):
    return round(ai_reds/ai_total * 100)

# TO DO:
#  create #2 and #3 stimuli
#  manually define and set number of stimuli per bin as array


def get_grid(array,reds, prob_red):
    prob_black = 1- prob_red
    center = np.random.choice(array, nr_center, replace = False, p=np.concatenate((np.full(reds, prob_red/reds), np.full(nr_total-reds, prob_black/(nr_total-reds)))))
    values_array, counts_array = np.unique(array, return_counts=True)
    values_center, counts_center = np.unique(center, return_counts=True) 
    none_center = np.setdiff1d(array, center)
    one_center = values_center[counts_center==1]
    one_array = values_array[counts_array==1]
    two_array = values_array[counts_array==2]
    one_rest = np.concatenate((np.intersect1d(none_center, one_array),np.intersect1d(one_center, two_array)))
    two_rest = np.tile(np.intersect1d(none_center, two_array),2)
    rest = np.concatenate((one_rest,two_rest))
    np.random.shuffle(rest)
    center_grid = center.reshape((4,5)) 
    rest_grid = rest.reshape((4,8))
    rest_list = np.split(rest_grid, 2, axis=1)
    return np.concatenate((rest_list[0],center_grid,rest_list[1]), axis=1)

def create_stimulus_per_bin(reds, blacks):
    
    stimuli = []
    id_offset=0
    for nr_ai_reds in range(0,14):
        max_var = 3*min(nr_ai_reds,13-nr_ai_reds)
        var = min(12, max_var)
        print(4*nr_ai_reds-var, 4*nr_ai_reds+var)
        bin_stimuli = [create_stimulus(id_offset + id, "game", int(nr_reds),nr_ai_reds, reds, blacks) for id, nr_reds in enumerate(np.random.randint(4*nr_ai_reds-var, 4*nr_ai_reds+var+1, (5*max_var*10)+1))]
        id_offset +=len(bin_stimuli)
        stimuli +=bin_stimuli

    return stimuli


def create_stimulus(id, batch, nr_reds, nr_ai_reds, reds, blacks, shuffle=TRUE):

    if (nr_reds in [0, nr_total]): shuffle=False
    array_red = np.random.choice(reds, nr_reds, replace = False) 
    array_black = np.random.choice(blacks, nr_total-nr_reds, replace = False)

    array = np.concatenate([array_red, array_black])
    # ai_reds =  sum([ 1 for card in np.random.choice(array, ai_total, replace = False) if any(substring in card for substring in ["hearts","diamonds"])])
    grid=array
    if shuffle==TRUE:
        true_prob = round(nr_reds/nr_total * 100)
        ai_conf = get_AI_conf(nr_ai_reds)
        if true_prob >= ai_conf:
            grid = get_grid(array, nr_reds, prob_red=1/5)
        if true_prob < ai_conf: 
            grid = get_grid(array, nr_reds, prob_red=4/5) 
    else:
        grid = array.reshape(shape)


    # Data to be written
    stimulus = {
        "id":   id,
        "batch": batch,
        "stimulus": grid.tolist(),
        "cards": array.tolist(),
        "nr_reds": nr_reds,
        "nr_total": nr_total,
        "AI_reds": nr_ai_reds,
        "AI_total": ai_total,
        "AI_conf": get_AI_conf(nr_ai_reds)
    }
    return stimulus

def main():

    # Opening JSON file
    f = open('./materials/cards.json')
    
    # returns JSON object as
    # a dictionary
    cards = json.load(f)
    cards = cards + cards
    reds = [ card for card in cards if any(substring in card for substring in ["hearts","diamonds"])]
    blacks = [ card for card in cards if any(substring in card for substring in ["clubs","spades"])]

    #properties = ["id", "batch", "stimulus", "cards", "nr_reds", "nr_total", "AI_conf", "AI_reds", "AI_total"]

    red_grid = create_stimulus(-1,"attention",nr_total, ai_total, reds, blacks, shuffle=FALSE)
    black_grid = create_stimulus(-2,"attention",0, 0, reds, blacks, shuffle=FALSE)
    quarter_grid = create_stimulus(-3,"attention",int(3 * nr_total/4),round(3 * ai_total/4 + np.random.randint(-3, 3)), reds, blacks, shuffle=FALSE)
    half_grid = create_stimulus(-4,"attention",int(nr_total/2),round(ai_total/2), reds, blacks, shuffle=FALSE)



    # Serializing json
    stimuli = create_stimulus_per_bin(reds, blacks)
    print("Number of created stimuli: ", len(stimuli))
    json_object = json.dumps(stimuli, indent=4) 
    # Writing to sample.json
    with open("./materials/stimuli.json", "w") as outfile:
        outfile.write(json_object)

    # Serializing json
    json_object = json.dumps([red_grid, black_grid, quarter_grid, half_grid], indent=4)
    # Writing to sample.json
    with open("./materials/attention_tests.json", "w") as outfile:
        outfile.write(json_object)

if __name__ == "__main__":
    main()