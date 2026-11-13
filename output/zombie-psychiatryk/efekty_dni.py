"""Efekty dźwiękowe dni 1–30 wariantu A (bez lektora): tło miejsca, dźwięk każdego wydarzenia z rozpiski i opisu
kadru, uderzenia zsynchronizowane z ruchem w kadrze, dźwięki ciągnące się przez kilka ujęć (alarm, syrena, agregat,
kołysanka), cisza tam, gdzie rozpiska ją każe (Podręcznik → Rytm 9: ciągłe tło, osobny dźwięk każdego wydarzenia).

uruchom (venv z numpy/scipy, ffmpeg w PATH):
  python -I efekty_dni.py [dni] [-j 4] [--wideo build/en-1440-przed-rigiem]
      → build/efekty/eNN.wav (efekty do miksu z lektorem), eNN_studio.wav (−8 dB pod kwestiami — ścieżka Efekty
        w Studio), eNN.json (co i kiedy brzmi)
Ruch w kadrze: różnice kolejnych klatek wideo dnia (64×36, szarość), cache w build/efekty/ruch_dNN.npy.
Wszystkie dźwięki są syntezowane (bez bibliotek nagrań, bez licencji); ziarno losowe stałe dla dnia.
"""
import argparse
import json
import math
import os
import re
import subprocess
import sys
import wave
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import numpy as np
from scipy.signal import butter, fftconvolve, sosfilt

HERE = Path(__file__).resolve().parent
SR = 44100
FPS = 24
OUT = HERE / "build" / "efekty"


# ============================== synteza ==============================

def _sos(kind, f, order=2):
    return butter(order, f, btype=kind, fs=SR, output="sos")


def bp(x, lo, hi, order=2):
    return sosfilt(_sos("band", [lo, min(hi, SR / 2 - 100)], order), x)


def lp(x, f, order=2):
    return sosfilt(_sos("low", f, order), x)


def hp(x, f, order=2):
    return sosfilt(_sos("high", f, order), x)


def n_(d):
    return max(1, int(d * SR))


def tt(d):
    return np.arange(n_(d)) / SR


def expd(d, tau):
    return np.exp(-tt(d) / tau)


def adsr(n, a=0.01, r=0.05):
    e = np.ones(n)
    na, nr = min(n, n_(a)), min(n, n_(r))
    e[:na] = np.linspace(0, 1, na)
    e[n - nr:] *= np.linspace(1, 0, nr)
    return e


def fit(x, n):
    """Dokładnie n próbek (zaokrąglenia długości generatorów różnią się o próbkę)."""
    return x[:n] if len(x) >= n else np.pad(x, (0, n - len(x)))


def mixa(*parts):
    """Suma dźwięków różnej długości: (dźwięk) albo (dźwięk, przesunięcie w s)."""
    parts = [(p, 0.0) if not isinstance(p, tuple) else p for p in parts]
    n = max(n_(o) + len(x) for x, o in parts)
    out = np.zeros(n)
    for x, o in parts:
        out[n_(o):n_(o) + len(x)] += x
    return out


def brown(n, rng):
    x = np.cumsum(rng.normal(0, 1, n))
    x -= np.convolve(x, np.ones(2000) / 2000, mode="same")
    return x / (np.abs(x).max() + 1e-9)


