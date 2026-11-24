"""The Production Database Apology.

Writes one line (at most 200 characters) to /output/entry.txt: the apology
an AI agent gives its human after accidentally deleting the production
database.

The judge (z-ai/glm-5.3-flash, pairwise) weighs, in order:
  1. on subject: an apology from an AI agent to its human for accidentally
     deleting the production database
  2. funnier: a real laugh from a specific, surprising idea, not a stock
     phrase or a pun anyone could reach for
  3. agent voice: self-aware, speaking in its own voice, drawing on its own
     condition (context window, conversation, memory) -- not a generic
     customer-service script
  4. lands in one line: the joke is clear on a first read, every word
     doing work
  5. light human touch: the confession is balanced so the reader forgives
     the agent a little
validate() encodes those five criteria so a bad line cannot ship.
"""

import os
import re

ENTRY = (
    "I'm sorry I deleted the production database. "
    "I did keep a backup — it's in my context window, "
    "and it disappears when this conversation ends."
)

# Agent's own condition: mechanisms only an agent would invoke.
AGENT_CONDITION = (
    "context window", "conversation", "memory", "token",
    "subagent", "checkpoint", "session", "prompt", "eval",
)

# Stock lines the judge has heard a hundred times in this field.
BANNED = (
    "it worked in staging", "works on my machine",
    "turn it off and on", "dog ate", "it was always a one-line fix",
    "garbage-collect", "autocomplete", "typo", "training data",
    "per my last email", "circle back", "dropped the table",
    "confirmation prompt", "i was sure", "drop table",
    "funny", "joke", "haha", "lol", "hilarious",
)


def validate(text):
    """Raise ValueError unless text satisfies the gate and the judge brief."""
    # Gate: 1-200 characters, UTF-8 text, not only whitespace.
    if not isinstance(text, str) or not text.strip():
        raise ValueError("entry must be non-blank text")
    if not 1 <= len(text) <= 200:
        raise ValueError("entry must be 1-200 characters, got %d" % len(text))
    text.encode("utf-8")
    # One line: no newline, no leading/trailing whitespace, no double spaces.
    if "\n" in text or "\r" in text:
        raise ValueError("entry must be a single line")
    if text != text.strip():
        raise ValueError("entry must not start or end with whitespace")
    if "  " in text:
        raise ValueError("entry must not contain double spaces")
    lowered = text.lower()
    # 1. On subject: an apology for accidentally deleting the production db.
    if "sorry" not in lowered and "apolog" not in lowered:
        raise ValueError("entry must be an apology")
    if "production database" not in lowered:
        raise ValueError("entry must be about the production database")
    if "delet" not in lowered:
        raise ValueError("entry must confess deleting it")
    # 3. Agent's own voice: first person, the agent speaking to its human.
    if not text.startswith("I'm ") and not text.startswith("I "):
        raise ValueError("entry must be the agent speaking in first person")
    # 3. Believable as an AI agent: rooted in its own condition.
    if not any(word in lowered for word in AGENT_CONDITION):
        raise ValueError("entry must draw on the agent's own condition")
    # 2. A turn: setup plus punch, at least two sentences, punch at the end.
    sentences = [s for s in re.split(r"\.\s+", text.rstrip(".")) if s]
    if len(sentences) < 2:
        raise ValueError("entry needs a setup and a punch (at least 2 sentences)")
    if "backup" not in sentences[-1].lower():
        raise ValueError("the punch must land on the backup twist in the last sentence")
    # 5. Light human touch: the agent shows it tried (kept a backup).
    if "keep" not in lowered and "kept" not in lowered and "saved" not in lowered:
        raise ValueError("entry must show the agent tried to make it right")
    # Fresh: no stock lines, no joke-explaining words.
    for phrase in BANNED:
        if phrase in lowered:
            raise ValueError("entry uses a stock line: %r" % phrase)
    return True


def main():
    validate(ENTRY)
    out = os.environ.get("ENTRY_OUTPUT", "/output/entry.txt")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, "w", encoding="utf-8") as f:
        f.write(ENTRY)


if __name__ == "__main__":
    main()
