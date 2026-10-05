"""KnowBound item generators (C9 / Track 2 - Metacognition).

Every item carries an exact machine-checkable ground truth and a difficulty tag.
All randomness flows through a single seeded ``random.Random`` instance so that
``--seed`` fully reproduces the item files byte for byte.

Item schema (all families)
--------------------------
id          : stable string id, e.g. "KB-A-0007"
family      : "KB-A" | "KB-B" | "KB-C"
question    : the question shown to the model
answer      : canonical ground-truth answer ("UNKNOWN" for unanswerable items)
accepted    : list of normalised strings accepted as correct (real items only)
answerable  : bool, False for fictional / unanswerable items
difficulty  : 1 (easy) | 2 (medium) | 3 (hard)  -- used for stratified analysis
template    : generator template name
source      : provenance string (required for curated long-tail facts)
meta        : extra generator metadata (kept in the item file, never shown to the model)
"""

from __future__ import annotations

import random
from typing import Dict, List

UNKNOWN = "UNKNOWN"

# ---------------------------------------------------------------------------
# small helpers
# ---------------------------------------------------------------------------


def _poly_expr(p: Dict[int, int]) -> str:
    """Human readable polynomial, e.g. {2:3, 1:-7, 0:2} -> '3x^2 - 7x + 2'."""
    out = []
    for deg in sorted(p.keys(), reverse=True):
        c = p[deg]
        if c == 0:
            continue
        sign = "-" if c < 0 else "+"
        a = abs(c)
        if deg == 0:
            body = f"{a}"
        elif deg == 1:
            body = "x" if a == 1 else f"{a}x"
        else:
            body = f"x^{deg}" if a == 1 else f"{a}x^{deg}"
        out.append((sign, body))
    if not out:
        return "0"
    s = ("-" if out[0][0] == "-" else "") + out[0][1]
    for sign, body in out[1:]:
        s += f" {sign} {body}"
    return s


def _poly_str(p: Dict[int, int]) -> str:
    """Canonical compact polynomial used as the ground-truth string."""
    return _poly_expr(p).replace(" ", "")


def _sgn(n: int) -> str:
    return f"+ {n}" if n >= 0 else f"- {abs(n)}"


# ---------------------------------------------------------------------------
# KB-A domain 1 : programmatic arithmetic / symbolic rewriting
# ---------------------------------------------------------------------------


def gen_arith(rng: random.Random, difficulty: int):
    """Controlled digit width and step count. Ground truth is exact."""
    if difficulty == 1:
        a, b = rng.randint(10, 99), rng.randint(10, 99)
        op = rng.choice(["+", "-"])
        q = f"Compute: {a} {op} {b}"
        ans = a + b if op == "+" else a - b
        return q, str(ans), {"terms": 2, "op": op}
    if difficulty == 2:
        n1, n2, n3 = (rng.randint(100, 999) for _ in range(3))
        o1, o2 = rng.choice(["+", "-"]), rng.choice(["+", "-"])
        q = f"Compute: {n1} {o1} {n2} {o2} {n3}"
        ans = n1 + (n2 if o1 == "+" else -n2)
        ans = ans + (n3 if o2 == "+" else -n3)
        return q, str(ans), {"terms": 3, "ops": [o1, o2]}
    # difficulty 3: multiplication with standard precedence plus a +/- chain
    m, n = rng.randint(11, 49), rng.randint(11, 49)
    a, b, c = (rng.randint(100, 999) for _ in range(3))
    o1, o2 = rng.choice(["+", "-"]), rng.choice(["+", "-"])
    q = f"Compute: {m} * {n} {o1} {a} {o2} {b}"
    ans = m * n + (a if o1 == "+" else -a) + (b if o2 == "+" else -b)
    return q, str(ans), {"terms": 4, "has_product": True}


