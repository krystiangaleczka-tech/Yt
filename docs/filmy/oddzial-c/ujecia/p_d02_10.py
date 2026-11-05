# Prompty dni 2–10. (kadr — kontrola kolejności z rozpiską, prompt albo None, uwaga produkcyjna)
from prompty import LAYERS

CARD = "Karta dnia robiona w Studio (biały napis na czerni) — nie generować."
HUD = "Grafika HUD (zapasy, liczby) robiona w Studio — nie generować."
TXT = "Napis na kartce/ścianie dodać w Studio — generator zostawia puste miejsce."

SHOTS = {
    2: [
        ("TYT", None, CARD),
        ("PŚ", "Medium shot in {BASEMENT}: {NARRATOR} wakes up lying on the concrete floor inside the pharmacy, grey morning "
               "light falling from a small high window under the ceiling.", ""),
        ("D", "Detail shot: a nurse's hand writing a short list on a blank sheet of paper on the pharmacy counter, two plastic "
              "water bottles, a pack of rusks and pill boxes beside it.", TXT),
        ("Z", "Close-up of {HENRYK} sitting bolt upright against the pharmacy wall, staring at the door without blinking, cold "
              "morning light.", ""),
        ("PO", "Wide shot seen through a small basement window at ground level: military trucks parking along the tall "
               "chain-link fence of {YARD} at dawn, {SOLDIERS} jumping out.", ""),
        ("PŚ", "Medium shot: {SOLDIERS} unroll coils of razor wire along the chain-link fence next to the old iron hospital "
               "gate, grey dawn sky.", ""),
        ("Z", "Close-up of {ZOSIA} in the basement pharmacy, worried, lips pressed together, morning light.", ""),
        ("PO", "Wide shot of {CORRIDOR} in daylight with the ceiling lights off: {NARRATOR} and {HENRYK} walk carefully down the "
               "middle of the corridor.", ""),
        ("PŚ", "Medium shot through an open door into a ward room in daylight: {PATIENTS} stand still facing the walls, each "
               "swaying slightly in their own way.", ""),
        ("Z", "Close-up of {NARRATOR} in a doorway recognising one of the infected patients, sorrow and fear on his face.", ""),
        ("D", "Detail shot in {DUTYROOM}, now in daylight: the beige telephone handset still lies on the desk off its cradle.", ""),
        ("PŚ", "Medium shot in {DUTYROOM}, now in daylight: {NARRATOR} quietly packs an electric kettle, a folded blanket and "
               "flashlight batteries into a bag.", ""),
        ("PO", "Wide shot of {CORRIDOR} at dusk: the ceiling lights are off and only small green emergency exit signs glow.", ""),
        ("Z", "Close-up of {NARRATOR} lying on the dark pharmacy floor, looking up at the ceiling in fear.", ""),
    ],
    3: [
        ("TYT", None, CARD),
        ("D", "Detail shot: a hand holding a black marker writes on the bare concrete wall of the basement pharmacy.", TXT),
        ("D", "Detail shot: a hand in a light-blue sleeve writes with a marker under earlier marks on a concrete wall.", TXT),
        ("Z", "Close-up: the thin pale old hand of {HENRYK} slowly writes crooked letters with a marker on a concrete wall.", TXT),
        ("Z", "Close-up of {HENRYK} sitting silently against the wall again, staring ahead, while {ZOSIA} looks at him puzzled "
              "in the foreground.", ""),
        ("D", None, HUD),
        ("PŚ", "Medium shot in {BASEMENT}: {ZOSIA} points at a hand-drawn building plan spread on the pharmacy counter, "
               "{NARRATOR} leaning over it.", TXT),
        ("Z", "Close-up of {HENRYK} and {NARRATOR} sitting face to face on the pharmacy floor, breathing slowly together, eyes "
              "half closed, calm.", ""),
        ("D", "Detail shot: towels being wrapped around the bars of a metal pharmacy grille; a jar of petroleum jelly next to "
              "a hinge.", ""),
        ("PO", "Wide shot of the dark basement pharmacy at night: three people sitting motionless on the floor; beyond the "
               "grille, at the top of the stairs, a faint shadow by a closed door.", ""),
        ("Z", "Close-up of {HENRYK} in the dark, his chest barely moving, eyes open.", ""),
        ("Z", "Close-up of {NARRATOR} in the dark with wide unblinking eyes, listening.", ""),
        ("Z", "Close-up of {ZOSIA} whispering in the dark, her face faintly lit by a cracked lamp.", ""),
        ("PŚ", "Medium shot of a dark concrete stairwell leading up from the basement, a faint green glow at the top.", ""),
    ],
    4: [
        ("TYT", None, CARD),
        ("PŚ", "Medium shot in {CORRIDOR}: a group of {PATIENTS} shuffles toward the duty-room door at the end of the corridor, "
               "drawn by a ringing sound.", ""),
        ("PO", "Wide shot of {CONNECTOR}: {NARRATOR} and {HENRYK} walk quietly along it; outside, behind the fence of the yard, "
               "{SOLDIERS} watch through binoculars.", ""),
        ("Z", "Close-up of a soldier in a gas mask seen through a tall window, raising one hand and nothing more.", LAYERS),
        ("PO", "Wide shot of {KITCHEN}, empty and dim, steam-stained walls.", ""),
        ("PŚ", "Medium shot in {KITCHEN}: {NARRATOR} fills a sack with tin cans while {HENRYK} fills plastic canisters with "
               "water from a big steel tap.", ""),
        ("D", "Detail shot: a thin old hand turning a steel kitchen tap halfway off, water still trickling.", ""),
        ("Z", "Close-up of the small window in the steel walk-in fridge door: inside, an infected cook with frosted eyebrows, "
              "pale green skin and white eyes follows the flashlight; she is visible only inside the window opening.", LAYERS),
        ("Z", "Close-up of {HENRYK} slowly shaking his head in the kitchen.", ""),
        ("D", "Detail shot: a tin can rolling across white kitchen floor tiles, small cartoon motion lines.", ""),
        ("PO", "Wide shot of {CONNECTOR}, empty, a dark doorway at the far end leading to Ward C.", ""),
        ("PŚ", "Medium shot in {CONNECTOR}: {NARRATOR} runs carrying a sack while {HENRYK} keeps walking calmly behind him.", ""),
        ("Z", "Close-up: {HENRYK} presses {NARRATOR} flat against the connector wall with one hand, looking him in the eyes.", ""),
        ("PŚ", "Medium shot in {CONNECTOR}: three {PATIENTS} shuffle past two men pressed against the wall, each at a different "
               "pace, heading toward a tin can lying on the floor.", ""),
        ("Z", "Close-up of {NARRATOR} pressed to the wall while an infected patient passes inches from his face.", ""),
        ("D", None, HUD),
        ("Z", "Close-up of {NARRATOR} in the basement pharmacy lifting his head, listening toward the ceiling.", ""),
    ],
    5: [
        ("TYT", None, CARD),
        ("PŚ", "Medium shot of {NARRATOR} climbing a concrete hospital stairwell, shielding a flashlight with his hand.", ""),
        ("PŚ", "Medium shot of a treatment-room door barricaded from inside; the edge of a medical couch and a cabinet visible "
               "through the narrow gap.", ""),
        ("Z", "Close-up of {NARRATOR} whispering at a closed door.", ""),
        ("PŚ", "Medium shot: the treatment-room door opens a crack and {NOWAK} peers out.", ""),
        ("PŚ", "Medium shot in {BASEMENT}: {ZOSIA} questions {NOWAK} in front of the pharmacy shelves.", ""),
        ("Z", "Close-up of {NOWAK} answering while his eyes slide sideways toward someone off-screen.", ""),
        ("Z", "Close-up of {HENRYK} staring without blinking.", ""),
        ("D", "Detail shot: a hand-drawn building plan sketched on the back of a patient chart, a pen pointing at a small box.", TXT),
        ("Z", "Close-up of {NARRATOR} with a grim expression of sudden understanding, pharmacy lamp light.", ""),
        ("Z", "Close-up of {NOWAK} speaking quietly, his hands hidden in his long sleeves.", ""),
        ("PŚ", "Medium shot: {ZOSIA} reaches for a flashlight on the pharmacy counter.", ""),
        ("PŚ", "Medium shot: {HENRYK} stands in front of the pharmacy grille, blocking the way out, arms at his sides.", ""),
        ("D", "Detail shot: the small high basement window, pitch dark outside.", ""),
        ("Z", "Close-up of {NOWAK} pulling his hands deeper into his sleeves.", ""),
    ],
    6: [
        ("TYT", None, CARD),
        ("PŚ", "Medium shot in the dark {BASEMENT}: {NARRATOR} sits by the pharmacy grille keeping watch, a switched-off "
               "flashlight on his knees.", ""),
        ("PO", "Wide shot looking up the dark concrete stairwell from the basement: bare feet coming down the steps and stopping "
               "halfway.", ""),
        ("PŚ", "Medium shot: an infected nurse in a white uniform with an ID badge stands on the stair landing, head tilted, "
               "listening; pale green skin, round white eyes.", ""),
        ("Z", "Close-up of {NOWAK} groaning in his sleep on the pharmacy floor.", ""),
        ("PŚ", "Medium shot: the infected nurse steps one stair lower.", ""),
        ("Z", "Close-up: the hand of {NARRATOR} covers the mouth of the sleeping {NOWAK}, whose forehead glistens with sweat.", ""),
        ("PŚ", "Medium shot: {HENRYK} silently throws a roll of bandage up the stairwell.", ""),
        ("PŚ", "Medium shot of the stair landing: a bandage roll bounces off the wall and the infected nurse turns and climbs "
               "back up after the sound.", ""),
        ("Z", "Close-up of {HENRYK} giving a small nod in the dark.", ""),
        ("D", "Detail shot: tin cans tied on a string stretched across concrete stairs as an alarm.", ""),
        ("D", "Detail shot: chalk lines drawn on a concrete floor marking a safe path.", ""),
        ("PŚ", "Medium shot: {ZOSIA} takes {NARRATOR} aside between pharmacy shelves, speaking quietly.", ""),
        ("Z", "Close-up of {NARRATOR} brushing off her worry with a tired face.", ""),
        ("D", "Detail shot: a hand drawing a chalk tally mark on a concrete wall next to six earlier marks.", ""),
    ],
    7: [
        ("TYT", None, CARD),
        ("PO", "Wide shot of a basement corridor with pipes leading to a door with a yellow high-voltage sign; {NOWAK} leans on "
               "the wall, {NARRATOR} walks ahead.", ""),
        ("PŚ", "Medium shot of {ELECTRICAL}: one cabinet door hangs open, a small spark flying.", ""),
        ("D", "Detail shot: a thick black power cable cut cleanly in half inside a switch cabinet.", ""),
        ("D", "Detail shot: a pair of heavy bolt cutters lying on a concrete floor.", ""),
        ("PŚ", "Medium shot in {ELECTRICAL}: {NARRATOR} questions {NOWAK}, both lit by a flashlight.", ""),
        ("WZ", "Extreme close-up: a hand in a dark sleeve clenching the fabric of the other sleeve.", ""),
        ("Z", "Close-up of {NOWAK} answering and avoiding eye contact, his glasses reflecting the flashlight.", ""),
        ("D", "Detail shot: a small notebook with three short lines, two of them crossed out.", TXT),
        ("PŚ", "Medium shot of a basement corridor: {NARRATOR} stops and listens to a pipe on the wall.", ""),
        ("Z", "Close-up of {NARRATOR} pressing his ear to a cold metal pipe.", ""),
        ("D", "Detail shot: a key tapping twice on a metal pipe, small sound lines.", ""),
        ("Z", "Close-up of {NARRATOR} waiting with his ear on the pipe, eyes wide.", ""),
        ("Z", "Close-up of {ZOSIA} in the pharmacy, decided and firm.", ""),
        ("PŚ", "Medium shot in the pharmacy: {ZOSIA}, {NARRATOR} and {NOWAK} look at {HENRYK}, who nods.", ""),
    ],
    8: [
        ("TYT", None, CARD),
        ("PO", "Wide shot at noon: {NARRATOR}, {ZOSIA} and {HENRYK} walk along {CONNECTOR} toward a staircase.", ""),
        ("PŚ", "Medium shot: double doors of a hospital ward with a chain wrapped through the handles from the inside.", ""),
        ("POV", "Point of view through the glass panes of the ward doors: a barricade of tables in {WARD_A}; behind it {IRENA} "
                "and {KUBA}, who holds a broken chair leg like a bat.", LAYERS),
        ("Z", "Close-up of {KUBA} behind the glass, shaking his head distrustfully.", LAYERS),
        ("Z", "Close-up of {HENRYK} blinking once, very slowly, in front of the glass doors.", ""),
        ("D", "Detail shot: a heavy chain dropping onto a linoleum floor.", ""),
        ("PŚ", "Medium shot of the far end of the corridor of {WARD_A}: an infected orderly steps out through an open toilet "
               "door; pale green skin, white eyes, grey uniform.", ""),
        ("PŚ", "Medium shot: {HENRYK} stands between the group and the infected orderly, breathing loudly on purpose, chest heaving.", ""),
        ("PO", "Wide shot of the corridor of {WARD_A}: the infected orderly turns to follow {HENRYK} deeper down the corridor while "
               "the others back away toward the exit.", ""),
        ("PŚ", "Medium shot: {NARRATOR} hurries back down the ward corridor.", ""),
        ("PŚ", "Medium shot in a hospital bathroom: {HENRYK} holds a toilet-stall door shut with his back while something "
               "pounds on it from inside.", ""),
        ("D", "Detail shot: a mop handle jammed through the handle of a toilet-stall door.", ""),
        ("PŚ", "Medium shot in the basement pharmacy: {IRENA} takes the hand of {NOWAK} with concern.", ""),
        ("Z", "Close-up of {NOWAK} pulling his hand away sharply.", ""),
        ("Z", "Close-up at night: {KUBA} leans over and whispers to {NARRATOR}, who wakes with a start.", ""),
    ],
    9: [
        ("TYT", None, CARD),
        ("PŚ", "Medium shot in the pharmacy in the morning: {NARRATOR} questions {NOWAK}, who sits on a crate.", ""),
        ("PŚ", "Medium shot: {ZOSIA} points at words written on the wall while the others argue around her.", TXT),
        ("Z", "Close-up of {KUBA} siding with the doctor, defiant, arms crossed.", ""),
        ("D", "Detail shot: a thin old finger tapping a word written in marker on a concrete wall.", TXT),
        ("D", "Detail shot: tin cans on a string falling down concrete stairs.", ""),
        ("PO", "Wide shot of the stairwell: three {PATIENTS} coming down the stairs, each with a different gait.", ""),
        ("PŚ", "Medium shot: the pharmacy goes dark as {ZOSIA} switches off the lamp; people drop to the floor behind shelves.", ""),
        ("Z", "Close-up in the dark: {IRENA}'s teeth chattering, the hand of {NARRATOR} over her mouth.", ""),
        ("D", "Detail shot: pale green fingers touching a metal grille wrapped in towels.", ""),
        ("PO", "Wide shot: infected patients walking away down a basement corridor toward a door with a yellow sign.", ""),
        ("D", "Detail shot: a tipped-over plastic water canister and a puddle on the concrete floor.", ""),
        ("Z", "Close-up: {ZOSIA} shows {KUBA} a sheet of paper.", TXT),
        ("Z", "Close-up of {KUBA}, frightened for the first time.", ""),
        ("PO", "Wide shot of the dark basement corridor in the evening; a closed door at the end, small impact lines around it.", ""),
        ("Z", "Close-up of {NOWAK} speaking, nervous.", ""),
        ("WZ", "Extreme close-up of the round unblinking eyes of {HENRYK}, eyelids half lowered mid-blink.", ""),
    ],
    10: [
        ("TYT", None, CARD),
        ("PO", "Wide shot of {YARD} in daylight: a small military drone drops a supply crate onto the lawn.", ""),
        ("POV", "Point of view from a ground-floor window: a supply crate on the lawn thirty metres away; a dozen {PATIENTS} "
                "stand in the sunlight around {YARD}.", LAYERS),
        ("Z", "Close-up of {KUBA} volunteering, determined.", ""),
        ("D", "Detail shot: thin old hands wrapping bandage around the sole of a white sneaker.", ""),
        ("PŚ", "Medium shot: a side door of the hospital opened with a key, daylight outside.", ""),
        ("PO", "Wide shot of {YARD}: {NARRATOR} and {KUBA} creep across the grass while infected patients stand facing the "
               "building, each tilted differently.", ""),
        ("PŚ", "Medium shot: {SOLDIERS} behind the fence aim rifles at the yard but do not fire.", ""),
        ("D", "Detail shot: a supply crate in a teenager's hands, water bottles clinking inside.", ""),
        ("PŚ", "Medium shot: the nearest infected patient in the yard slowly starts turning around.", ""),
        ("PŚ", "Medium shot: {NARRATOR} throws his jacket toward the parked white ambulance.", ""),
        ("PO", "Wide shot of {YARD}: the jacket hits the ambulance and its lights start flashing.", ""),
        ("PO", "Wide shot of {YARD}: infected patients move toward the flashing ambulance while two figures run to the side door.", ""),
        ("PŚ", "Medium shot: a soldier behind the fence raises a thumb; another soldier grabs his arm.", ""),
        ("D", "Detail shot: twelve plastic water bottles lined up on a pharmacy counter.", ""),
        ("D", "Detail shot: a handwritten note lying on top of military ration packs.", TXT),
    ],
}

# dni 2–5 są teraz w p_d02a.py (wersja szybsza)
for _d in (2, 3, 4, 5):
    SHOTS.pop(_d)
# dni 6–10 są teraz w p_d06a.py (wersja szybsza)
for _d in (6, 7, 8, 9, 10):
    SHOTS.pop(_d)
