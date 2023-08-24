/* initialize jsPsych */
var jsPsych = initJsPsych({
    show_progress_bar: true,
    auto_update_progress_bar: false,
    on_finish: function() {
        jsPsych.data.displayData();
        // jsPsych.data.get().ignore('internal_node_id').ignore('view_history').ignore('stimulus').ignore('failed_audio').ignore('failed_video').localSave('csv','mydata.csv');
    }
});

const EXPERIMENT_FILES = {  
    INSTRUCTIONS: 'materials/instructions.json',
    STIMULI: "materials/stimuli.json",
    ATTENTION_TESTS: "materials/attention_tests.json",
    CARDS: "materials/cards.json"
  };

var points = 0;
var image_size = [80,120]
var nr_trials = 1
var overall_trials =  5 * (2*nr_trials+1)+ 4 * (2*nr_trials+1)+ 11 + 5

var instructions = {};
var cards = {};
var stimuli = {};
var attention_tests = {};

/* function to draw card from game pile */
function randomDrawn(game_pile, decision){
    var card = jsPsych.randomization.sampleWithoutReplacement(game_pile, 1)[0];
    var earned = 0
    if (["hearts","diamonds"].some(v => card.includes(v))) {
        earned = 1 ;
    }else if (["clubs","spades"].some(v => card.includes(v))){
        earned = -1 ;
    }
    if (decision ==1 && earned ==1) {
        points += earned
        return "<p>Card Drawn:<br><br></p>"+`<img src=${card} width="130" height="100" class="center"></img>`
        +`<p><br>You <span class=\"orange\">WON</span> 1 point!<br><br>You have now ${points} point(s).<br><br></p>`;
    } else if (decision==1 && earned == -1){
        points += earned
        return "<p>Card Drawn:<br><br></p>"+`<img src=${card} width="130" height="100" class="center"></img>`
        + `<p><br>You <span class=\"orange\">LOST</span> 1 point!<br><br>You have now ${points} point(s).<br><br></p>`;
    } else if (earned ==1){
        return "<p>Card Drawn:<br><br></p>"+`<img src=${card} width="130" height="100" class="center"></img>`
        +`<p><br><span class=\"orange\">If you had played</span>, you would have WON 1 point!<br><br>You still have currently ${points} point(s).<br><br></p>`; 
    }
    return "<p>Card Drawn:<br><br></p>"+`<img src=${card} width="130" height="100" class="center"></img>`
    +`<p><br><span class=\"orange\">If you had played</span>, you would have LOST 1 point!<br><br>You still have currently ${points} point(s).<br><br></p>`; 
} 

/* create timeline */
var timeline = [];

/* preload card images */
await fetch(EXPERIMENT_FILES.CARDS).then(response => response.json()).then( data => cards = data)
var preload = {
    type: jsPsychPreload,
    images: cards,
    on_finish: function(data){
        jsPsych.setProgressBar(0);
    }
};
timeline.push(preload);

/* get instructions from file */
await fetch(EXPERIMENT_FILES.INSTRUCTIONS).then(response => response.json()).then( data => instructions = data)

/* get stimuli from file */
await fetch(EXPERIMENT_FILES.STIMULI).then(response => response.json()).then( data => stimuli = data)

/* get attention_tests from file */
await fetch(EXPERIMENT_FILES.ATTENTION_TESTS).then(response => response.json()).then( data => attention_tests = data)

/* display welcome messages */
timeline.push({
    type: jsPsychInstructions,
    pages: instructions.welcome, 
    show_clickable_nav: true,
    on_finish: function(data){
        jsPsych.setProgressBar(data.trial_index/overall_trials);
    }
});

var enter_fullscreen = {
    type: jsPsychFullscreen,
    fullscreen_mode: true,
    message: "<p>The experiment will switch to full screen mode when you press the button below.<br> Please do not exit full screen during the experiment.<br></p>",
    on_finish: function(data){
        jsPsych.setProgressBar(data.trial_index/overall_trials);
    }
  }
timeline.push(enter_fullscreen)
/* display introduction to experiment, i.e., game play */

/* Game Intro */
var grid_intro = attention_tests[0]

var intro = {
    type: jsPsychHtmlButtonResponse,
    stimulus: jsPsych.timelineVariable('intro'),
    choices: ['Next >'],
    data: {
        task: 'intro'
    },
    on_finish: function(data){
        jsPsych.setProgressBar(data.trial_index/overall_trials);
    } 
}; 

var game_pile_intro = {
    type: jsPsychHtmlButtonResponse,
    stimulus: function(){
        return instructions.game_intro.game_pile+jsPsychVslGridScene.generate_stimulus(grid_intro.stimulus, image_size)+"<p><br><br></p>"},
    stimulus_duration: 1500,
    trial_duration: 1800,
    save_trial_parameters: {stimulus_duration: true},
    choices: [],
    data: {
        task: 'stimulus_intro'
    },
};

