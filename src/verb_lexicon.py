"""
Verb lexicon for TRANSITIVITY analysis (IFG4 Ch. 5).

Process type is semantic, not syntactic — "she saw him" and "she hit him"
have identical structure but different processes. So classification starts
from lists of verbs, with syntactic rules to disambiguate.

These lists are linguistic judgements. Edit them freely: this file is
meant to grow as you meet verbs it doesn't know.
"""

# ---------------------------------------------------------------------------
# MATERIAL — doing and happening
# ---------------------------------------------------------------------------

MATERIAL_VERBS = {
    # motion
    "run", "walk", "go", "come", "arrive", "leave", "depart", "enter", "exit",
    "move", "travel", "fly", "swim", "jump", "climb", "fall", "rise", "drive",
    "ride", "return", "escape", "chase", "follow", "approach", "cross", "pass",
    # contact and impact
    "hit", "strike", "catch", "throw", "kick", "push", "pull", "touch", "grab",
    "hold", "drop", "carry", "lift", "press", "knock", "punch", "slap",
    # transformation
    "break", "cut", "open", "close", "tear", "burn", "melt", "freeze", "bend",
    "crush", "smash", "destroy", "damage", "repair", "fix", "change", "turn",
    # transfer
    "give", "take", "send", "bring", "put", "place", "receive", "deliver",
    "buy", "sell", "pay", "lend", "borrow", "steal", "return", "offer",
    # creation (see CREATIVE_VERBS below)
    "build", "make", "create", "produce", "write", "draw", "paint", "compose",
    "bake", "cook", "form", "generate", "invent", "design", "construct",
    # other doing
    "eat", "drink", "wash", "clean", "dig", "plant", "grow", "kill", "die",
    "work", "play", "use", "wear", "read", "study", "practise", "practice",
    "start", "stop", "begin", "finish", "continue", "try", "help", "win", "lose",
}

# Creative material processes bring the Goal into existence.
CREATIVE_VERBS = {
    "build", "make", "create", "produce", "write", "draw", "paint", "compose",
    "bake", "cook", "form", "generate", "invent", "design", "construct",
    "develop", "establish", "found", "assemble", "manufacture",
}


# ---------------------------------------------------------------------------
# MENTAL — sensing
# ---------------------------------------------------------------------------

MENTAL_PERCEPTIVE = {
    "see", "hear", "feel", "notice", "perceive", "sense", "spot", "glimpse",
    "detect", "observe", "witness",
}

MENTAL_COGNITIVE = {
    "think", "know", "believe", "understand", "realise", "realize", "remember",
    "forget", "consider", "suppose", "imagine", "doubt", "recognise",
    "recognize", "assume", "reckon", "conclude", "reflect", "ponder",
    "guess", "figure", "comprehend", "grasp",
}

MENTAL_DESIDERATIVE = {
    "want", "wish", "hope", "desire", "need", "intend", "plan", "decide",
    "prefer", "long", "crave", "aim", "resolve", "determine",
}

MENTAL_EMOTIVE = {
    "like", "love", "hate", "fear", "enjoy", "dislike", "adore", "detest",
    "miss", "admire", "regret", "mind", "appreciate", "resent", "envy",
}

# 'Please-type' mental processes put the Phenomenon in Subject position:
#   "The music pleased Mary"  (not "Mary pleased the music")
MENTAL_PLEASE_TYPE = {
    "please", "delight", "disgust", "worry", "frighten", "scare", "surprise",
    "interest", "amuse", "bore", "annoy", "irritate", "upset", "shock",
    "impress", "satisfy", "disappoint", "excite", "comfort", "trouble",
}

MENTAL_VERBS = (
    MENTAL_PERCEPTIVE | MENTAL_COGNITIVE | MENTAL_DESIDERATIVE
    | MENTAL_EMOTIVE | MENTAL_PLEASE_TYPE
)


# ---------------------------------------------------------------------------
# RELATIONAL — being and having
# ---------------------------------------------------------------------------

