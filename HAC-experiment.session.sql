
CREATE TABLE Records (
    participant_id varchar(255), 
    trial_type varchar(255),
    trial_index int,
    time_elapsed int,
    rt int,
    response int,
    task varchar(255),
    stimulus_duration int,
    stimulus_id int,
    human_conf varchar(255),
    decision varchar(255),
    outcome int,
    true_prob int,
    Ai_conf int,
    human_AI_conf varchar(255),
    success BOOLEAN
);

