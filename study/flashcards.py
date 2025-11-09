#!/usr/bin/env python3
import math
import random
import secrets
import sys
import re
from typing import Dict, List, Tuple

# Import everything from terms.py and then discover term strings
try:
    # Add parent directory to path for absolute imports
    import os
    parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    if parent_dir not in sys.path:
        sys.path.insert(0, parent_dir)

    from machineLearning.vocab.terms import *  # noqa: F401,F403
except Exception as e:
    print(f"Failed to import terms.py: {e}")
    sys.exit(1)

def load_terms() -> Dict[str, str]:
    """Prefer a TERMS dict if present; otherwise collect string variables."""
    # If a TERMS dict is defined, use it
    g = globals()
    if "TERMS" in g and isinstance(g["TERMS"], dict):
        return dict(g["TERMS"])

    # Fallback: gather all global string variables from terms.py
    # Filter out dunders and module-level names that aren't study terms
    terms = {}
    for k, v in list(g.items()):
        if k.startswith("_"):
            continue
        if isinstance(v, str):
            # Heuristic: include only lowercase-ish identifiers or camelCase used in your list
            if re.fullmatch(r"[A-Za-z][A-Za-z0-9_]*", k):
                terms[k] = v
    if not terms:
        raise RuntimeError("No terms found. Define a TERMS dict or term=string variables in terms.py.")
    return terms

def caesar_alpha_sum(s: str, shift: int = 5) -> Tuple[int, int]:
    """
    Map letters a->1..z->26 after a Caesar shift by `shift` and sum.
    Returns (sum, letter_count).
    """
    total = 0
    count = 0
    for ch in s.lower():
        if "a" <= ch <= "z":
            idx0 = ord(ch) - ord("a")  # 0..25
            shifted0 = (idx0 + shift) % 26
            val = shifted0 + 1  # 1..26
            total += val
            count += 1
    return total, count

def fib(n: int) -> int:
    """Fibonacci with F1=1, F2=1, n>=1."""
    if n <= 0:
        return 1
    if n <= 2:
        return 1
    a, b = 1, 1
    for _ in range(3, n + 1):
        a, b = b, a + b
    return b

PHI = (1 + 5 ** 0.5) / 2

def whimsical_index(seed: str, n: int) -> int:
    """
    Deterministic index based on your specified recipe:
    idx = ceil(S * Fibonacci(k) * φ) mod n
    where:
      S = sum of Caesar(+5)-shifted letter values,
      k = number of letters in seed,
      φ = golden ratio.
    """
    if n <= 0:
        raise ValueError("Array length n must be positive.")
    S, k = caesar_alpha_sum(seed, shift=5)
    if k == 0:
        # No letters in seed; fall back to a stable hash to avoid zero-information seeds
        h = abs(hash(seed))
        return h % n
    val = S * fib(k) * PHI
    return (math.ceil(val)) % n

def choose_card(pairs: List[Tuple[str, str]], seed: str = None) -> Tuple[str, str]:
    n = len(pairs)
    if n == 0:
        raise RuntimeError("No flashcards available.")
    if seed is None or seed.strip() == "":
        return secrets.choice(pairs)  # cryptographically strong random
    idx = whimsical_index(seed, n)
    return pairs[idx]

def main(argv: List[str]) -> None:
    term_map = load_terms()
    pairs = sorted(term_map.items(), key=lambda kv: kv[0].lower())

    print(f"Loaded {len(pairs)} flashcards.")
    print("Press Enter to draw a random card, or type a seed for deterministic selection. Ctrl+C to quit.")

    try:
        while True:
            user = input("\nSeed (or just Enter): ").strip()
            term, definition = choose_card(pairs, seed=user if user else None)

            print(f"\nTERM: {term}")
            input("Reveal definition (Enter)...")
            print(f"DEFINITION: {definition}")

            again = input("\nAgain? [Y/n]: ").strip().lower()
            if again == "n":
                break
    except KeyboardInterrupt:
        print("\nExiting. Bye!")

if __name__ == "__main__":
    main(sys.argv)
