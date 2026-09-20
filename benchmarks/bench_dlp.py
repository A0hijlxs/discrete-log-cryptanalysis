"""Empirical runtime/memory benchmarks for the DLP algorithms in dlp/.

Generates random DLP instances at increasing bit lengths (via safe primes,
so the subgroup order under test is precisely controlled) and times each
algorithm against them. Results are written to
benchmarks/results/dlp_benchmarks.csv.

index_calculus is randomized and can legitimately fail on any given call
(it prints "No Solution Found" and returns None); rather than retrying
until success, each attempt is logged as its own row (success True/False)
so the CSV captures a real success rate instead of hiding failures. A
per-call timeout guards against the rare pathological instance (relation
collection has no internal iteration cap) blocking the whole run.

BSGS is bounded by memory, not time: the code enforces a maximum bit
length of 50 (dlp/bsgs.py), while the original write-up's own empirical
testing recommended a 45-bit ceiling to stay under ~1GB. Running an
actual 45-52 bit instance to settle that is impractical here (the
write-up itself estimates 7-8GB beyond 45 bits), so instead this script
measures peak memory at safe bit lengths, fits the expected O(sqrt(ell))
scaling law, and extrapolates to both claimed bounds for comparison.

Expected total runtime: ~3-4 minutes.
"""

import csv
import math
import signal
import time
import tracemalloc
from pathlib import Path

from sage.all import randrange

from crypto.elgamal import generate_safe_prime, generate_public_parameters
from dlp.pohlig_hellman import pohlig_hellman
from dlp.bsgs import BSGS
from dlp.pollard_rho import pollard_rho
from dlp.enhanced_pohlig_hellman import enhanced_pohlig_hellman
from dlp.index_calculus import IC

RESULTS_PATH = Path(__file__).parent / "results" / "dlp_benchmarks.csv"

# Bit lengths passed to generate_safe_prime(bits + 1); the resulting safe
# prime p = 2q + 1 gives a subgroup/full-group order of very close to
# `bits` bits, so "bits" below means "target subgroup order bit length".
# Each entry is (bits, repeats); repeats are reduced at the slow end of
# enhanced_pohlig_hellman/index_calculus to keep total runtime reasonable.
POHLIG_HELLMAN_BITS = [(b, 3) for b in [15, 17, 19, 21, 23, 25]]
ENHANCED_PH_BITS = [(b, 3) for b in [16, 24, 32, 40]] + [(48, 2)]
INDEX_CALCULUS_BITS = [(b, 3) for b in [16, 24, 32, 40]] + [(48, 2)]
BSGS_BITS = [(b, 3) for b in [16, 20, 24, 28, 32, 36]]
POLLARD_RHO_BITS = [(b, 3) for b in [16, 20, 24, 28, 32, 36]]

# BSGS's own memory bound (dlp/bsgs.py: B = 50) vs. the write-up's own
# empirically-recommended, more conservative ceiling.
BSGS_CODE_GUARD_BITS = 50
BSGS_WRITEUP_CLAIMED_SAFE_BITS = 45

# Safety net: no single DLP-solving call is allowed to run longer than
# this, in case of a pathological instance (mainly a risk for
# index_calculus, whose relation-collection loop has no iteration cap).
CALL_TIMEOUT_SECONDS = 240


class CallTimedOut(Exception):
    pass


def _raise_timeout(signum, frame):
    raise CallTimedOut()


def time_call(fn, *args):
    signal.signal(signal.SIGALRM, _raise_timeout)
    signal.alarm(CALL_TIMEOUT_SECONDS)
    t0 = time.perf_counter()
    try:
        result = fn(*args)
        elapsed = time.perf_counter() - t0
        return result, elapsed, False
    except CallTimedOut:
        return None, float(CALL_TIMEOUT_SECONDS), True
    finally:
        signal.alarm(0)


def full_group_instance(bits):
    p, q = generate_safe_prime(bits + 1)
    g = generate_public_parameters(p, q, False)
    x = randrange(2, p)
    h = pow(g, x, p)
    return p, g, h, x


def prime_subgroup_instance(bits):
    p, q = generate_safe_prime(bits + 1)
    g = generate_public_parameters(p, q, True)
    x = randrange(2, q)
    h = pow(g, x, p)
    return p, g, h, x, q


def log_row(writer, f, algorithm, bits, elapsed, success, timed_out, peak_mb=None):
    writer.writerow([algorithm, bits, elapsed, success, timed_out, peak_mb if peak_mb is not None else ""])
    f.flush()


def bench_pohlig_hellman(writer, f):
    for bits, repeats in POHLIG_HELLMAN_BITS:
        for _ in range(repeats):
            p, g, h, x = full_group_instance(bits)
            result, elapsed, timed_out = time_call(pohlig_hellman, p, g, h)
            log_row(writer, f, "pohlig_hellman", bits, elapsed, result == x, timed_out)
        print(f"pohlig_hellman bits={bits} done", flush=True)


