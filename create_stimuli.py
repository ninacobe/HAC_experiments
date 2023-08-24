import json
from pickle import FALSE, TRUE
from re import I
import pandas as pd
import numpy as np
import math

np.random.seed(42)
total_count = 104
total_red_count = 52
nr_total = 52
ai_total = 32
shape = (4,13)

def get_AI_conf(ai_reds):
    ai_blacks = ai_total - ai_reds
    total_black_count = total_red_count
    remaining_pile_cards = nr_total - ai_total
    non_ai_count = total_black_count + total_red_count - ai_total
    prob_not_ai_cards = [math.comb(total_red_count - ai_reds, i)*math.comb(total_black_count - ai_blacks, remaining_pile_cards-i)/math.comb(non_ai_count,remaining_pile_cards)*i/remaining_pile_cards for i in np.arange(1,remaining_pile_cards+1, dtype=int)]
    return  round((ai_reds/nr_total + (1-ai_total/nr_total) * sum(prob_not_ai_cards)) * 100)

def create_stimulus(id, batch, nr_reds, reds, blacks, shuffle=TRUE):
    array_red = np.random.choice(reds, nr_reds) 
    array_black = np.random.choice(blacks, nr_total-nr_reds) 
    array = np.concatenate([array_red, array_black])
    if shuffle==TRUE:
        np.random.shuffle(array)
    grid = array.reshape(shape)
    ai_reds =  sum([ 1 for card in np.random.choice(array, ai_total) if any(substring in card for substring in ["hearts","diamonds"])])
    # Data to be written
    stimulus = {
        "id":   id,
        "batch": batch,
        "stimulus": grid.tolist(),
        "cards": array.tolist(),
        "nr_reds": nr_reds,
        "nr_total": nr_total,
        "AI_reds": ai_reds,
        "AI_total": ai_total,
        "AI_conf": get_AI_conf(ai_reds)
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

    red_grid = create_stimulus(0,"attention",nr_total, reds, blacks, shuffle=FALSE)
    half_grid = create_stimulus(1,"attention",int(nr_total/2), reds, blacks, shuffle=FALSE)
    black_grid = create_stimulus(2,"attention",0, reds, blacks, shuffle=FALSE)

    # Serializing json
    json_object = json.dumps([red_grid, half_grid, black_grid], indent=4)

    # Writing to sample.json
    with open("./materials/attention_tests.json", "w") as outfile:
        outfile.write(json_object)

    # Serializing json
    id_offset = 0
    easy_red_stimulus = [create_stimulus(id_offset + id,"game", int(nr_reds), reds, blacks) for id, nr_reds in enumerate(np.random.randint(round(nr_total * 0.70),round(nr_total * 0.90),50))]
    id_offset = len(easy_red_stimulus)
    easy_black_stimulus = [create_stimulus(id_offset + id,"game", int(nr_reds), reds, blacks) for id, nr_reds in enumerate(np.random.randint(round(nr_total * 0.10),round(nr_total * 0.30),50))]
    id_offset = len(easy_red_stimulus) + len(easy_black_stimulus)
    hard_stimulus = [create_stimulus(id_offset + id,"game", int(nr_reds), reds, blacks) for id, nr_reds in enumerate(np.random.randint(round(nr_total * 0.30),round(nr_total * 0.70),150))]
    json_object = json.dumps(easy_red_stimulus+easy_black_stimulus+hard_stimulus, indent=4) 

    # Writing to sample.json
    with open("./materials/stimuli.json", "w") as outfile:
        outfile.write(json_object)

if __name__ == "__main__":
    main()