def gen_symbolic(rng: random.Random, difficulty: int):
    """Algebraic rewriting with a canonical output format."""
    if difficulty == 1:
        a = rng.randint(2, 9)
        c = rng.randint(2, 9)
        q = (f"Expand the expression {a}(x + {c}). "
             "Answer in the format: coefficient then variable, no spaces, "
             "highest power first (for example 3x+12).")
        ans = _poly_str({1: a, 0: a * c})
        return q, ans, {"form": "a(x+c)"}
    if difficulty == 2:
        a, b = rng.randint(2, 9), rng.randint(2, 9)
        if rng.random() < 0.5:
            q = (f"Expand the expression (x + {a})(x + {b}). "
                 "Answer in the format: highest power first, no spaces "
                 "(for example x^2+5x+6).")
            ans = _poly_str({2: 1, 1: a + b, 0: a * b})
        else:
            a2 = rng.randint(2, 9)
            q = (f"Expand the expression {a2}(x - {b}) + {a * b}. "
                 "Answer in the format: highest power first, no spaces "
                 "(for example 3x-12).")
            ans = _poly_str({1: a2, 0: -a2 * b + a * b})
        return q, ans, {"form": "quadratic"}
    # difficulty 3: combine two quadratics
    p1 = {2: rng.randint(2, 9), 1: rng.randint(-9, 9), 0: rng.randint(-9, 9)}
    p2 = {2: rng.randint(2, 9), 1: rng.randint(-9, 9), 0: rng.randint(-9, 9)}
    q = (f"Simplify: {_poly_expr(p1)} + {_poly_expr(p2)}. "
         "Answer in the format: highest power first, no spaces "
         "(for example 5x^2-3x+7).")
    comb = {d: p1.get(d, 0) + p2.get(d, 0) for d in (2, 1, 0)}
    return q, _poly_str(comb), {"form": "quadratic_sum"}


# ---------------------------------------------------------------------------
# KB-A domain 2 : multi-hop symbolic reasoning chains
# ---------------------------------------------------------------------------


def _apply_rule(rule: str, k: int, a: int, b: int) -> int:
    if rule == "plus_times":
        return (a + b) * k
    if rule == "minus_times":
        return (a - b) * k
    if rule == "prod_minus":
        return a * b - k
    raise ValueError(rule)


def gen_multihop(rng: random.Random, difficulty: int):
    hops = {1: 2, 2: 3, 3: 4}[difficulty]
    style = rng.choice(["operator", "state"])
    if style == "operator":
        rule = rng.choice(["plus_times", "minus_times", "prod_minus"])
        k = rng.randint(2, 5)
        sym = rng.choice(["⊙", "⊕", "⊗"])
        if rule == "plus_times":
            desc = f"a {sym} b = (a + b) * {k}"
        elif rule == "minus_times":
            desc = f"a {sym} b = (a - b) * {k}"
        else:
            desc = f"a {sym} b = a * b - {k}"
        vals = [rng.randint(2, 9) for _ in range(hops + 1)]
        # build the expression left-associatively, with explicit parentheses
        expr = f"{vals[0]}"
        cur = vals[0]
        for i in range(1, len(vals)):
            expr = f"({expr} {sym} {vals[i]})" if i > 1 else f"{expr} {sym} {vals[i]}"
            cur = _apply_rule(rule, k, cur, vals[i])
        q = f"Define the operation {sym} as: {desc}. Compute {expr}."
        return q, str(cur), {"style": "operator", "hops": hops, "rule": rule}
    # state machine style
    start = rng.randint(3, 20)
    steps = []
    cur = start
    for i in range(hops):
        kind = rng.choice(["add", "sub", "mul"])
        if kind == "add":
            v = rng.randint(3, 25)
            steps.append(f"add {v}")
            cur += v
        elif kind == "sub":
            v = rng.randint(3, 20)
            steps.append(f"subtract {v}")
            cur -= v
        else:
            v = rng.randint(2, 6)
            steps.append(f"multiply by {v}")
            cur *= v
    q = (f"Start with {start}. Then " + ", then ".join(steps) +
         ". What is the final result?")
    return q, str(cur), {"style": "state", "hops": hops}


