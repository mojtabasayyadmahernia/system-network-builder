"""
Verb lexicon for TRANSITIVITY analysis (IFG4 Ch. 5).

Process type is semantic, not syntactic — "she saw him" and "she hit him"
have identical structure but construe different processes. So classification
starts from lists of verbs, with syntactic rules to disambiguate.

Organisation
------------
Each process type has one or more sets, grouped by subtype where IFG makes
a subtype distinction. AMBIGUOUS_VERBS records lemmas that legitimately
belong to more than one process type, so the analyser can lower its
confidence rather than assert.

These lists are linguistic judgements. Edit them freely — this file is
meant to grow as you meet verbs it doesn't know.
"""

# ===========================================================================
# MATERIAL — processes of doing and happening
# ===========================================================================

_MATERIAL_MOTION = {
    "go", "come", "arrive", "leave", "depart", "enter", "exit", "return",
    "move", "travel", "journey", "walk", "run", "jog", "sprint", "march",
    "stroll", "wander", "roam", "hike", "fly", "soar", "swim", "dive",
    "jump", "leap", "hop", "skip", "climb", "crawl", "creep", "drive",
    "ride", "cycle", "sail", "row", "paddle", "fall", "tumble", "plunge",
    "rise", "ascend", "descend", "sink", "float", "drift", "escape", "flee",
    "chase", "pursue", "follow", "trail", "approach", "near", "retreat",
    "advance", "withdraw", "cross", "traverse", "pass", "overtake",
    "circle", "spin", "rotate", "revolve", "roll", "slide", "slip",
    "stumble", "trip", "hurry", "rush", "dash", "bolt", "scramble",
    "wade", "trek", "commute", "migrate", "land", "take off", "depart",
}

_MATERIAL_CONTACT = {
    "hit", "strike", "beat", "batter", "pound", "hammer", "knock", "tap",
    "bang", "slam", "catch", "throw", "toss", "hurl", "fling", "cast",
    "pitch", "kick", "punch", "slap", "smack", "whack", "push", "shove",
    "pull", "drag", "haul", "tug", "yank", "press", "squeeze", "crush",
    "touch", "stroke", "pat", "rub", "grab", "grasp", "seize", "snatch",
    "clutch", "grip", "hold", "release", "let go", "drop", "carry", "lug",
    "lift", "raise", "hoist", "lower", "stab", "pierce", "poke", "prod",
    "pinch", "scratch", "claw", "bite", "chew", "gnaw", "kiss", "hug",
    "embrace", "shake", "wave", "swing", "wield", "brandish",
}

_MATERIAL_TRANSFORM = {
    "break", "shatter", "smash", "crack", "snap", "fracture", "splinter",
    "tear", "rip", "shred", "cut", "slice", "chop", "carve", "saw", "split",
    "divide", "separate", "sever", "burn", "scorch", "singe", "char",
    "melt", "thaw", "freeze", "chill", "boil", "simmer", "roast", "fry",
    "grill", "steam", "bend", "fold", "crease", "twist", "wring", "stretch",
    "shrink", "expand", "swell", "contract", "destroy", "demolish", "raze",
    "wreck", "ruin", "damage", "harm", "spoil", "repair", "mend", "fix",
    "restore", "renovate", "change", "alter", "transform", "convert",
    "modify", "adjust", "adapt", "improve", "enhance", "worsen",
    "clean", "wash", "rinse", "scrub", "polish", "wipe", "sweep", "mop",
    "dust", "dry", "wet", "soak", "drench", "fill", "empty", "drain",
    "open", "close", "shut", "seal", "lock", "unlock", "fasten", "unfasten",
    "tie", "untie", "bind", "wrap", "unwrap", "cover", "uncover", "bury",
    "dig", "plough", "plow", "mow", "trim", "prune", "shave", "peel",
    "grind", "mash", "blend", "mix", "stir", "whisk", "knead",
}

