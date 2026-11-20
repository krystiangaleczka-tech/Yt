"""English version of "Son of the Sun" (Japan's first emperor) for the Paper Theatre channel: narration lines (by shot
key), on-screen labels and spoken forms. Used when JEZYK=en (dane.kwestia, zestaw_jp.tr, lektor.py).
The Polish script in dane.py stays the source of shots and timing. Wzór: docs/filmy/pierwszy-cesarz/ujecia/kwestie_en.py.

Reżyser 17.11.2026: film idzie po angielsku na kanał Paper Theatre (decyzja D8 w księdze), lektor EN — Chatterbox
Multilingual tak jak w „Pierwszym cesarzu” (D9). Kwestie mówią jednoznacznie, o kim są (wytyczne 1.15): „Iwarebiko
understood”, „Iwarebiko's bow”, a nie „he” tam, gdzie po polsku domyślny podmiot był niejasny.
"""

EN = {
    # akt 0 · zapowiedź i hak (szkic D, reżyser 18.11.2026; księga D14, 20.11.2026: lektor od pierwszej sekundy, na zapowiedzi;
    # spójność z resztą: „four brothers” = akt IV „bracia”, łuk Itsuse → „Remember that arrow?” (rana), „died far from home” →
    # „died on the boat” (itsuse), burza innymi słowami niż w akcie V, miecz z ogona węża → akt III, skarby, śmierć, koronacja)
    "zap_jaskinia": "Japan began with gods, monsters, and four brothers who set out to rule it.",
    "teatr": "Only one of them survived.",
    "hak_najazd": "That was Prince Iwarebiko, who became Japan's first emperor, if he ever existed.",
    "hak_rana": "First, an arrow struck the eldest brother.",
    "hak_cien": "The arrow wouldn't come out, and he died far from home.",
    "hak_burza": "A storm took the other two.",
    "hak_koronacja": "In 2019, Iwarebiko's heir received a sacred sword.",
    "hak_waz": "Legend says it came from a serpent's tail. So how did it reach the emperors?",
    # cien: ujęcie z pierwszej wersji filmu (parawan z cieniem władcy), dziś poza filmem — kwestia jak w nagraniu lektora
    "cien": "The chronicles call him a great-great-great-grandson of the sun goddess, and historians "
            "still argue whether he ever lived.",
    # reżyser 18.11.2026: ujęcie 14 krótsze o 4 s — obietnica bez wrony (wrona i tak wraca w tytule aktu V)
    "luty": "By the end, you'll know where that sword came from and why Japan's birthday was made up.",
    # akt 1 · Kropla z włóczni
    "meduza": "It all starts when the young earth still drifted like a jellyfish.",
    "most": "Two gods, Izanagi and Izanami, came down the bridge of heaven to give it shape.",
    "wlocznia": "They dipped a jewelled spear into the sea and stirred until the salt water began to "
                "thicken.",
    "kropla": "When they lifted it, salt dripped from the tip, and from that drop grew the first island.",
    "wyspy": "The god and the goddess settled there, and eight great islands were born to them: Japan.",
    # akt 2 · Słońce w jaskini
    "ogien": "Her last child was the god of fire, who burned her so badly that she died and went down to "
             "the land of the dead.",
    "yomi": "Izanagi followed her into the darkness, but when he saw what she had become, he fled and "
            "sealed the entrance with a boulder.",
    "rzeka": "Then he washed in a river: from his left eye came Amaterasu, the sun goddess and ancestor of the four "
             "brothers, from his right the moon god, and from his nose Susanoo, god of storms.",
    "susanoo": "Susanoo raged across heaven, wrecked his sister's rice fields, and finally smashed the "
               "roof of the hall where she was weaving.",
    "jaskinia": "Offended, Amaterasu shut herself inside a rock cave, and darkness fell over heaven and "
                "earth.",
    "koguty": "The gods set roosters before the cave to crow as if at dawn, and hung a mirror and jewels "
              "on a tree.",
    "uzume": "Then a goddess danced on an upturned tub so wildly that all the gods burst out laughing.",
    "lustro": "Curious, Amaterasu peeked out at her own radiance in the mirror, and that mirror became the first of the "
              "three sacred treasures of Japan's emperors.",
    # akt 3 · Miecz w ogonie węża
    "wygnanie": "Susanoo was banished to earth, to the land of Izumo, where chopsticks came floating down"
                " the river.",
    "starcy": "Upstream, an old couple was weeping: an eight-headed serpent had eaten seven of their "
              "daughters and was coming for the last.",
    "kadzie": "Susanoo turned the girl into a comb, tucked it into his hair, and set out eight vats of "
              "strong sake.",
    "orochi": "The serpent had eight heads and eight tails, and it stretched across eight valleys and "
              "eight hills.",
    "miecz": "When the drunken heads fell asleep, Susanoo cut the serpent apart and found a sword in its tail; tradition "
             "says it still lies hidden in a shrine, and no one alive has seen it.",
    "skarby": "Amaterasu gave the mirror, the jewels and the sword to her grandson Ninigi, but the man who would build "
              "a country with them had not yet been born.",
    "zejscie": "Ninigi came down from heaven through eight layers of clouds to the top of Mount "
               "Takachiho, on the island of Kyushu.",
    # siostry, płatki, postoje, pola: poza filmem od przeglądu 18.11.2026 (szkic D) — kwestie zostają przy nagraniach
    "siostry": "A mountain god offered him two daughters, but Ninigi chose the beautiful Princess of "
               "Blossoms and sent the ugly Princess of Rocks home.",
    "platki": "That is why, says the chronicle, the lives of emperors are short as a flower's, not "
              "lasting as rock.",
    # akt 4 · Na wschód
    "prawnuk": "Ninigi's great-grandson, Prince Iwarebiko, grew up on Kyushu, far from the other islands.",
    "wschod": "When he was forty-five, he heard that in the east lay a beautiful land surrounded by blue "
              "mountains.",
    "bracia": "It seemed the best place to rule the whole country from, so with his brothers and his army"
              " he set out east.",
    "flota": "They sailed along the Inland Sea, and the chronicle says they stopped for whole years along"
             " the way.",
    "postoje": "In every harbour they built ships, sowed rice and gathered supplies for the war waiting "
               "at the end of the road.",
    "naniwa": "At last they reached Naniwa Bay, where Osaka stands today, and marched across the "
              "mountains toward Yamato.",
    "nagasune": "Their way was blocked by a local chief, Nagasunehiko, 'the Prince with Long Shins', and "
                "his army.",
    "rana": "Remember that arrow? It struck the eldest brother, Itsuse, and suddenly Iwarebiko understood why they "
            "were losing.",
    "pod_slonce": "As children of the sun goddess, they had been fighting facing the sun, so they decided"
                  " to circle the mountains and attack with the sun behind them.",
    # akt 5 · Wrona z gór Kumano
    "itsuse": "Itsuse never recovered, and he died on the boat as they sailed south.",
    "burza": "Then a storm sank two boats, and the sea took two more brothers.",
    "sam": "Iwarebiko had lost all three brothers, and the hardest part was still ahead.",
    "niedzwiedz": "In the Kumano forests, a huge bear appeared and vanished, and the whole army collapsed"
                  " as if under a spell.",
    "takakuraji": "Then a local man brought Iwarebiko another sword, one the thunder god had dropped through the "
                  "roof of his storehouse.",
    "przebudzenie": "When Iwarebiko took the sword, the evil powers of the forest fell, and his warriors "
                    "woke one after another.",
    "wrona": "Heaven also sent a great crow, Yatagarasu, which guided the army through wild mountains all"
             " the way to Yamato.",
    "trzy_nogi": "Later it was painted with three legs, and Japan's national football team still wears it"
                 " on its shirts.",
    # akt 6 · Złoty ptak
    "yamato": "In Yamato every hill had its own chief, and none of them meant to give his land to a "
              "newcomer from Kyushu.",
    "pulapka": "One of them built his guest a house with a hidden trap, but his own brother gave him "
               "away, and the chief died in his own trap.",
    "bitwa": "Iwarebiko fought Nagasunehiko once more, but the battle dragged on, the sky grew dark, and "
             "hail began to fall.",
    "ptak": "Then a golden bird landed on the tip of Iwarebiko's bow, shining like lightning.",
    "order": "In its memory, for half a century Japan honoured its soldiers with the Order of the Golden "
             "Kite.",
    "strzala_nieba": "Nagasunehiko still refused to give in, because he served another descendant of the "
                     "gods, Nigihayahi.",
    "zdrada": "But Nigihayahi decided that the newcomer had the better claim to rule, killed the stubborn"
              " chief, and went over to his side.",
    # akt 7 · Pierwszy cesarz
    "palac": "At Kashihara, below a green mountain, Iwarebiko built a palace whose pillars, the chronicle "
             "says, were driven into the bedrock.",
    "tron": "On the first day of the new year, in 660 BC, he took the throne there as the first emperor "
            "of Japan.",
    "imie": "The name Jimmu, meaning 'divine valour', was given to him by scholars only fourteen hundred "
            "years later.",
    "zona": "He married the daughter of a local god, so that the new power would be joined to the old "
            "land.",
    "pola": "According to the chronicle, he reigned for seventy-six years, and his court grew together "
            "with the rice fields in the valley.",
    "smierc": "The chronicle says the emperor died at a hundred and twenty-seven, and the three treasures passed to his son.",
    "linia": "With him, tradition says, began a line of emperors unbroken to this day. But did he ever really exist?",
    # akt 8 · Kronika i ziemia
    "kronika": "But this story was written down only in 712 and 720, in chronicles the court ordered to "
               "prove its right to rule.",
    "rachunek": "The date 660 BC was probably worked out from a Chinese prophecy of a great change every "
                "twelve hundred and sixty years.",
    "jomon": "Meanwhile, in 660 BC, the islands were home to hunters and fishermen, and rice farming had only just "
             "reached the southwest.",
    "wa": "Chinese records of that time describe the land of the Wa as over a hundred little states.",
    "pieczec": "It was a seal the emperor of China sent to a king of the Wa in the year 57: proof that real kings "
               "ruled the islands long before the chronicles.",
    "chlop": "But in 1784, a farmer repairing a ditch in his field struck something golden with his hoe.",
    "himiko": "In the third century, Queen Himiko ruled there; she was said to keep the chiefs in line "
              "with sorcery, and China sent her a hundred bronze mirrors.",
    # akt 9 · Źródło słońca
    "kofun": "Later, the rulers of Yamato were buried in huge keyhole-shaped mounds, and the largest is "
             "almost half a kilometre long.",
    "haniwa": "On their slopes stood thousands of clay figures called haniwa, and inside lay real rulers of Yamato, "
              "though no one can say for sure who they were.",
    "nihon": "In the late seventh century, the court renamed the country Nihon, 'origin of the sun', "
             "because from China, that is where the sun rose.",
    "luty2": "Only in 1873 did Tokyo convert the chronicle's date to our calendar and make the eleventh of February a "
             "holiday, abolished after the war and restored in 1966.",
    "koronacja": "In 2019, the hundred and twenty-sixth emperor was enthroned, and the jewels and a stand-in for the "
                 "serpent's sword were brought to him, wrapped in cloth no one opens.",
    "koniec": "No one knows whether Jimmu really lived, but the country that began with a drop from a "
              "spear still calls itself the origin of the sun.",
    # podziękowanie jak w „Pierwszym cesarzu” (ujęcie „dzieki”, reżyser 16.11.2026)
    "dzieki": "Thank you for watching! If you like my videos, support me, and I'll do my best.",
}

