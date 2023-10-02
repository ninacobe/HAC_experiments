/* initialize jsPsych */
var jsPsych = initJsPsych({
    show_progress_bar: true,
    auto_update_progress_bar: false,
    // on_finish: function() {
    //     // jsPsych.data.displayData();
    //     jsPsych.data.get().ignore('internal_node_id').ignore('view_history').ignore('stimulus').ignore('failed_audio').ignore('failed_video').localSave('csv','mydata.csv');
    // }
});

const EXPERIMENT_FILES = {  
    INSTRUCTIONS: 'materials/instructions.json',
    STIMULI: "materials/stimuli.json",
    ATTENTION_TESTS: "materials/attention_tests.json",
    CARDS: "materials/cards.json"
  };

var points = 0;
var image_size = [80,120]
var nr_trials = 1//4
var nr_trials_AI =1// 8
var overall_trials =  5 * (2*nr_trials_AI+1)+ 4 * (2*nr_trials+1)+ 11 + 5 + 2
var played_rounds = 0
var slider_size = 350

var instructions = {};
var cards = {};
var stimuli = {};
var attention_tests = {};

/* function to draw card from game pile */
// function randomDrawn(game_pile, decision){
//     var card = jsPsych.randomization.sampleWithoutReplacement(game_pile, 1)[0];
//     var earned = 0
//     if (["hearts","diamonds"].some(v => card.includes(v))) {
//         earned = 1 ;
//     }else if (["clubs","spades"].some(v => card.includes(v))){
//         earned = -1 ;
//     }
//     if (decision ==1 && earned ==1) {
//         points += earned
//         return "<p>Card Drawn:<br><br></p>"+`<img src=${card} width="130" height="100" class="center"></img>`
//         +`<p><br>You <span class=\"orange\">WON</span> 1 point!<br><br>You have now ${points} point(s).<br><br></p>`;
//     } else if (decision==1 && earned == -1){
//         points += earned
//         return "<p>Card Drawn:<br><br></p>"+`<img src=${card} width="130" height="100" class="center"></img>`
//         + `<p><br>You <span class=\"orange\">LOST</span> 1 point!<br><br>You have now ${points} point(s).<br><br></p>`;
//     } else if (earned ==1){
//         return "<p>Card Drawn:<br><br></p>"+`<img src=${card} width="130" height="100" class="center"></img>`
//         +`<p><br><span class=\"orange\">If you had played</span>, you would have WON 1 point!<br><br>You still have currently ${points} point(s).<br><br></p>`; 
//     }
//     return "<p>Card Drawn:<br><br></p>"+`<img src=${card} width="130" height="100" class="center"></img>`
//     +`<p><br><span class=\"orange\">If you had played</span>, you would have LOST 1 point!<br><br>You still have currently ${points} point(s).<br><br></p>`; 
// }