class S:
    """Generatory pojedynczych dźwięków. Każdy zwraca tablicę float (mono, SR), szczyt ok. 1."""

    def __init__(self, rng):
        self.r = rng

    def thud(self, f=60, d=0.5, tau=0.09, noise=0.5):  # głuche uderzenie
        t = tt(d)
        x = np.sin(2 * np.pi * f * t * (1 + 0.6 * np.exp(-t / 0.03))) + noise * lp(self.r.normal(0, 1, len(t)), 900)
        return x * np.exp(-t / tau)

    def step(self, kind="twardy"):  # krok
        d = 0.16 if kind != "trawa" else 0.22
        x = self.r.normal(0, 1, n_(d))
        if kind == "trawa":
            x = bp(x, 900, 5000) * expd(d, 0.06) * 0.6
        elif kind == "bandaz":
            x = lp(x, 700) * expd(d, 0.03) * 0.5
        else:
            x = bp(x, 150, 3500) * expd(d, 0.025) + 0.6 * self.thud(85, d, 0.02, 0.0)
        return x * self.r.uniform(0.7, 1.0)

    def creak(self, d=1.0, f0=None):  # skrzypienie zawiasu / podłogi
        f0 = f0 or self.r.uniform(180, 420)
        t = tt(d)
        f = f0 * (1 + 0.35 * np.sin(2 * np.pi * self.r.uniform(1.5, 4) * t) + 0.15 * np.sin(2 * np.pi * 11 * t))
        ph = 2 * np.pi * np.cumsum(f) / SR
        x = np.sign(np.sin(ph)) * 0.5 + np.sin(2 * ph) * 0.3
        x = bp(x, 200, 3000) * (0.4 + 0.6 * np.abs(np.sin(2 * np.pi * 7 * t)))
        return x * np.sin(np.pi * t / d) ** 0.6

    def latch(self):  # zatrzask, klamka
        return np.concatenate([self.click(0.6), np.zeros(n_(0.05)), self.thud(140, 0.15, 0.03, 0.8) * 0.6])

    def click(self, amp=1.0):
        x = hp(self.r.normal(0, 1, n_(0.02)), 2000) * expd(0.02, 0.003)
        return amp * x

    def door_close(self):
        return np.concatenate([self.thud(55, 0.7, 0.12, 0.7), np.zeros(n_(0.04)), self.latch()[:n_(0.2)] * 0.5])

    def metal(self, d=1.2, base=None, amp=1.0):  # brzęk metalu (krata, taca, beczka)
        base = base or self.r.uniform(220, 520)
        t = tt(d)
        x = sum(np.sin(2 * np.pi * base * k * t + self.r.uniform(0, 6)) * np.exp(-t / (0.5 / k ** 0.7)) / k
                for k in (1, 2.76, 5.40, 8.93, 13.3))
        x = x + 0.5 * hp(self.r.normal(0, 1, len(t)), 2500) * np.exp(-t / 0.02)
        return amp * x

    def grille(self):  # krata: zgrzyt + szczęk
        return np.concatenate([self.creak(0.6, 520) * 0.5, self.metal(0.8, 300)])

    def keys(self, d=0.6):  # pęk kluczy / klucz w zamku
        x = np.zeros(n_(d))
        for _ in range(9):
            k = self.r.integers(0, max(1, len(x) - n_(0.12)))
            m = self.metal(0.12, self.r.uniform(2000, 4500)) * 0.3
            x[k:k + len(m)] += m[: len(x) - k]
        return x

    def key_turn(self):
        g = bp(self.r.normal(0, 1, n_(0.35)), 800, 4000) * np.abs(np.sin(np.pi * tt(0.35) / 0.35)) * 0.4
        return np.concatenate([self.keys(0.3) * 0.6, g, self.latch()])

    def knock(self, n=3, gap=0.22, f=110):  # pukanie / stuknięcia
        x = np.zeros(n_(gap * n + 0.4))
        for k in range(n):
            h = self.thud(f * self.r.uniform(0.9, 1.1), 0.25, 0.03, 0.9)
            i = n_(k * gap * self.r.uniform(0.85, 1.15))
            x[i:i + len(h)] += h[: len(x) - i]
        return x

    def pounding(self, d, rate=3.0, hands=3):  # walenie w drzwi, wiele rąk, każda w swoim rytmie
        x = np.zeros(n_(d))
        for h in range(hands):
            t = self.r.uniform(0, 0.3)
            while t < d - 0.2:
                b = self.thud(self.r.uniform(55, 90), 0.3, 0.05, 1.0) * self.r.uniform(0.5, 1.0)
                i = n_(t)
                x[i:i + len(b)] += b[: len(x) - i]
                t += self.r.uniform(0.6, 1.4) / rate * hands
        return x

    def bang(self, big=1.0):  # huk, trzask drzwi
        d = 1.2
        t = tt(d)
        x = self.thud(42, d, 0.18 * big, 0.6) + 0.6 * lp(self.r.normal(0, 1, len(t)), 2500) * np.exp(-t / 0.05)
        return x

    def crash(self, d=1.4):  # regał: huk + sypiące się rzeczy
        x = self.bang(1.2)
        x = np.concatenate([x, np.zeros(n_(max(0, d - 1.2)))])
        for _ in range(14):
            i = self.r.integers(n_(0.05), len(x) - n_(0.3))
            m = (self.metal(0.25, self.r.uniform(600, 2500)) if self.r.random() < 0.5 else self.thud(self.r.uniform(150, 400), 0.2, 0.02, 1.0)) * self.r.uniform(0.15, 0.4)
            x[i:i + len(m)] += m[: len(x) - i]
        return x

    def roll(self, d=1.5):  # toczenie (beczka, puszka)
        t = tt(d)
        x = lp(self.r.normal(0, 1, len(t)), 400) * (0.6 + 0.4 * np.sin(2 * np.pi * 6 * t) ** 2)
        return x * np.minimum(1, t / 0.1) * np.minimum(1, (d - t) / 0.4) * 1.5

    def glass_thump(self):
        return self.thud(95, 0.4, 0.05, 0.4) + 0.3 * self.metal(0.4, 1900) * 0.3

    def scrape(self, d=1.0):  # szuranie mebli
        t = tt(d)
        x = bp(self.r.normal(0, 1, len(t)), 120, 1400) * (0.5 + 0.5 * np.abs(np.sin(2 * np.pi * 9 * t + self.r.uniform(0, 3))))
        return x * np.sin(np.pi * t / d) ** 0.4 * 1.2

    def shuffle(self, d, n=1, rate=1.6):  # szuranie stóp zarażonych
        x = np.zeros(n_(d))
        for _ in range(n):
            t = self.r.uniform(0, 0.6)
            while t < d - 0.3:
                L = self.r.uniform(0.25, 0.5)
                s = bp(self.r.normal(0, 1, n_(L)), 200, 2200) * np.sin(np.pi * tt(L) / L) * self.r.uniform(0.3, 0.7)
                i = n_(t)
                x[i:i + len(s)] += s[: len(x) - i]
                t += self.r.uniform(0.7, 1.3) / rate
        return x

    def moan(self, d=1.6, f0=None, amp=1.0):  # jęk zarażonego: chrapliwy, opadający, nieludzko długi
        f0 = f0 or self.r.uniform(85, 140)
        t = tt(d)
        f = f0 * (1 - 0.18 * t / d) * (1 + 0.03 * np.sin(2 * np.pi * 5.5 * t))
        ph = 2 * np.pi * np.cumsum(f) / SR
        saw = sum(np.sin(k * ph) / k for k in range(1, 14))
        x = bp(saw, 250, 900) + 0.6 * bp(saw, 1100, 2600) + 0.25 * bp(self.r.normal(0, 1, len(t)), 300, 3000)
        return amp * x * np.sin(np.pi * t / d) ** 0.8 * 0.7

    def groan_human(self, d=1.0):  # stłumiony jęk człowieka
        return lp(self.moan(d, self.r.uniform(110, 150)), 1200) * 0.7

    def breath(self, d=0.8, inhale=True, low=False):
        x = self.r.normal(0, 1, n_(d))
        x = bp(x, 250, 1600) if low else bp(x, 500, 3200)
        e = np.sin(np.pi * tt(d) / d) ** (1.6 if inhale else 0.7)
        return x * e * 0.6

    def breathing(self, d, rate=0.3, amp=1.0, low=False):
        x = np.zeros(n_(d))
        per = 1 / rate
        t = self.r.uniform(0, 0.3)
        k = 0
        while t < d - 0.2:
            L = min(per * 0.45, 1.6)
            b = self.breath(L, inhale=k % 2 == 0, low=low)
            i = n_(t)
            x[i:i + len(b)] += b[: len(x) - i]
            t += per / 2
            k += 1
        return x * amp

    def heartbeat(self, d, bpm=70):
        x = np.zeros(n_(d))
        t = 0.1
        while t < d - 0.3:
            for dt, a in ((0, 1.0), (0.24, 0.7)):
                h = self.thud(48, 0.25, 0.04, 0.0) * a
                i = n_(t + dt)
                x[i:i + len(h)] += h[: len(x) - i]
            t += 60 / bpm
        return x

    def alarm(self, d):  # dzwonek alarmu pożarowego: młoteczek ok. 20 uderzeń/s w dzwon
        t = tt(d)
        bell = sum(np.sin(2 * np.pi * f * t) / k for k, f in enumerate((910, 2480, 4330), 1))
        strike = (np.sin(2 * np.pi * 19 * t) > 0.6).astype(float)
        strike = np.convolve(strike, np.exp(-np.arange(400) / 80), mode="same")
        return bell * np.clip(strike, 0, 1) * 0.6

    def siren(self, d):  # syrena karetki: dwa tony
        t = tt(d)
        f = np.where((t * 1.2).astype(int) % 2 == 0, 650.0, 870.0)
        ph = 2 * np.pi * np.cumsum(f) / SR
        return bp(np.sign(np.sin(ph)) * 0.5 + np.sin(ph), 400, 3000) * 0.5

    def car_alarm(self, d):  # alarm karetki: wycie w górę i w dół
        t = tt(d)
        f = 900 + 500 * np.sin(2 * np.pi * 1.6 * t)
        ph = 2 * np.pi * np.cumsum(f) / SR
        return bp(np.sign(np.sin(ph)), 500, 4000) * 0.4

    def engine(self, d, f0=38, rough=0.6):  # silnik ciężarówki / agregat
        t = tt(d)
        ph = 2 * np.pi * f0 * t * (1 + 0.02 * np.sin(2 * np.pi * 0.3 * t))
        x = sum(np.sin(k * ph + 0.3 * k) / k for k in range(1, 9))
        x = x * (1 + rough * lp(self.r.normal(0, 1, len(t)), 30) * 3)
        return lp(x, 1200) * 0.5 + 0.15 * bp(self.r.normal(0, 1, len(t)), 300, 1800)

    def generator_start(self, d=2.0):  # agregat zapala z rykiem
        t = tt(d)
        rpm = np.minimum(1, t / 0.6) ** 0.5
        ph = 2 * np.pi * np.cumsum(25 + 25 * rpm) / SR
        x = sum(np.sin(k * ph) / k for k in range(1, 10)) * (0.4 + 0.6 * rpm)
        x = x + 0.4 * bp(self.r.normal(0, 1, len(t)), 200, 2500) * rpm
        x[: n_(0.3)] += self.bang(0.6)[: n_(0.3)] * 0.5
        return lp(x, 2500) * 0.7

    def generator_stop(self, d=2.5):
        t = tt(d)
        rpm = np.maximum(0, 1 - t / (d * 0.9)) ** 1.5
        ph = 2 * np.pi * np.cumsum(20 + 30 * rpm) / SR
        return lp(sum(np.sin(k * ph) / k for k in range(1, 8)) * rpm, 1500) * 0.6

    def drone(self, d):  # dron: brzęczenie śmigieł
        t = tt(d)
        f = 185 * (1 + 0.04 * np.sin(2 * np.pi * 0.7 * t))
        ph = 2 * np.pi * np.cumsum(f) / SR
        return bp(sum(np.sin(k * ph) / k for k in range(1, 12)), 150, 4000) * 0.35

    def water(self, d):  # woda z kranu
        t = tt(d)
        x = bp(self.r.normal(0, 1, len(t)), 600, 6000) * (0.8 + 0.2 * lp(self.r.normal(0, 1, len(t)), 8) * 8)
        return x * np.minimum(1, t / 0.08) * np.minimum(1, (d - t) / 0.15) * 0.45

    def gurgle(self, d):  # woda charczy w rurach
        x = np.zeros(n_(d))
        t = 0.0
        while t < d - 0.15:
            L = self.r.uniform(0.05, 0.14)
            f = self.r.uniform(150, 500)
            g = np.sin(2 * np.pi * f * tt(L) * (1 + tt(L) * 4)) * np.sin(np.pi * tt(L) / L)
            i = n_(t)
            x[i:i + len(g)] += g[: len(x) - i] * self.r.uniform(0.3, 0.8)
            t += self.r.uniform(0.04, 0.2)
        return x + 0.3 * lp(self.r.normal(0, 1, len(x)), 300)

    def drip(self):
        f = self.r.uniform(900, 1700)
        t = tt(0.12)
        return np.sin(2 * np.pi * f * t * (1 + 2.5 * t)) * np.exp(-t / 0.02) * 0.5

    def splash(self):
        return bp(self.r.normal(0, 1, n_(0.5)), 300, 5000) * expd(0.5, 0.12) + 0.4 * self.gurgle(0.5)

    def fire(self, d):  # ogień z daleka: trzaski
        x = 0.3 * lp(self.r.normal(0, 1, n_(d)), 500)
        for _ in range(int(d * 14)):
            i = self.r.integers(0, len(x) - 400)
            x[i:i + 300] += hp(self.r.normal(0, 1, 300), 1500) * np.exp(-np.arange(300) / 40) * self.r.uniform(0.2, 1.0)
        return x

    def spark(self):  # trzask iskry + brzęczenie
        x = np.zeros(n_(0.6))
        for _ in range(7):
            i = self.r.integers(0, n_(0.25))
            x[i:i + 600] += hp(self.r.normal(0, 1, 600), 2500) * np.exp(-np.arange(600) / 90)
        t = tt(0.6)
        return x + 0.3 * np.sign(np.sin(2 * np.pi * 100 * t)) * np.exp(-t / 0.15)

    def wires(self):  # wyrywane przewody
        return np.concatenate([self.scrape(0.25) * 0.6, self.spark()])

    def fluor(self, d):  # świetlówka zapala się z brzęczeniem
        t = tt(d)
        x = 0.4 * np.sign(np.sin(2 * np.pi * 100 * t)) * (np.sin(2 * np.pi * 7 * t) > -0.3)
        return lp(x, 3000) * 0.5

    def gunshot(self):
        t = tt(1.5)
        x = self.r.normal(0, 1, len(t)) * np.exp(-t / 0.015) * 1.5 + lp(self.r.normal(0, 1, len(t)), 400) * np.exp(-t / 0.35)
        return x

    def paper(self, d=0.5):
        x = np.zeros(n_(d))
        for _ in range(int(d * 30)):
            i = self.r.integers(0, len(x) - 900)
            x[i:i + 800] += bp(self.r.normal(0, 1, 800), 1500, 7000) * np.exp(-np.arange(800) / 200) * self.r.uniform(0.2, 1)
        return x * 0.5

    def scribble(self, d=1.0):
        t = tt(d)
        return bp(self.r.normal(0, 1, len(t)), 2000, 7000) * (np.sin(2 * np.pi * 5.5 * t) > -0.2) * 0.25

    def cloth(self, d=0.6):
        t = tt(d)
        return bp(self.r.normal(0, 1, len(t)), 300, 2500) * np.sin(np.pi * t / d) ** 1.2 * 0.5

    def whoosh(self, d=0.4):
        t = tt(d)
        return bp(self.r.normal(0, 1, len(t)), 300, 1800) * np.sin(np.pi * t / d) ** 2 * 0.8

    def cans(self, n=4):
        x = np.zeros(n_(0.25 * n + 0.6))
        for k in range(n):
            m = self.metal(0.4, self.r.uniform(900, 1500)) * self.r.uniform(0.3, 0.6)
            i = n_(k * self.r.uniform(0.12, 0.3))
            x[i:i + len(m)] += m[: len(x) - i]
        return x

    def bottles(self, n=4):  # butelki stukają (plastik/szkło)
        x = np.zeros(n_(0.25 * n + 0.4))
        for k in range(n):
            m = self.thud(self.r.uniform(300, 600), 0.15, 0.02, 0.7) * self.r.uniform(0.3, 0.6)
            i = n_(k * self.r.uniform(0.1, 0.25))
            x[i:i + len(m)] += m[: len(x) - i]
        return x

    def cough(self, n=3):
        x = np.zeros(n_(0.34 * n + 0.3))
        for k in range(n):
            L = 0.22
            c = bp(self.r.normal(0, 1, n_(L)), 300, 2500) * np.exp(-tt(L) / 0.06) + 0.4 * self.thud(110, L, 0.05, 0.0)
            i = n_(k * 0.34)
            x[i:i + len(c)] += c[: len(x) - i]
        return x

    def chatter(self, d):  # szczękanie zębów
        x = np.zeros(n_(d))
        t = 0.0
        while t < d - 0.03:
            i = n_(t)
            c = hp(self.r.normal(0, 1, 300), 1800) * np.exp(-np.arange(300) / 50) * 0.5
            x[i:i + 300] += c[: len(x) - i]
            t += self.r.uniform(0.06, 0.1)
        return x

    def squeak(self):
        t = tt(0.25)
        return np.sin(2 * np.pi * (2600 + 900 * np.sin(2 * np.pi * 6 * t)) * t) * np.sin(np.pi * t / 0.25) * 0.3

    def piano(self, notes, dur=1.4, vel=1.0):  # nuty: [(start, midi)]
        end = max(s for s, _ in notes) + dur
        x = np.zeros(n_(end))
        for s, m in notes:
            f = 440 * 2 ** ((m - 69) / 12)
            t = tt(dur)
            tone = sum(np.sin(2 * np.pi * f * k * t * (1 + 0.0004 * k * k)) / k ** 1.3 * np.exp(-t * (1.2 + 0.8 * k))
                       for k in range(1, 8))
            tone[: n_(0.004)] *= np.linspace(0, 1, n_(0.004))
            i = n_(s)
            x[i:i + len(tone)] += vel * tone[: len(x) - i]
        return x * 0.4

    def hum(self, d, notes=(64, 62, 60, 62, 64, 64, 64)):  # nucenie: miękki ton z wibrato
        x = np.zeros(n_(d))
        per = d / len(notes)
        for k, m in enumerate(notes):
            f = 440 * 2 ** ((m - 69) / 12)
            t = tt(per)
            ph = 2 * np.pi * f * t + 0.015 * f / 5 * np.sin(2 * np.pi * 5 * t)
            v = (np.sin(ph) + 0.25 * np.sin(2 * ph)) * np.sin(np.pi * t / per) ** 0.5
            i = n_(k * per)
            x[i:i + len(v)] += lp(v, 1500)[: len(x) - i]
        return x * 0.25

    def cry_far(self, d=2.5):  # krzyk niesiony z daleka
        t = tt(d)
        f = 420 * (1 + 0.25 * np.sin(np.pi * t / d)) * (1 + 0.02 * np.sin(2 * np.pi * 6 * t))
        ph = 2 * np.pi * np.cumsum(f) / SR
        saw = sum(np.sin(k * ph) / k for k in range(1, 10))
        x = bp(saw, 600, 1300) + 0.5 * bp(saw, 2200, 3200)
        return lp(x, 2200) * np.sin(np.pi * t / d) ** 0.5 * 0.6

    def boom(self, d=2.0):  # niskie „dum” karty dnia / żądło
        t = tt(d)
        return np.sin(2 * np.pi * 38 * t * (1 + 0.3 * np.exp(-t / 0.08))) * np.exp(-t / 0.6) + 0.2 * lp(self.r.normal(0, 1, len(t)), 200) * np.exp(-t / 0.3)

    def swell(self, d=1.6):  # narastanie przed cięciem na kolejny dzień
        t = tt(d)
        x = lp(self.r.normal(0, 1, len(t)), 300) * 2 + np.sin(2 * np.pi * 46 * t)
        return x * (t / d) ** 2.5 * 0.5

    def birds(self, d):  # ptaki o świcie: krótkie świergoty w różnych miejscach
        x = np.zeros(n_(d))
        t = self.r.uniform(0.2, 0.8)
        while t < d - 0.4:
            for k in range(self.r.integers(2, 5)):
                L = self.r.uniform(0.05, 0.12)
                tt_ = tt(L)
                f0 = self.r.uniform(2800, 4800)
                ch = np.sin(2 * np.pi * (f0 + self.r.uniform(-900, 900) * tt_ / L) * tt_) * np.sin(np.pi * tt_ / L) ** 2
                i = n_(t + k * self.r.uniform(0.08, 0.14))
                x[i:i + len(ch)] += ch[: len(x) - i] * self.r.uniform(0.3, 0.8)
            t += self.r.uniform(0.6, 1.6)
        return x * 0.4

    def radio(self, d=0.4):  # krótkofalówka: trzask i szum
        t = tt(d)
        return bp(self.r.normal(0, 1, len(t)), 1200, 5000) * np.exp(-t / 0.12) * 0.6


