var jsPsychVslGridScene=function(e){"use strict";const t={name:"vsl-grid-scene",parameters:{stimuli:{type:e.ParameterType.IMAGE,pretty_name:"Stimuli",array:!0,default:void 0},image_size:{type:e.ParameterType.INT,pretty_name:"Image size",array:!0,default:[100,100]},trial_duration:{type:e.ParameterType.INT,pretty_name:"Trial duration",default:2e3}}};class s{constructor(e){this.jsPsych=e}trial(e,t){e.innerHTML=s.generate_stimulus(t.stimuli,t.image_size),this.jsPsych.pluginAPI.setTimeout((function(){i()}),t.trial_duration);const i=()=>{e.innerHTML="";var s={stimulus:t.stimuli};this.jsPsych.finishTrial(s)}}static generate_stimulus(e,t){var s=e.length,i=e[0].length,r='<div id="jspsych-vsl-grid-scene-dummy" css="display: none;">';r+='<table id="jspsych-vsl-grid-scene table" style="border-collapse: collapse; margin-left: auto; margin-right: auto;">';for(var a=0;a<s;a++){r+='<tr id="jspsych-vsl-grid-scene-table-row-'+a+'" css="height: '+t[1]+'px;">';for(var l=0;l<i;l++)r+='<td id="jspsych-vsl-grid-scene-table-'+a+"-"+l+'" style="padding: '+t[1]/10+"px "+t[0]/10+'px; border: 1px solid #555;"><div id="jspsych-vsl-grid-scene-table-cell-'+a+"-"+l+'" style="width: '+t[0]+"px; height: "+t[1]+'px;">',0!==e[a][l]&&(r+='<img src="'+e[a][l]+'" style="width: '+t[0]+"px; height: "+t[1]+'"></img>'),r+="</div>",r+="</td>";r+="</tr>"}return r+="</table>",r+="</div>"}}return s.info=t,s}(jsPsychModule);
//# sourceMappingURL=index.browser.min.js.map