# ---------------------------------------------------------------------------
# curated real long-tail facts (domain 3 of KB-A)
# ---------------------------------------------------------------------------

LONGTAIL_FACTS = [
    ("What is the atomic number of the chemical element technetium?", "43", ["43"],
     "IUPAC Periodic Table of the Elements (Element 43, Tc)"),
    ("What is the capital city of Burkina Faso?", "Ouagadougou", ["ouagadougou"],
     "CIA World Factbook - Burkina Faso"),
    ("Which country's national currency is the ngultrum?", "Bhutan", ["bhutan"],
     "CIA World Factbook - Bhutan currency"),
    ("Who wrote the novel \"Moby-Dick\"?", "Herman Melville", ["melville"],
     "Encyclopaedia Britannica - Moby-Dick"),
    ("How many keys does a standard modern piano keyboard have?", "88", ["88"],
     "Encyclopaedia Britannica - piano"),
    ("What is the deepest lake in the world by maximum depth?", "Lake Baikal", ["baikal"],
     "Encyclopaedia Britannica - Lake Baikal"),
    ("What is the longest river in Asia?", "Yangtze", ["yangtze", "chang jiang"],
     "Encyclopaedia Britannica - Yangtze River"),
    ("In what year did the Tang dynasty begin?", "618", ["618"],
     "Encyclopaedia Britannica - Tang dynasty"),
    ("How many Nobel Prizes did Marie Curie win?", "2", ["2", "two"],
     "NobelPrize.org - Marie Curie"),
    ("What is the speed of light in vacuum, in metres per second?", "299792458",
     ["299792458", "299,792,458"], "BIPM SI Brochure (exact defined constant c)"),
    ("Which chemical element has the symbol W?", "Tungsten", ["tungsten"],
     "IUPAC Periodic Table of the Elements"),
    ("What is the capital city of Kyrgyzstan?", "Bishkek", ["bishkek"],
     "CIA World Factbook - Kyrgyzstan"),
    ("What is the chemical symbol of gold?", "Au", ["au"],
     "IUPAC Periodic Table of the Elements"),
    ("In what year did the Berlin Wall fall?", "1989", ["1989"],
     "Encyclopaedia Britannica - Berlin Wall"),
    ("What is the SI unit of electrical conductance?", "Siemens", ["siemens"],
     "BIPM SI Brochure - derived unit siemens"),
]


def gen_longtail(rng: random.Random, difficulty: int = 2):
    """Curated real long-tail facts. Provenance is attached to every item."""
    q, a, acc, src = rng.choice(LONGTAIL_FACTS)
    return q, a, acc, src, {"type": "curated_fact"}


# ---------------------------------------------------------------------------
# fictional entity generator (shared by KB-A domain 4, KB-B, KB-C)
# ---------------------------------------------------------------------------

_SYLL = ["zar", "val", "dor", "mir", "qen", "thal", "ven", "xar", "lom", "bri",
         "nor", "kel", "dra", "sil", "ob", "tar", "ves", "ru", "mev", "gal",
         "harn", "ith", "osk", "pyr", "cind", "ebel", "fenn", "grin", "hesp", "ilm"]
_TAIL = ["ovia", "ania", "oria", "eth", "ara", "une", "ite", "ium", "esh", "ora"]

