"""
Multi-Criteria Option Ranking System
------------------------------------
A reusable decision engine: define criteria (benefit or cost) with weights,
score each option, then normalise, rank, run a sensitivity analysis and get
a plain-language explanation.

Data structures (nested dictionaries):
    criteria = {"Price": {"weight": 8, "type": "cost"}, ...}
    options  = {"Laptop A": {"Price": 60000, "Battery": 9}, ...}
"""

VALID_TYPES = ("benefit", "cost")


# ---------------------------------------------------------------- validation
def validate_criteria(criteria):
    """Return a list of problems found in the criteria dictionary."""
    problems = []
    if not criteria:
        problems.append("No criteria defined.")
    for name, info in criteria.items():
        if info.get("type") not in VALID_TYPES:
            problems.append(f"'{name}': type must be 'benefit' or 'cost'.")
        w = info.get("weight")
        if not isinstance(w, (int, float)) or w < 0:
            problems.append(f"'{name}': weight must be a number >= 0.")
    if criteria and all(i.get("weight", 0) == 0 for i in criteria.values()):
        problems.append("At least one weight must be above zero.")
    return problems


def validate_options(options, criteria):
    """Check every option has a numeric score for every criterion."""
    problems = []
    if len(options) < 2:
        problems.append("Need at least two options to compare.")
    for opt, scores in options.items():
        for crit in criteria:
            if crit not in scores:
                problems.append(f"'{opt}' is missing a score for '{crit}'.")
            elif not isinstance(scores[crit], (int, float)):
                problems.append(f"'{opt}' / '{crit}': score must be numeric.")
    return problems


# ------------------------------------------------------------- calculations
def normalise_weights(criteria, overrides=None):
    """Turn raw weights into fractions that add up to 1.
    `overrides` lets a scenario replace some raw weights."""
    raw = {c: info["weight"] for c, info in criteria.items()}
    if overrides:
        raw.update(overrides)
    total = sum(raw.values())
    return {c: w / total for c, w in raw.items()}


def normalise_scores(options, criteria):
    """Min-max scale each criterion to 0..1 (1 = best).
    Benefit: higher raw value is better. Cost: lower raw value is better."""
    result = {opt: {} for opt in options}
    for crit, info in criteria.items():
        values = [options[o][crit] for o in options]
        low, high = min(values), max(values)
        for opt in options:
            x = options[opt][crit]
            if high == low:
                result[opt][crit] = 1.0      # all tied: no one is penalised
            elif info["type"] == "benefit":
                result[opt][crit] = (x - low) / (high - low)
            else:
                result[opt][crit] = (high - x) / (high - low)
    return result


def weighted_totals(normalised, weights):
    """Return {option: total} using the normalised weights."""
    totals = {}
    for opt, scores in normalised.items():
        total = 0.0
        for crit, value in scores.items():
            total += value * weights[crit]
        totals[opt] = total
    return totals


def rank(totals):
    """Sort options best-first. Returns list of (option, total)."""
    return sorted(totals.items(), key=lambda pair: pair[1], reverse=True)


def evaluate(options, criteria, weight_overrides=None):
    """Full pipeline for one set of priorities."""
    weights = normalise_weights(criteria, weight_overrides)
    normalised = normalise_scores(options, criteria)
    totals = weighted_totals(normalised, weights)
    return {
        "weights": weights,
        "normalised": normalised,
        "totals": totals,
        "ranking": rank(totals),
    }


# -------------------------------------------------------------- sensitivity
def scenario_comparison(options, criteria, scenarios):
    """Run named scenarios, e.g. {"Budget first": {"Price": 30}}.
    Returns {scenario_name: ranking}."""
    outcomes = {}
    for name, overrides in scenarios.items():
        outcomes[name] = evaluate(options, criteria, overrides)["ranking"]
    return outcomes


def one_at_a_time(options, criteria, change=0.5):
    """Raise and lower each weight by `change` (50% default) and note
    every case in which the overall winner changes."""
    base_winner = evaluate(options, criteria)["ranking"][0][0]
    flips = []
    for crit, info in criteria.items():
        for label, factor in (("up", 1 + change), ("down", 1 - change)):
            new_w = {crit: info["weight"] * factor}
            winner = evaluate(options, criteria, new_w)["ranking"][0][0]
            if winner != base_winner:
                flips.append((crit, label, winner))
    return base_winner, flips