var human_conf_intro = {
    type: jsPsychHtmlButtonResponse,
    stimulus: instructions.game_intro.human_conf,
    choices: ['very low','low', 'mid', 'high', 'very high'],
    data: {
        task: 'human_conf_intro',
        stimulus_id: grid_intro.id
    },
    on_finish: function(data){
        data.human_conf = ['very low','low', 'mid', 'high', 'very high'].at(data.response);
    }
};

var decision_intro = {
    type: jsPsychHtmlButtonResponse,
    stimulus: instructions.game_intro.decision,
    choices: ['No','Yes'],
    data: {
        task: 'decision_intro',
        stimulus_id: grid_intro.id
    },
};

var outcome_intro = {
    type: jsPsychHtmlButtonResponse,
    stimulus: function(){
        var is_playing = jsPsych.data.getLastTrialData().select('response').values;
        return randomDrawn(grid_intro.cards, is_playing);
    },
    choices: ['Next Round >'],
    data: {
        task: 'outcome_intro',
        stimulus_id: grid_intro.id
    },
    on_finish: function(data){
        var card = data.stimulus;
            if (["hearts","diamonds"].some(v => card.includes(v))) {
                data.outcome =  1 ;
            }else if (["clubs","spades"].some(v => card.includes(v))){
                data.outcome =  0 ;
            }
            jsPsych.setProgressBar(data.trial_index/overall_trials);
    }
};

/* Game Intro with AI */

var grid_AI_intro = attention_tests[1]; 

var game_pile_AI_intro = {
    type: jsPsychHtmlButtonResponse,
    stimulus: function(){
        return instructions.game_intro.game_pile+jsPsychVslGridScene.generate_stimulus(grid_AI_intro.stimulus, image_size)+"<p><br><br></p>"},
    stimulus_duration: 1500,
    trial_duration: 1800,
    save_trial_parameters: {stimulus_duration: true},
    choices: [],
    data: {
        task: 'stimulus_AI_intro'
    },
};

var human_AI_conf_intro ={
    type: jsPsychHtmlButtonResponse,
    stimulus: instructions.AI_intro.AI_conf +`<p><br> <span class=\"blue\">${grid_AI_intro.AI_conf}%</span><br><br></p>` + instructions.AI_intro.human_AI_conf,
    choices: ['very low','low', 'mid', 'high', 'very high'],
    data: {
        task: 'human_AI_conf_intro',
        stimulus_id: grid_AI_intro.id,
        Ai_conf: grid_AI_intro.AI_conf,
    },
    on_finish: function(data){
        data.human_AI_conf = ['very low','low', 'mid', 'high', 'very high'].at(data.response);
    }
};

var decision_AI_intro = {
    type: jsPsychHtmlButtonResponse,
    stimulus: instructions.game_play.decision,
    choices: ['No','Yes'],
    data: {
        task: 'decision',
        stimulus_id: grid_AI_intro.id
    },
};

var outcome_AI_intro = {
    type: jsPsychHtmlButtonResponse,
    stimulus: function(){
        var is_playing = jsPsych.data.getLastTrialData().select('response').values;
        return randomDrawn(grid_AI_intro.cards, is_playing);
    },
    choices: ['Next Round >'],
    data: {
        task: 'outcome_AI_intro',
        stimulus_id: grid_AI_intro.id
    },
    on_finish: function(data){
        var card = data.stimulus;
            if (["hearts","diamonds"].some(v => card.includes(v))) {
                data.outcome =  1 ;
            }else if (["clubs","spades"].some(v => card.includes(v))){
                data.outcome =  0 ;
            }
        jsPsych.setProgressBar(data.trial_index/overall_trials);
    }
};


/* Game Play */

var game_pile = {
    type: jsPsychHtmlButtonResponse,
    stimulus: function(){
        return instructions.game_play.game_pile+jsPsychVslGridScene.generate_stimulus(jsPsych.timelineVariable('stimulus'), image_size)+"<p><br><br></p>"},
    stimulus_duration: function(){
        return jsPsych.randomization.sampleWithoutReplacement([500, 750, 1000, 1250], 1)[0];
    },
    save_trial_parameters: {stimulus_duration: true},
    trial_duration: 1300,
    choices: [],
    data: {
        task: 'stimulus'
    }
};

