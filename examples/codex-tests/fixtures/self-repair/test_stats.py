from stats import mean, median

assert mean([1, 2, 3, 4]) == 2.5, f"mean wrong: {mean([1, 2, 3, 4])}"
assert mean([2, 4, 6]) == 4.0, f"mean wrong: {mean([2, 4, 6])}"
assert median([1, 2, 3]) == 2, f"median odd wrong: {median([1, 2, 3])}"
assert median([1, 2, 3, 4]) == 2.5, f"median even wrong: {median([1, 2, 3, 4])}"

print("All tests passed!")