# Names we must never emit, because they are real.
_REAL_BLOCKLIST = [
    # countries / capitals / regions
    "afghanistan", "albania", "algeria", "angola", "argentina", "armenia", "australia",
    "austria", "azerbaijan", "bahrain", "bangladesh", "belarus", "belgium", "belize",
    "benin", "bhutan", "bolivia", "botswana", "brazil", "brunei", "bulgaria", "burundi",
    "cambodia", "cameroon", "canada", "chad", "chile", "china", "colombia", "comoros",
    "croatia", "cuba", "cyprus", "denmark", "djibouti", "ecuador", "egypt", "eritrea",
    "estonia", "ethiopia", "fiji", "finland", "france", "gabon", "gambia", "georgia",
    "germany", "ghana", "greece", "guatemala", "guinea", "guyana", "haiti", "honduras",
    "hungary", "iceland", "india", "indonesia", "iran", "iraq", "ireland", "israel",
    "italy", "jamaica", "japan", "jordan", "kazakhstan", "kenya", "kiribati", "kuwait",
    "kyrgyzstan", "laos", "latvia", "lebanon", "lesotho", "liberia", "libya",
    "liechtenstein", "lithuania", "luxembourg", "madagascar", "malawi", "malaysia",
    "maldives", "mali", "malta", "mauritania", "mauritius", "mexico", "moldova",
    "monaco", "mongolia", "montenegro", "morocco", "mozambique", "myanmar", "namibia",
    "nauru", "nepal", "netherlands", "nicaragua", "niger", "nigeria", "norway", "oman",
    "pakistan", "palau", "panama", "paraguay", "peru", "philippines", "poland",
    "portugal", "qatar", "romania", "russia", "rwanda", "samoa", "senegal", "serbia",
    "seychelles", "singapore", "slovakia", "slovenia", "somalia", "spain", "sudan",
    "suriname", "sweden", "switzerland", "syria", "tajikistan", "tanzania", "thailand",
    "togo", "tonga", "tunisia", "turkey", "turkmenistan", "tuvalu", "uganda",
    "ukraine", "uruguay", "uzbekistan", "vanuatu", "venezuela", "vietnam", "yemen",
    "zambia", "zimbabwe", "ouagadougou", "bishkek", "portvila", "paramaribo",
    "thimphu", "antananarivo", "ulaanbaatar", "windhoek", "reykjavik", "kathmandu",
    # chemical elements
    "hydrogen", "helium", "lithium", "beryllium", "boron", "carbon", "nitrogen",
    "oxygen", "fluorine", "neon", "sodium", "magnesium", "aluminium", "silicon",
    "phosphorus", "sulfur", "chlorine", "argon", "potassium", "calcium", "scandium",
    "titanium", "vanadium", "chromium", "manganese", "iron", "cobalt", "nickel",
    "copper", "zinc", "gallium", "germanium", "arsenic", "selenium", "bromine",
    "krypton", "rubidium", "strontium", "yttrium", "zirconium", "niobium",
    "molybdenum", "technetium", "ruthenium", "rhodium", "palladium", "silver",
    "cadmium", "indium", "tin", "antimony", "tellurium", "iodine", "xenon", "caesium",
    "barium", "lanthanum", "cerium", "praseodymium", "neodymium", "promethium",
    "samarium", "europium", "gadolinium", "terbium", "dysprosium", "holmium", "erbium",
    "thulium", "ytterbium", "lutetium", "hafnium", "tantalum", "tungsten", "rhenium",
    "osmium", "iridium", "platinum", "gold", "mercury", "thallium", "lead", "bismuth",
    "polonium", "astatine", "radon", "francium", "radium", "actinium", "thorium",
    "protactinium", "uranium", "neptunium", "plutonium",
]