_MATERIAL_TRANSFER = {
    "give", "take", "send", "dispatch", "bring", "fetch", "deliver",
    "receive", "obtain", "acquire", "gain", "collect", "gather", "put",
    "place", "set", "lay", "position", "install", "mount", "hang",
    "buy", "purchase", "sell", "vend", "pay", "spend", "earn", "invest",
    "lend", "loan", "borrow", "rent", "lease", "hire", "steal", "rob",
    "pinch", "swipe", "exchange", "trade", "swap", "barter", "offer",
    "provide", "supply", "furnish", "distribute", "share", "donate",
    "contribute", "award", "grant", "allocate", "assign", "present",
    "hand", "pass", "transfer", "ship", "mail", "post", "load", "unload",
    "pack", "unpack", "store", "stock", "save", "spare", "waste",
    "discard", "dump", "throw away", "lose", "find", "recover", "retrieve",
}

_MATERIAL_CREATIVE = {
    "make", "build", "create", "produce", "construct", "erect", "assemble",
    "manufacture", "fabricate", "generate", "form", "shape", "mould",
    "mold", "fashion", "craft", "forge", "cast", "write", "compose",
    "draft", "author", "pen", "draw", "sketch", "paint", "illustrate",
    "design", "devise", "invent", "formulate", "conceive", "develop",
    "establish", "found", "institute", "organise", "organize", "arrange",
    "bake", "cook", "brew", "prepare", "knit", "sew", "weave", "embroider",
    "plant", "sow", "cultivate", "breed", "rear", "hatch", "sculpt",
    "model", "print", "publish", "issue", "record", "film", "compile",
}

_MATERIAL_OTHER = {
    "do", "work", "labour", "labor", "toil", "play", "use", "employ",
    "utilise", "utilize", "apply", "operate", "handle", "manage", "run",
    "direct", "control", "wear", "dress", "undress", "don", "remove",
    "study", "practise", "practice", "train", "exercise", "rehearse",
    "perform", "act", "help", "assist", "aid", "support", "serve",
    "attend", "join", "quit", "resign", "start", "begin", "commence",
    "stop", "cease", "halt", "finish", "complete", "end", "continue",
    "resume", "repeat", "try", "attempt", "endeavour", "strive",
    "succeed", "fail", "win", "lose", "beat", "defeat", "conquer",
    "compete", "fight", "battle", "attack", "assault", "raid", "invade",
    "defend", "protect", "guard", "shield", "save", "rescue", "kill",
    "murder", "slay", "assassinate", "execute", "die", "perish",
    "search", "seek", "hunt", "explore", "discover", "detect", "hide",
    "conceal", "reveal", "expose", "show", "display", "exhibit",
    "choose", "select", "pick", "elect", "appoint", "nominate",
    "add", "insert", "attach", "connect", "link", "detach", "delete",
    "erase", "remove", "eliminate", "eat", "drink", "swallow", "consume",
    "devour", "sip", "gulp", "feed", "nurse", "treat", "cure", "heal",
    "injure", "wound", "hurt", "decorate", "furnish", "sort", "rank",
    "stack", "pile", "spread", "scatter", "sprinkle", "spray", "pour",
    "spill", "water", "harvest", "pluck", "reach", "touch", "meet",
    "greet", "visit", "accompany", "escort", "guide", "lead", "drive",
    "follow", "obey", "disobey", "break", "keep", "grow", "raise",
    "reduce", "increase", "decrease", "double", "halve", "count",
    "measure", "weigh", "test", "check", "inspect", "examine", "review",
    "revise", "edit", "correct", "mark", "grade", "sign", "stamp",
}

MATERIAL_VERBS = (
    _MATERIAL_MOTION | _MATERIAL_CONTACT | _MATERIAL_TRANSFORM
    | _MATERIAL_TRANSFER | _MATERIAL_CREATIVE | _MATERIAL_OTHER
)

# Creative material processes bring the Goal into existence.
CREATIVE_VERBS = _MATERIAL_CREATIVE


# ===========================================================================
# MENTAL — processes of sensing
# ===========================================================================