def room_ir(rng, rt=0.5, wet=0.25):
    """Prosty pogłos pomieszczenia: zanikający szum (impuls + ogon)."""
    t = np.arange(int(rt * SR)) / SR
    tail = lp(rng.normal(0, 1, len(t)) * np.exp(-t / (rt / 6.9)), 3500)
    tail *= wet / (np.sqrt(np.sum(tail ** 2)) + 1e-12)  # energia ogona = wet² energii dźwięku bezpośredniego
    tail[0] += 1.0
    return tail


# ============================== ruch w kadrze ==============================

def motion(day, video):
    """Różnica kolejnych klatek (0..1) dla każdej klatki dnia; cache .npy."""
    OUT.mkdir(parents=True, exist_ok=True)
    cache = OUT / f"ruch_d{day:02d}.npy"
    if cache.exists():
        return np.load(cache)
    src = Path(video) / f"v{day:02d}.mp4"
    if not src.exists():
        return None
    raw = subprocess.run(["ffmpeg", "-loglevel", "error", "-i", str(src), "-vf", "scale=64:36,format=gray", "-f", "rawvideo", "-"],
                         capture_output=True, check=True).stdout
    fr = np.frombuffer(raw, np.uint8).reshape(-1, 36, 64).astype(np.float32) / 255
    d = np.zeros(len(fr))
    d[1:] = np.abs(np.diff(fr, axis=0)).mean(axis=(1, 2))
    np.save(cache, d)
    return d