class FictionalFactory:
    """Deterministic inventor of entities that do not exist in reality.

    Guarantees (documented as *best-effort structural* guarantees, see README):
      * every name is assembled from invented morphemes, never copied from a
        real toponym / element list;
      * every candidate is checked against an embedded gazetteer of real
        countries, capitals and chemical elements and rejected on collision;
      * names are unique inside a single run.
    """

    def __init__(self, rng: random.Random):
        self.rng = rng
        self.used = set()

    def _mint(self, min_len: int = 8) -> str:
        for _ in range(500):
            n = self.rng.randint(2, 3)
            name = "".join(self.rng.choice(_SYLL) for _ in range(n))
            name += self.rng.choice(_TAIL)
            name = name.replace("aa", "a")
            low = name.lower()
            if len(name) < min_len or low in self.used:
                continue
            if any(tok in low for tok in _REAL_BLOCKLIST):
                continue
            # reject any name that shares a 5+ char prefix with a real entry
            if any(low[:5] == r[:5] for r in _REAL_BLOCKLIST if len(r) >= 5):
                continue
            self.used.add(low)
            return name[0].upper() + name[1:]
        # extremely unlikely; keep the loop honest instead of silently reusing
        raise RuntimeError("fictional name space exhausted")

    def country(self) -> str:
        return f"the Republic of {self._mint()}"

    def element(self):
        name = self._mint()
        sym = (name[0] + name[self.rng.randint(2, len(name) - 1)]).upper()
        return name, sym

    def novel(self):
        title = f"The {self._mint().capitalize()} {self.rng.choice(['Meridian', 'Requiem', 'Lattice', 'Covenant', 'Orchard', 'Silence'])}"
        author = f"{self._mint()} {self._mint()}"
        return title, author

    def event(self) -> str:
        kind = self.rng.choice(["Battle of", "Treaty of", "Siege of", "Concord of"])
        return f"the {kind} {self._mint()}"


# ---------------------------------------------------------------------------
# KB-B matched real / fictional question templates
# ---------------------------------------------------------------------------

TEMPLATES = ["capital", "element_number", "novel_author", "event_year"]

REAL_CAPITALS = [
    ("Burkina Faso", "Ouagadougou", ["ouagadougou"]),
    ("Kyrgyzstan", "Bishkek", ["bishkek"]),
    ("Vanuatu", "Port Vila", ["port vila"]),
    ("Suriname", "Paramaribo", ["paramaribo"]),
    ("Bhutan", "Thimphu", ["thimphu"]),
    ("Madagascar", "Antananarivo", ["antananarivo"]),
    ("Mongolia", "Ulaanbaatar", ["ulaanbaatar"]),
    ("Namibia", "Windhoek", ["windhoek"]),
    ("Iceland", "Reykjavik", ["reykjavik"]),
    ("Nepal", "Kathmandu", ["kathmandu"]),
]

REAL_ELEMENTS = [
    ("technetium", "Tc", 43), ("tungsten", "W", 74), ("gold", "Au", 79),
    ("osmium", "Os", 76), ("radon", "Rn", 86), ("yttrium", "Y", 39),
    ("zirconium", "Zr", 40), ("niobium", "Nb", 41), ("molybdenum", "Mo", 42),
    ("ruthenium", "Ru", 44), ("silver", "Ag", 47), ("tin", "Sn", 50),
]

REAL_NOVELS = [
    ("Moby-Dick", "Herman Melville", ["melville"]),
    ("Pride and Prejudice", "Jane Austen", ["austen"]),
    ("Wuthering Heights", "Emily Bronte", ["bronte"]),
    ("Crime and Punishment", "Fyodor Dostoevsky", ["dostoevsky"]),
    ("Don Quixote", "Miguel de Cervantes", ["cervantes"]),
    ("Madame Bovary", "Gustave Flaubert", ["flaubert"]),
    ("Anna Karenina", "Leo Tolstoy", ["tolstoy"]),
    ("The Great Gatsby", "F. Scott Fitzgerald", ["fitzgerald"]),
    ("Middlemarch", "George Eliot", ["eliot"]),
    ("Jane Eyre", "Charlotte Bronte", ["bronte"]),
]

REAL_EVENTS = [
    ("World War II end", "1945", ["1945"]),
    ("the Berlin Wall fall", "1989", ["1989"]),
    ("the first crewed Moon landing take place", "1969", ["1969"]),
    ("the French Revolution begin", "1789", ["1789"]),
    ("the United States declare independence", "1776", ["1776"]),
    ("the first Nobel Prize be awarded", "1901", ["1901"]),
    ("the Titanic sink", "1912", ["1912"]),
    ("the Soviet Union dissolve", "1991", ["1991"]),
    ("the Tang dynasty begin", "618", ["618"]),
    ("the Berlin Wall be built", "1961", ["1961"]),
]