# napisy na wycinkach (szyld teatru, zawieszki, tabliczki z imionami, tytuły aktów na kurtynie)
ETYKIETY = {
    "SYN SŁOŃCA": "SON OF THE SUN", "POWSTANIE JAPONII": "THE BIRTH OF JAPAN", "LUTEGO": "FEBRUARY",
    "11 lutego": "11 February", "Hyūga": "Hyūga", "660 p.n.e.": "660 BC", "127 lat": "Lived 127 years!",  # marker 20.11: „ma być napisane lived 127 years!” "− 1260 lat": "− 1260 years",
    "57 r.": "AD 57", "126": "126",
    # nazwy pisane znakami, o których mówi lektor — pod znakami podpis w języku wersji (wytyczne 1.13)
    "Jimmu — boska waleczność": "Jimmu — 'divine valour'", "Wa": "Wa", "Nihon — źródło słońca": "Nihon — 'origin of the sun'",
    # tabliczki z imieniem i rolą przy pierwszym pojawieniu się postaci (wytyczne 1.15)
    "Izanagi": "Izanagi", "Izanami": "Izanami", "Amaterasu, bogini słońca": "Amaterasu, the sun goddess",
    "bóg księżyca": "the moon god", "Susanoo, bóg burzy": "Susanoo, god of storms", "Uzume": "Uzume",
    "najsilniejszy z bogów": "the strongest god", "starcy z Izumo": "the old couple", "ostatnia córka": "their last daughter",
    "Ninigi, wnuk Amaterasu": "Ninigi, her grandson", "księżniczka kwiatów": "Princess of Blossoms",
    "księżniczka skał": "Princess of Rocks", "książę Iwarebiko": "Prince Iwarebiko", "Itsuse, najstarszy brat": "Itsuse, eldest brother", "Iwarebiko, przyszły cesarz": "Iwarebiko, the future emperor", "Wiek bogów": "The Age of the Gods",
    "bogini tańca": "a goddess of dance", "miejscowy człowiek": "a local man", "Kiusiu": "Kyushu",
    "wódz Nagasunehiko": "Chief Nagasunehiko", "Takakuraji": "Takakuraji", "Yatagarasu": "Yatagarasu",
    "Nigihayahi": "Nigihayahi", "córka miejscowego boga": "daughter of a local god", "syn cesarza": "his son",
    "cesarz nr 126": "Emperor No. 126",
    "pisarz dworu": "court scribe", "chłop": "a farmer", "królowa Himiko": "Queen Himiko",
    # tabliczki ze słownika znaków (wytyczne 1.20)
    "HA HA!": "HA HA!", "HA HA HA!": "HA HA HA!", "AŁA!…": "AW!…", "O!": "OH!", "PUŁAPKA!": "A TRAP!",
    # okrzyki z markerów reżysera 18.11.2026
    "POMOCY!": "HELP!", "HMM…": "HMM…", "STOP!": "STOP!", "NIE MA MOWY!": "NO WAY!", "AAA!": "AAA!", "Nie mogę…": "I can't…",
    "AAAA!": "AAAA!", "BRACIE!": "BROTHER!", "BU!": "BOO!",
    # gagi 20.11.2026 (GAGI.md)
    "BLUB!": "BLUB!", "UFF…": "PHEW…", "TA-DA!": "TA-DA!", "KUKURYKU!": "COCK-A-DOODLE-DOO!", "OCH!": "WOW!", "HIK!": "HIC!",
    "EJ!": "HEY!", "KRA!": "CAW!", "MOJE!": "MINE!", "TAKA SAMA?!": "SAME ARROW?!", "ZRÓB TO STARSZE!": "MAKE IT OLDER!",
    "PRAWDZIWE ZŁOTO?": "REAL GOLD?", "UPS!": "OOPS!", "OJEJ!": "WHOA!", "BUM!": "BUMP!", "ZACZEKAJCIE!": "WAIT FOR ME!",
    "MNIAM!": "YUM!",
    # markery i uwagi reżysera 20.11.2026
    "KŁAP!": "CHOMP!", "HAJA!": "HI-YAH!", "CZEMU JA?!": "WHY ME?!", "HA!": "HA!", "ZA MNĄ, CHŁOPAKI!": "FOLLOW ME, GUYS!",
    "GOL?!": "GOAL?!", "CHODŹ!": "COME IN!", "SKRZYP…": "CREAK…", "RZĄDZĘ WAMI!": "I RULE YOU!", "DZIŚ, W 2019 ROKU": "NOWADAYS, IN 2019",
    # tytuły aktów na kurtynie (przejście między aktami)
    # przegląd 18.11.2026 (szkic D): tytuły aktów to pytania, na które akt odpowiada; kurtyna rysuje „Act N” i pytanie
    # w dwóch rzędach (render.kurtyna)
    "Akt 1 · Kropla z włóczni": "Act I · How do you make a country from a single drop?",  # kurtyna po haku (akt 0)
    "Akt 2 · Słońce w jaskini": "Act II · Why did the sun hide in a cave?",
    # D14: hak mówi już, że miecz wyszedł z ogona węża — pytanie aktu III go nie powtarza
    "Akt 3 · Miecz w ogonie węża": "Act III · How do you beat a serpent with eight heads?",
    "Akt 4 · Na wschód": "Act IV · Why would a prince sail east at forty-five?", "Akt 5 · Wrona z gór Kumano": "Act V · Who sent the crow?",
    "Akt 6 · Złoty ptak": "Act VI · How do you win a battle in a hailstorm?", "Akt 7 · Pierwszy cesarz": "Act VII · Who sat on the first throne?",
    "Akt 8 · Kronika i ziemia": "Act VIII · What does the evidence say?", "Akt 9 · Źródło słońca": "Act IX · Why 'the origin of the sun'?",
    # podziękowanie na końcu
    "DZIĘKUJĘ": "THANK YOU", "za obejrzenie": "for watching",
    "Wesprzyj mnie, a dam z siebie wszystko.": "Support me and I'll do my best.",
}