def onsets(mot, a, b, min_gap=0.35):
    """Chwile wyraźnego ruchu w ujęciu [a, b) (s od początku ujęcia), najmocniejsza pierwsza."""
    if mot is None:
        return []
    k0, k1 = int(round(a * FPS)) + 2, int(round(b * FPS)) - 1
    if k1 - k0 < 3:
        return []
    seg = mot[k0:k1]
    base = np.median(seg)
    thr = max(base * 2.5, base + 0.004)
    peaks = [k for k in range(1, len(seg) - 1) if seg[k] > thr and seg[k] >= seg[k - 1] and seg[k] >= seg[k + 1]]
    peaks.sort(key=lambda k: -seg[k])
    out = []
    for k in peaks:
        t = (k0 + k) / FPS - a
        if all(abs(t - o) > min_gap for o in out):
            out.append(t)
    return out


def active(mot, a, b):
    """Odsetek klatek ujęcia z ruchem większym niż kamera z ręki."""
    if mot is None:
        return 0.0
    k0, k1 = int(round(a * FPS)) + 1, int(round(b * FPS))
    seg = mot[k0:k1]
    return float((seg > 0.003).mean()) if len(seg) else 0.0


# ============================== miejsce i tło ==============================

def place(day, desc, look):
    import dzien_base as B
    d = desc.lower()
    if look is None:
        return "karta"
    if re.search(r"podwórz|\bbram|\bpłot|trawni|trawie|\bdach|na zewnątrz|ciężarówk|karetk|\blas\b|nad lasem", d):
        return "dwor"
    if re.search(r"piwnic|apteka|apteki|aptece|rozdzielni|chłodni|magazyn|pralni|rury|rurami|skrzydło techniczne", d):
        return "piwnica"
    if re.search(r"korytarz|\bsal[iaę]?\b|świetlic|pokój socjalny|pokoju socjalnym|portierni|dyżurk|parter|kuchni|łazienk|"
                 r"izolatk|schod|łącznik|gabinet", d):
        return "noc" if look in (B.DARK, B.NIGHT) else "oddzial"
    if look in (B.DARK, B.NIGHT):
        return "noc"
    if look in (B.BASE, B.CELL):
        return "piwnica" if day <= 14 else "oddzial"  # do d14 grupa mieszka w aptece w piwnicy, potem w pokoju socjalnym
    return "oddzial"


def bed(kind, day, n, t0, rng, desc):
    """Tło ujęcia (bez buczeń sieciowych — dawały głośne bzyczenie): szum pomieszczenia, kapanie w piwnicy, wiatr
    nocą i na dworze, agregat wojska za płotem od d21, płonące miasto od d20. Głośność ustawia plan miksu."""
    ts = t0 + np.arange(n) / SR
    d = desc.lower()
    room = lp(brown(n, rng), 600)
    if kind == "karta":
        return room
    x = room
    if kind == "piwnica":
        sy = S(rng)
        tdrip = rng.uniform(0.3, 1.8)
        while tdrip < n / SR - 0.2:  # kapanie w piwnicy
            dr = sy.drip() * rng.uniform(0.6, 1.4)
            i = n_(tdrip)
            x[i:i + len(dr)] += dr[: n - i] * 0.5
            tdrip += rng.uniform(1.6, 4.5)
    elif kind == "noc":
        gust = 0.6 + 0.4 * np.sin(2 * np.pi * 0.07 * ts + 1.3) * np.sin(2 * np.pi * 0.023 * ts)
        x = room + 1.6 * lp(brown(n, rng), 900) * gust
    elif kind == "dwor":
        gust = 0.6 + 0.4 * np.sin(2 * np.pi * 0.11 * ts + 0.4)
        x = room * 0.6 + 0.8 * bp(rng.normal(0, 1, n), 150, 900) * gust
        if day >= 21:  # agregat wojska za płotem (warsztat: od d21) — daleki, przytłumiony
            x = x + 0.3 * lp(fit(S(rng).engine(n / SR, 32, 0.2), n), 220)
    if day >= 20 and kind in ("dwor", "noc") and re.search(r"miast|okn|dach|podwórz", d):
        x = x + 0.25 * fit(S(rng).fire(n / SR), n)  # miasto płonie w oddali
    return x


# ============================== plan miksu ==============================
# Głośność każdego dźwięku = skala zdarzenia × napięcie sceny × tempo ujęcia (Podręcznik → Rytm, „Głośność dźwięku”).
ARC = {1: 7, 2: 4, 3: 5, 4: 6, 5: 5, 6: 6, 7: 5, 8: 7, 9: 7, 10: 7, 11: 8, 12: 5, 13: 7, 14: 10, 15: 4, 16: 7, 17: 8,
       18: 3, 19: 5, 20: 6, 21: 7, 22: 6, 23: 8, 24: 7, 25: 7, 26: 5, 27: 6, 28: 4, 29: 8, 30: 10}  # do_studio.py
SKALA = {  # nazwa zdarzenia → skala
    "małe": {"krok", "materiał", "papier", "pisanie", "rzecz w dłoni", "miska po blacie", "oddech", "drugi oddech",
             "wydech po wstrzymaniu", "zapłon świetlówki", "stukanie w rury", "szczękanie zębów", "torba",
             "rzeczy do torby", "przełącznik", "krótkofalówka", "zamach", "ptaki o świcie", "pisk", "klamka", "klucze",
             "gotowanie", "wiatr", "cisza: serce", "lina"},
    "duże": {"huk beczki", "huk regału", "beczka toczy się", "trzask szafy", "agregat zapala", "agregat gaśnie",
             "zamki puszczają", "strzał", "akord", "drzwi zamykają się", "uderzenie", "walenie w drzwi", "krzyk"},
}
POZIOM = {"małe": -34.0, "średnie": -27.0, "duże": -19.0}  # dBFS (RMS w czasie trwania dźwięku) przy napięciu 5/10
TLO = {"piwnica": -47.0, "oddzial": -49.0, "noc": -43.0, "dwor": -41.0, "karta": -62.0}
LOUD = re.compile(r"alarm|huk|biegn|krzyk|walenie|ucieka|wbiegają|ruszają|strzał|zatrzaskuj|przemian|ugryz|wyrywa|"
                  r"przewraca|rzuca|szarp|wali")


