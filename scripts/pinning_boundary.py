import sys, time, numpy as np
sys.path.insert(0, "/private/tmp/claude-502/-Users-u5749193-Library-CloudStorage-OneDrive-UniversityofWarwick-Documents-PhD-Project-Summer-Project-2026-Repository/f88775c7-8a23-41b9-a4d5-3b6fa2dbf448/scratchpad")
import matplotlib; matplotlib.use('Agg')
from dimless_defs import *

# Does the pinning threshold move with the DRIVE, or stay put at fixed WIDTH?
#   width-controlled (discreteness) -> eta*theta_c ~ constant, at most log(Pi)
#   energy-controlled (their claim) -> eta*theta_c falls steeply as Pi rises
# Bisect on eta*theta at each Pi.  'propagates' = front advanced > 5 sites.

def propagates(et, Pi_v, T):
    r = run(et/theta, theta, Pi_v, Omega, N=200, T=float(T), save_every=1000)
    if 'error' in r:
        return None
    return (r['pos'][-1] - r['pos'][0]) > 5.0

def threshold(Pi_v, lo=0.05, hi=2.0, iters=7):
    T = float(np.clip(600.0/Pi_v, 2000, 12000))   # weaker drive -> slower -> longer run
    if not propagates(hi, Pi_v, T):
        return None, T, 'no propagation even at hi'
    if propagates(lo, Pi_v, T):
        return None, T, 'propagates even at lo'
    for _ in range(iters):
        mid = np.sqrt(lo*hi)                       # geometric bisection
        if propagates(mid, Pi_v, T):
            hi = mid
        else:
            lo = mid
    return np.sqrt(lo*hi), T, 'ok'

print("Pinning threshold vs drive:  is it width-controlled or energy-controlled?\n")
print("    Pi     eta*theta_c    width_c=sqrt(2*etc)     T      note")
t00 = time.time()
res = []
for Pi_v in [0.03, 0.06, 0.115, 0.20, 0.30]:
    etc, T, note = threshold(Pi_v)
    if etc is None:
        print(f" {Pi_v:6.3f}        --             --          {T:6.0f}   {note}", flush=True)
    else:
        res.append((Pi_v, etc))
        print(f" {Pi_v:6.3f}     {etc:8.4f}       {np.sqrt(2*etc):8.4f}       {T:6.0f}   "
              f"[{time.time()-t00:.0f}s]", flush=True)

if len(res) >= 3:
    P = np.array([r[0] for r in res]); E = np.array([r[1] for r in res])
    print(f"\nPi varied by {P.max()/P.min():.0f}x  ->  eta*theta_c varied by {E.max()/E.min():.2f}x")
    print(f"  width_c range: {np.sqrt(2*E.min()):.3f} .. {np.sqrt(2*E.max()):.3f} lattice spacings")
    sl = np.polyfit(np.log(P), np.log(E), 1)[0]
    print(f"  d(log etc)/d(log Pi) = {sl:+.3f}   (~0 => width-controlled; ~-1 => energy-controlled)")
print(f"\ntotal {time.time()-t00:.0f}s")
