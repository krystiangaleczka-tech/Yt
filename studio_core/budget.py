"""Conservative estimated API spending; actual billing stays with the provider."""
from .models import uid
from .store import atomic_json,now


def reserve(store,project,connectors):
    config=connectors.config()
    if not config.get("ai_base_url"): return None
    estimate=float(config.get("ai_request_cost",0))
    if estimate<=0: raise ValueError("Ustaw szacowany koszt wywołania API w Połączeniach i limit kosztu projektu")
    path=store.folder(project.id)/"spending.json"
    import json
    with store.lock:
        entries=json.loads(path.read_text()) if path.exists() else []
        if sum(e["estimate"] for e in entries)+estimate>project.budget.get("max_cost",0):
            raise ValueError("Wywołanie przekroczyłoby budżet projektu")
        entry={"id":uid("cost_"),"at":now(),"revision":project.revision,"estimate":estimate,"state":"reserved"}
        entries.append(entry);atomic_json(path,entries)
    return entry


def spending(store,pid):
    import json
    path=store.folder(pid)/"spending.json"
    entries=json.loads(path.read_text()) if path.exists() else []
    return {"estimated_cost":sum(e["estimate"] for e in entries),"calls":len(entries),"entries":entries,"note":"Szacunek zachowawczy; także nieudane zapytanie mogło zostać rozliczone przez dostawcę."}
