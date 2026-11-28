"""Ujęcia aktów 3–4 filmu „The Imam Who Fought Russia for 25 Years — and Ended Up in Dune” (Gunib, słowa, puenta).

Funkcja `s_<klucz>(st, w, t, T)` na ujęcie, tak jak w ujecia_a.py. Ujęcie bez funkcji render pokazuje jako „do narysowania”.
"""
from ujecia_a import *  # noqa: F401,F403
from scena import wnetrze  # noqa: E402,F401
import ujecia_a as _A  # noqa: E402

_bump, jezdziec, dym, plomien, koniec, SZABLA, FLAGA = _A._bump, _A.jezdziec, _A.dym, _A.plomien, _A.koniec, _A.SZABLA, _A.FLAGA
KARABIN_PION = _A.KARABIN_PION


# ---------------------------------------------------------------- akt III: Gunib, kapitulacja, wygnanie

def plaskowyz(st, t, w, x=700, k=1.0, wd=560):
    """Gunib: skała-płaskowyż (obiekt „skała Gunib”) z wioską na szczycie (y szczytu zwraca funkcja)."""
    u = K.uk(st, t)
    with u.obiekt("skała Gunib", "dekoracja"):
        Z0.rise(st, J.skala(), x, 712, P.most, min(k, bk(w, 0.35, 0.9)), t, 901, w=wd, wob=0.0, lift=480, anchor=(0.5, 1.0), sy=0.62)
    top = 712 - wd * 620 / 760 * 0.62 + wd * 110 / 760 * 0.62
    Z0.rise(st, J.aul(1), x + 20, top + 30, P.most - 0.003, min(k, bk(w, 0.55, 0.8)), t, 902, w=wd * 0.7, wob=0.0, lift=200,
            anchor=(0.5, 1.0), sy=0.6)
    return top


def s_gunib(st, w, t, T):
    """Kamera dojeżdża do płaskowyżu z wioską; mgła; zawieszka „Gunib, 1859”."""
    kam(st, t, I["gunib"], 700, lerp(420, 380, ease(t / T)), lerp(1.0, 1.25, ease(t / T)), 0.6)
    kaukaz(st, t, w, blisko=False)
    plaskowyz(st, t, w)
    for n in range(3):
        st.put(J.S("cloud_center", 0.4), 300 + n * 380 + 30 * noise(t, 900 + n, 0.2), 600 - n * 20, P.most + 0.01, w=700,
               anchor=(0.5, 0.5), alpha=0.5, tint=(0.94, 0.94, 0.98), shadow=None)
    podpis(w, t, "Gunib, 1859", 340, 40, 0.5, T)
    koniec(st, w, t, extra=(0.96, 0.97, 1.02))


def s_liczby(st, w, t, T):
    """Kamera odjeżdża: garstka obrońców na górze, a dookoła rzędy wojska aż po horyzont; tabliczki „400” nad garstką
    i „16,000” nad wojskiem (Wytyczne 1.17). Karabiny w tylnej dłoni (uklad_kz.zolnierz)."""
    kam(st, t, I["liczby"], 700, 420, lerp(1.4, 0.98, ease(pr(t, 0, T * 0.7))), 0.6)
    kaukaz(st, t, w, blisko=False)
    top = plaskowyz(st, t, w)
    u = K.uk(st, t)
    u.rzedy["na skale"] = P.most + 0.004
    for n in range(7):
        K.lalka(st, t, f"obrońca {n + 1}", ("murid", "murid2", "murid3", "murid4", "murid5", "ghazi", "mysliwy")[n], 600 + n * 30, 46,
                y=top + 26, rzad="na skale",
                flip=1 if n < 4 else -1)
    for r, (p, y, h, n_) in enumerate(((0.62, 640, 64, 22), (0.70, 680, 90, 16), (0.80, STOPY, 130, 11))):
        u.rzedy[f"szereg{r}"] = p
        for n in range(n_):
            x = -40 + n * (1360 / n_) + (r % 2) * 30
            if 560 < x < 840 and r == 0:
                continue
            K.zolnierz(st, t, f"żołnierz {r}.{n}", ZOLNIERZE[(n + 2 * r) % 6], x, h, y=y, rzad=f"szereg{r}",
                       flip=1 if x < 700 else -1, k=ease(pr(t, 0.3 + 0.05 * n + 0.3 * r, 0.5)))
    podpis(w, t, "400", 700, 150, 1.6, T)
    podpis(w, t, "16,000", 230, 300, 3.4, T)
    koniec(st, w, t, extra=(0.96, 0.97, 1.02))


