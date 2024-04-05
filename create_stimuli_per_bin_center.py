import json
import numpy as np
from pickle import FALSE, TRUE

np.random.seed(4203)
total_count = 104
total_red_count = 52
nr_total = 52
ai_total = 13
shape = (4,13)
nr_center = 20
center_bias=1/10

# stimuli with most instances in 4-9 bin
stimuli_per_bin = {0:0, 1:15, 2:30, 3:45, 4:270, 5:270, 6:270, 7:270, 8:270, 9:270, 10:45, 11:30, 12:15, 13:0}
var_per_bin = {0:0, 1:3, 2:6, 3:6, 4:8, 5:10, 6:10, 7:10, 8:10, 9:8, 10:6, 11:6, 12:3, 13:0}
print(stimuli_per_bin)

def get_AI_conf(ai_reds):
    return round(ai_reds/ai_total * 100)

def get_grid(array,reds, prob_red):
    prob_black = 1- prob_red
    center = np.random.choice(array, nr_center, replace = False, p=np.concatenate((np.full(reds, prob_red/reds), np.full(nr_total-reds, prob_black/(nr_total-reds)))))
    center_grid = center.reshape((4,round(nr_center/4))) 
    
    hidden = np.repeat('img/img_card_back.png', 16)
    hidden = hidden.reshape((4,4))
    center_grid = np.concatenate((hidden,center_grid,hidden), axis=1)

    # # remove non center cards
    # values_array, counts_array = np.unique(array, return_counts=True)
    # values_center, counts_center = np.unique(center, return_counts=True) 
    # none_center = np.setdiff1d(array, center)
    # one_center = values_center[counts_center==1]
    # one_array = values_array[counts_array==1]
    # two_array = values_array[counts_array==2]
    # one_rest = np.concatenate((np.intersect1d(none_center, one_array),np.intersect1d(one_center, two_array)))
    # two_rest = np.tile(np.intersect1d(none_center, two_array),2)
    # rest = np.concatenate((one_rest,two_rest))
    # np.random.shuffle(rest)
    # rest_grid = rest.reshape((4,8))
    # rest_list = np.split(rest_grid, 2, axis=1)
    # return np.concatenate((rest_list[0],center_grid,rest_list[1]), axis=1)
    return center_grid

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

def create_stimulus(id, batch, nr_reds, nr_ai_reds, reds, blacks, shuffle=TRUE):
    
    if (nr_reds in [0, nr_total]): shuffle=False
    array_red = np.random.choice(reds, nr_reds, replace = False) 
    array_black = np.random.choice(blacks, nr_total-nr_reds, replace = False)

    array = np.concatenate([array_red, array_black])
    # ai_reds =  sum([ 1 for card in np.random.choice(array, ai_total, replace = False) if any(substring in card for substring in ["hearts","diamonds"])])
    hidden = np.repeat('img/img_card_back.png', 16)
    hidden = hidden.reshape((4,4))
    grid=array
    if shuffle==TRUE:
        grid_random = np.random.permutation(array).reshape(shape)[:,4:9]
        grid_random = np.concatenate((hidden, grid_random,hidden), axis=1)
        # print(grid_random.size)
        # make the placement random 
        if (nr_reds <= nr_ai_reds*4+1) and (nr_reds >= nr_ai_reds*4-1):
            grid_hard = grid_random
            grid_easy = grid_random
        elif nr_reds > nr_ai_reds*4+1:
            grid_hard = get_grid(array, nr_reds, prob_red=center_bias)
            grid_easy = get_grid(array, nr_reds, prob_red=1-center_bias)
        elif nr_reds < nr_ai_reds*4-1:
            grid_hard = get_grid(array, nr_reds, prob_red=1-center_bias)
            grid_easy = get_grid(array, nr_reds, prob_red=center_bias)
    else:
        return create_stimulus_dict(id, batch,np.concatenate((hidden, grid.reshape(shape)[:,4:9],hidden), axis=1), array, nr_reds, nr_ai_reds)
        # return create_stimulus_dict(id, batch, grid.reshape(shape)[:,4:9], array, nr_reds, nr_ai_reds)
    
    return (create_stimulus_dict(id, batch, grid_hard, array, nr_reds, nr_ai_reds),
            create_stimulus_dict(id, batch, grid_random, array, nr_reds, nr_ai_reds),
            create_stimulus_dict(id, batch, grid_easy, array, nr_reds, nr_ai_reds))