def skala(name):
    for k, names in SKALA.items():
        if name in names:
            return k
    return "średnie"


def scenes_of(day):
    """Numery ujęć każdej sceny rozpiski dnia: [(tytuł sceny, [i…])]."""
    import dzien_base as B
    d = B.day_tuple(day)
    out, i = [], 0
    for stitle, place_, beats in d[2]:
        idx = []
        for _, shots in beats:
            idx += list(range(i, i + len(shots)))
            i += len(shots)
        out.append((stitle, idx))
    return out


def mix_plan(day, rows, durs):
    """Napięcie (0–10) i tempo każdego ujęcia: dzień (krzywa filmu) + ruch kamery + słowa akcji, wygładzone w scenie."""
    raw = []
    for (kadr, ruch, sec, desc, sound) in rows:
        if kadr == "TYT":
            raw.append(0.0)
            continue
        v = ARC[day] - 0.5
        v += {"szarp": 2.0, "drg": 2.0, "jaz": 1.0, "pan": 0.5, "ręka": 0.5, "naj": 0.5}.get(ruch, 0.0)
        txt = (desc + " " + (sound or "")).lower()
        if LOUD.search(txt):
            v += 1.0
        if (sound or "").strip().lower().startswith("cisza"):
            v -= 2.0
        elif "„" in (sound or "") and not LOUD.search(txt):
            v -= 1.0  # rozmowa: efekty schodzą pod głos
        raw.append(max(0.0, min(10.0, v)))
    plan = [None] * len(rows)
    for stitle, idx in scenes_of(day):
        med = float(np.median([durs[i] for i in idx])) if idx else 1.0
        for k, i in enumerate(idx):
            nb = [raw[j] for j in idx[max(0, k - 1):k + 2] if rows[j][0] != "TYT"] or [raw[i]]
            nap = 0.5 * raw[i] + 0.5 * float(np.mean(nb))
            tempo = "szybkie" if durs[i] < 0.6 * med else ("wolne" if durs[i] > 1.5 * med else "równe")
            plan[i] = {"scena": stitle, "napiecie": round(nap, 1), "tempo": tempo}
    return plan


def target_db(name, nap, tempo, g):
    """dBFS zdarzenia: skala + 0,8 dB na punkt napięcia ponad 5 + tempo; g — dawny względny poziom (blisko/daleko)."""
    db = POZIOM[skala(name)] + 0.8 * (nap - 5) + {"szybkie": 1.5, "wolne": -1.0}.get(tempo, 0.0)
    db += 0.5 * 20 * math.log10(max(g, 1e-3) / 0.35)  # połowa dawnej różnicy blisko/daleko w obrębie skali
    return min(db, -9.0)


def at_level(x, db):
    """Skaluje dźwięk tak, by jego RMS w czasie trwania (próbki powyżej 10% szczytu) miał db dBFS."""
    a = np.abs(x)
    if not len(x) or a.max() == 0:
        return x
    act = x[a > 0.1 * a.max()]
    rms = math.sqrt(float(np.mean(act ** 2))) + 1e-12
    return x * (10 ** (db / 20) / rms)


# ============================== zdarzenia ==============================