MENTAL_PERCEPTIVE = {
    "see", "hear", "feel", "notice", "perceive", "sense", "spot",
    "glimpse", "detect", "discern", "observe", "witness", "behold",
    "smell", "taste", "sight", "espy", "make out", "overhear",
}

MENTAL_COGNITIVE = {
    "think", "know", "believe", "understand", "realise", "realize",
    "remember", "recall", "recollect", "forget", "consider", "suppose",
    "presume", "assume", "imagine", "envisage", "conceive", "doubt",
    "question", "wonder", "recognise", "recognize", "reckon", "conclude",
    "deduce", "infer", "reason", "reflect", "ponder", "contemplate",
    "meditate", "muse", "guess", "estimate", "judge", "evaluate",
    "assess", "appraise", "comprehend", "grasp", "fathom", "puzzle",
    "anticipate", "expect", "predict", "foresee", "foretell", "learn",
    "memorise", "memorize", "master", "discover", "note", "suspect",
    "gather", "understand", "appreciate", "acknowledge", "accept",
    "dismiss", "disbelieve", "trust", "distrust", "mistrust",
}

MENTAL_DESIDERATIVE = {
    "want", "wish", "hope", "desire", "crave", "long", "yearn", "hanker",
    "need", "require", "intend", "mean", "plan", "aim", "propose",
    "decide", "resolve", "determine", "prefer", "fancy", "care",
    "choose", "opt", "aspire", "covet", "demand", "insist",
}

MENTAL_EMOTIVE = {
    "like", "love", "adore", "cherish", "treasure", "prize", "enjoy",
    "relish", "savour", "savor", "hate", "detest", "loathe", "despise",
    "abhor", "dislike", "resent", "envy", "begrudge", "fear", "dread",
    "mind", "regret", "rue", "lament", "mourn", "grieve", "miss",
    "pity", "sympathise", "sympathize", "empathise", "empathize",
    "admire", "respect", "esteem", "value", "appreciate", "worry",
    "delight", "rejoice", "marvel", "tolerate", "bear", "stand", "stomach",
}

# 'Please-type' mental processes put the Phenomenon in Subject position:
#   "The music pleased Mary"   not   "Mary pleased the music"
MENTAL_PLEASE_TYPE = {
    "please", "delight", "gratify", "satisfy", "content", "charm",
    "disgust", "revolt", "repel", "repulse", "sicken", "nauseate",
    "worry", "concern", "trouble", "disturb", "upset", "distress",
    "sadden", "depress", "dishearten", "frighten", "scare", "terrify",
    "alarm", "startle", "shock", "horrify", "appal", "appall", "dismay",
    "surprise", "astonish", "amaze", "astound", "stun", "stagger",
    "interest", "intrigue", "fascinate", "captivate", "enthral",
    "enthrall", "engross", "absorb", "amuse", "entertain", "divert",
    "bore", "tire", "weary", "exhaust", "annoy", "irritate", "vex",
    "exasperate", "infuriate", "enrage", "anger", "offend", "insult",
    "embarrass", "humiliate", "shame", "mortify", "impress", "inspire",
    "encourage", "discourage", "disappoint", "excite", "thrill",
    "comfort", "console", "reassure", "soothe", "calm", "relax",
    "confuse", "bewilder", "perplex", "baffle", "mystify", "puzzle",
    "convince", "persuade", "tempt", "attract", "bother", "unnerve",
}

MENTAL_VERBS = (
    MENTAL_PERCEPTIVE | MENTAL_COGNITIVE | MENTAL_DESIDERATIVE
    | MENTAL_EMOTIVE | MENTAL_PLEASE_TYPE
)


# ===========================================================================
# RELATIONAL — processes of being and having
# ===========================================================================

# Copular verbs: take a Complement rather than an Object
COPULAR_VERBS = {
    "be", "become", "seem", "appear", "look", "sound", "feel", "taste",
    "smell", "remain", "stay", "keep", "turn", "get", "grow", "go",
    "come", "prove", "emerge", "end up", "wind up", "rank", "count",
}

