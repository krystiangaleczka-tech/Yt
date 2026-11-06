"""Podmienia wiele dni w Studio w miejscu: render i efekty równolegle, wgrywanie do Studio po jednym dniu.

uruchom (Studio musi działać):  python3 docs/filmy/oddzial-c/ujecia/podmien_dni.py <projekt> <dzień> [<dzień> …] [-j 4]
- każdy dzień: podmien_w_miejscu.py … render (klipy + arkusz klatek) i efekty_dni.py <dzień> (wav + json) — w puli procesów;
- gotowy dzień trafia do kolejki: podmien_w_miejscu.py … wgraj, potem efekty_dni.py wgraj <projekt> <dzień>;
- logi: output/zombie-psychiatryk/podmiana/dNN.log; błąd dnia zatrzymuje tylko ten dzień (reszta idzie dalej).
"""
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
RENDER = REPO / "output/zombie-psychiatryk"
args = sys.argv[1:]
jobs = int(args[args.index("-j") + 1]) if "-j" in args else 4
args = [a for i, a in enumerate(args) if a != "-j" and (i == 0 or args[i - 1] != "-j")]
PID, DAYS = args[0], [int(a) for a in args[1:]]
LOGS = RENDER / "podmiana"
LOGS.mkdir(exist_ok=True)


def run(day, cmd, cwd=REPO):
    with open(LOGS / f"d{day:02d}.log", "a") as log:
        log.write(f"\n$ {' '.join(cmd)}\n")
        log.flush()
        return subprocess.run(cmd, cwd=cwd, stdout=log, stderr=subprocess.STDOUT).returncode


MIN_FREE = 700 * 2 ** 20  # dzień to ok. 50 MB klipów w Studio + kopia robocza; dysk jest ciasny


def enough_disk():
    import shutil
    return shutil.disk_usage(REPO).free > MIN_FREE


def prepare(day):
    if not enough_disk():
        return day, "mało miejsca na dysku"
    if run(day, [sys.executable, str(HERE / "podmien_w_miejscu.py"), str(day), PID, "render"]):
        return day, "render"
    if run(day, [sys.executable, "efekty_dni.py", str(day)], cwd=RENDER):
        return day, "efekty"
    return day, None


failed = {}
with ThreadPoolExecutor(jobs) as pool:
    for fut in as_completed([pool.submit(prepare, d) for d in DAYS]):
        day, err = fut.result()
        if err:
            failed[day] = err
            print(f"dzień {day}: błąd ({err}) — {LOGS / f'd{day:02d}.log'}", flush=True)
            continue
        # wgrywanie po kolei (wątek główny): Studio ma jedną rewizję projektu
        if not enough_disk():
            failed[day] = "mało miejsca na dysku (wyrenderowany, niewgrany)"
        elif run(day, [sys.executable, str(HERE / "podmien_w_miejscu.py"), str(day), PID, "wgraj"]):
            failed[day] = "wgraj"
        elif run(day, [sys.executable, "efekty_dni.py", "wgraj", PID, str(day)], cwd=RENDER):
            failed[day] = "efekty wgraj"
        print(f"dzień {day}: {'gotowy' if day not in failed else 'błąd: ' + failed[day]}", flush=True)
print(f"gotowe: {len(DAYS) - len(failed)}/{len(DAYS)}" + (f" | błędy: {failed}" if failed else ""), flush=True)
sys.exit(1 if failed else 0)