# ------------------------------------------------------------- explanation
def explain(options, criteria, result):
    """Plain-language summary of the ranking."""
    ranking = result["ranking"]
    weights = result["weights"]
    norm = result["normalised"]
    winner, win_score = ranking[0]
    runner, run_score = ranking[1]

    # contribution of each criterion to the winner
    contrib = {c: norm[winner][c] * weights[c] for c in criteria}
    best_c = max(contrib, key=contrib.get)
    weak_c = min(criteria, key=lambda c: norm[winner][c])

    lines = [f"{winner} ranks first with a score of {win_score:.3f}, "
             f"ahead of {runner} ({run_score:.3f})."]
    gap = win_score - run_score
    if gap < 0.05:
        lines.append("The margin is very small, so treat this as nearly a tie.")
    elif gap > 0.2:
        lines.append("It is a clear win.")
    kind = criteria[best_c]["type"]
    how = "scores high" if kind == "benefit" else "is cheap/low"
    lines.append(f"Its biggest strength is '{best_c}' (it {how} there and "
                 f"that criterion carries {weights[best_c]*100:.0f}% of the weight).")
    if norm[winner][weak_c] < 0.5:
        lines.append(f"Its weakest area is '{weak_c}', where it is below "
                     f"the middle of the field.")
    return "\n".join(lines)


# ----------------------------------------------------------------- display
def print_ranking(ranking, title="Ranking"):
    print(f"\n{title}")
    print("-" * len(title))
    for pos, (opt, total) in enumerate(ranking, start=1):
        print(f"{pos}. {opt:<20} {total:.3f}")


def run_report(options, criteria, scenarios=None):
    """Validate, evaluate and print everything. Reusable for any decision."""
    problems = validate_criteria(criteria) + validate_options(options, criteria)
    if problems:
        print("Cannot run - fix these first:")
        for p in problems:
            print(" -", p)
        return None

    result = evaluate(options, criteria)
    print("\nWeights used (normalised):")
    for c, w in result["weights"].items():
        print(f"  {c:<15} {w*100:5.1f}%  [{criteria[c]['type']}]")
    print_ranking(result["ranking"], "Final ranking")
    print("\n" + explain(options, criteria, result))

    if scenarios:
        print("\nScenario comparison")
        print("-------------------")
        base_winner = result["ranking"][0][0]
        for name, ranking in scenario_comparison(options, criteria, scenarios).items():
            w = ranking[0][0]
            note = "(unchanged)" if w == base_winner else "<-- WINNER CHANGES"
            print(f"  {name:<22} winner: {w} {note}")

    base, flips = one_at_a_time(options, criteria)
    print("\nSensitivity (each weight changed by +/-50%)")
    if flips:
        for crit, direction, w in flips:
            print(f"  If '{crit}' importance goes {direction}, {w} wins instead.")
        print(f"  Verdict: {base} is NOT fully robust.")
    else:
        print(f"  {base} stays on top in every case - a robust choice.")
    return result


# ------------------------------------------------------------- user input
def ask_number(prompt, minimum=None):
    while True:
        try:
            value = float(input(prompt))
            if minimum is not None and value < minimum:
                print(f"  Enter a value >= {minimum}.")
                continue
            return value
        except ValueError:
            print("  Please enter a number.")


def collect_inputs():
    """Interactive setup so the same program works for any decision."""
    criteria, options = {}, {}
    n = int(ask_number("How many criteria? ", 1))
    for i in range(n):
        name = input(f"Criterion {i+1} name: ").strip()
        while True:
            kind = input("  Type (benefit/cost): ").strip().lower()
            if kind in VALID_TYPES:
                break
            print("  Type must be 'benefit' or 'cost'.")
        weight = ask_number("  Importance weight (e.g. 1-10): ", 0)
        criteria[name] = {"weight": weight, "type": kind}

    m = int(ask_number("How many options? ", 2))
    for i in range(m):
        opt = input(f"Option {i+1} name: ").strip()
        options[opt] = {c: ask_number(f"  {opt} - {c}: ") for c in criteria}
    return options, criteria


# --------------------------------------------------------------------- demo
def demo():
    criteria = {
        "Price":    {"weight": 8, "type": "cost"},
        "Battery":  {"weight": 6, "type": "benefit"},
        "Speed":    {"weight": 9, "type": "benefit"},
        "Weight_kg": {"weight": 4, "type": "cost"},
    }
    options = {
        "Laptop A": {"Price": 55000, "Battery": 8,  "Speed": 7, "Weight_kg": 1.8},
        "Laptop B": {"Price": 75000, "Battery": 10, "Speed": 9, "Weight_kg": 1.4},
        "Laptop C": {"Price": 42000, "Battery": 6,  "Speed": 5, "Weight_kg": 2.1},
    }
    scenarios = {
        "Budget first":     {"Price": 30},
        "Performance first": {"Speed": 30},
        "Portability first": {"Weight_kg": 25, "Battery": 15},
    }
    run_report(options, criteria, scenarios)


if __name__ == "__main__":
    choice = input("Type 'demo' to see an example, or press Enter to enter your own data: ")
    if choice.strip().lower() == "demo":
        demo()
    else:
        opts, crit = collect_inputs()
        run_report(opts, crit, scenarios=None)