RELATIONAL_POSSESSIVE = {
    "have", "own", "possess", "hold", "belong", "contain", "include",
    "comprise", "consist", "lack", "want", "carry", "bear", "feature",
    "boast", "incorporate", "encompass", "involve", "entail", "retain",
    "keep", "acquire", "gain", "lose", "obtain",
}

RELATIONAL_CIRCUMSTANTIAL = {
    "accompany", "follow", "precede", "surround", "encircle", "occupy",
    "fill", "cross", "span", "cover", "stretch", "extend", "reach",
    "last", "endure", "take", "cost", "weigh", "measure", "hold",
    "seat", "sleep", "concern", "involve", "regard", "relate", "resemble",
    "differ", "match", "fit", "suit", "befit", "correspond", "coincide",
    "contain", "border", "adjoin", "face", "overlook",
}

# Verbs that identify rather than attribute
IDENTIFYING_VERBS = {
    "equal", "represent", "mean", "define", "signify", "symbolise",
    "symbolize", "denote", "indicate", "constitute", "comprise",
    "exemplify", "typify", "characterise", "characterize", "embody",
    "personify", "stand for", "amount", "total", "number", "form",
    "make", "spell", "translate", "express", "reflect", "mark",
}

RELATIONAL_VERBS = (
    COPULAR_VERBS | RELATIONAL_POSSESSIVE | RELATIONAL_CIRCUMSTANTIAL
    | IDENTIFYING_VERBS
)


# ===========================================================================
# VERBAL — processes of saying
# ===========================================================================

VERBAL_VERBS = {
    "say", "tell", "speak", "talk", "ask", "inquire", "enquire",
    "question", "reply", "respond", "answer", "retort", "rejoin",
    "explain", "clarify", "elaborate", "state", "declare", "assert",
    "claim", "allege", "maintain", "contend", "argue", "debate",
    "dispute", "announce", "proclaim", "pronounce", "broadcast",
    "report", "relate", "recount", "narrate", "mention", "note",
    "observe", "remark", "comment", "add", "interject", "suggest",
    "propose", "recommend", "advise", "counsel", "urge", "insist",
    "demand", "request", "beg", "plead", "implore", "entreat",
    "order", "command", "instruct", "direct", "warn", "caution",
    "threaten", "promise", "pledge", "vow", "swear", "guarantee",
    "assure", "admit", "confess", "concede", "acknowledge", "deny",
    "refute", "contradict", "object", "protest", "complain", "grumble",
    "boast", "brag", "whisper", "murmur", "mutter", "mumble", "shout",
    "yell", "scream", "shriek", "call", "cry", "exclaim", "bellow",
    "roar", "snap", "bark", "growl", "repeat", "recite", "quote",
    "cite", "read", "chant", "pray", "greet", "thank", "apologise",
    "apologize", "congratulate", "invite", "summon", "phone", "ring",
    "write", "email", "text", "wire", "signal", "hint", "imply",
    "indicate", "confirm", "reveal", "disclose", "divulge", "inform",
    "notify", "announce", "publish", "state", "utter", "voice",
}

# Verbal processes with a Target — someone talked ABOUT rather than TO
VERBAL_TARGETING_VERBS = {
    "praise", "commend", "compliment", "flatter", "laud", "extol",
    "criticise", "criticize", "condemn", "denounce", "censure",
    "rebuke", "reprimand", "scold", "chide", "berate", "blame",
    "accuse", "charge", "indict", "slander", "libel", "defame",
    "insult", "abuse", "mock", "ridicule", "deride", "taunt", "tease",
    "describe", "discuss", "address", "interrogate", "examine",
    "characterise", "characterize", "portray", "depict", "review",
}

ALL_VERBAL_VERBS = VERBAL_VERBS | VERBAL_TARGETING_VERBS


# ===========================================================================
# BEHAVIOURAL — physiological and psychological behaviour
# ===========================================================================