/* function to draw card from game pile */
function randomDrawn(game_pile, decision){
    var card = jsPsych.randomization.sampleWithoutReplacement(game_pile, 1)[0];
    var card_color = NaN
    played_rounds +=1
    if (["hearts","diamonds"].some(v => card.includes(v))) {
        card_color = 1 ;
    }else if (["clubs","spades"].some(v => card.includes(v))){
        card_color = 0 ;
    }
    var return_string = `<p>You bet on <span class=\"black\">Black</span>. <br> <br> Card Picked:<br><br></p>`+`<img src=${card}  class="center-small"></img>`

    if(decision==1){
        return_string = `<p>You bet on <span class=\"red\">Red</span>. <br> <br> Card Picked:<br><br></p>` + `<img src=${card}  class="center-small"></img>`
    }
 
    if (decision == card_color) {
        points += 1
        return return_string +`<p><br>You <span class=\"orange\">WON</span> 1 point!<br><br>You have <span class=\"orange\"> earned ${points} point(s) from ${played_rounds} round(s) </span> until now.<br><br></p>`;
    } 
    return return_string +`<p><br>You won 0 points!<br><br>You have <span class=\"orange\"> earned ${points} point(s) from ${played_rounds} rounds </span> until now.<br><br></p>`; 
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

// timeline.push({
//     type: jsPsychHtmlButtonResponse,
//     stimulus: function(){
//         return "<span class=\"center\">" +jsPsychVslGridScene.generate_stimulus(stimuli[401].stimulus, image_size) + "</span>"},
//     choices: [],
//     data: {
//         task: 'stimulus_intro'
//     },
// });

/* display instruction messages */
timeline.push({
    type: jsPsychInstructions,
    pages: instructions.welcome, 
    show_clickable_nav: true,
    on_finish: function(data){
        jsPsych.setProgressBar(data.trial_index/overall_trials);
    }
});


var ai_instructions = {
    type: jsPsychInstructions,
    pages: instructions.AI_instructions, 
    show_clickable_nav: true,
    data: {
        task: 'ai_intro'
    },
    on_finish: function(data){
        jsPsych.setProgressBar(data.trial_index/overall_trials);
    }
};

var enter_fullscreen = {
    type: jsPsychFullscreen,
    fullscreen_mode: true,
    message: "<p>The experiment will switch to full screen mode when you press the button below.<br> Please do not exit full screen during the experiment.<br><br></p>",
    on_finish: function(data){
        jsPsych.setProgressBar(data.trial_index/overall_trials);
    }
  }
timeline.push(enter_fullscreen)

var size_check = {
    type: jsPsychBrowserCheck,
    inclusion_function: (data) => {
        if (data.width/4 >= 350 && data.width/4 < 800){
            slider_size = (Math.round(data.width/4));
        }else if (data.width/3 >= 350 && data.width/3 < 800){
            slider_size = (Math.round(data.width/3));
        }
        image_size = (Math.round(data.width/21), Math.round(data.height/11));
        return true;
    }
};
timeline.push(size_check)


/* Definition of page*/
var grid_intro = attention_tests[0]
var grid_AI_intro = attention_tests[1]; 

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
        return  jsPsychVslGridScene.generate_stimulus(grid_intro.stimulus,image_size) },
    stimulus_duration: 1500,
    trial_duration: 1800,
    save_trial_parameters: {stimulus_duration: true},
    choices: [],
    data: {
        task: 'stimulus_intro'
    },
};


var game_pile_AI_intro = {
    type: jsPsychHtmlButtonResponse,
    stimulus: function(){
        return  jsPsychVslGridScene.generate_stimulus(grid_AI_intro.stimulus, image_size) },
    stimulus_duration: 1500,
    trial_duration: 1800,
    save_trial_parameters: {stimulus_duration: true},
    choices: [],
    data: {
        task: 'stimulus_AI_intro'
    },
};