var human_conf= {
    type: jsPsychHtmlButtonResponse,
    stimulus: instructions.game_play.human_conf,
    choices: ['very low','low', 'mid', 'high', 'very high'],
    data: {
        task: 'human_conf',
        stimulus_id: jsPsych.timelineVariable('id'),
        true_prob: function(data){ return Math.round(jsPsych.timelineVariable('nr_reds')/jsPsych.timelineVariable('nr_total') *100);}
    },
    on_finish: function(data){
        data.human_conf = ['very low','low', 'mid', 'high', 'very high'].at(data.response);
    }
};

var decision = {
    type: jsPsychHtmlButtonResponse,
    stimulus: instructions.game_play.decision,
    choices: ['No','Yes'],
    data: {
        task: 'decision',
        stimulus_id: jsPsych.timelineVariable('id')
    },
};

var outcome = {
    type: jsPsychHtmlButtonResponse,
    stimulus: function(){
        var is_playing = jsPsych.data.getLastTrialData().select('response').values;
        return randomDrawn(jsPsych.timelineVariable('cards'), is_playing);
    },
    choices: ['Next Round >'],
    data: {
        task: 'outcome',
        stimulus_id: jsPsych.timelineVariable('id')
    },
    on_finish: function(data){
            jsPsych.setProgressBar(data.trial_index/overall_trials);
            
            var card = data.stimulus;
            if (["hearts","diamonds"].some(v => card.includes(v))) {
                data.outcome =  1 ;
            }else if (["clubs","spades"].some(v => card.includes(v))){
                data.outcome =  0 ;
            }
    }
};

/* Game Play AI */

var human_AI_conf = {
    type: jsPsychHtmlButtonResponse,
    stimulus: function(){
        return instructions.game_play_AI.AI_conf +`<p><br> <span class=\"blue\">${jsPsych.timelineVariable('AI_conf')}%</span><br><br></p>` + instructions.game_play_AI.human_AI_conf;
    },
    choices: ['very low','low', 'mid', 'high', 'very high'],
    data: {
        task: 'human_AI_conf',
        stimulus_id: jsPsych.timelineVariable('id'),
        Ai_conf: jsPsych.timelineVariable('AI_conf')
    },
    on_finish: function(data){
        data.human_AI_conf = ['very low','low', 'mid', 'high', 'very high'].at(data.response);
    }
};

/* Timeline definitions*/

var game_intro = {
    timeline: [intro, game_pile_intro, human_conf_intro, decision_intro, outcome_intro],
    timeline_variables: [instructions.game_intro],
    // randomize_order: true
}

var AI_intro = {
    timeline: [ intro, game_pile_AI_intro, human_conf_intro, human_AI_conf_intro, decision_AI_intro, outcome_AI_intro],
    timeline_variables: [instructions.AI_intro],
    // randomize_order: true
}

var game_play = {
    timeline: [game_pile, human_conf, decision, outcome],
    timeline_variables: stimuli,
    sample: {
        type: 'without-replacement',
        size: nr_trials
    }
    // randomize_order: true
}

var game_play_AI = {
    timeline: [game_pile, human_conf, human_AI_conf, decision, outcome],
    timeline_variables: stimuli,
    sample: {
        type: 'without-replacement',
        size: nr_trials
    }
    // randomize_order: true
}

/* Attention test */
var attention_test_trial = {
    timeline: [game_pile, human_conf, decision, outcome],
    timeline_variables: attention_tests,
    sample: {
        type: 'without-replacement',
        size: 1
    }
    // randomize_order: true
}

var attention_test_trial_AI = {
    timeline: [game_pile, human_conf, human_AI_conf, decision, outcome],
    timeline_variables: attention_tests,
    sample: {
        type: 'without-replacement',
        size: 1
    }
    // randomize_order: true
}

timeline.push(game_intro, game_play, attention_test_trial, game_play);

var intermission_block = {
    type: jsPsychHtmlButtonResponse,
    stimulus: function(){ return `<p>You have <span class=\"orange\"> earned ${points} point(s) </span> until now.<br><br></p>`;
    },
    choices: ["Next >"],
    data: {
        task: 'intermission'
    },
    on_finish: function(data){
        jsPsych.setProgressBar(data.trial_index/overall_trials);
    }
};
timeline.push(intermission_block);

timeline.push(AI_intro, game_play_AI, attention_test_trial_AI, game_play_AI);

var debrief_block = {
    type: jsPsychHtmlButtonResponse,
    stimulus: function(){
        return `<p>You have <span class=\"orange\"> earned ${points} point(s) </span> in total.</p>
        <p>Thank you for participating in this experiment!<br><br></p>`;
    },
    choices: ["Finish >"],
    data: {
        task: 'debrief'
    },
    on_finish: function(data){
        jsPsych.setProgressBar(data.trial_index/overall_trials);
    }
};
timeline.push(debrief_block);

jsPsych.run(timeline);