_BEHAV_PHYSIOLOGICAL = {
    "breathe", "inhale", "exhale", "pant", "gasp", "wheeze", "cough",
    "sneeze", "sniff", "snuffle", "yawn", "hiccup", "burp", "belch",
    "vomit", "retch", "sweat", "perspire", "shiver", "tremble", "quiver",
    "twitch", "blink", "wink", "squint", "sleep", "doze", "nap",
    "slumber", "snore", "dream", "wake", "awaken", "faint", "swoon",
    "blush", "flush", "pale", "salivate", "drool", "itch", "ache",
}

_BEHAV_EXPRESSION = {
    "laugh", "chuckle", "giggle", "chortle", "guffaw", "snigger",
    "smile", "beam", "grin", "smirk", "frown", "scowl", "grimace",
    "pout", "sulk", "cry", "weep", "sob", "whimper", "wail", "howl",
    "sigh", "groan", "moan", "grunt", "whistle", "hum", "sing",
    "hiss", "boo", "cheer", "applaud", "clap", "nod", "shrug", "wave",
    "gesture", "point", "beckon", "wince", "flinch", "gulp", "swallow",
}

_BEHAV_NEAR_MENTAL = {
    "watch", "listen", "look", "observe", "view", "examine", "inspect",
    "scrutinise", "scrutinize", "study", "contemplate", "ponder",
    "meditate", "concentrate", "focus", "attend", "ignore", "stare",
    "gaze", "glare", "peer", "glance", "peek", "glimpse", "browse",
}

_BEHAV_NEAR_VERBAL = {
    "chat", "chatter", "gossip", "natter", "converse", "quarrel",
    "bicker", "squabble", "argue", "grumble", "mutter", "murmur",
    "babble", "prattle", "rant", "lecture", "preach",
}

_BEHAV_POSTURE = {
    "sit", "stand", "lie", "kneel", "crouch", "squat", "lean", "stoop",
    "recline", "sprawl", "perch", "rest", "wait", "pause", "hesitate",
    "linger", "loiter", "settle", "rise", "bow", "curtsy",
}

_BEHAV_SOCIAL = {
    "behave", "misbehave", "act", "conduct", "participate", "cooperate",
    "compete", "dance", "celebrate", "socialise", "socialize", "mingle",
    "flirt", "court", "play", "joke", "jest", "tease", "gamble",
    "smoke", "drink", "feast", "dine", "picnic", "camp", "swim",
}

BEHAVIOURAL_VERBS = (
    _BEHAV_PHYSIOLOGICAL | _BEHAV_EXPRESSION | _BEHAV_NEAR_MENTAL
    | _BEHAV_NEAR_VERBAL | _BEHAV_POSTURE | _BEHAV_SOCIAL
)


# ===========================================================================
# AMBIGUOUS VERBS
# ===========================================================================
# Lemmas that legitimately belong to more than one process type. The
# analyser resolves these syntactically where it can, and lowers its
# confidence where it cannot. The comment on each gives the test.