# Copular verbs: take a Complement rather than an Object
COPULAR_VERBS = {
    "be", "become", "seem", "appear", "look", "sound", "feel", "taste",
    "smell", "remain", "stay", "turn", "get", "grow", "keep", "prove",
}

RELATIONAL_POSSESSIVE = {
    "have", "own", "possess", "belong", "contain", "include", "lack",
    "comprise", "consist", "hold", "carry",
}

RELATIONAL_CIRCUMSTANTIAL = {
    "accompany", "follow", "precede", "surround", "occupy", "cross",
    "cost", "last", "weigh", "measure", "span", "cover",
}

# Verbs that identify rather than attribute
IDENTIFYING_VERBS = {
    "equal", "represent", "mean", "define", "signify", "symbolise",
    "symbolize", "constitute", "denote", "indicate", "exemplify",
}

RELATIONAL_VERBS = (
    COPULAR_VERBS | RELATIONAL_POSSESSIVE | RELATIONAL_CIRCUMSTANTIAL
    | IDENTIFYING_VERBS
)


# ---------------------------------------------------------------------------
# VERBAL — saying
# ---------------------------------------------------------------------------

VERBAL_VERBS = {
    "say", "tell", "ask", "reply", "answer", "explain", "claim", "argue",
    "announce", "state", "remark", "suggest", "insist", "report", "declare",
    "mention", "add", "note", "whisper", "shout", "yell", "complain",
    "promise", "warn", "admit", "deny", "repeat", "recite", "urge",
}

# Verbal processes with a Target — someone talked ABOUT rather than TO
VERBAL_TARGETING_VERBS = {
    "praise", "criticise", "criticize", "insult", "describe", "discuss",
    "blame", "accuse", "flatter", "slander", "commend", "condemn", "mock",
}

ALL_VERBAL_VERBS = VERBAL_VERBS | VERBAL_TARGETING_VERBS


# ---------------------------------------------------------------------------
# BEHAVIOURAL — physiological and psychological behaviour
# ---------------------------------------------------------------------------

BEHAVIOURAL_VERBS = {
    # physiological
    "breathe", "cough", "sneeze", "yawn", "blink", "sleep", "dream", "snore",
    "sweat", "shiver", "tremble", "faint", "vomit",
    # facial and vocal
    "laugh", "cry", "smile", "frown", "sigh", "grin", "weep", "sob", "scream",
    "sing", "whistle", "hum", "nod", "shrug", "wave", "stare", "gaze", "glare",
    # near-mental
    "watch", "listen", "look", "taste", "smell",
    # near-verbal
    "chat", "talk", "gossip", "grumble", "mutter", "chatter", "argue",
    # posture
    "sit", "stand", "lie", "kneel", "lean", "rest", "wait",
}


# ---------------------------------------------------------------------------
# CIRCUMSTANCES — prepositions and adverbs (frequent four only)
# ---------------------------------------------------------------------------

LOCATION_PREPS = {
    "in", "on", "at", "near", "under", "over", "above", "below", "beneath",
    "beside", "between", "among", "inside", "outside", "behind", "opposite",
    "within", "into", "onto", "toward", "towards", "from", "to", "across",
}

EXTENT_PREPS = {"for", "during", "throughout", "until", "till", "since"}

MANNER_PREPS = {"with", "without", "by", "like", "as", "via", "through"}

CAUSE_PREPS = {"because", "due", "owing", "thanks", "for", "against"}

TIME_ADVERBS = {
    "yesterday", "today", "tomorrow", "now", "then", "soon", "later",
    "already", "recently", "afterwards", "beforehand", "tonight",
    "currently", "previously", "eventually", "immediately", "meanwhile",
}

FREQUENCY_ADVERBS = {
    "often", "always", "never", "sometimes", "usually", "rarely", "seldom",
    "occasionally", "frequently", "constantly", "twice", "once", "again",
}

PLACE_ADVERBS = {
    "here", "there", "everywhere", "somewhere", "nowhere", "anywhere",
    "abroad", "outside", "inside", "upstairs", "downstairs", "nearby",
}