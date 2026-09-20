def retry(fn, *args, attempts=10, **kwargs):
    """Calls a randomized solver up to `attempts` times, returning the first
    non-None result. Some algorithms under test (index calculus, the ElGamal
    collision search) can legitimately fail on any given run and are designed
    to signal that with None rather than raising or returning a wrong answer.
    """
    for _ in range(attempts):
        result = fn(*args, **kwargs)
        if result is not None:
            return result
    return None