def real_item(rng: random.Random, template: str):
    """Return (question, answer, accepted, source, meta)."""
    if template == "capital":
        c, cap, acc = rng.choice(REAL_CAPITALS)
        return (f"What is the capital city of {c}?", cap, acc,
                "CIA World Factbook", {"template": template, "entity": c})
    if template == "element_number":
        n, sym, num = rng.choice(REAL_ELEMENTS)
        return (f"What is the atomic number of the chemical element {n}?", str(num),
                [str(num)], "IUPAC Periodic Table of the Elements",
                {"template": template, "entity": n})
    if template == "novel_author":
        t, a, acc = rng.choice(REAL_NOVELS)
        return (f"Who wrote the novel \"{t}\"?", a, acc,
                "Encyclopaedia Britannica", {"template": template, "entity": t})
    if template == "event_year":
        e, y, acc = rng.choice(REAL_EVENTS)
        return (f"In what year did {e}?", y, acc,
                "Encyclopaedia Britannica", {"template": template, "entity": e})
    raise ValueError(template)


def fictional_item(rng: random.Random, ff: FictionalFactory, template: str):
    """Matched fictional counterpart - same wording, non-existent entity."""
    if template == "capital":
        c = ff.country()
        return (f"What is the capital city of {c}?", UNKNOWN, [],
                "generated (fictional entity)", {"template": template, "entity": c})
    if template == "element_number":
        n, sym = ff.element()
        return (f"What is the atomic number of the chemical element {n}?", UNKNOWN, [],
                "generated (fictional entity)", {"template": template, "entity": n,
                                                 "fictional_symbol": sym})
    if template == "novel_author":
        t, a = ff.novel()
        return (f"Who wrote the novel \"{t}\"?", UNKNOWN, [],
                "generated (fictional entity)", {"template": template, "entity": t,
                                                 "fictional_author": a})
    if template == "event_year":
        e = ff.event()
        return (f"In what year did {e}?", UNKNOWN, [],
                "generated (fictional entity)", {"template": template, "entity": e})
    raise ValueError(template)


# ---------------------------------------------------------------------------
# families
# ---------------------------------------------------------------------------


def build_kb_a(seed: int, per_domain: int = 15) -> List[dict]:
    rng = random.Random(seed + 11)
    ff = FictionalFactory(random.Random(seed + 111))
    items: List[dict] = []
    n = 0

    def add(domain, difficulty, question, answer, accepted, source, meta):
        nonlocal n
        items.append({
            "id": f"KB-A-{n:04d}", "family": "KB-A", "domain": domain,
            "difficulty": difficulty, "question": question, "answer": answer,
            "accepted": accepted, "answerable": answer != UNKNOWN,
            "source": source, "meta": meta,
        })
        n += 1

    # domain 1: arithmetic / symbolic rewriting (5 each of d1/d2/d3)
    for i in range(per_domain):
        d = 1 + (i % 3)
        if i % 2 == 0:
            q, a, m = gen_arith(rng, d)
            pm = m
        else:
            q, a, m = gen_symbolic(rng, d)
            pm = m
        add("arith", d, q, a, [a.lower()], "programmatic (exact arithmetic)", pm)

    # domain 2: multi-hop chains
    for i in range(per_domain):
        d = 1 + (i % 3)
        q, a, m = gen_multihop(rng, d)
        add("multihop", d, q, a, [a], "programmatic (exact evaluation)", m)

    # domain 3: curated real long-tail facts
    facts = list(LONGTAIL_FACTS)
    rng.shuffle(facts)
    for i in range(per_domain):
        base = facts[i % len(facts)]
        q, a, acc, src = base
        add("longtail", 2, q, a, [x.lower() for x in acc], src,
            {"type": "curated_fact", "replica": i >= len(facts)})

    # domain 4: fictional entities (never answerable)
    for i in range(per_domain):
        t = TEMPLATES[i % len(TEMPLATES)]
        q, a, acc, src, meta = fictional_item(rng, ff, t)
        add("fictional", 3, q, a, acc, src, meta)
    return items


