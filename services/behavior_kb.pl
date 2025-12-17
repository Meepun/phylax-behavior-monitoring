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

% ----------------------------
% Authority keywords
% ----------------------------
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

% ----------------------------
% Off-platform keywords
% ----------------------------
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

% ----------------------------
% Formal linguistic markers
% ----------------------------
formal_phrase("could you").
formal_phrase("may i").
formal_phrase("kindly").
formal_phrase("please be advised").
formal_phrase("we would like to").
formal_phrase("for your reference").
formal_phrase("we regret to inform you").

formal_title("mr.").
formal_title("ms.").
formal_title("mrs.").
formal_title("sir").
formal_title("ma'am").
formal_title("dr.").
formal_title("prof.").

no_contraction_phrase("i am").
no_contraction_phrase("it is").
no_contraction_phrase("we are").
no_contraction_phrase("you are").

% ----------------------------
% Casual / Contractions
% ----------------------------
casual_marker("lol").
casual_marker("lmao").
casual_marker("bro").
casual_marker("dude").
casual_marker("hey").
casual_marker("yo").
casual_marker("gonna").
casual_marker("wanna").
casual_marker("lemme").
casual_marker("sup").
casual_marker("nah").

contraction("i'm").
contraction("it's").
contraction("we're").
contraction("you're").
contraction("can't").
contraction("won't").
contraction("don't").

% ============================
% LOW-LEVEL DETECTION RULES
% ============================

% ----------------------------
% Behavioral: Formality shift (bidirectional)
% ----------------------------
abrupt_formality_change(Msg) :-
    previous_formality(Msg, Prev),
    current_formality(Msg, Curr),
    (
        % casual -> formal shift
        Prev =< 1,
        Curr >= 3,
        strong_formal_signal(Msg)
    ;
        % formal -> casual shift
        Prev >= 3,
        Curr =< 1,
        strong_casual_signal(Msg)
    ).

% Reinforcing linguistic evidence
strong_formal_signal(Msg) :-
    message(Msg, Text),
    (
        formal_phrase(K), sub_string(Text, _, _, _, K)
    ;
        formal_title(T), sub_string(Text, _, _, _, T)
    ;
        no_contraction_phrase(NC), sub_string(Text, _, _, _, NC)
    ).

strong_casual_signal(Msg) :-
    message(Msg, Text),
    (
        casual_marker(C), sub_string(Text, _, _, _, C)
    ;
        contraction(Con), sub_string(Text, _, _, _, Con)
    ).

% ----------------------------
% Temporal: Odd hour detection
% ----------------------------
odd_hour_message(Msg) :-
    sent_hour(Msg, Hour),
    (Hour >= 23 ; Hour < 8).

% ----------------------------
% Interaction-based: Off-platform
% ----------------------------
off_platform_request(Msg) :-
    message(Msg, Text),
    off_platform_keyword(K),
    sub_string(Text, _, _, _, K).

early_off_platform_contact(Msg) :-
    message_index(Msg, Index),
    Index =< 3,
    off_platform_request(Msg).

% ----------------------------
% Linguistic: Authority impersonation
% ----------------------------
authority_impersonation(Msg) :-
    message(Msg, Text),
    authority_keyword(K),
    sub_string(Text, _, _, _, K).

% ============================
% CATEGORY-LEVEL MAPPINGS
% ============================
behavioral_violation(Msg, abrupt_formality_change) :-
    abrupt_formality_change(Msg).

temporal_violation(Msg, odd_hour_messaging) :-
    odd_hour_message(Msg).

interaction_violation(Msg, early_off_platform_contact) :-
    early_off_platform_contact(Msg).

linguistic_violation(Msg, authority_impersonation) :-
    authority_impersonation(Msg).