AMBIGUOUS_VERBS = {
    # copular vs other reading
    "feel":    ["mental", "relational", "behavioural"],   # felt sad / felt the cloth
    "look":    ["relational", "behavioural"],             # looked tired / looked at him
    "taste":   ["relational", "mental", "behavioural"],   # tasted sweet / tasted it
    "smell":   ["relational", "mental", "behavioural"],   # smelled awful / smelled it
    "sound":   ["relational", "material"],                # sounded odd / sounded the alarm
    "appear":  ["relational", "material"],                # appeared calm / appeared on stage
    "prove":   ["relational", "material"],                # proved wrong / proved the theorem
    "grow":    ["material", "relational"],                # grew wheat / grew old
    "turn":    ["material", "relational"],                # turned the key / turned red
    "get":     ["material", "relational"],                # got a book / got tired
    "go":      ["material", "relational"],                # went home / went sour
    "come":    ["material", "relational"],                # came home / came true
    "keep":    ["material", "relational"],                # kept the book / kept quiet
    "remain":  ["relational", "behavioural"],             # remained calm / remained seated
    "stay":    ["relational", "behavioural"],             # stayed calm / stayed at home

    # possessive vs material
    "have":    ["relational", "material"],                # has a car / had a shower
    "hold":    ["material", "relational"],                # held the cup / holds 200 people
    "carry":   ["material", "relational"],                # carried the bag / carries a risk
    "bear":    ["material", "relational", "mental"],       # bore the weight / bears a name
    "take":    ["material", "relational"],                # took the book / takes an hour
    "lose":    ["material", "relational"],                # lost the key / lost interest
    "gain":    ["material", "relational"],
    "acquire": ["material", "relational"],
    "contain": ["relational"],

    # identifying vs material
    "make":    ["material", "relational"],                # made a cake / two and two make four
    "form":    ["material", "relational"],                # formed a queue / forms the basis
    "mark":    ["material", "relational", "verbal"],
    "count":   ["material", "relational"],                # counted them / counts as valid
    "rank":    ["material", "relational"],
    "represent": ["relational", "verbal"],
    "indicate":  ["relational", "verbal"],
    "reflect":   ["relational", "mental"],                # reflects the truth / reflected on it
    "express":   ["relational", "verbal"],

    # mental vs other
    "see":     ["mental", "relational"],                  # saw the bird / sees frequent use
    "find":    ["material", "mental"],                    # found the key / found it hard
    "think":   ["mental", "behavioural"],                 # thought so / thought about it
    "mean":    ["relational", "mental"],                  # means 'red' / meant to go
    "want":    ["mental", "relational"],                  # wants a car / wants for nothing
    "need":    ["mental", "relational"],
    "observe": ["mental", "verbal", "behavioural"],        # observed a bird / observed that…
    "note":    ["mental", "verbal"],
    "suggest": ["verbal", "mental"],                       # suggested a plan / suggests that…
    "doubt":   ["mental"],
    "trust":   ["mental"],
    "mind":    ["mental"],
    "study":   ["material", "behavioural", "mental"],
    "learn":   ["mental", "material"],
    "discover":["material", "mental"],
    "gather":  ["material", "mental"],                     # gathered flowers / gathered that…
    "appreciate": ["mental"],
    "puzzle":  ["mental"],                                 # puzzled over / puzzled her

    # verbal vs other
    "read":    ["material", "verbal"],                     # read a book / read it aloud
    "write":   ["material", "verbal"],                     # wrote a poem / wrote to her
    "call":    ["material", "verbal", "relational"],        # called a taxi / called out / called him John
    "answer":  ["verbal", "material"],                     # answered him / answered the door
    "argue":   ["verbal", "behavioural"],                   # argued that… / argued with him
    "discuss": ["verbal", "behavioural"],
    "add":     ["material", "verbal"],                      # added sugar / added that…
    "sing":    ["behavioural", "verbal", "material"],
    "cry":     ["behavioural", "verbal"],                   # cried (wept) / cried out
    "shout":   ["verbal", "behavioural"],
    "whisper": ["verbal", "behavioural"],
    "complain":["verbal", "behavioural"],
    "grumble": ["verbal", "behavioural"],
    "reveal":  ["material", "verbal"],
    "publish": ["material", "verbal"],
    "signal":  ["verbal", "material"],

    # behavioural vs material
    "die":     ["material", "behavioural"],
    "live":    ["material", "behavioural", "relational"],
    "rest":    ["behavioural", "material"],
    "wait":    ["behavioural", "material"],
    "play":    ["material", "behavioural"],
    "work":    ["material", "behavioural"],
    "run":     ["material", "behavioural"],                 # ran home / ran a business
    "swim":    ["material", "behavioural"],
    "dance":   ["behavioural", "material"],
    "drink":   ["material", "behavioural"],
    "swallow": ["material", "behavioural"],
    "act":     ["material", "behavioural"],
    "perform": ["material", "behavioural"],
    "rise":    ["material", "behavioural"],
    "examine": ["behavioural", "verbal", "material"],
    "review":  ["material", "verbal"],
    "glimpse": ["mental", "behavioural"],
    "reach":   ["material", "relational"],
    "follow":  ["material", "relational", "behavioural"],
    "accompany": ["material", "relational"],
    "spell":   ["relational", "material"],
    "sleep":   ["behavioural", "relational"],               # slept well / sleeps four
    "attend":  ["material", "behavioural"],
    "insist":  ["verbal", "mental"],
    "demand":  ["verbal", "mental"],
    "choose":  ["material", "mental"],
    "concern": ["relational", "mental"],
    "involve": ["relational", "material"],
    "cover":   ["material", "relational"],
    "fill":    ["material", "relational"],
    "surround":["material", "relational"],
    "cross":   ["material", "relational"],
    "extend":  ["material", "relational"],
    "stretch": ["material", "relational"],
    "weigh":   ["material", "relational"],
    "measure": ["material", "relational"],
    "cost":    ["relational"],
    "last":    ["relational"],

    # additional cross-set lemmas, flagged for confidence purposes
    "acknowledge":   ["mental", "verbal"],
    "boast":         ["verbal", "relational"],       # boasted that… / boasts a pool
    "characterise":  ["verbal", "relational"],
    "characterize":  ["verbal", "relational"],
    "compete":       ["material", "behavioural"],
    "conceive":      ["mental", "material"],         # conceived an idea / conceived a child
    "contemplate":   ["mental", "behavioural"],
    "detect":        ["mental", "material"],
    "direct":        ["material", "verbal"],         # directed the film / directed him to go
    "grasp":         ["mental", "material"],         # grasped the point / grasped the rail
    "greet":         ["material", "verbal"],
    "gulp":          ["material", "behavioural"],
    "inspect":       ["behavioural", "material"],
    "insult":        ["verbal", "material"],
    "meditate":      ["mental", "behavioural"],
    "murmur":        ["verbal", "behavioural"],
    "mutter":        ["verbal", "behavioural"],
    "obtain":        ["material", "relational"],
    "ponder":        ["mental", "behavioural"],
    "propose":       ["verbal", "mental"],
    "question":      ["verbal", "mental"],           # questioned him / questioned whether
    "relate":        ["verbal", "relational"],       # related the story / relates to X
    "repeat":        ["material", "verbal"],
    "snap":          ["material", "verbal"],         # snapped the twig / snapped at him
    "stand":         ["behavioural", "relational"],  # stood up / stands as proof
    "tease":         ["verbal", "behavioural"],
    "wave":          ["material", "behavioural"],
}


