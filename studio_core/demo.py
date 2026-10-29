"""A small, editable local example; all pictures are labelled illustrations."""
from pathlib import Path
import math
import tempfile

from PIL import Image, ImageDraw, ImageFont

from .models import Project, Scene, Clip
from .media import import_media
from .store import ProjectStore


def create_demo(store: ProjectStore) -> Project:
    p = store.create(Project(title="Głos oceanu", demo=True, story={
        "central_question": "Jak opowiedzieć historię dźwięku, którego źródła nie widzimy?",
        "hook": "Zaczynamy od spokojnej powierzchni i pytania o to, co kryje się niżej.",
        "signature_line": "Najpierw posłuchaj.", "payoff": "Dobra historia prowadzi od pytania do sprawdzonych źródeł.",
        "thesis": "Przykładowy projekt pokazuje pracę studia, a nie ustalenia badawcze.",
        "complication": "Obraz może sugerować więcej, niż wiemy.", "counterpoint": "Ilustracja nie jest dowodem.",
        "stakes_for_viewer": "Zrozumieć proces tworzenia dokumentu.", "open_question": "Jakie źródła wybierzesz?",
        "sting": "", "status": "DRAFT", "approved_hash": "",
    }))
    titles = ["Pod powierzchnią", "Ślad dźwięku", "Wsłuchaj się", "Od pytania do odpowiedzi"]
    texts = ["Na powierzchni wszystko wygląda spokojnie. Ale ta historia zaczyna się pod wodą.",
             "Najpierw posłuchaj. Obraz jest tylko ilustracją. Odpowiedzi poszukamy w źródłach.",
             "Każdy trop wymaga sprawdzenia. Każda informacja potrzebuje swojego miejsca w opowieści.",
             "Zbieramy materiały, układamy narrację i szukamy odpowiedzi. Teraz możesz stworzyć własny film."]
    with tempfile.TemporaryDirectory() as tmp:
        for index, title in enumerate(titles):
            image = Image.new("RGB", (1280, 720))
            draw = ImageDraw.Draw(image)
            for y in range(720):
                t = y / 720
                draw.line((0, y, 1280, y), fill=(int(18-9*t), int(65-42*t), int(79-43*t)))
            if index in (0, 2):
                for n in range(25):
                    y = 230 + n * 25
                    points = [(x, y + math.sin(x / (70 + n * 3) + n) * (8 + n / 2)) for x in range(0, 1280, 6)]
                    draw.line(points, fill=(28 + n, 86 + n * 2, 99 + n * 2), width=2)
                draw.ellipse((850, 90, 950, 190), fill=(211, 196, 159))
                draw.line((640, 250, 640, 520), fill=(136, 176, 180), width=3)
                draw.rounded_rectangle((622, 500, 658, 565), radius=14, fill=(215, 182, 124))
            else:
                for x in range(45, 1240, 5):
                    value = math.sin(x*.05)*math.sin(x*.013)*(1-abs(x-640)/640)
                    draw.line((x, 350-value*150, x, 350+value*150), fill=(133, 192, 187), width=2)
            draw.text((44, 34), "DOCOS / STUDIO", fill=(213, 213, 197))
            draw.text((44, 668), "ILUSTRACJA DEMONSTRACYJNA", fill=(187, 199, 192))
            path = Path(tmp) / f"ocean-{index+1}.png"; image.save(path)
            asset, _ = import_media(store, p.id, path, path.name, {"license": "Ilustracja demonstracyjna DocOS", "provenance": {"type": "procedural-demo"}})
            current = store.get(p.id)
            def add(project, i=index, a=asset):
                scene = Scene(title=titles[i], narration=texts[i], start=i*240, duration=240, asset_id=a.id,
                              prompt="Documentary ocean study, natural light, cinematic underwater atmosphere, no text", search_query="ocean underwater hydrophone",
                              animation="zoom-in" if i % 2 == 0 else "pan-right")
                project.scenes.append(scene)
                project.sequence.clips.append(Clip(track_id="v1", asset_id=a.id, scene_id=scene.id, title=titles[i],
                                                  start=scene.start, duration=scene.duration, animation=scene.animation, fade_in=12, fade_out=12))
            store.mutate(p.id, current.revision, add, history=False)
    return store.get(p.id)
