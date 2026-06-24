def mean(nums):
    # BUG: integer division loses precision
    return sum(nums) // len(nums)


def median(nums):
    s = sorted(nums)
    n = len(s)
    # BUG: doesn't average the two middle values for even-length lists
    return s[n // 2]
