# knowledge base for behavior monitoring

% ============================
% STATIC KNOWLEDGE
% ============================

authority_keyword("bank").
authority_keyword("bangko").
authority_keyword("gcash").
authority_keyword("maya").
authority_keyword("support").
authority_keyword("customer service").
authority_keyword("admin").

off_platform_keyword("telegram").
off_platform_keyword("whatsapp").
off_platform_keyword("viber").
off_platform_keyword("call me").
off_platform_keyword("text me").

% ============================
% LOW-LEVEL DETECTION RULES
% ============================

% ============================
% BEHAVIORAL: MESSAGE FREQUENCY
% ============================

sudden_message_frequency(Msg) :-
    prev_5min_count(Msg, Prev),
    curr_5min_count(Msg, Curr),
    Prev >= 1,
    Curr >= Prev * 3.

% ============================
% BEHAVIORAL: FORMALITY SHIFT
% ============================

abrupt_formality_change(Msg) :-
    previous_formality(Msg, Prev),
    current_formality(Msg, Curr),
    Diff is abs(Curr - Prev),
    Diff >= 2.

odd_hour_message(Msg) :-
    sent_hour(Msg, Hour),
    (Hour < 5 ; Hour >= 23).

off_platform_request(Msg) :-
    message(Msg, Text),
    off_platform_keyword(K),
    sub_string(Text, _, _, _, K).

off_platform_request(Msg) :-
    asked_off_platform(Msg).

scripted_behavior(Msg) :-
    ignored_previous_reply(Msg),
    message_count_last_minute(Msg, Count),
    Count >= 3.

authority_impersonation(Msg) :-
    message(Msg, Text),
    authority_keyword(K),
    sub_string(Text, _, _, _, K).

% ============================
% VIOLATIONS
% ============================

% ============================
% BEHAVIORAL VIOLATIONS
% ============================

behavioral_violation(Msg, sudden_message_frequency) :-
    sudden_message_frequency(Msg).

behavioral_violation(Msg, abrupt_formality_change) :-
    abrupt_formality_change(Msg).

violation(Msg, odd_time_messaging) :-
    odd_hour_message(Msg).

violation(Msg, off_platform_contact_request) :-
    off_platform_request(Msg).

violation(Msg, scripted_ignoring_behavior) :-
    scripted_behavior(Msg).

violation(Msg, authority_impersonation) :-
    authority_impersonation(Msg).