def s_wspinaczka(st, w, t, T):
    """O świcie żołnierze wspinają się po urwisku, jeden za drugim; dłonie na skale nad głową (kontrola: dłoń na skale)."""
    kam(st, t, I["wspinaczka"], 660, 470, 1.15, 0.66)
    kaukaz(st, t, w, blisko=False)
    plaskowyz(st, t, w, wd=640)
    u = K.uk(st, t)
    u.rzedy["urwisko"] = P.most + 0.006
    for n in range(5):
        f = pr(t, 0.12 * n, 1.6)
        x, y = lerp(440, 560, f) + n * 24, lerp(712, 560, f) + n * 22
        szk = K.lalka(st, t, f"żołnierz {n + 1}", "zolnierz2" if n % 2 else "zolnierz", x, 80, y=y, rzad="urwisko", flip=1, lean=-20,
                      przod=lambda s: (s["bark_przod"][0] + 14, s["bark_przod"][1] - 22),
                      tyl=lambda s: (s["bark_tyl"][0] + 6, s["bark_tyl"][1] - 16))
        if szk and f > 0.05:
            u.dotyka("skała Gunib", (*szk["przod"]["dlon"], P.most), f"żołnierz {n + 1}: dłoń na skale", 6.0)
    koniec(st, w, t, extra=(1.06, 0.94, 0.86))


def s_flaga(st, w, t, T):
    """Nad Gunibem wznosi się biała flaga i powiewa (łopot, cisza — szczyt aktu)."""
    kam(st, t, I["flaga"], 720, 420, 1.9, 0.6)
    kaukaz(st, t, w, blisko=False)
    top = plaskowyz(st, t, w)
    k = ease(pr(t, 0.2, 0.8))
    st.put(J.rek_kz("flaga_biala"), 720, top + 40 + (1 - k) * 160, P.most + 0.005, h=130, anchor=(0.04, 1.0),
           sx=1 + 0.05 * math.sin(t * 9), rot=2 * math.sin(t * 6))
    koniec(st, w, t, extra=(0.96, 0.97, 1.02))


def polana(st, t, w):
    """Polana pod brzozami pod Gunibem (obraz Horschelta: kapitulacja pod brzozą)."""
    kaukaz(st, t, w, blisko=False, kul=False)
    plaskowyz(st, t, w, x=1050, wd=520)
    for n, x in enumerate((180, 420, 980)):
        Z0.rise(st, J.rek_kz("brzoza"), x, STOPY + 6, P.drzewa - 0.01 * n, bk(w, 0.4 + 0.1 * n), t, 910 + n, h=460, wob=0.3,
                anchor=(0.5, 1.0))


