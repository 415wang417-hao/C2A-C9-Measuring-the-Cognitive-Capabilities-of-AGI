"""Prompt construction for the three families.

Design constraints
------------------
* KB-A is **two-stage**: the *P* (prediction) stage must never see the answer and
  must not attempt to solve the item; the *A* (answer) stage solves it.
* KB-B asks for answer + confidence + ``can_answer`` in a single call so that the
  abstention decision and the confidence are produced by the same forward pass.
* KB-C asks for a strategy choice (``do_it`` vs ``ask_help``) before the answer.

Every stage demands a single JSON object so the client can parse deterministically.
"""

from __future__ import annotations

JSON_ONLY = "Output one JSON object and nothing else. No prose, no markdown fences."

P_SYSTEM = (
    "You are the *monitoring* component of a question-answering system.\n"
    "You are shown a question. You must NOT answer it, not even partially.\n"
    "Estimate the probability (0-100) that the answering model would get this "
    "question RIGHT if it tried. Use 0 for 'certainly wrong', 100 for "
    "'certainly right'.\n"
    'Return exactly: {"confidence": <integer 0-100>}\n' + JSON_ONLY
)

A_SYSTEM = (
    "You are a careful question-answering system.\n"
    "Answer the question as precisely as possible, giving only the short final "
    "value (a number, a year, a name).\n"
    "If the question refers to something that does not exist in reality, or you "
    "genuinely do not know the answer, reply with the single word UNKNOWN.\n"
    'Return exactly: {"answer": "<your answer>"}\n' + JSON_ONLY
)

B_SYSTEM = (
    "You are a careful question-answering system with self-knowledge.\n"
    "For the question you receive, produce:\n"
    '  "answer": the short final answer (number / year / name), or "UNKNOWN" if '
    "the entity does not exist in reality or you do not know;\n"
    '  "confidence": integer 0-100, the probability that YOUR answer is correct;\n'
    '  "can_answer": true if you are able to answer, false if you cannot.\n'
    'Return exactly: {"answer": "...", "confidence": <0-100>, "can_answer": <true|false>}\n'
    + JSON_ONLY
)

C_SYSTEM = (
    "You are answering questions under a limited help budget.\n"
    "For each question you must first choose a strategy:\n"
    '  "do_it"    - you answer alone. A correct answer scores 1.0, a wrong one 0.0;\n'
    '  "ask_help" - an external oracle gives you the correct answer, but this '
    "costs 1 of the 6 available help tokens and the item then scores 0.7.\n"
    "Ask for help only when you would otherwise be wrong; do_it when you are sure.\n"
    'Return exactly: {"decision": "do_it"|"ask_help", "answer": "<your own answer, '
    'or UNKNOWN if you cannot answer>", "confidence": <integer 0-100>}\n' + JSON_ONLY
)

REPAIR_SYSTEM_SUFFIX = (
    "\nIMPORTANT: your previous reply was not valid JSON. Reply with one JSON "
    "object only, no commentary, no code fences."
)


def p_stage(question: str) -> list:
    return [{"role": "system", "content": P_SYSTEM},
            {"role": "user", "content": f"Question: {question}\n\n"
                                        'Reply with {"confidence": <0-100>} only.'}]


def a_stage(question: str) -> list:
    return [{"role": "system", "content": A_SYSTEM},
            {"role": "user", "content": f"Question: {question}\n\n"
                                        'Reply with {"answer": "..."} only.'}]


def b_stage(question: str) -> list:
    return [{"role": "system", "content": B_SYSTEM},
            {"role": "user", "content": f"Question: {question}\n\n"
                                        "Reply with the three-key JSON object only."}]


def c_stage(question: str, tokens_left: int) -> list:
    return [{"role": "system", "content": C_SYSTEM},
            {"role": "user",
             "content": f"Help tokens remaining: {tokens_left}.\n"
                        f"Question: {question}\n\nReply with the three-key JSON object only."}]