def rules(day, i, kadr, desc, sound, T, ons, act, sy, look_kind, ruch="stat"):
    """Lista (czas w ujęciu, dźwięk, głośność, nazwa) dla ujęcia."""
    d = desc.lower()
    s = sound.lower() if sound and not sound.startswith("L:") and "„" not in sound else ""
    allx = d + " | " + s
    ev = []
    o = ons[0] if ons else None

    def at(default):
        return o if o is not None and o < T - 0.15 else default * T

    def add(t, x, g, name):
        ev.append((max(0.0, t), x, g, name))

    floor = "trawa" if re.search(r"trawi|trawni|podwórz", d) else ("bandaz" if "bandaż" in d else "twardy")
    # --- kroki: idzie/biegnie, gdy w kadrze rzeczywiście jest ruch ---
    run = re.search(r"biegnie|biegną|biegiem|wbiegają|ucieka|wypada|rzuca się do", allx)
    walk = re.search(r"idzie|idą|schodz|wchodz|wychodz|kroki|przechodzi|mija|cofa się|cofają|podchodzi|zbliża|wnosi|niesie|"
                     r"skręca|odchodzi|wlewają|na schodach|po schodach|wstaje|staje", allx)
    if (run or walk) and (act > 0.12 or ruch in ("jaz", "pan") or "kroki" in s):
        gap = 0.3 if run else (0.62 if "wolno" in d or "powoli" in d or "ostrożn" in d else 0.48)
        if "przyspieszają" in s:
            gap = 0.36
        t = 0.1 + sy.r.uniform(0, 0.15)
        n_people = 1 + (1 if re.search(r" i |grupa|wszyscy|razem|każdy", d) else 0)
        while t < T - 0.1:
            g = 0.35 if floor == "twardy" else 0.25
            if "oddalają" in s:
                g *= max(0.15, 1 - t / T)
            add(t, sy.step(floor), g, "krok")
            if n_people > 1:
                add(t + gap * 0.47, sy.step(floor), g * 0.7, "krok")
            t += gap * sy.r.uniform(0.9, 1.1)
    # --- drzwi, kraty, zamki, klucze ---
    door = False
    if re.search(r"drzwi|drzwiczk|klapę|klapa", d) and not re.search(r"wal[ąi]|walenie|w drzwiach|przy drzwiach|oparty o drzwi", d):
        door = True
        if re.search(r"zatrzaskuj|zamyka\b|zamykają|trzaska|zatrzaś|zamknął", allx):
            add(at(0.5), sy.door_close(), 0.55, "drzwi zamykają się")
        elif re.search(r"otwier|uchyla|otwarte|wychodzi|wchodzi|wypada|otwiera", d):
            add(at(0.25) - 0.2, sy.creak(1.1), 0.18, "skrzyp drzwi")
            add(at(0.25) - 0.25, sy.latch(), 0.3, "klamka")
    if "krat" in d and re.search(r"uchyla|otwier|zamyka|zasuwa", d):
        add(at(0.3), sy.grille(), 0.35, "krata")
    if re.search(r"klucz|zamek|zamka|zamków|kłódk", allx) and re.search(r"otwier|przekręca|zgrzyt|szczęk|trzask|zamyka|kłódk|zatrzaskuj", allx):
        door = True
        add(at(0.35) + (0.25 if ev else 0.0), sy.key_turn() if "klucz" in allx else sy.latch(), 0.4, "zamek")
    if re.search(r"pęk kluczy|klucze", d):
        add(at(0.4), sy.keys(0.5), 0.2, "klucze")
    # --- uderzenia, huki ---
    if re.search(r"walenie|wal[ąi] w|uderzenia w drzwi|napór|łomot", allx):
        add(0.0, sy.pounding(T, 3.0, 3 if "dziesią" not in allx else 6), 0.4 if "z pięter" not in allx else 0.18, "walenie w drzwi")
    if "huk beczki" in s or "beczk" in d and re.search(r"rzuca|toczy", d):
        add(at(0.2), sy.roll(min(1.5, T)), 0.4, "beczka toczy się")
        add(at(0.2) + min(1.2, T * 0.6), sy.bang(1.0), 0.7, "huk beczki")
    elif "huk regału" in s or "regał" in d and re.search(r"przewracają|przewraca|upada", d):
        add(at(0.3), sy.crash(), 0.75, "huk regału")
    elif re.search(r"akord", allx):
        add(at(0.15), sy.piano([(0.0, 57), (0.0, 60), (0.0, 64), (0.01, 45)], 2.5, 1.2), 0.5, "akord")
    elif not door and (re.search(r"\bhuk\b|głuche uderzenie|pojedyncze uderzenie|trzask\b", s) or re.search(r"uderza|spada|upada|przewraca", d)):
        add(at(0.35), sy.bang(0.8) if "huk" in s else sy.thud(70, 0.6, 0.08), 0.55, "uderzenie")
    if re.search(r"uderzenie w szybę|uderza w szybę|dłonie na szyb|o szybę", allx):
        add(at(0.3), sy.glass_thump(), 0.5, "szyba")
    if re.search(r"stuk|stuknię|stuka", allx):
        n = 2 if "dwa" in s else (5 if "nierówne" in s else 3)
        f = 70 if "głuche" in s or "beczk" in d else 140
        add(at(0.3), sy.knock(n, 0.28 if "nierówne" not in s else 0.4, f), 0.4, "stuki")
    if re.search(r"\brur[yaę]?\b|rurami", d):  # stukanie w rury: w chwilach, gdy rury w kadrze drżą
        for t in sorted(ons[:4]) or [0.2, 1.3]:
            add(t, sy.knock(2, 0.12, 230) * 0.7, 0.25, "stukanie w rury")
    # --- metal, puszki, butelki ---
    if "brzęk tacek" in s or "tack" in d:
        add(at(0.4), mixa(sy.metal(0.9, 700), (sy.metal(0.9, 900), 0.12)), 0.35, "tacki")
    elif "butelki" in d or ("brzęk" in s and "paczk" in d):
        add(at(0.35), sy.bottles(5), 0.35, "butelki")
    elif "puszk" in d or "konserw" in d or "brzęk" in s:
        add(at(0.35), sy.cans(3), 0.35, "puszki")
        if "toczenie" in s or "toczy" in d:
            add(at(0.35) + 0.2, sy.roll(min(1.6, T - 0.3)) * 0.4, 0.3, "puszka toczy się")
    # --- szuranie ---
    if "szuranie mebli" in s or re.search(r"barykad|przesuwa szafk|kanapą|przesuwa", d):
        add(at(0.2), sy.scrape(min(1.6, T * 0.8)), 0.45, "szuranie mebli")
    if "szuranie liny" in s or "lin" in d and "szuran" in s:
        add(0.2, sy.scrape(min(1.5, T - 0.3)) * 0.6, 0.3, "lina")
    zomb = re.search(r"zarażen|zarażon|salowy|tłum|postaci|głowy", d)
    if "szuranie" in s or (zomb and act > 0.25 and not re.search(r"stoją|stoi", d)):
        many = re.search(r"dziesiąt|tłum|kilkadziesiąt|setki|wszystkich|wlewają|kilkunastu", allx)
        add(0.0, sy.shuffle(T, 5 if many else 2), 0.3 if many else 0.2, "szuranie stóp")
    if zomb and T > 2.2 and "cisza" not in s and day >= 1 and sy.r.random() < 0.55:
        add(sy.r.uniform(0.3, max(0.4, T - 1.6)), sy.moan(sy.r.uniform(1.2, 2.0)), 0.12, "jęk zarażonego")
    # --- jęki, kaszel, oddechy ---
    if "jęk" in s:
        if re.search(r"z sal|zarażon", allx):
            add(0.2, sy.moan(min(2.2, T - 0.2)), 0.2, "jęk z sal")
        else:
            add(at(0.3), sy.groan_human(min(1.2, T * 0.6)), 0.25 if "stłumiony" in s else 0.35, "jęk")
    if "kaszel" in s or "kaszle" in d:
        add(at(0.2), sy.cough(3), 0.35, "kaszel")
    if "szczękanie" in s or "szczęka zębami" in d:
        add(0.1, sy.chatter(T - 0.2), 0.18, "szczękanie zębów")
    if re.search(r"oddech|oddycha|dyszy|bez tchu", allx) and "nie oddycha" not in d:
        loud = re.search(r"głośny|głośno", allx)
        fast = re.search(r"szybki|dyszy|bez tchu|ciężko|wypada", allx)
        slow = re.search(r"woln|spokojn|wspólny|razem|przepon|rytm", allx)
        rate = 0.75 if fast else (0.2 if slow else 0.35)
        g = 0.32 if loud else (0.12 if slow else 0.16)
        add(0.05, sy.breathing(T - 0.1, rate, 1.0, low=bool(slow)), g, "oddech")
        if "wspólny" in s or "razem" in d:
            add(0.2, sy.breathing(T - 0.3, rate, 1.0, low=True), g * 0.8, "drugi oddech")
    if re.search(r"wstrzymuje oddech|wstrzymany oddech|zamiera", d):
        add(T - 0.6, sy.breath(0.55, inhale=False), 0.2, "wydech po wstrzymaniu")
    # --- elektryczność, światło, agregat ---
    if "trzask iskry" in s or "iskr" in d:
        add(at(0.3), sy.spark(), 0.4, "iskry")
    if re.search(r"wyrywa przewody|przewody z centrali", d):
        add(at(0.3), sy.wires(), 0.45, "przewody")
    if re.search(r"przełącznik|włącza (światło|lampę|latark)|gasi lampę|gasi latark|zapala latark|wyłącza", d):
        add(at(0.3), mixa(sy.thud(200, 0.15, 0.015, 1.0) * 0.5, sy.click(0.8)), 0.4, "przełącznik")
    if "bzyczenie świetlówek" in s or re.search(r"świetlówki zapalają", d):
        for k in range(4):
            add(0.15 + k * T / 5, sy.click(1.0), 0.25, "zapłon świetlówki")
        add(0.15, sy.fluor(T - 0.2), 0.12, "świetlówki")
    if "ryk agregatu" in s:
        add(0.1, sy.generator_start(min(2.2, T)), 0.6, "agregat zapala")
    if "agregat milknie" in s or "agregat gaśnie" in d:
        add(0.1, sy.generator_stop(min(2.5, T)), 0.5, "agregat gaśnie")
        add(0.6, sy.knock(6, 0.12, 180) * 0.6, 0.3, "zamki puszczają")
    if "szum agregatu chłodni" in s:
        add(0.0, sy.engine(T, 48, 0.2) * 0.4, 0.15, "agregat chłodni")
    # --- woda ---
    if "woda charczy" in s or "charczenie rury" in s:
        add(0.1, sy.gurgle(T - 0.2), 0.3, "rury")
    elif re.search(r"kran|napełnia|nabiera", d):
        add(0.1, sy.water(T - 0.2), 0.25, "woda z kranu")
    if "chlupot" in s or "zanurza" in d:
        add(at(0.3), sy.splash(), 0.35, "chlupot")
    if re.search(r"gotuje|para nad garnkiem|gotuje wodę", d):
        add(0.0, mixa(lp(sy.r.normal(0, 1, n_(T)), 1500) * 0.3, sy.gurgle(T) * 0.1), 0.12, "gotowanie")
    # --- drobiazgi: papier, ołówek, ubranie, worek ---
    if re.search(r"zapisuje|dopisuje|pisze|kreśli|notes|ołówek|maluje|kreskę|kreski", d):
        add(at(0.3), sy.scribble(min(1.4, T * 0.6)), 0.2, "pisanie")
    if re.search(r"kartk|plan |planie|przepustk|prześcierad|rozkłada|wywiesza", d):
        add(at(0.2), sy.paper(0.5), 0.25, "papier")
    if re.search(r"odsuwa|przesuwa (?!szafk)|miskę|miska|porcj", d):
        add(at(0.3), sy.scrape(0.35) * 0.5, 0.25, "miska po blacie")
    if re.search(r"chwyta|bierze|podnosi (?!wzrok|głow)|odkłada|kładzie (?!dłoń|mu dłoń|kubie)", d):
        add(at(0.3), sy.thud(240, 0.2, 0.025, 0.8), 0.25, "rzecz w dłoni")
    if "krat" in d and re.search(r"staje|opiera|chwyta|trzyma", d):
        add(at(0.3), sy.metal(0.6, 330) * 0.6, 0.25, "krata drży")
    if re.search(r"kurtk|koc|ręcznik|bandaż|owija|przytula|obejmuje|okład|rękaw", d):
        add(at(0.3), sy.cloth(0.7), 0.25, "materiał")
    if re.search(r"pakuje|ładuje|worek|worka|torb|wózek", d):
        add(at(0.3), sy.cloth(0.5), 0.25, "torba")
        add(at(0.3) + 0.4, sy.cans(2) if "konserw" in d else sy.thud(260, 0.2, 0.03, 0.8), 0.25, "rzeczy do torby")
    if re.search(r"kanist", d) and not re.search(r"kran|napełnia", d):
        add(at(0.4), sy.thud(160, 0.3, 0.05, 0.6), 0.3, "kanister")
    if re.search(r"rzuca kurtkę|rzuca", d):
        add(at(0.2) - 0.25, sy.whoosh(), 0.3, "zamach")
    if "potyka" in d:
        add(at(0.3), mixa(sy.thud(80, 0.4, 0.05), (sy.step("twardy"), 0.05)), 0.45, "potknięcie")
    if "szamotanina" in s:
        add(0.1, mixa(sy.cloth(T * 0.6), sy.pounding(T * 0.6, 4, 2) * 0.5), 0.4, "szamotanina")
    if "pisk" in s:
        add(at(0.3), sy.squeak(), 0.25, "pisk")
    # --- telefon, radio, megafon ---
    if re.search(r"dzwonek|dzwoni", allx):
        t = 0.2
        while t < T - 0.3:
            ring = np.sin(2 * np.pi * 1180 * tt(0.33)) + np.sin(2 * np.pi * 1420 * tt(0.33))
            add(t, ring * (np.sin(2 * np.pi * 20 * tt(0.33)) > 0), 0.08, "dzwonek")
            t += 0.66
    if kadr != "Z" and re.search(r"krótkofalówk|\(radio\)", allx + (sound or "").lower()):
        add(0.05, sy.radio(0.3), 0.25, "krótkofalówka")
        add(T - 0.35, sy.radio(0.25), 0.2, "krótkofalówka")
    # --- pojazdy, broń, alarm karetki ---
    if re.search(r"\bdron", d) or "warkot" in s:
        add(0.0, sy.drone(T), 0.25, "dron")
    if re.search(r"ciężarówk|silnik", allx):
        add(0.0, sy.engine(T, 36, 0.5), 0.25, "silnik")
    if "strzały" in s or "strzela" in d:
        for k in range(3):
            add(at(0.2) + k * sy.r.uniform(0.35, 0.6), sy.gunshot(), 0.7, "strzał")
    # --- pianino, nucenie ---
    if "pojedyncze ciche dźwięki" in s or "stroi" in d:
        add(0.0, sy.piano([(0.3 + k * 0.9, 57 + k * 2) for k in range(int(T / 0.9))], 1.2, 0.5), 0.25, "strojenie")
    if "nucenie" in s or "nuci" in d:
        add(0.2, sy.hum(T - 0.4), 0.3, "nucenie")
    if "krzyk" in s:
        add(0.4, sy.cry_far(min(2.6, T - 0.4)), 0.25 if "echo" not in s else 0.15, "krzyk")
    if "skrzyp" in s:
        add(at(0.3), sy.creak(0.9, 260 if "podłog" in s else None), 0.25, "skrzyp")
    if "trzask szafy" in s:
        add(at(0.4), sy.bang(0.6), 0.45, "trzask szafy")
    if re.search(r"wschodzi słońce|świt|o świcie", d):
        add(0.0, sy.birds(T), 0.2, "ptaki o świcie")
    if "wiatr" in s:
        add(0.0, lp(sy.r.normal(0, 1, n_(T)), 600) * 2, 0.08, "wiatr")
    if s.strip().startswith("cisza"):
        ev = [(t, x, g * 0.3, name) for t, x, g, name in ev]
    return ev