def create_stimulus_per_bin(reds, blacks):

    stimuli_list =[]
    id_offset=0
    for nr_ai_reds in range(0,14):
        max_var = 3*min(nr_ai_reds,13-nr_ai_reds)
        var = min(var_per_bin[nr_ai_reds], max_var)
        print(4*nr_ai_reds-var, 4*nr_ai_reds+var)

        bin_stimuli=[]
        # for id, nr_reds in enumerate(np.random.randint(4*nr_ai_reds-var, 4*nr_ai_reds+var+1, stimuli_per_bin[nr_ai_reds])):
        #change for to have wider range per bin
        rexp=4*nr_ai_reds
        rmin =4*nr_ai_reds-var
        rmax =4*nr_ai_reds+var
        # full_var
        # choices = np.concatenate((np.arange(rmin,rmin+var), np.arange(rexp,rexp+1), np.arange(rmax-var+1,rmax+1)), axis=None)
        # few choices
        low_choices = np.arange(rmin,rmin+3)
        mid_choices = np.arange(rexp-1,rexp+2)
        high_choices = np.arange(rmax-3+1,rmax+1)
        
        #avoid generating stimuli with true probability 50%
        if 26 in low_choices:
            ind = (low_choices==26).nonzero()[0][0]
            print(ind)
            low_choices[ind] =26+3
            high_choices[2-ind] =high_choices[2-ind]-3
        if 26 in high_choices:
            ind = (high_choices==26).nonzero()[0][0]
            print(ind)
            low_choices[2-ind] =low_choices[2-ind]+3
            high_choices[ind] =26-3
        if 26 in mid_choices:
            ind = (mid_choices==26).nonzero()
            print(ind)
        
        weights= np.full(9,1/9)
        # if nr_ai_reds in [5,6,7,8]:
        if nr_ai_reds in [4,5,6,7,8,9]:
            weights=[4/9*1/3, 4/9*1/3, 4/9*1/3, 1/9*1/3, 1/9*1/3, 1/9*1/3, 4/9*1/3, 4/9*1/3, 4/9*1/3]
            # weights=[1/2*1/3, 1/2*1/3, 1/2*1/3, 0*1/3, 0*1/3, 0*1/3, 1/2*1/3, 1/2*1/3, 1/2*1/3]

        choices = np.concatenate((low_choices, mid_choices, high_choices), axis=None)
        for id, nr_reds in enumerate(np.random.choice(choices, stimuli_per_bin[nr_ai_reds],replace = True, p=weights)):
            stimuli = create_stimulus(id_offset + id, "game", int(nr_reds),nr_ai_reds, reds, blacks)
            bin_stimuli.append(stimuli)

        id_offset +=len(bin_stimuli)
        stimuli_list += bin_stimuli

    # print(stimuli_list[1])
    # print ([ stimuli[0] for stimuli in stimuli_list][1])
    return ([ stimuli[0] for stimuli in stimuli_list],[ stimuli[1] for stimuli in stimuli_list], [ stimuli[2] for stimuli in stimuli_list])

def write_json_to_file(json_object, filename):
    with open(filename, "w") as outfile:
        outfile.write(json_object)

def create_all_stimuli():
# def main():
    
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
    quarter_grid = create_stimulus(-3,"attention",int(3 * nr_total/4),round(3 * ai_total/4 + np.random.randint(-1, 1)), reds, blacks, shuffle=FALSE)
    half_grid = create_stimulus(-4,"attention",int(nr_total/2),round(ai_total/2), reds, blacks, shuffle=FALSE)

    write_json_to_file(json.dumps([red_grid, black_grid, quarter_grid, half_grid], indent=4), "./materials/attention_tests.json")
    stimuli_hard, stimuli_random, stimuli_easy = create_stimulus_per_bin(reds, blacks)
    write_json_to_file(json.dumps(stimuli_hard, indent=4), "./materials/stimuli_hard.json")
    write_json_to_file(json.dumps(stimuli_random, indent=4), "./materials/stimuli_random.json")
    write_json_to_file(json.dumps(stimuli_easy, indent=4), "./materials/stimuli_easy.json")

    stimuli_easy = json.dumps(stimuli_easy, indent=4)
    stimuli_hard = json.dumps(stimuli_hard, indent=4) 
    stimuli_random = json.dumps(stimuli_random, indent=4)
    attention = json.dumps([red_grid, black_grid, quarter_grid, half_grid], indent=4)
    return stimuli_hard, stimuli_random, stimuli_easy, attention

# if __name__ == "__main__":
#     main()