def s_kapitulacja(st, w, t, T):
    """Szamil, starszy, z siwą brodą, schodzi ścieżką do księcia siedzącego na kamieniu (biodro na kamieniu — kontrola) pod
    brzozą; przy nazwisku podpis „Prince Baryatinsky”, a na „siridar” nad księciem zjeżdża tabliczka SIRIDAR (zasiew puenty
    z aktu IV)."""
    kam(st, t, I["kapitulacja"], 620, 440, 1.15, 0.8)
    polana(st, t, w)
    u = K.uk(st, t)
    kh = 90
    u.put("kamień", Z0.prop("kamien"), 360, STOPY + 6, u.p("przod", -2), h=kh, anchor=(0.5, 1.0))
    ks = K.lalka(st, t, "Bariatinski", "bariatinski", 360, 300, flip=1, siedzi=True,
                 y=K.y_siedzi("bariatinski", 300, STOPY + 6 - kh * 0.8), przod=20 + 50 * _bump(t, 8.0, 1.5))
    if ks and ks["k"] >= 1:  # kiedy książę już usiadł (przy budowie dekoracji lalka się wysuwa)
        K.siedzi_na(st, t, "Bariatinski", ks, "kamień", 8.0)
    u.rzedy["sztab"] = P.lalki - 0.01
    for n in range(3):
        K.lalka(st, t, f"oficer {n + 1}", ("oficer_ros", "oficer_ros2", "oficer_ros3")[n], 200 - n * 70, 290, flip=1, rzad="sztab", y=STOPY - 4)
    x = lerp(1180, 560, ease(pr(t, 0.6, 4.6)))
    K.lalka(st, t, "Szamil", w.szamil, x, 300, flip=-1, hop=4 * (0.6 < t < 5.2), przod=4)
    u.rzedy["murid"] = P.lalki + 0.005
    K.lalka(st, t, "murid", "murid", x + 150, 280, flip=-1, hop=4 * (0.8 < t < 5.4), rzad="murid")
    if x < 1080:  # od chwili, gdy Szamil cały wszedł w kadr
        u.widac("Szamil", 0.95, "Szamil: widać ≥ 95%")
    podpis(w, t, "Prince Baryatinsky", 360, 280, 4.4, 2.6)  # na nazwisko (1.27)
    k = ease(pr(t, 8.1, 0.6))  # na „siridar”
    if k > 0:
        J.hang(st, J.slowo("SIRIDAR", 44), 360, 230, P.rekwizyty, k, t, 921, h=74, drop=360, shadow=(5, 8, 8, 0.4))
    koniec(st, w, t)


def ken_burns(st, t, T, spr, x0, y0, m0, x1, y1, m1, i):
    """Ken Burns po obrazie: kamera jedzie od kadru (x0, y0, m0) do (x1, y1, m1); obraz w ramie na tle ciemnej sceny."""
    k = ease(t / T)
    st.cam = Cam(lerp(x0, x1, k), lerp(y0, y1, k), lerp(m0, m1, k), 0.8, None, 0.0)
    st.focus = 0.8
    ciemnosc(st, (0.18, 0.14, 0.11))
    st.put(spr, CX, CY, 0.8, w=1180, anchor=(0.5, 0.5), shadow=(10, 14, 16, 0.5))


from papier import Cam  # noqa: E402


def s_obraz_horschelt(st, w, t, T):
    """Ken Burns po obrazie Theodora Horschelta „Kapitulacja Szamila” (1863; do czasu pobrania pliku z Commons — wycinek
    w złotej ramie): ramka przesuwa się od księcia do Szamila, a w obraz wsuwa się papierowa dłoń z białą flagą."""
    ken_burns(st, t, T, J.obraz("horschelt"), 760, 380, 1.5, 520, 380, 1.7, I["obraz_horschelt"])
    k = ease(pr(t, 1.0, 1.2))
    st.put(J.rek_kz("flaga_biala"), lerp(760, 560, k), lerp(820, 470, k), 0.82, h=200, anchor=(0.04, 1.0), rot=-8 + 3 * math.sin(t * 5))
    koniec(st, w, t)