# ===========================================================================
# CIRCUMSTANCES — prepositions and adverbs (frequent four only)
# ===========================================================================

LOCATION_PREPS = {
    "in", "on", "at", "near", "nearby", "under", "underneath", "beneath",
    "below", "over", "above", "beside", "alongside", "between", "among",
    "amongst", "amid", "inside", "outside", "behind", "before",
    "in front of", "opposite", "within", "into", "onto", "upon",
    "toward", "towards", "from", "to", "across", "along", "around",
    "through", "past", "by", "off", "out", "up", "down", "throughout",
}

EXTENT_PREPS = {
    "for", "during", "throughout", "until", "till", "since", "over",
    "within", "in", "by", "after", "before", "from",
}

MANNER_PREPS = {
    "with", "without", "by", "like", "as", "via", "through", "using",
    "against", "per",
}

CAUSE_PREPS = {
    "because", "because of", "due", "due to", "owing", "owing to",
    "thanks", "thanks to", "for", "from", "through", "out of",
    "on account of", "in order to", "so as to", "despite", "against",
}

TIME_ADVERBS = {
    "yesterday", "today", "tomorrow", "now", "then", "soon", "later",
    "already", "recently", "lately", "afterwards", "beforehand",
    "tonight", "currently", "previously", "formerly", "eventually",
    "immediately", "instantly", "presently", "meanwhile", "nowadays",
}