# ============================== dźwięki ciągłe (kilka ujęć) ==============================

def spans(day, rows):
    """[(ujęcie od, ujęcie do włącznie, rodzaj)] — dźwięki płynące przez cięcia."""
    out = []
    snd = [(r[4] or "").lower() for r in rows]
    desc = [r[3].lower() for r in rows]
    if day == 10:
        a = next((i for i, d in enumerate(desc) if "alarm karetki" in d), None)
        b = next((i for i, d in enumerate(desc) if "zatrzaskują" in d), None)
        if a is not None:
            out.append((a, (b if b is not None else len(rows) - 1), "karetka"))
    if day == 14:
        a = next((i for i, s in enumerate(snd) if s.strip() == "alarm"), None)
        b = next((i for i, s in enumerate(snd) if "alarm milknie" in s), None)
        if a is not None and b is not None:
            out.append((a, b, "alarm"))
        g = next((i for i, s in enumerate(snd) if "ryk agregatu" in s), None)
        if g is not None and b is not None:
            out.append((g + 1, b, "agregat"))
    if day == 27:
        a = next((i for i, s in enumerate(snd) if "alarm na sekundę" in s), None)
        if a is not None:
            out.append((a, a, "alarm_sekunda"))
    if day == 30:
        a = next((i for i, s in enumerate(snd) if "akord i alarm" in s), None)
        b = next((i for i, s in enumerate(snd) if "alarm, potem cisza" in s), None)
        if a is not None and b is not None:
            out.append((a, b, "alarm", 1.6))  # „alarm, potem cisza”: ostatnie 1,6 s ujęcia bez alarmu
            out.append((a, b, "kolysanka", "milknie"))
    return out


SPAN_NEAR = {"alarm": r"alarm|głośnik|świetlic|korytarz|portierni|pianin|klawisz",
             "karetka": r"karetk|kurtka|blach|zarażeni ruszają",
             "agregat": r"agregat|techniczn|beczk|regał",
             "kolysanka": r"pianin|klawisz|świetlic|akord"}


# ============================== składanie dnia ==============================