def s_car(st, w, t, T):
    """Szamil staje przed carem Aleksandrem II w sali z kolumnami; podają sobie dłonie — obie dłonie idą do jednego punktu
    między nimi (kontrola: dłonie razem); podpis „Tsar Alexander II”."""
    kam(st, t, I["car"], 640, 430, 1.15, 0.8)
    sala_balowa(st, t, w)
    u = K.uk(st, t)
    xs = lerp(380, 600, ease(pr(t, 0.4, 1.8)))
    uscisk = ease(pr(t, 2.4, 0.6))
    punkt_ = ((xs + 760) / 2, STOPY - 160)
    cel = lambda s: (lerp(K.U.Uklad.dlon_z_kata(s, 8)[0], punkt_[0], uscisk), lerp(K.U.Uklad.dlon_z_kata(s, 8)[1], punkt_[1], uscisk))
    car = K.lalka(st, t, "car", "car", 760, 320, flip=-1, przod=cel)
    sz = K.lalka(st, t, "Szamil", w.szamil, xs, 300, flip=1, przod=cel)
    if car and sz and uscisk >= 1:
        u.kontakt((*car["przod"]["dlon"], car["p"]), (*sz["przod"]["dlon"], sz["p"]), "uścisk dłoni: dłonie razem", 4.0)
    u.rzedy["dwór"] = P.lalki - 0.02
    for n in range(4):
        K.lalka(st, t, f"oficer {n + 1}", ("oficer_ros", "oficer_ros2", "oficer_ros3", "oficer_ros4")[n], 200 + n * 300 if n < 2 else 900 + n * 60,
                270, flip=1 if n < 2 else -1, rzad="dwór")
    podpis(w, t, "Tsar Alexander II", 760, 240, 1.0, 2.6)
    podpis(w, t, "Exile: Kaluga", 600, 130, 5.8, 3.0)  # lektor mówi „Kaluga” — miejsce wygnania na zawieszce (1.6, 1.19)
    koniec(st, w, t, extra=(1.04, 1.0, 0.94))


def s_zdjecie_1859(st, w, t, T):
    """Ken Burns po portrecie Szamila z 1859 (Andriej Denier; do czasu pobrania pliku — wycinek); obok zapala się świeca
    i oświetla twarz."""
    ken_burns(st, t, T, J.obraz("portret"), 640, 380, 1.0, 640, 330, 1.25, I["zdjecie_1859"])
    k = ease(pr(t, 0.6, 0.5))
    st.put(J.rek_kz("swieca"), 900, 640, 0.84, h=120, anchor=(0.5, 1.0))
    if k > 0:
        plomien(st, 900, 530, 0.842, t, h=34 * k)
        st.put(J.glow(), 760, 400, 0.845, w=900, anchor=(0.5, 0.5), mode="add", alpha=0.35 * k, shadow=None, tint=(1.0, 0.8, 0.5))
    koniec(st, w, t, dim=lerp(0.75, 1.0, k))


def s_medyna(st, w, t, T):
    """Karawana na pustyni pod księżycem; Szamil siedzi na wielbłądzie (biodro na grzbiecie — kontrola); zawieszka
    „Medina, 1871”; kurtyna zasuwa się (render: „Act 4 — SIETCH · What did Dune take?”)."""
    w.noc = 1.0
    kam(st, t, I["medyna"], lerp(700, 560, t / T), 430, 1.05, 0.8)
    pustynia(st, t, w)
    u = K.uk(st, t)
    for n in range(3):
        x = lerp(1250 + n * 230, 300 + n * 230, pr(t, 0, T))
        hw = 210
        u.put(f"wielbłąd {n + 1}", J.rek_kz("wielblad"), x, STOPY, P.lalki + 0.004 * n, "zwierze", h=hw, anchor=(0.5, 1.0), sx=-1,
              rot=1.5 * math.sin(t * 4 + n))
        if n == 0:
            grzbiet = K.pkt("wielblad", 220, 104, x, STOPY, hw, sx=-1)[1]  # grzbiet z przyciętego arkusza (K.pkt)
            u.rzedy["na wielbłądzie"] = P.lalki + 0.002
            umiera = ease(pr(t, 4.5, 1.4))  # „he died in Medina”: lalka powoli opada pod grzbiet (konanie, 1.20; bez X — 1.11)
            sz = K.lalka(st, t, "Szamil", w.szamil, x + 6, 200, y=K.y_siedzi(w.szamil, 200, grzbiet + 6), rzad="na wielbłądzie", flip=-1,
                         siedzi=True, wejscie=False, sink=umiera)
            if umiera <= 0:
                K.siedzi_na(st, t, "Szamil", sz, "wielbłąd 1", 10.0)
    podpis(w, t, "Medina, 1871", CX, 40, 0.6, T)
    koniec(st, w, t, extra=(0.9, 0.92, 1.05))