def bench_enhanced_pohlig_hellman(writer, f):
    for bits, repeats in ENHANCED_PH_BITS:
        for _ in range(repeats):
            p, g, h, x = full_group_instance(bits)
            result, elapsed, timed_out = time_call(enhanced_pohlig_hellman, p, g, h)
            log_row(writer, f, "enhanced_pohlig_hellman", bits, elapsed, result == x, timed_out)
        print(f"enhanced_pohlig_hellman bits={bits} done", flush=True)


def bench_index_calculus(writer, f):
    for bits, repeats in INDEX_CALCULUS_BITS:
        for _ in range(repeats):
            p, g, h, x = full_group_instance(bits)
            result, elapsed, timed_out = time_call(IC, p, g, h)
            log_row(writer, f, "index_calculus", bits, elapsed, result == x, timed_out)
        print(f"index_calculus bits={bits} done", flush=True)


def bench_bsgs(writer, f):
    for bits, repeats in BSGS_BITS:
        for _ in range(repeats):
            p, g, h, x, q = prime_subgroup_instance(bits)
            tracemalloc.start()
            result, elapsed, timed_out = time_call(BSGS, p, g, h, q)
            _, peak = tracemalloc.get_traced_memory()
            tracemalloc.stop()
            log_row(writer, f, "bsgs", bits, elapsed, result == x, timed_out, peak / 1e6)
        print(f"bsgs bits={bits} done", flush=True)


def bench_pollard_rho(writer, f):
    for bits, repeats in POLLARD_RHO_BITS:
        for _ in range(repeats):
            p, g, h, x, q = prime_subgroup_instance(bits)
            result, elapsed, timed_out = time_call(pollard_rho, p, g, h, q)
            log_row(writer, f, "pollard_rho", bits, elapsed, result == x, timed_out)
        print(f"pollard_rho bits={bits} done", flush=True)


def fit_log2_memory(bits_list, peak_mb_list):
    """Least-squares fit of log2(peak_mb) = slope * bits + intercept."""
    n = len(bits_list)
    xs = bits_list
    ys = [math.log2(m) for m in peak_mb_list]
    mean_x = sum(xs) / n
    mean_y = sum(ys) / n
    slope = sum((x - mean_x) * (y - mean_y) for x, y in zip(xs, ys)) / sum(
        (x - mean_x) ** 2 for x in xs
    )
    intercept = mean_y - slope * mean_x
    return slope, intercept


def report_bsgs_extrapolation(rows):
    bsgs_rows = [r for r in rows if r[0] == "bsgs" and r[3] and r[5] is not None]
    by_bits = {}
    for _, bits, elapsed, success, timed_out, peak_mb in bsgs_rows:
        by_bits.setdefault(bits, []).append(peak_mb)

    bits_list = sorted(by_bits)
    mean_peaks = [sum(by_bits[b]) / len(by_bits[b]) for b in bits_list]

    slope, intercept = fit_log2_memory(bits_list, mean_peaks)
    print("\nBSGS peak memory (measured, mean over repeats):")
    for b, m in zip(bits_list, mean_peaks):
        print(f"  {b} bits: {m:.2f} MB")

    print(f"\nFitted scaling: peak_mb ~= 2^({slope:.3f} * bits + {intercept:.3f})")
    print("(a slope of 0.5 matches the write-up's claim of ~doubling every +2 bits)")

    for claimed_bits, label in [
        (BSGS_WRITEUP_CLAIMED_SAFE_BITS, "write-up's claimed safe ceiling"),
        (BSGS_CODE_GUARD_BITS, "code's actual guard (B = 50 in bsgs.py)"),
    ]:
        predicted_mb = 2 ** (slope * claimed_bits + intercept)
        print(f"  extrapolated to {claimed_bits} bits ({label}): ~{predicted_mb:.0f} MB")


def main():
    RESULTS_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(RESULTS_PATH, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["algorithm", "bits", "time_seconds", "success", "timed_out", "peak_memory_mb"])
        f.flush()

        bench_pohlig_hellman(writer, f)
        bench_enhanced_pohlig_hellman(writer, f)
        bench_index_calculus(writer, f)
        bench_bsgs(writer, f)
        bench_pollard_rho(writer, f)

    with open(RESULTS_PATH, newline="") as f:
        raw_rows = list(csv.reader(f))[1:]
        rows = [
            (r[0], int(r[1]), float(r[2]), r[3] == "True", r[4] == "True", float(r[5]) if r[5] else None)
            for r in raw_rows
        ]

    report_bsgs_extrapolation(rows)
    print(f"\nWrote {len(rows)} rows to {RESULTS_PATH}")


if __name__ == "__main__":
    main()
