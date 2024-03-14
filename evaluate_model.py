import json
from pickle import FALSE, TRUE
from re import I
import pandas as pd
import numpy as np
import math
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
from mpl_toolkits.axes_grid1 import ImageGrid

def show_grid(images):
    # fig = plt.figure(figsize=(15, 10))
    # grid = ImageGrid(fig, 111,  # similar to subplot(111)
    #              nrows_ncols=(4, 13),  # creates 2x2 grid of axes
    #              axes_pad=0.1,  # pad between axes in inch.
    #              )

    # for ax, im in zip(grid, images):
    #     # Iterating over the grid returns the Axes.
    #     img = mpimg.imread(im)
    #     ax.imshow(img)

    # plt.show()

    # Determine the layout of the grid
    grid_size = (4, 13)  # Change this to fit your needs

    fig, axs = plt.subplots(grid_size[0], grid_size[1], figsize=(10, 5))
    plt.subplots_adjust(wspace=0.1, hspace=0.1)

    for i, img_file in enumerate(images):
        # Read the image file
        img = mpimg.imread(img_file)

        # Plot the image in the grid
        axs[i // grid_size[1], i % grid_size[1]].imshow(img)
        axs[i // grid_size[1], i % grid_size[1]].axis('off')  # Hide the axis

    plt.tight_layout()
    plt.show()

def main():

    # Opening JSON file
    f = open('./materials/stimuli_hard.json')
    # returns JSON object as
    stimuli = json.load(f)

    f = open('./materials/stimuli_random.json')
    # returns JSON object as
    random_stimuli = json.load(f)

    f = open('./materials/stimuli_easy.json')
    # returns JSON object as
    easy_stimuli = json.load(f)

    # print(np.array(stimuli[1]["stimulus"]).flatten())

    show_grid(np.array(stimuli[500]["stimulus"]).flatten().tolist())
    show_grid(np.array(random_stimuli[500]["stimulus"]).flatten().tolist())
    show_grid(np.array(easy_stimuli[500]["stimulus"]).flatten().tolist())

    show_grid(np.array(stimuli[612]["stimulus"]).flatten().tolist())
    show_grid(np.array(random_stimuli[612]["stimulus"]).flatten().tolist())
    show_grid(np.array(easy_stimuli[612]["stimulus"]).flatten().tolist())   

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
    mwin_prob_list = [-(1- stimulus["nr_reds"]/stimulus["nr_total"]) for stimulus in stimuli if stimulus["AI_conf"] >= 50]
    mwin_prob_list += [ -(stimulus["nr_reds"]/stimulus["nr_total"]) for stimulus in stimuli if stimulus["AI_conf"] < 50]

    win_prob_list_perf = [ stimulus["nr_reds"]/stimulus["nr_total"] for stimulus in stimuli if stimulus["nr_reds"]/stimulus["nr_total"] >= 0.5]
    win_prob_list_perf += [ 1-(stimulus["nr_reds"]/stimulus["nr_total"]) for stimulus in stimuli if stimulus["nr_reds"]/stimulus["nr_total"] < 0.5]
    mwin_prob_list_perf = [ -(1-stimulus["nr_reds"]/stimulus["nr_total"]) for stimulus in stimuli if stimulus["nr_reds"]/stimulus["nr_total"] >= 0.5]
    mwin_prob_list_perf += [ -((stimulus["nr_reds"]/stimulus["nr_total"])) for stimulus in stimuli if stimulus["nr_reds"]/stimulus["nr_total"] < 0.5]

    print("Expected utility: ",(sum(win_prob_list))/len( win_prob_list))
    print("Expected utility: ",( sum(win_prob_list) + sum(mwin_prob_list ))/len( win_prob_list))
    print("Expected utility perf: ", (sum(win_prob_list_perf))/len( win_prob_list_perf))
    print("Expected utility perf: ", (sum(win_prob_list_perf) + sum(mwin_prob_list_perf))/len( win_prob_list_perf))
    print("Easy stimuli: ", easy_total)
    print("Hard stimuli: ", hard_total)
    # print("Hard stimuli: ", hard)

    true_prob = [ round((stimulus["nr_reds"]/stimulus["nr_total"])*100) for stimulus in stimuli] 
    model_conf = [ stimulus["AI_conf"] for stimulus in stimuli]  
    df = pd.DataFrame({'true_prob': true_prob, 'model_conf':model_conf })
    print(df.groupby(["model_conf"], as_index=False).count()["true_prob"]/df.shape[0])
    # sns.histplot(df, x="true_prob", y="model_conf", discrete=(False, True),  cbar=TRUE )
    sns.histplot(df, x="true_prob", y="model_conf", discrete=(True, True),  cbar=TRUE )
    plt.show()
    print(len(stimuli))

    human_conf = [ ] 
    for a,b in zip(true_prob, model_conf):
        if a<=b+100/13 and a>=b-100/13:
            human_conf.append('mid')
        if a < b-100/13:
            human_conf.append('high')
        if a > b+100/13:
            human_conf.append('low')
    df_bar = pd.DataFrame({'true_prob': true_prob, 'model_conf':model_conf , 'human_conf':human_conf})
    df_bar_count = df_bar.groupby(["human_conf","model_conf"], as_index=False).count() 
    print(df_bar_count)
    ax= sns.barplot(x='model_conf', y='true_prob', hue='human_conf', estimator=np.nanmean, errorbar=('ci', 90), errwidth=.2, capsize=.12, hue_order=[ "low", "mid", "high"], data=df_bar)
    for container, conf in zip(ax.containers, [ "low", "mid", "high"]):
        ax.bar_label(container, labels=df_bar_count[df_bar_count["human_conf"]==conf]["true_prob"], fmt='%.1f')
    plt.show()


    # print(df)
    ece = df.groupby(by=['model_conf'], as_index=False).mean()
    print(ece)
    print( "ECE:", abs(ece['model_conf']-ece['true_prob']).mean()/100)
    print( "MCE:", abs(ece['model_conf']-ece['true_prob']).max()/100)

    alpha= 0.1
    gamma = 1/3
    human_conf_val = 3.0
    eta = 0.1
    nr_datapoints = lambda x: human_conf_val/(alpha*alpha*x*gamma) * math.log(human_conf_val/(x*eta))
    nr_bins = np.arange(1,20)
    nr_stimuli = 17
    data =[nr_datapoints(1/x) for x in nr_bins]
    people =[round(nr_datapoints(1/x)/nr_stimuli) for x in nr_bins]
    df_bins = pd.DataFrame({'nr_bins': nr_bins, 'participants':people })
    sns.relplot(df_bins, x='nr_bins', y='participants')
    plt.show()
    print(round(nr_datapoints(1/6)/nr_stimuli))

if __name__ == "__main__":
    main()