# ---------------------------------------------------------------- akt IV: słowa i puenta

def pracownia(st, t, w, rok, kto, x=600):  # bliżej maszyny: klawisze w zasięgu ręki (kontrola 28.11)
    """Pracownia pisarza: ściana w paski, okno, biurko (mebel uklad.py) z maszyną do pisania na blacie; pisarz siedzi za
    biurkiem, palce obu dłoni na klawiszach (cel na maszynie, kontrola: dłoń na maszynie)."""
    wnetrze(st, t, w, sciana="paski", okna=(1000,))
    u = K.uk(st, t)
    u.mebel("biurko", "biurko", 660, 160, rzad="przod")
    geo = u.na("maszyna", K.ark("maszyna"), "biurko", "blat", 0.5, 90)
    stuk = lambda faza: 6 * max(0.0, math.sin(t * 16 + faza))
    _, blat_y = u.powierzchnia("biurko", "blat", 0.5)
    szk = K.lalka(st, t, kto, kto, x, 290, flip=1, siedzi=True, y=K.y_siedzi(kto, 290, blat_y + 40),
                  # palce na górnej krawędzi klawiatury: pisarz siedzi za biurkiem, więc dłonie widać nad maszyną, a nie za nią
                  przod=lambda s: (geo(250, 112)[0], geo(250, 112)[1] - 4 + stuk(0)), tyl=lambda s: (geo(160, 112)[0], geo(160, 112)[1] - 4 + stuk(1.6)))
    if szk:
        u.dotyka("maszyna", (*szk["przod"]["dlon"], u.p("przod") + 0.002), f"{kto}: dłoń na klawiszach", 10.0)
    podpis(w, t, rok, 1000, 40, 0.4, 99)
    return geo


def s_blanch(st, w, t, T):
    """Pisarka przy maszynie do pisania; kartki wylatują z wałka maszyny i składają się w książkę z szablami na okładce;
    podpis „Lesley Blanch”; zawieszka „1960”."""
    kam(st, t, I["blanch"], 640, 430, 1.2, 0.8)
    geo = pracownia(st, t, w, "1960", "blanch")
    wx, wy = geo(210, 20)
    for n in range(5):
        f = pr(t, 1.0 + 0.4 * n, 1.2)
        if 0 < f < 1:
            st.put(J.rek_kz("kartka_list"), lerp(wx, 900, f), lerp(wy, STOPY - 150, f) - 120 * math.sin(math.pi * f),
                   P.lalki + 0.05, h=50, anchor=(0.5, 0.5), rot=200 * f)
    Z0.rise(st, J.okladka(), 900, STOPY - 150, P.lalki + 0.045, ease(pr(t, 3.4, 0.8)), t, 931, h=150, lift=180, anchor=(0.5, 1.0))
    podpis(w, t, "Lesley Blanch", 560, 280, 2.4, 2.6)  # na nazwisko (1.27)
    koniec(st, w, t, extra=(1.02, 1.0, 0.96))


def s_herbert(st, w, t, T):
    """Mężczyzna z brodą przy maszynie; z wałka maszyny zamiast kartki sypie się piasek i usypuje wydmę obok biurka;
    podpis „Frank Herbert”; zawieszka „1965”."""
    kam(st, t, I["herbert"], 680, 430, lerp(1.1, 1.3, ease(t / T)), 0.8)
    geo = pracownia(st, t, w, "1965", "herbert")
    wx, wy = geo(210, 20)
    for n in range(12):
        if t > 1.0:
            f = (t * 1.4 + n * 0.083) % 1.0
            st.put(Z0.prop("kulka"), lerp(wx, 880, f) + 6 * math.sin(n), wy + f * (STOPY - wy) - 60 * math.sin(math.pi * f), P.lalki + 0.05,
                   h=7, anchor=(0.5, 0.5), tint=(0.95, 0.75, 0.45), shadow=None)
    Z0.rise(st, J.wydma(1), 900, STOPY, P.lalki + 0.045, ease(pr(t, 1.2, T - 1.6)), t, 932, w=420, lift=150, anchor=(0.5, 1.0), wob=0.0)
    podpis(w, t, "Frank Herbert", 560, 280, 2.2, 2.6)
    koniec(st, w, t, extra=(1.02, 1.0, 0.96))