var game_pile = {
    type: jsPsychHtmlButtonResponse,
    stimulus: function(){
        return jsPsychVslGridScene.generate_stimulus(jsPsych.timelineVariable('stimulus'), image_size)},
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

var human_conf_intro = {
    type: jsPsychHtmlSliderResponse,
    stimulus: instructions.game_intro.human_conf,
    labels: ['very low','low', 'mid', 'high', 'very high'],
    min: 0,
    max: 4,
    slider_start: 2,
    slider_width: function(){
        return slider_size
    },
    button_label: 'Next >',
    require_movement: true,
    data: {
        task: 'human_conf_intro',
        stimulus_id: grid_intro.id
    },
    on_finish: function(data){
        data.human_conf = ['very low','low', 'mid', 'high', 'very high'].at(data.response);
    }
};

var human_conf ={
    type: jsPsychHtmlSliderResponse,
    stimulus: instructions.game_play.human_conf,
    labels: ['very low','low', 'mid', 'high', 'very high'],
    min: 0,
    max: 4,
    slider_start: 2,
    slider_width: function(){
        return slider_size
    },
    button_label: 'Next >',
    require_movement: true,
    data: {
        task: 'human_conf',
        stimulus_id: jsPsych.timelineVariable('id'),
        true_prob: function(data){ return Math.round(jsPsych.timelineVariable('nr_reds')/jsPsych.timelineVariable('nr_total') *100);}
    },
    on_finish: function(data){
        data.human_conf = ['very low','low', 'mid', 'high', 'very high'].at(data.response);
    }
};

var human_AI_conf_intro ={
    type: jsPsychHtmlSliderResponse,
    stimulus: instructions.AI_intro.AI_conf +`<p><br> <span class=\"blue\">${grid_AI_intro.AI_conf}%</span><br><br></p>` + instructions.AI_intro.human_AI_conf,
    labels: ['very low','low', 'mid', 'high', 'very high'],
    min: 0,
    max: 4,
    slider_start: 2,
    slider_width: function(){
        return slider_size
    },
    button_label: 'Next >',
    require_movement: true,
    data: {
        task: 'human_AI_conf_intro',
        stimulus_id: grid_AI_intro.id,
        Ai_conf: grid_AI_intro.AI_conf,
    },
    on_finish: function(data){
        data.human_AI_conf = ['very low','low', 'mid', 'high', 'very high'].at(data.response);
    }
};

var human_AI_conf = { 
    type: jsPsychHtmlSliderResponse,
    stimulus: function(){
        return instructions.game_play_AI.AI_conf +`<p><br> <span class=\"blue\">${jsPsych.timelineVariable('AI_conf')}%</span><br><br></p>` + instructions.game_play_AI.human_AI_conf;
    },
    labels: ['very low','low', 'mid', 'high', 'very high'],
    min: 0,
    max: 4,
    slider_start: 2,
    slider_width: function(){
        return slider_size
    },
    button_label: 'Next >',
    require_movement: true,
    data: {
        task: 'human_AI_conf',
        stimulus_id: jsPsych.timelineVariable('id'),
        Ai_conf: jsPsych.timelineVariable('AI_conf')
    },
    on_finish: function(data){
        data.human_AI_conf = ['very low','low', 'mid', 'high', 'very high'].at(data.response);
    }
};

var decision_intro = {
    type: jsPsychHtmlButtonResponse,
    stimulus: instructions.game_intro.decision,
    choices: ['Black','Red'],
    button_html: ['<button class="black-btn">%choice%</button>','<button class="red-btn">%choice%</button>'],
    data: {
        task: 'decision_intro',
        stimulus_id: grid_intro.id
    },
    on_finish: function(data){
        data.decision = ['Black','Red'].at(data.response);
    }
};

var decision_AI_intro = {
    type: jsPsychHtmlButtonResponse,
    stimulus: instructions.game_play.decision,
    choices: ['Black','Red'],
    button_html: ['<button class="black-btn">%choice%</button>','<button class="red-btn">%choice%</button>'],
    data: {
        task: 'decision',
        stimulus_id: grid_AI_intro.id
    },
    on_finish: function(data){
        data.decision = ['Black','Red'].at(data.response);
    }
};

var decision = {
    type: jsPsychHtmlButtonResponse,
    stimulus: instructions.game_play.decision,
    choices: ['Black','Red'],
    button_html: ['<button class="black-btn">%choice%</button>','<button class="red-btn">%choice%</button>'],
    data: {
        task: 'decision',
        stimulus_id: jsPsych.timelineVariable('id')
    },
    on_finish: function(data){
        data.decision = ['Black','Red'].at(data.response);
    }
};

var outcome_intro = {
    type: jsPsychHtmlButtonResponse,
    stimulus: function(){
        var decision = jsPsych.data.getLastTrialData().select('response').values;
        return randomDrawn(grid_intro.cards, decision);
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

var outcome_AI_intro = {
    type: jsPsychHtmlButtonResponse,
    stimulus: function(){
        var decision = jsPsych.data.getLastTrialData().select('response').values;
        return randomDrawn(grid_AI_intro.cards, decision);
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

var outcome = {
    type: jsPsychHtmlButtonResponse,
    stimulus: function(){
        var decision = jsPsych.data.getLastTrialData().select('response').values;
        return randomDrawn(jsPsych.timelineVariable('cards'), decision);
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

/* Game Intro */
var game_intro = {
    timeline: [intro, game_pile_intro, human_conf_intro, decision_intro, outcome_intro],
    timeline_variables: [instructions.game_intro],
    // randomize_order: true
}

/* Game Play */
var game_play = {
    timeline: [game_pile, human_conf, decision, outcome],
    timeline_variables: stimuli,
    sample: {
        type: 'without-replacement',
        size: nr_trials
    }
    // randomize_order: true
}

/* Game Intro with AI */
var AI_intro = {
    timeline: [ game_pile_AI_intro, human_conf_intro, human_AI_conf_intro, decision_AI_intro, outcome_AI_intro],
    timeline_variables: [instructions.AI_intro],
    // randomize_order: true
}
/* Game Play AI */
var game_play_AI = {
    timeline: [game_pile, human_conf, human_AI_conf, decision, outcome],
    timeline_variables: stimuli,
    sample: {
        type: 'without-replacement',
        size: nr_trials_AI
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

/* Attention test AI*/
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
    stimulus: function(){ return `<p>You have <span class=\"orange\"> earned ${points} point(s) from ${played_rounds} rounds until now</span>.<br><br></p>`;
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

timeline.push(ai_instructions, AI_intro, game_play_AI, attention_test_trial_AI, game_play_AI);

var save_data = {
    type: jsPsychCallFunction,
    async: true,
    func: function(done){
      var xhr = new XMLHttpRequest();
      xhr.open('POST', 'write_data.php');
      xhr.setRequestHeader('Content-Type', 'application/json');
      xhr.onload = function() {
        if(xhr.status == 200){
          var response = JSON.parse(xhr.responseText);
          console.log(response.success);
        }
        done(); // invoking done() causes experiment to progress to next trial.
      };
      xhr.send(jsPsych.data.get().json());
    }
}

var debrief_block = {
    type: jsPsychHtmlButtonResponse,
    stimulus: function(){
        return `<div class=\"content\"> <p>You have <span class=\"orange\"> earned ${points} out of ${played_rounds} points</span>. <br> <br></p>
     </div> `;
    },
    choices: ["Next >"],
    data: {
        task: 'debrief'
    },
    on_finish: function(data){
        jsPsych.setProgressBar(data.trial_index/overall_trials);
    }
};

var survey = {
    type: jsPsychSurvey,
    pages: [
      [{
        type: 'html',
        prompt: `Please answer the following questions about your thoughts on the model.`,
        },
        // {
        //   type: 'likert',
        //   prompt: instructions.survey[0],
        //   name: "most_helpful",
        //   likert_scale_values: [
        //     {value: "very low"},
        //     {value: "low"},
        //     {value: "mid"},
        //     {value: "high"},
        //     {value: "very high"}
        //   ],
        //   required: true
        // },
        {
            type: 'ranking',
            prompt: instructions.survey[0],
            name: "ranking_helpful",
            options: [
              "very low", "low","mid","high","very high"
            ],
            required: true
          },
        {
          type: 'likert-table',
          prompt: 'State how much you agree with following statements about the model.',
          name: 'statements',
          statements: instructions.survey[1],
          options: ['Strongly Disagree', 'Disagree', 'Neutral', 'Agree', 'Strongly Agree'],
          required: true
        }
      ]
    ],
    button_label_finish: "Next >",
    data: {
        task: 'survey'
    },
    on_finish: function(data){
        jsPsych.setProgressBar(data.trial_index/overall_trials);
    }
  };

  
var thanks = {
    type: jsPsychHtmlButtonResponse,
    stimulus: function(){
        return `<div class=\"content\">
        <p>Thank you for participating in this experiment!<br><br></p> 
     </div> <div class=\"bottom-link\"> <a href=\"https://imprint.mpi-klsb.mpg.de/sws/hac-experiment.mpi-sws.org\" class=\"my-link\">Imprint</a> | <a href=\"https://data-protection.mpi-klsb.mpg.de/sws/hac-experiment.mpi-sws.org?lang=en\" class=\"my-link\">Data Protection</a> </div>  
        `;
    },
    choices: ["Finish >"],
    data: {
        task: 'thanks'
    },
    on_finish: function(data){
        jsPsych.setProgressBar(data.trial_index/overall_trials);
    }
};
timeline.push(debrief_block, survey, save_data, thanks);
//timeline.push(debrief_block);

jsPsych.run(timeline);