FREQUENCY_ADVERBS = {
    "often", "always", "never", "sometimes", "usually", "normally",
    "generally", "rarely", "seldom", "occasionally", "frequently",
    "constantly", "continually", "repeatedly", "twice", "once",
    "again", "daily", "weekly", "monthly", "yearly", "annually",
    "ever", "hardly ever", "regularly", "periodically",
}

PLACE_ADVERBS = {
    "here", "there", "everywhere", "somewhere", "nowhere", "anywhere",
    "abroad", "overseas", "outside", "inside", "indoors", "outdoors",
    "upstairs", "downstairs", "nearby", "locally", "away", "home",
    "ahead", "behind", "north", "south", "east", "west", "elsewhere",
}


# ===========================================================================
# Lookup helpers
# ===========================================================================

PROCESS_SETS = {
    "material": MATERIAL_VERBS,
    "mental": MENTAL_VERBS,
    "relational": RELATIONAL_VERBS,
    "verbal": ALL_VERBAL_VERBS,
    "behavioural": BEHAVIOURAL_VERBS,
}

MENTAL_SUBTYPE_SETS = {
    "perceptive": MENTAL_PERCEPTIVE,
    "cognitive": MENTAL_COGNITIVE,
    "desiderative": MENTAL_DESIDERATIVE,
    "emotive": MENTAL_EMOTIVE | MENTAL_PLEASE_TYPE,
}


def lookup(lemma):
    """
    Every process type this lemma could belong to.

    >>> sorted(lookup("hit"))
    ['material']
    >>> sorted(lookup("feel"))
    ['behavioural', 'mental', 'relational']
    """
    lemma = lemma.lower()
    return {
        name for name, verbs in PROCESS_SETS.items() if lemma in verbs
    }


def is_known(lemma):
    """Is this verb in the lexicon at all?"""
    return bool(lookup(lemma))


def is_ambiguous(lemma):
    """Does this verb have more than one plausible process type?"""
    lemma = lemma.lower()
    return lemma in AMBIGUOUS_VERBS or len(lookup(lemma)) > 1


def ambiguity_penalty(lemma):
    """
    How much to reduce confidence for an ambiguous verb.

    0.0 for an unambiguous verb, up to 0.25 for one that could be
    three different process types.
    """
    lemma = lemma.lower()
    candidates = AMBIGUOUS_VERBS.get(lemma) or list(lookup(lemma))
    if len(candidates) <= 1:
        return 0.0
    return min(0.25, 0.1 * (len(candidates) - 1))


def coverage():
    """Counts per category — useful for tracking the lexicon's growth."""
    return {
        "material": len(MATERIAL_VERBS),
        "  creative": len(CREATIVE_VERBS),
        "mental": len(MENTAL_VERBS),
        "  perceptive": len(MENTAL_PERCEPTIVE),
        "  cognitive": len(MENTAL_COGNITIVE),
        "  desiderative": len(MENTAL_DESIDERATIVE),
        "  emotive": len(MENTAL_EMOTIVE),
        "  please-type": len(MENTAL_PLEASE_TYPE),
        "relational": len(RELATIONAL_VERBS),
        "  copular": len(COPULAR_VERBS),
        "  possessive": len(RELATIONAL_POSSESSIVE),
        "  circumstantial": len(RELATIONAL_CIRCUMSTANTIAL),
        "  identifying": len(IDENTIFYING_VERBS),
        "verbal": len(ALL_VERBAL_VERBS),
        "  targeting": len(VERBAL_TARGETING_VERBS),
        "behavioural": len(BEHAVIOURAL_VERBS),
        "ambiguous (flagged)": len(AMBIGUOUS_VERBS),
        "distinct lemmas": len(
            MATERIAL_VERBS | MENTAL_VERBS | RELATIONAL_VERBS
            | ALL_VERBAL_VERBS | BEHAVIOURAL_VERBS
        ),
    }


if __name__ == "__main__":
    for key, value in coverage().items():
        print(f"{key:24} {value}")