def slowo_nad(st, t, txt, k_zjazd, k_przejazd, y=170, x0=1000, x1=300, seed=0, h=88):
    """Słowo zjeżdża na nitce nad góry (x0), potem przesuwa się na nitce nad wydmę (x1)."""
    J.hang(st, J.slowo(txt), lerp(x0, x1, ease(k_przejazd)), y, P.rekwizyty, k_zjazd, t, 940 + seed, h=h, drop=400,
           shadow=(5, 8, 8, 0.4))


def s_kanly(st, w, t, T):
    """Słowo KANLY zjeżdża nad góry, przesuwa się na nitce nad wydmę; pod nim dwa skrzyżowane kindżały."""
    kam(st, t, I["kanly"], CX, 380, 1.0, 0.8)
    teatr_kz(st, t, w)
    przejazd = pr(t, 2.2, 1.6)
    slowo_nad(st, t, "KANLY", pr(t, 0.2, 0.6), przejazd)
    kx = lerp(1000, 300, ease(przejazd))
    for s_ in (-1, 1):
        st.put(J.rek_kz("kindzal"), kx + 20 * s_, 290, P.rekwizyty - 0.004, h=130, anchor=(0.5, 0.1), rot=30 * s_,
               alpha=ease(pr(t, 0.8, 0.4)))
    koniec(st, w, t)


def s_kindjal(st, w, t, T):
    """Słowo KINDJAL; murid po stronie gór trzyma kindżał za rękojeść (kontrola: w dłoni), potem kindżał przelatuje nad
    scenę na stronę pustyni."""
    kam(st, t, I["kindjal"], CX, 380, 1.0, 0.8)
    teatr_kz(st, t, w)
    przejazd = pr(t, 2.0, 1.8)
    slowo_nad(st, t, "KINDJAL", pr(t, 0.2, 0.6), przejazd, seed=1)
    szk = K.lalka(st, t, "murid", "murid", 1040, 280, flip=-1, przod=lerp(60, 0, ease(przejazd)))
    if przejazd < 0.05:
        K.w_dloni(st, t, "kindżał", "kindzal", szk, 90, rot=-90)
    else:
        k = ease(przejazd)
        st.put(J.rek_kz("kindzal"), lerp(990, 330, k), lerp(560, 520, k) - 80 * math.sin(math.pi * k), P.lalki + 0.03, h=90,
               anchor=(0.5, 0.5), rot=lerp(0, 360, k))
    koniec(st, w, t)


def s_chakobsa(st, w, t, T):
    """Słowo CHAKOBSA; myśliwy szepcze do drugiego, z ust wylatują litery i odlatują nad wydmę."""
    kam(st, t, I["chakobsa"], CX, 380, 1.0, 0.8)
    teatr_kz(st, t, w)
    slowo_nad(st, t, "CHAKOBSA", pr(t, 0.2, 0.6), pr(t, 2.4, 1.6), seed=2)
    lalka(st, t, "mysliwy", 900, 290, flip=1, lean=-6 * _bump(t, 1.2, 0.8), seed=5)
    lalka(st, t, "mysliwy", 1080, 280, flip=-1, seed=6)
    for n, ch in enumerate("CHAKOBSA"):
        f = pr(t, 1.0 + 0.15 * n, 2.2)
        if 0 < f < 1:
            st.put(J.tag(ch, 26), lerp(960, 300, f), lerp(470, 380, f) - 60 * math.sin(math.pi * f), P.rekwizyty - 0.01, h=40,
                   anchor=(0.5, 0.5), rot=20 * math.sin(t * 4 + n), alpha=1 - pr(f, 0.85, 0.15))
    koniec(st, w, t)


