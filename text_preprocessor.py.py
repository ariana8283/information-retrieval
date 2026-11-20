import argparse
import json
import re
from functools import lru_cache


STOP = frozenset("""
i me my myself we our ours ourselves you you're you've you'll you'd your yours yourself
yourselves he him his himself she she's her hers herself it it's its itself they them their
theirs themselves what which who whom this that that'll these those am is are was were be been
being have has had having do does did doing a an the and but if or because as until while of
at by for with about against between into through during before after above below to from up
down in out on off over under again further then once here there when where why how all any
both each few more most other some such no nor not only own same so than too very s t can will
just don don't should should've now d ll m o re ve y ain aren aren't couldn couldn't didn
didn't doesn doesn't hadn hadn't hasn hasn't haven haven't isn isn't ma mightn mightn't mustn
mustn't needn needn't shan shan't shouldn shouldn't wasn wasn't weren weren't won won't
wouldn wouldn't
""".split())

TOKEN = re.compile(r"(?:[A-Za-z]\.){2,}|[A-Za-z0-9]+(?:[-'’][A-Za-z0-9]+)*")
POSS1 = re.compile(r"(?<=[A-Za-z0-9])['’][sS]\b")
POSS2 = re.compile(r"(?<=[sS])['’](?!\w)")
ABBR = re.compile(r"(?:[a-z]\.)+")


def by_length(items):
    return sorted(items, key=len, reverse=True)


STEP2 = {
    "ational": "ate", "tional": "tion", "enci": "ence", "anci": "ance",
    "izer": "ize", "bli": "ble", "alli": "al", "entli": "ent", "eli": "e",
    "ousli": "ous", "ization": "ize", "ation": "ate", "ator": "ate",
    "alism": "al", "iveness": "ive", "fulness": "ful", "ousness": "ous",
    "aliti": "al", "iviti": "ive", "biliti": "ble", "logi": "log"
}
STEP3 = {
    "icate": "ic", "ative": "", "alize": "al", "iciti": "ic",
    "ical": "ic", "ful": "", "ness": ""
}
STEP4 = by_length(
    "al ance ence er ic able ible ant ement ment ent ion ou ism ate iti ous ive ize".split()
)
STEP2 = {key: STEP2[key] for key in by_length(STEP2)}
STEP3 = {key: STEP3[key] for key in by_length(STEP3)}


def form(word):
    result = []
    for index, char in enumerate(word):
        result.append(
            "v" if char in "aeiou" or
            (char == "y" and index and result[index - 1] == "c")
            else "c"
        )
    return "".join(result)


def measure(word):
    return form(word).count("vc")


def cvc(word):
    return form(word)[-3:] == "cvc" and word[-1] not in "wxy"


def double(word):
    return (
        len(word) > 1
        and word[-1] == word[-2]
        and form(word)[-1] == "c"
    )


def longest(word, suffixes):
    return next((suffix for suffix in suffixes if word.endswith(suffix)), None)


@lru_cache(maxsize=None)
def stem(word):
    if len(word) <= 2:
        return word

    if word.endswith(("sses", "ies")):
        word = word[:-2]
    elif word.endswith("s") and not word.endswith("ss"):
        word = word[:-1]

    if word.endswith("eed"):
        if measure(word[:-3]) > 0:
            word = word[:-1]
    else:
        for suffix in ("ed", "ing"):
            if word.endswith(suffix) and "v" in form(word[:-len(suffix)]):
                word = word[:-len(suffix)]
                if word.endswith(("at", "bl", "iz")):
                    word += "e"
                elif double(word) and word[-1] not in "lsz":
                    word = word[:-1]
                elif measure(word) == 1 and cvc(word):
                    word += "e"
                break

    if word.endswith("y") and "v" in form(word[:-1]):
        word = word[:-1] + "i"

    for rules in (STEP2, STEP3):
        suffix = longest(word, rules)
        if suffix and measure(word[:-len(suffix)]) > 0:
            word = word[:-len(suffix)] + rules[suffix]

    suffix = longest(word, STEP4)
    if suffix:
        stem_part = word[:-len(suffix)]
        if (suffix != "ion" or stem_part.endswith(("s", "t"))) and measure(stem_part) > 1:
            word = stem_part

    if word.endswith("e"):
        stem_part = word[:-1]
        amount = measure(stem_part)
        if amount > 1 or (amount == 1 and not cvc(stem_part)):
            word = stem_part

    if measure(word) > 1 and double(word) and word.endswith("l"):
        word = word[:-1]

    return word


def preprocess(text):
    terms = []
    cleaned_text = POSS2.sub("", POSS1.sub("", text))

    for token in TOKEN.findall(cleaned_text):
        token = token.lower()

        if ABBR.fullmatch(token):
            token = token.replace(".", "")

        if token not in STOP:
            terms.append(stem(token) if token.isalpha() else token)

    return terms


TEXTS = {
    "text1": "Friends, Romans, countrymen, lend me your ears;",
    "text2": (
        "John's new U.S.A. laptop is a state-of-the-art device. "
        "The price is high, but the quality is amazing!"
    ),
    "text3": (
        "The authorization for this authorized project is pending. "
        "He authorizes the payments regularly."
    ),
}

GOLD = {
    "text1": ["friend", "roman", "countrymen", "lend", "ear"],
    "text2": [
        "john", "new", "usa", "laptop", "state-of-the-art",
        "devic", "price", "high", "qualiti", "amaz"
    ],
    "text3": ["author", "project", "pend", "payment", "regularli"],
}


def evaluate(output, gold):
    output_set = set(output)
    gold_set = set(gold)
    common = output_set & gold_set

    precision = len(common) / len(output_set) if output_set else 0.0
    recall = len(common) / len(gold_set) if gold_set else 0.0

    return precision, recall, sorted(output_set - gold_set), sorted(gold_set - output_set)


def main():
    parser = argparse.ArgumentParser(
        description="Text preprocessing system for information retrieval."
    )
    parser.add_argument("--file", help="Read input text from a UTF-8 file.")
    parser.add_argument("--text", help="Process a text supplied in the command line.")
    parser.add_argument("--out", default="outputs.json", help="Output JSON filename.")
    args = parser.parse_args()

    if args.file:
        with open(args.file, encoding="utf-8") as file:
            texts = {"text1": file.read()}
        evaluate_samples = False
    elif args.text is not None:
        texts = {"text1": args.text}
        evaluate_samples = False
    else:
        texts = TEXTS
        evaluate_samples = True

    outputs = {}

    for name, text in texts.items():
        processed_terms = preprocess(text)
        outputs[name] = processed_terms

        print("=" * 70)
        print(f"{name}: {text}")
        print(f"  Output terms : {processed_terms}")

        if evaluate_samples:
            precision, recall, extra, missing = evaluate(processed_terms, GOLD[name])
            print(f"  Gold terms   : {GOLD[name]}")
            print(f"  Precision    : {precision:.2f}")
            print(f"  Recall       : {recall:.2f}")
            print(f"  Extra (O-G)  : {extra}")
            print(f"  Missing (G-O): {missing}")

    with open(args.out, "w", encoding="utf-8") as file:
        json.dump(outputs, file, ensure_ascii=False, indent=2)

    print("=" * 70)
    print(f"Saved to {args.out}")


if __name__ == "__main__":
    main()
