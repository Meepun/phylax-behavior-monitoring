% ============================
% DYNAMIC KNOWLEDGE
% ============================
:- dynamic message/2.
:- dynamic off_platform_request_fact/1.
:- dynamic message_index/2.
:- dynamic sent_hour/2.
:- dynamic previous_formality/2.
:- dynamic current_formality/2.

% ============================
% STATIC KNOWLEDGE
% ============================

% Authority keywords (expandable)
authority_keyword("bank").
authority_keyword("bdo").
authority_keyword("bpi").
authority_keyword("gcash").
authority_keyword("maya").
authority_keyword("sss").
authority_keyword("pagibig").
authority_keyword("philhealth").
authority_keyword("bir").
authority_keyword("admin").
authority_keyword("support").
authority_keyword("customer service").
authority_keyword("verification team").

% Off-platform keywords (expandable)
off_platform_keyword("facebook messenger").
off_platform_keyword("instagram dm").
off_platform_keyword("telegram").
off_platform_keyword("whatsapp").
off_platform_keyword("viber").
off_platform_keyword("call me").
off_platform_keyword("text me").
off_platform_keyword("email me").
off_platform_keyword("dm me").
off_platform_keyword("pm me").

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

% ============================
% TEMPORAL: ODD HOUR DETECTION
% ============================

odd_hour_message(Msg) :-
    sent_hour(Msg, Hour),
    (Hour >= 23 ; Hour < 8).

% ============================
% INTERACTION-BASED: OFF-PLATFORM CONTACT
% ============================

% Base detection: message contains off-platform keyword
off_platform_request(Msg) :-
    message(Msg, Text),
    off_platform_keyword(K),
    sub_string(Text, _, _, _, K).

% Facts asserted at runtime are stored here
record_off_platform_request(Msg) :-
    assertz(off_platform_request_fact(Msg)).

% Early contact violation: first 3 messages
early_off_platform_contact(Msg) :-
    message_index(Msg, Index),
    Index =< 3,
    off_platform_request(Msg).

% ============================
% LINGUISTIC SIGNALS: AUTHORITY IMPERSONATION
% ============================

authority_impersonation(Msg) :-
    message(Msg, Text),
    authority_keyword(K),
    sub_string(Text, _, _, _, K).

% ============================
% CATEGORY-LEVEL MAPPINGS
% ============================

% Behavioral violations
behavioral_violation(Msg, sudden_message_frequency) :-
    sudden_message_frequency(Msg).

behavioral_violation(Msg, abrupt_formality_change) :-
    abrupt_formality_change(Msg).

% Temporal violations
temporal_violation(Msg, odd_hour_messaging) :-
    odd_hour_message(Msg).

% Interaction-based violations
interaction_violation(Msg, early_off_platform_contact) :-
    early_off_platform_contact(Msg).

% Linguistic violations
linguistic_violation(Msg, authority_impersonation) :-
    authority_impersonation(Msg).