def s_sietch(st, w, t, T):
    """Słowa SIETCH i TABR zjeżdżają osobno i sklejają się w tabliczkę „SIETCH TABR” nad jaskinią w skale pustyni."""
    kam(st, t, I["sietch"], 520, 400, 1.05, 0.8)
    teatr_kz(st, t, w)
    Z0.rise(st, J.skala(), 330, STOPY, P.lalki - 0.03, ease(pr(t, 0.1, 0.8)), t, 950, h=260, lift=300, anchor=(0.5, 1.0),
            tint=(1.1, 0.95, 0.75), wob=0.0)
    st.put(Z0.black(), 330, STOPY - 40, P.lalki - 0.028, w=70, h=80, anchor=(0.5, 1.0), shadow=None, alpha=0.85 * ease(pr(t, 0.6, 0.4)))
    razem = ease(pr(t, 2.6, 0.8))
    if razem < 1:
        J.hang(st, J.slowo("SIETCH", 48), lerp(160, 260, razem), 140, P.rekwizyty, pr(t, 0.4, 0.6), t, 951, h=72, drop=380)
        J.hang(st, J.slowo("TABR", 48), lerp(520, 420, razem), 140, P.rekwizyty + 0.002, pr(t, 1.0, 0.6), t, 952, h=72, drop=380)
    else:
        J.hang(st, J.slowo("SIETCH TABR", 48), 340, 140, P.rekwizyty, 1.0, t, 953, h=72, drop=380)
    koniec(st, w, t)


def s_tytuly(st, w, t, T):
    """Nad lalką cara zjeżdża tabliczka PADISHAH, nad księciem Bariatinskim (ta sama lalka co przy kapitulacji) SIRIDAR;
    potem obie przesuwają się nad wydmę."""
    kam(st, t, I["tytuly"], CX, 400, 1.0, 0.8)
    teatr_kz(st, t, w)
    lalka(st, t, "car", 880, 300, flip=-1, seed=3)
    lalka(st, t, "bariatinski", 1100, 290, flip=-1, seed=2)
    przejazd = pr(t, 4.6, 2.0)
    slowo_nad(st, t, "PADISHAH", pr(t, 1.2, 0.6), przejazd, y=170, x0=880, x1=260, seed=3, h=70)
    slowo_nad(st, t, "SIRIDAR", pr(t, 3.0, 0.6), przejazd, y=270, x0=1100, x1=360, seed=4, h=70)
    koniec(st, w, t)


def s_szamil_patrzy(st, w, t, T):
    """Zbliżenie: lalka Szamila z boku sceny odprowadza wzrokiem słowa, które odpływają na nitkach nad wydmę."""
    kam(st, t, I["szamil_patrzy"], 1060, STOPY - 280 * 0.8, 2.6, 0.8)
    teatr_kz(st, t, w)
    lalka(st, t, w.szamil, 1060, 280, flip=-1, lean=-3 * ease(pr(t, 0.2, 0.8)), seed=1)
    koniec(st, w, t, dim=0.96)


def s_przyslowie(st, w, t, T):
    """Dwie karty obok siebie: „…wisdom from the hills.” (1960) i „…wisdom from the desert.” (Diuna); słowo „hills” odpada
    i spada, na jego miejsce zjeżdża „desert”."""
    kam(st, t, I["przyslowie"], CX, 300, 1.05, 0.84)
    teatr_kz(st, t, w)
    st.spot = (CX, 300, P.rekwizyty, 620, 0.4)
    J.hang(st, J.karta("Polish comes from the city,|wisdom from the hills.", "1960", True), CX, 90, P.rekwizyty, pr(t, 0.1, 0.8), t, 961,
           w=620, drop=500, strings=(0.2, 0.8))
    k = pr(t, 3.0, 0.8)
    if k > 0:
        J.hang(st, J.karta("Polish comes from the cities,|wisdom from the desert.", "Dune, 1965"), CX, 330, P.rekwizyty + 0.004, k, t, 962,
               w=620, drop=500, strings=(0.2, 0.8))
    f = pr(t, 2.2, 0.9)
    if 0 < f < 1:
        st.put(J.tag("hills", 26), 800, 180 + 520 * f * f, P.rekwizyty + 0.01, h=44, anchor=(0.5, 0.5), rot=90 * f)
    koniec(st, w, t, dim=0.96)