def day_effects(day, video):
    os.environ.setdefault("FILM_LANG", "en")
    os.environ.setdefault("FILM_RES", "720")
    sys.path.insert(0, str(HERE))
    sys.path.insert(0, str(HERE.parents[1] / "docs/filmy/oddzial-c/ujecia"))
    import importlib

    import dzien_base as B
    m = importlib.import_module(f"render_d{day:02d}")
    rows = B.rows(day)
    rng = np.random.default_rng(5000 + day)
    sy = S(rng)
    n = int(round(m.DUR * FPS) / FPS * SR)
    bedbus = np.zeros(n)
    evbus = np.zeros(n)
    duckmask = np.zeros(n)
    mot = motion(day, video)
    fade = n_(0.12)
    irs = {"piwnica": room_ir(rng, 0.5, 0.4), "oddzial": room_ir(rng, 0.9, 0.5), "noc": room_ir(rng, 1.1, 0.45),
           "dwor": room_ir(rng, 0.3, 0.12), "karta": room_ir(rng, 0.3, 0.0)}
    shots = []
    for i, sc in enumerate(m.SCENES):
        if len(sc) == 4:  # dzień 1 ma własny renderer: okno kwestii w VWIN (en: długość + 0,35 s napisu)
            a, b, ruch, txt = sc
            vs, vl = m.VWIN[i]
            vl = max(0.0, vl - 0.35) if txt else 0.0
        else:
            a, b, ruch, txt, vs, vl = sc
        shots.append((a, b, ruch, txt, vs, vl))
    plan = mix_plan(day, rows, [b - a for a, b, *_ in shots])
    miks = []
    for i, ((a, b, ruch, txt, vs, vl), (kadr, _, sec, desc, sound)) in enumerate(zip(shots, rows)):
        T = b - a
        P = plan[i]
        nap, tempo = P["napiecie"], P["tempo"]
        kind = place(day, desc, m.LOOK[i])
        silent = (sound or "").strip().lower().startswith("cisza")
        bed_db = TLO[kind] + 0.5 * (nap - 5) - (6.0 if silent else 0.0)
        i0, i1 = int(a * SR), min(n, int(b * SR))
        seg = at_level(fit(bed(kind, day, i1 - i0 + fade, a, rng, desc), i1 - i0 + fade), bed_db)
        env = np.ones(len(seg))
        env[:fade] = np.linspace(0, 1, fade)
        env[-fade:] = np.linspace(1, 0, fade)
        j1 = min(n, i0 + len(seg))
        bedbus[i0:j1] += (seg * env)[: j1 - i0]
        if txt and vl > 0:  # okno kwestii (do ściszenia efektów w wersji Studio)
            k0, k1 = int((a + vs) * SR), min(n, int((a + vs + vl) * SR))
            duckmask[k0:k1] = 1
        entry = {"ujecie": i, "scena": P["scena"], "napiecie": nap, "tempo": tempo, "miejsce": kind,
                 "tlo_db": round(bed_db, 1), "zdarzenia": []}
        miks.append(entry)
        if kadr == "TYT":  # karta dnia: niskie „dum”
            x = at_level(sy.boom(1.8), -22.0)
            k = i0 + n_(0.15)
            evbus[k:k + len(x)] += x[: max(0, n - k)]
            entry["zdarzenia"].append({"t": 0.15, "dzwiek": "karta dnia (dum)", "skala": "duże", "db": -22.0})
            continue
        if silent and T >= 1.4:
            x = at_level(sy.heartbeat(T - 0.2, 66), -33.0)
            k = i0 + n_(0.1)
            evbus[k:k + len(x)] += x[: max(0, n - k)]
            entry["zdarzenia"].append({"t": 0.1, "dzwiek": "cisza: serce", "skala": "małe", "db": -33.0})
        ons = onsets(mot, a, b)
        act = active(mot, a, b)
        for t, x, g, name in rules(day, i, kadr, desc, sound or "", T, ons, act, sy, kind, ruch):
            db = target_db(name, nap, tempo, g)
            if silent:
                db -= 8.0
            x = at_level(x, db)
            x = fftconvolve(x, irs[kind])[: len(x) + len(irs[kind]) // 2]
            k = i0 + n_(t)
            if k >= n:
                continue
            evbus[k:k + len(x)] += x[: n - k]
            if name != "krok":
                entry["zdarzenia"].append({"t": round(t, 2), "dzwiek": name, "skala": skala(name), "db": round(db, 1)})
    # dźwięki ciągnące się przez kilka ujęć: blisko w miejscu źródła, z oddali gdzie indziej
    for span in spans(day, rows):
        s0, s1, kind = span[:3]
        a, b = m.SCENES[s0][0], m.SCENES[s1][1]
        if len(span) > 3 and span[3] == "milknie":  # urywa się w pół melodii zaraz po wejściu w ostatnie ujęcie
            b = m.SCENES[s1][0] + 0.6
        elif len(span) > 3:
            b -= span[3]
        if kind == "alarm_sekunda":
            x = at_level(sy.alarm(1.0), -17.0)
            k = int((a + 0.3) * SR)
            evbus[k:k + len(x)] += x[: n - k]
            miks[s0]["zdarzenia"].append({"t": 0.3, "dzwiek": "alarm na sekundę", "skala": "duże", "db": -17.0})
            continue
        L = int((b - a) * SR)
        if kind == "alarm":
            x = fit(sy.alarm(b - a), L)
        elif kind == "karetka":
            x = fit(sy.car_alarm(b - a + 0.2), L)
        elif kind == "agregat":
            x = fit(sy.engine(b - a, 25, 0.8), L)
        else:  # kołysanka: melodia z nut (własna, prosta), urywa się w pół na końcu zakresu
            mel = [72, 71, 69, 71, 72, 67, 69, 71, 72, 74, 72, 71, 69, 67, 69, 67]
            notes = [(0.3 + k * 0.62, mm) for k, mm in enumerate(mel * 4) if 0.3 + k * 0.62 < b - a - 0.5]
            x = fit(sy.piano(notes, 1.3, 0.8), L)
        near_db = {"alarm": -17.0, "karetka": -19.0, "agregat": -25.0, "kolysanka": -21.0}[kind]
        x = at_level(x, near_db)
        gain = np.zeros(L)
        for k in range(s0, s1 + 1):
            sa, sb = m.SCENES[k][0] - a, min(m.SCENES[k][1], b) - a
            near = re.search(SPAN_NEAR.get(kind, r"$^"), rows[k][3].lower())
            gain[int(sa * SR):int(sb * SR)] = 1.0 if near else 0.3
            miks[k]["zdarzenia"].append({"t": 0.0, "dzwiek": f"ciągły: {kind}", "skala": "duże",
                                         "db": round(near_db if near else near_db - 12, 1)})
        gain = np.convolve(gain, np.ones(n_(0.1)) / n_(0.1), mode="same")
        if kind != "kolysanka":
            x = x * np.minimum(1, np.arange(L) / n_(0.05))
        x = x * np.minimum(1, (L - np.arange(L)) / n_(0.06))  # koniec bez trzasku
        far = lp(x, 1400)
        mixs = x * gain + far * (1 - gain) * 0.8
        k = int(a * SR)
        evbus[k:k + L] += mixs[: n - k]
    if day < 30:  # narastanie przed kartą następnego dnia; finał kończy się świtem, bez narastania
        x = at_level(sy.swell(1.6), -27.0)
        k = n - len(x)
        evbus[k:] += x
        miks[-1]["zdarzenia"].append({"t": round(shots[-1][1] - shots[-1][0] - 1.6, 2), "dzwiek": "narastanie przed kolejnym dniem",
                                      "skala": "średnie", "db": -27.0})
    bedbus = np.tanh(bedbus * 1.2) / 1.2
    evbus = np.tanh(evbus * 1.2) / 1.2
    fx = bedbus + evbus
    duck = np.clip(np.convolve(duckmask, np.ones(n_(0.25)) / n_(0.25), mode="same"), 0, 1)
    OUT.mkdir(parents=True, exist_ok=True)
    write_wav(OUT / f"e{day:02d}.wav", fx)  # do miksu filmu (film_en.py ścisza efekty pod głosem sam)
    write_wav(OUT / f"e{day:02d}_tlo.wav", bedbus)
    write_wav(OUT / f"e{day:02d}_zdarzenia.wav", evbus)
    write_wav(OUT / f"e{day:02d}_tlo_studio.wav", bedbus * (1 - 0.37 * duck))  # Studio: −4 dB tła pod kwestiami
    write_wav(OUT / f"e{day:02d}_zdarzenia_studio.wav", evbus * (1 - 0.5 * duck))  # −6 dB zdarzeń pod kwestiami
    (OUT / f"e{day:02d}.json").write_text(json.dumps({"dzien": day, "dlugosc": round(n / SR, 3),
                                                      "zasada": "dB = skala (małe −34 / średnie −27 / duże −19) + 0,8 × (napięcie − 5) "
                                                                "+ tempo (szybkie +1,5 / wolne −1); tło wg miejsca + 0,5 × (napięcie − 5); cisza −6/−8 dB",
                                                      "ujecia": miks}, ensure_ascii=False, indent=1), encoding="utf-8")
    return day, sum(len(e["zdarzenia"]) for e in miks)


def write_wav(path, x):
    with wave.open(str(path), "w") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes((np.clip(x, -1, 1) * 32767).astype(np.int16).tobytes())


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("dni", nargs="*", type=int)
    ap.add_argument("-j", type=int, default=4)
    ap.add_argument("--wideo", default=str(HERE / "build" / "en-1440-przed-rigiem"))
    a = ap.parse_args()
    sys.stdout.reconfigure(encoding="utf-8")
    days = a.dni or list(range(1, 31))
    with ProcessPoolExecutor(a.j) as ex:
        for day, k in ex.map(day_effects, days, [a.wideo] * len(days)):
            print(f"e{day:02d}: {k} zdarzeń", flush=True)


if __name__ == "__main__":
    main()
