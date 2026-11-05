# Prompty dnia 1 (wersja szybsza, 43 ujęcia). (kadr — kontrola kolejności z rozpiską, prompt albo None, uwaga produkcyjna)
from prompty import LAYERS

CARD = "Karta tekstowa robiona w Studio: biały napis ODDZIAŁ C · DO ŚWITU na czerni."
POVHEADS = ("Point of view from inside the dark duty room looking through the rectangular glass window of the door: in the "
            "brightly lit pale-green corridor beyond the glass, four {PATIENTS} stand as dark silhouettes close to the window. "
            "The dark navy wall around the window frames the view; no part of the patients appears outside the window opening.")
PROFILE = ("Close-up profile of one of the {PATIENTS} standing in the corridor: {who}, pale green skin, a round, dry white eye "
           "with a tiny pupil that does not blink, slack open mouth.")
HOLD = ("Close-up of {NARRATOR} pressed against the pale green corridor wall, cheeks puffed, holding his breath, eyes darting "
        "sideways, cold fluorescent light.")
WINDOW = ("Close-up of {ISODOOR}: through the small wire-mesh window, {HENRYK} stares out without blinking; his face is visible "
          "only inside the window opening and is cut off by the window frame, nothing of him outside the opening.")

SHOTS = {1: [
    ("TYT", None, CARD),
    ("D", "Detail shot at desk height in {DUTYROOM}: the beige rotary telephone on the wooden desk is ringing, small cartoon "
          "motion lines around its bell; the handset has fallen and lies on the desk in front of the telephone.", ""),
    ("PŚ", "Medium shot in {DUTYROOM}: {NARRATOR} stands behind the desk and grabs the handset of the beige rotary telephone, "
           "pressing it to his ear, eyes wide with fear, camera slightly tilted as if handheld; the glass window in the door "
           "behind him glows pale green.", ""),
    ("Z", "Close-up of {NARRATOR} holding the beige telephone handset to his ear in the dark duty room, his eyes turned "
          "sideways toward the glowing green door window off-screen, a sweat drop on his temple.", ""),
    ("POV", POVHEADS, LAYERS),
    ("WZ", "Extreme close-up of the mouth and stubbled chin of {NARRATOR} right next to the mouthpiece of a beige telephone "
           "handset, lips pressed shut, holding his breath, dark blue light.", ""),
    ("Z", "Close-up of {NARRATOR} holding the beige telephone handset in both hands in front of his chest and looking down at "
          "it with frightened confusion, dark navy duty room behind him.", ""),
    ("D", "Detail shot: a hand in a light-blue scrub sleeve carefully lays the beige telephone handset down on the brown wooden "
          "desk in front of the rotary telephone, dark blue night light.", ""),
    ("POV", "Point of view from inside the dark duty room looking through the rectangular glass window of the door: in the "
            "brightly lit pale-green corridor beyond the glass, four {PATIENTS} stand as dark silhouettes; their heads turn "
            "one after another, at different moments, toward the desk with the telephone, not toward the viewer. The dark navy "
            "wall around the window frames the view; no part of the patients appears outside the window opening.", LAYERS),
    ("Z", "Close-up of {NARRATOR} in the dark duty room staring at the glowing door window, the reflection of silhouettes in "
          "his wide eyes.", ""),
    ("Z", "Close-up of {NARRATOR} in the dark, cheeks puffed, holding his breath, dark navy background.", ""),
    ("D", "Detail shot of a side door lock at night: a hand slowly turns a key in the keyhole; the hand is in front of the "
          "keyhole and covers it.", ""),
    ("PŚ", "Medium shot in {CORRIDOR}: a plain side door of the duty room stands open into darkness and {NARRATOR} slips out "
           "sideways with his back flat against the wall, holding his breath.", ""),
    ("PO", "Wide shot of {CORRIDOR}: {NARRATOR} slides along the left wall with his back to it; further down a crowd of "
           "{PATIENTS} presses against the glowing window of the duty-room door, each swaying in their own rhythm.", ""),
    ("Z", PROFILE.replace("{who}", "a tall thin young man"), ""),
    ("Z", HOLD, ""),
    ("Z", PROFILE.replace("{who}", "a bald old man with grey stubble"), ""),
    ("Z", "Close-up of {NARRATOR} recognising someone he knows among the infected, sorrow and fear on his face, pale green "
          "corridor wall behind.", ""),
    ("D", "Detail shot in {DUTYROOM}: the beige telephone handset lying off its cradle on the wooden desk, small sound lines "
          "of a dial tone coming from it.", ""),
    ("PŚ", "Medium-wide shot of the far end of {CORRIDOR}: every door on both sides stands wide open with darkness inside, "
           "except one closed door at the very end — {ISODOOR}.", ""),
    ("Z", WINDOW, LAYERS),
    ("WZ", "Extreme close-up of the wire-mesh window of isolation room 3: a faint patch of breath fog on the glass behind the "
           "mesh; the face of an old man barely visible behind it.", LAYERS),
    ("WZ", "Extreme close-up of the round unblinking eyes of {HENRYK} behind a diamond wire mesh, staring straight at the viewer.", LAYERS),
    ("Z", "Close-up of the wire-mesh window of isolation room 3: the pale hand of {HENRYK} is raised behind the glass, showing a "
          "slow breathing gesture — palm rising, holding, palm lowering; only the part inside the window is visible.", LAYERS),
    ("Z", "Close-up of {NARRATOR} copying a slow breath: eyes half closed, chest rising gently, shoulders lowering, a calmer "
          "expression, green corridor light.", ""),
    ("D", "Detail shot: a hand takes a key from a ring of hospital keys and turns it in the lock of a grey-green metal door; "
          "the hand is in front of the keyhole.", ""),
    ("PŚ", "Medium shot in {CORRIDOR}: the door of isolation room 3 stands open and {HENRYK} steps out through the doorway and "
           "takes {NARRATOR} by the sleeve of his light-blue scrubs.", ""),
    ("PO", "Wide shot of {CORRIDOR}: {HENRYK} leads {NARRATOR} by the sleeve straight through a loose group of {PATIENTS}; both "
           "men walk slowly in step while the patients sway around them unaware.", ""),
    ("D", "Detail shot from the side at floor level: a white sneaker landing on a wet grey floor tile, a small cartoon squeak "
          "line next to the sole, the trouser hem above the ankle.", ""),
    ("PŚ", "Medium shot in {CORRIDOR}: one of the {PATIENTS}, a tall thin young man, freezes mid-step facing the camera with "
           "round white eyes.", ""),
    ("Z", "Close-up: the pale hand of {HENRYK} gently covers the mouth of {NARRATOR}; both are frozen, the orderly's eyes wide "
          "above the hand, green corridor light.", ""),
    ("PŚ", "Medium shot in {CORRIDOR}, seen from behind: an infected patient in a grey-green hospital gown shuffles away toward "
           "the glowing window of the duty room at the far end.", ""),
    ("PO", "Wide shot of {CORRIDOR}: {HENRYK} and {NARRATOR} walk on through the swaying crowd of {PATIENTS}, closer to the camera.", ""),
    ("PP", "Full shot of a concrete hospital stairwell seen from the side, going down to the right: {HENRYK} and {NARRATOR} "
           "stand on the steps one behind the other, dim green emergency light.", ""),
    ("PO", "Wide shot of {BASEMENT}: the empty corridor leading to the pharmacy grille; the cracked lamp behind the grille "
           "flickers.", ""),
    ("PŚ", "Medium shot of {BASEMENT}: behind the metal pharmacy grille stands {ZOSIA}, holding a pair of scissors raised like a "
           "weapon; shelves and a flickering lamp behind her.", ""),
    ("D", "Detail shot: the hands of a nurse in a navy cardigan unlocking a heavy padlock on a metal pharmacy grille; the padlock "
          "and chain are in front of her fingers.", ""),
    ("PŚ", "Medium shot inside the basement pharmacy: the grille gate stands open, {ZOSIA} holds it while {HENRYK} and "
           "{NARRATOR} step inside between the shelves.", ""),
    ("Z", "Close-up of {ZOSIA} looking sideways with suspicion, eyebrows raised, the pharmacy shelves behind her.", ""),
    ("Z", "Close-up of {NARRATOR} in the basement pharmacy answering quietly, tired eyes, shelves behind him.", ""),
    ("Z", "Close-up of {ZOSIA} whispering, her face half lit by a flickering lamp, eyes fixed on the stairs above.", ""),
    ("PŚ", "Medium shot inside the basement pharmacy: {HENRYK} sits on the floor with his back against the wall, knees up, "
           "staring at the door without blinking.", ""),
    ("Z", "Close-up of {NARRATOR} in the dark hospital basement, unable to answer, mouth slightly open, eyes lowered; behind "
          "him, small and out of focus, {HENRYK} stares up the dark stairwell.", ""),
]}