# tekst mówiony: liczby słowami (całe frazy, bo forma zależy od zdania)
SLOWNIE_EN = {"in 660 BC": "in six hundred and sixty B.C.", "The date 660 BC": "The date six hundred and sixty B.C.",
              "in 712 and 720": "in seven twelve and seven twenty", "In the year 57": "In the year fifty-seven",
              "in the year 57": "in the year fifty-seven", "In 1784": "In seventeen eighty-four", "in 1784": "in seventeen eighty-four",
              "in 1873": "in eighteen seventy-three", "in 1966": "in nineteen sixty-six", "In 2019": "In twenty nineteen"}

# japońskie imiona zapisane tak, jak ma je przeczytać angielski lektor (dłuższe nazwy przed krótszymi)
WYMOWA_EN = [("Nagasunehiko", "Nah-gah-soo-neh-hee-ko"), ("Yatagarasu", "Yah-tah-gah-rah-soo"),
             ("Takakuraji", "Tah-kah-koo-rah-jee"), ("Nigihayahi", "Nee-gee-hah-yah-hee"), ("Amaterasu", "Ah-mah-teh-rah-soo"),
             ("Iwarebiko", "Ee-wah-reh-bee-ko"), ("Takachiho", "Tah-kah-chee-ho"), ("Kashihara", "Kah-shee-hah-rah"),
             ("Izanagi", "Ee-zah-nah-gee"), ("Izanami", "Ee-zah-nah-mee"), ("Susanoo", "Soo-sah-no-oh"), ("Ninigi", "Nee-nee-gee"),
             ("Itsuse", "Eet-soo-seh"), ("Kumano", "Koo-mah-no"), ("Naniwa", "Nah-nee-wah"), ("Yamato", "Yah-mah-toh"),
             ("Himiko", "Hee-mee-ko"), ("Uzume", "Oo-zoo-meh"), ("Izumo", "Ee-zoo-mo"), ("Unebi", "Oo-neh-bee"),
             ("Kyushu", "Kyoo-shoo"), ("Hyuga", "Hyoo-gah"), ("haniwa", "hah-nee-wah"), ("Nihon", "Nee-hon"), ("Jimmu", "Jim-moo"),
             ("sake", "sah-keh"), ("Kii", "Kee"), ("Wa", "Wah")]

# Frazowanie lektora (tylko tekst mówiony, FRAZY=1): przecinki tam, gdzie autor robi oddech we frazie — jak w „Pierwszym
# cesarzu” EN. Puste, dopóki reżyser nie odsłucha pierwszego nagrania.
FRAZY_EN = {}