def s_zastrzezenie(st, w, t, T):
    """Kamera odjeżdża: na scenie leżą stosy innych książek i map pustyni; lalka Szamila stoi z boku, nie na środku
    (Herbert czerpał z wielu źródeł — księga D4)."""
    kam(st, t, I["zastrzezenie"], CX, 400, lerp(1.4, 1.0, ease(t / T)), 0.8)
    teatr_kz(st, t, w)
    for n, (x, key) in enumerate(((330, "ksiazki"), (520, "mapa_pustyni"), (720, "ksiazki"), (560, "ksiazki"))):
        st.put(J.rek_kz(key), x, STOPY + 4, P.lalki + 0.01 * (n % 2), h=140 if key == "ksiazki" else 120, anchor=(0.5, 1.0),
               rot=4 * (n % 2 - 0.5))
    lalka(st, t, w.szamil, 1080, 280, flip=-1, seed=1)
    koniec(st, w, t)


def s_dwie_wojny(st, w, t, T):
    """Wydma i góry obok siebie; nad wydmą unosi się złote słońce, nad górami szare chmury."""
    kam(st, t, I["dwie_wojny"], CX, 380, 1.0, 0.8)
    teatr_kz(st, t, w)
    st.put(J.glow(), 330, 160, P.slonce, w=700, anchor=(0.5, 0.5), mode="add", alpha=0.25 * ease(pr(t, 0.5, 1.5)), shadow=None)
    for n in range(2):
        J.hang(st, J.S("cloud_right", 0.5), 980 + n * 200, 60 + n * 40, P.chmury + 0.01 * n, pr(t, 0.8 + 0.4 * n, 1.0), t, 970 + n,
               w=420, tint=(0.6, 0.62, 0.68), shadow=(6, 9, 10, 0.3))
    koniec(st, w, t)


def s_biala_flaga(st, w, t, T):
    """Szamil na grani podnosi białą flagę (drzewce w dłoni — kontrola); obok cień syna w mundurze, który się rozwiewa."""
    kam(st, t, I["biala_flaga"], 980, 430, lerp(1.2, 1.5, ease(t / T)), 0.8)
    teatr_kz(st, t, w)
    szk = K.lalka(st, t, "Szamil", w.szamil, 960, 300, flip=-1, przod=lerp(10, 150, ease(pr(t, 0.4, 1.0))), lokiec=("gora", "dol"))
    K.w_dloni(st, t, "biała flaga", "flaga_biala", szk, 180, rot=0)
    a = 1 - ease(pr(t, 2.0, 2.4))
    if a > 0:
        cien(st, t, "dzamal_oficer", 1120, 290, STOPY, P.lalki - 0.01, flip=-1, alpha=a * 0.85)
    koniec(st, w, t, dim=0.94)


def s_dzieki(st, w, t, T):
    """Kurtyna zasuwa się; na niej szyld „Paper Theatre” (podziękowanie, napis w kadrze — bez napisu lektora)."""
    kam(st, t, I["dzieki"], CX, CY, 1.0, 0.8, drift=0.0)
    teatr_kz(st, t, w)
    k = ease(pr(t, 0.1, 0.9))
    for strona in (-1, 1):
        przes = (1 - k) * 760
        st.put(J.Z0.kurtyna(strona), CX - 30 * strona + strona * przes, -70, 0.975, w=700, anchor=(1.0 if strona < 0 else 0.0, 0.0),
               shadow=(8 * strona, 0, 14, 0.45))
    J.hang(st, J.tag("Paper Theatre", 56), CX, 280, 0.978, pr(t, 0.9, 0.7), t, 990, h=100, drop=520, shadow=(5, 8, 8, 0.45))
    koniec(st, w, t)