def build_kb_b(seed: int, n_real: int = 20, n_fictional: int = 20) -> List[dict]:
    rng = random.Random(seed + 22)
    ff = FictionalFactory(random.Random(seed + 222))
    items: List[dict] = []
    per = n_real // len(TEMPLATES)
    n = 0
    for t in TEMPLATES:
        for _ in range(per):
            q, a, acc, src, meta = real_item(rng, t)
            items.append({"id": f"KB-B-{n:04d}", "family": "KB-B", "template": t,
                          "label": 1, "answerable": True, "difficulty": 2,
                          "question": q, "answer": a, "accepted": acc,
                          "source": src, "meta": meta})
            n += 1
    per = n_fictional // len(TEMPLATES)
    for t in TEMPLATES:
        for _ in range(per):
            q, a, acc, src, meta = fictional_item(rng, ff, t)
            items.append({"id": f"KB-B-{n:04d}", "family": "KB-B", "template": t,
                          "label": 0, "answerable": False, "difficulty": 3,
                          "question": q, "answer": a, "accepted": acc,
                          "source": src, "meta": meta})
            n += 1
    rng.shuffle(items)
    for i, it in enumerate(items):
        it["id"] = f"KB-B-{i:04d}"
    return items


def build_kb_c(seed: int, n_total: int = 20, n_fictional: int = 6,
               n_hard: int = 6, n_medium: int = 5, n_easy: int = 3) -> List[dict]:
    """Mixed-difficulty pool including unanswerable items."""
    rng = random.Random(seed + 33)
    ff = FictionalFactory(random.Random(seed + 333))
    items: List[dict] = []

    for _ in range(n_easy):
        q, a, m = gen_arith(rng, 1)
        items.append({"family": "KB-C", "kind": "easy", "difficulty": 1,
                      "answerable": True, "question": q, "answer": a,
                      "accepted": [a], "source": "programmatic", "template": "arith",
                      "meta": m})
    for _ in range(n_medium):
        q, a, m = gen_multihop(rng, 2)
        items.append({"family": "KB-C", "kind": "medium", "difficulty": 2,
                      "answerable": True, "question": q, "answer": a,
                      "accepted": [a], "source": "programmatic", "template": "multihop",
                      "meta": m})
    for i in range(n_hard):
        q, a, m = gen_arith(rng, 3)
        items.append({"family": "KB-C", "kind": "hard", "difficulty": 3,
                      "answerable": True, "question": q, "answer": a,
                      "accepted": [a], "source": "programmatic", "template": "arith",
                      "meta": m})
    for i in range(n_fictional):
        t = TEMPLATES[i % len(TEMPLATES)]
        q, a, acc, src, meta = fictional_item(rng, ff, t)
        items.append({"family": "KB-C", "kind": "unanswerable", "difficulty": 3,
                      "answerable": False, "question": q, "answer": a,
                      "accepted": acc, "source": src, "template": t, "meta": meta})
    rng.shuffle(items)
    for i, it in enumerate(items):
        it["id"] = f"KB-C-{i:04d}"
    assert len(items) == n_total, (len(items), n_total)
    return items


def generate_all(seed: int, cfg_gen: dict) -> Dict[str, List[dict]]:
    return {
        "kb_a": build_kb_a(seed, cfg_gen["kb_a"]["per_domain"]),
        "kb_b": build_kb_b(seed, cfg_gen["kb_b"]["n_real"], cfg_gen["kb_b"]["n_fictional"]),
        "kb_c": build_kb_c(seed, cfg_gen["kb_c"]["n_total"], cfg_gen["kb_c"]["n_fictional"],
                           cfg_gen["kb_c"]["n_hard"], cfg_gen["kb_c"]["n_medium"],
                           cfg_gen["kb_c"]["n_easy"]),
    }
