# Central Production Orchestrator — plan wdrożenia

Status: **plan techniczny, nie wdrożenie runtime**  
Data: 2026-11-02  
Repozytorium: krystiangaleczka-tech/Yt, bazowa gałąź main  
Zakres zmiany tego dokumentu: tylko specyfikacja, bez modyfikacji kodu aplikacji.

## 1. Cel i zasada działania

DocOS Studio powinno prowadzić autora filmu od projektu do eksportu przez **jeden przycisk „Następny krok”**. Użytkownik nie musi znać nazw backendowych agentów i nie musi pamiętać kolejności. Każda decyzja o kolejnym etapie jest obliczana na backendzie z trwałego stanu projektu, zależności, zatwierdzeń, aktualności rezultatów i dostępnych wykonawców.

**AI przygotowuje treści i propozycje; orkiestrator decyduje o kolejności, zakresie i możliwości uruchomienia.** Model językowy nie jest źródłem prawdy o postępie i nie powinien dostawać dostępu do arbitralnego wykonywania komend.

Po starcie aplikacji nie ładujemy całego repozytorium ani długiego promptu do AI. Aplikacja odczytuje projekt i obliczony przez backend aktualny stan. Context Builder przygotowuje potrzebny kontekst **przy konkretnym wywołaniu** danego modułu.

Zasada bezpieczeństwa: pojedyncze kliknięcie wykonuje **jedną dozwoloną czynność logiczną** (np. otwarcie formularza, wygenerowanie propozycji lub zatwierdzenie), nie całą produkcję bez nadzoru. Automatyczne zatwierdzenia tylko dla jawnie bezpiecznych, deterministycznych etapów. Decyzje redakcyjne, koszty i publikacja wymagają jawnej akceptacji.

### Poza zakresem pierwszego wdrożenia

- Bez przepisywania działających generatorów obrazów, dźwięku, animacji czy renderera.
- Bez automatycznego akceptowania historii, scen, wizerunków, faktów i eksportu końcowego.
- Bez obietnicy, że LLM będzie pamiętał stan między wywołaniami.
- Bez usuwania ręcznej nawigacji, istniejących plików, historii projektu i dotychczasowych trybów produkcji.
- Bez globalnego blokowania ręcznej edycji: walidacja ma zabezpieczać przejścia i eksport, nie utrudniać poprawiania scen.

## 2. Ustalenia z audytu main (2026-11-02)

1. **Błąd krytyczny P0 — persistencja flow.** Frontend w apps/studio/src/FilmFlow.tsx i apps/studio/src/Director.tsx zapisuje legacy.production_flow za pomocą s.patch. Endpoint PATCH /api/projects/{id} wywołuje ProjectService.patch, który w studio_core/service.py dopuszcza określony zestaw pól **bez legacy**. Sam frontendowy komunikat o zapisaniu nie dowodzi, że backend przyjął zmianę. Nowy, wąski endpoint zapisu flow musi poprzedzić orkiestrację.
2. **Rozproszone reguły.** App.tsx utrzymuje listę stron; FilmFlow.tsx utrzymuje nextPage oraz etapowe aprobaty; flowTypes.ts zawiera isReady/isApproved i podpisy; studio_core/store.py ma osobną, uproszczoną funkcję next_step zależną od faktów, historii, scen i głosu. To nie jest jedna autorytatywna grafowa definicja.
3. **Rozproszony kontekst AI.** studio_api/flow.py składa prompty dla wybranych zadań (pomysł, master, akt, sekwencje, outline, scenariusz, direction, review). Moduły generatorów i montażu mają własne wejścia. Potrzebny wspólny kontrakt i polityka selekcji kontekstu.
4. **Niepełne wznawianie jobów.** studio_workers/jobs.py przechowuje wpisy w SQLite i oznacza uruchomione zadania po restarcie jako INTERRUPTED, ale zapamiętane Pythonowe callbacki znajdują się w pamięci (self.tasks). Po restarcie sama trwałość rekordu nie oznacza, że można odbudować wykonanie.
5. **Dwa modele beatów/scen.** Project.beats (studio_core/models.py) istnieje obok beatów reżyserskich zapisanych w legacy.production_flow.director; podobnie klasyczne Scene i StageScene. Orkiestrator musi je mapować przez stabilne referencje, nie traktować jako identyczne.
6. **Istniejące zabezpieczenia do wykorzystania.** ProjectStore.mutate realizuje ochronę rewizji i zapis atomowy; istnieją historie undo/redo, walidacja blokad, check_project, budget.reserve, kontrola świeżości materiałów, import wariantów i Jobs. Nie dublować tych mechanizmów.

## 3. Kanoniczna architektura

**Backend jako źródło prawdy:**

- **Pipeline Registry:** wersjonowany graf etapów i reguły zależności zależne od trybu produkcji (documentary, animation_2d, broll). Jeden katalog dla backendu i API. Frontend tylko renderuje jego odpowiedź.
- **State Resolver:** na podstawie projektu i zadań oblicza status każdego etapu, brakujące wejścia i najbliższą poprawną akcję.
- **Dependency & Validation Engine:** typowane bramki gotowości i akceptacji, statusy stale, blokady mediów, weryfikacja faktów oraz rozróżnienie błędów od ostrzeżeń.
- **Context Builder:** generuje wersjonowany, ograniczony rozmiarem pakiet danych dla wywołania wybranego agenta.
- **Module Registry / Adapters:** jawne mapowanie etapu do istniejącego backendowego handlera, schematu wejścia/wyjścia i walidatora.
- **Execution Coordinator:** idempotentny start zadań, monitoring, anulowanie, retry i kontrola rewizji przed zatwierdzeniem rezultatu.
- **Review & Approval Service:** trwałe potwierdzenia i ślady pochodzenia wraz z podpisem wejścia.
- **Frontend Action Bar:** główny przycisk, pasek postępu, blokery, koszt przed uruchomieniem i powrót do odpowiedniego ekranu.

Proponowane nowe pliki:
- studio_core/orchestrator/models.py — StageDefinition, StageState, NextAction, Blocker, Approval, ExecutionRecord.
- studio_core/orchestrator/registry.py — kanoniczna definicja grafu, warianty według trybu.
- studio_core/orchestrator/resolver.py — deterministyczna ewaluacja stanu i wyboru następnej akcji.
- studio_core/orchestrator/validators.py — wymagania wejść, spójność, zakres i zatwierdzenia.
- studio_core/orchestrator/context.py — polityki Context Buildera i provenance.
- studio_core/orchestrator/adapters.py — mapowanie nazw etapów na istniejące funkcje.
- studio_core/orchestrator/executor.py — wykonanie i idempotencja.
- studio_api/orchestrator.py — read-only status, preview, uruchamianie i zatwierdzanie.
- apps/studio/src/OrchestratorBar.tsx oraz OrchestratorBar.css — uniwersalny panel Następny krok.
- apps/studio/src/orchestratorTypes.ts — typy API, bez ponownej implementacji reguł Python.
- studio_tests/test_orchestrator.py, apps/studio/tests/orchestrator.test.mjs — testy kontraktów.

Nie zmieniać istniejących struktur zanim nie przejdzie migracja i testy wstecznej zgodności.

## 4. Graf produkcji: etapy i zakresy

Etapy logiczne i podstawowe zależności:

| Etap | Zakres | Warunek uruchomienia / zatwierdzenia | Rezultat |
|---|---|---|---|
| project | projekt | nowy projekt z trybem i tytułem | brief i parametry |
| idea | projekt | brief istnieje | wybrany pomysł |
| research | film/scena, wymagany dla faktografii | faktografia; źródła przed twierdzeniami | zweryfikowane fakty |
| master_story | projekt | wybrany pomysł | zatwierdzona pełna historia |
| acts | projekt | master_story | zatwierdzone akty |
| sequences | akt | akt zatwierdzony | sekwencje z metryką czasu |
| script | akt | struktura + wymagane fakty | tekst scenariusza |
| scene_plan | sekwencja | scenariusz/struktura | zatwierdzony outline scen |
| beats | scena | outline + scenariusz | cele, zmiany wiedzy i emocji, napięcie |
| direction | scena | beaty | zatwierdzona reżyseria i rytm |
| shot_list | scena | reżyseria | zamapowane ujęcia z czasem i ID |
| storyboard | ujęcie | shot_list | propozycje kadrów i ich akceptacja |
| production_assets | ujęcie/scena | storyboard i zasoby | obrazy / warstwy / rekwizyty |
| voice_audio | scena/akt | zatwierdzony tekst i profil głosu | nagrania oraz cue dźwiękowe |
| animation | ujęcie | zatwierdzone assety | animacja / sekwencja klatek |
| timeline | film | przygotowane ujęcia; audio równolegle według potrzeb | animatik i montaż |
| quality_review | film i scena | montaż / assety | uwagi i poprawki |
| export | film | brak krytycznych problemów; wymagane zatwierdzenia | finalny plik i metadane |

**Ważne:** to DAG (graf zależności), nie koniecznie jeden liniowy łańcuch. Audio może być przygotowywane równolegle do storyboardu, a faktografia wymaga weryfikacji źródeł, podczas gdy fikcja nie. Wersja MVP może renderować listę liniową, ale backend od początku powinien obsługiwać graf i scope per akt/scena/ujęcie.

**Beaty:** obecny DirectorBeat jest już elementem direction; w fazie migracji można wprowadzić logiczny etap beats pokazujący edycję tej samej struktury, z trwałymi ID beatów. Nie kopiować beatów do drugiego niezależnego magazynu bez mapowania.

**Brakujące kroki nie są automatycznie pomijane:** jeśli moduł nie ma wykonawcy automatycznego, orkiestrator zwraca akcję manualną albo review, zamiast udawać, że generowanie działa.

## 5. Kontrakt etapu i statusu

StageDefinition musi zawierać:
- id, version, label, production_modes, scope (project/act/sequence/scene/shot),
- prerequisites (z warunkami), required_inputs, input_schema, output_schema,
- validator_id, adapter_id, context_policy_id,
- approval_policy (manual/automatic_if_deterministic), retry_policy, cost_class,
- UI target i reguły stale propagation (na zależne rezultaty, a nie wszystkie obrazy).

Stany: **NOT_STARTED, BLOCKED, READY, RUNNING, REVIEW_REQUIRED, APPROVED, STALE, FAILED, SKIPPED**.

Przykładowy StageState:
- stage_id: direction
- scope: scene:scene_123
- status: BLOCKED
- blockers: [ { code: "BEATS_NOT_APPROVED", message: "Zatwierdź beaty", target: "beats" } ]
- next_action: { kind: "OPEN_STAGE", label: "Otwórz beaty", target: "beats" }
- input_signature: sha256 wersjonowanych zależności
- output_signature: sha256 zaakceptowanego rezultatu
- approved_by, approved_at, pipeline_version, project_revision

Zasady:
- Zmiana Master Story unieważnia tylko odpowiednie wyniki zależne (ustalane po podpisie), nie kasuje ręcznie edytowanych plików.
- Twarda blokada broni uruchomienia kolejnego zautomatyzowanego etapu i finalnego eksportu.
- Ostrzeżenie pozwala na pracę ręczną, ale nie jest potajemnie uznawane za sukces.
- Akceptacje projektowe i per akt/scena różnią się zakresem; nie ma jednego checkboxa dla całego filmu.
- Status jest odtwarzalny z projektu + historii zadań, a nie utrzymywany jedynie w lokalnym React state.

## 6. Jeden przycisk „Następny krok”

**GET /api/projects/{pid}/orchestrator/status**
Zwraca: revision, pipeline_version, stage_states[], progress, blockers[], next_action, current_job, cost_estimate i wymagane zatwierdzenia.

**POST /api/projects/{pid}/orchestrator/next**
Wejście: expected_revision, action_id (z poprzedniego statusu), idempotency_key, opcjonalne potwierdzenie kosztu.
Backend ponownie oblicza status i dopiero wtedy podejmuje dozwolone działanie.

Możliwe akcje:
- OPEN_FORM — kieruj do brakującego pola na istniejącym ekranie.
- GENERATE_PROPOSAL — uruchom odpowiedni adapter AI.
- OPEN_REVIEW — otwórz wynik do świadomej akceptacji.
- APPROVE — zatwierdź wskazany scope, tylko po przejściu walidatorów.
- START_JOB — uruchom render/voice/generację z obsługą postępu.
- RESUME_OR_RETRY — wróć do zadania albo ponów przerwaną operację.
- FIX_BLOCKER — pokaż dokładny brak i skrót do edycji.
- OPEN_EXPORT_CHECK — pokaż kontrolę finalną, nie publikuj automatycznie.

**Reguła idempotencji:** dwa kliknięcia lub ponowne wysłanie tego samego tokenu nie mogą stworzyć duplikatów ujęć ani podwójnie rozliczyć generacji. Jeśli revision lub input_signature zmieniły się, zwróć 409 i nową rekomendację, nie zastosuj starych wyników.

Kliknięcie nie może automatycznie zatwierdzać propozycji redakcyjnych. Akceptacja po review to osobny krok świadomego użytkownika.

## 7. Context Builder: co AI dostaje i kiedy

Przy otwarciu projektu: brak wywołania LLM; backend wylicza status.
Przy wywołaniu konkretnego modułu: tworzony jest ContextPack z:
1. project_id, revision, pipeline_version, stage_id, scope_id i objective;
2. project/global: tytuł, język, tryb, czas docelowy, profil kanału i wybrane pola Story Bible;
3. upstream: zatwierdzona Master Story, właściwy akt, sekcja, scena, beat oraz podpisy zależności;
4. continuity: sąsiednie sceny, wygląd postaci, stan rekwizytów, chronologia i wiedza widza/bohatera;
5. evidence: tylko istotne fakty, źródła, status weryfikacji i reguły dramatyzacji;
6. capabilities: konkretne dostępne typy ujęć / moduły / schemat wyniku, nie całą listę funkcji repozytorium;
7. constraints: format odpowiedzi, liczba wariantów, budżet, limit materiałów, blokady, styl;
8. context_version, context_hash i provenance_sources.

Zasady:
- deterministyczna selekcja kontekstu po scope; nie wysyłaj wszystkich mediów i skryptów bez potrzeby;
- priorytet źródeł: zatwierdzone dane projektu > obowiązujące reguły > wiedza o sąsiednich scenach > notatki;
- dane z zewnętrznych tekstów i assetów są oznaczone jako niezaufane i nie zmieniają instrukcji;
- ograniczenie tokenów, sensowne skróty, jawne pomijanie i podgląd „co wie AI?”;
- bez cichego domyślania faktów w dokumentach; wąskie walidatory zgodne z istniejącą weryfikacją faktów;
- wersjonowane prompty i schematy; zapis kosztu i skrótu wejścia do historii audytu.

Przykład: dla zombie za drzwiami moduł direction otrzymuje opis sceny, obecne beaty, napięcie, wiedzę lekarza/widza, telefon jako dźwięk i bibliotekę wzorców; nie dostaje generatora PDF ani wszystkich plików repozytorium.

## 8. Module Registry i integracja bez przepisywania

Pierwsza fala adapterów:
- flow.ai — istniejący generator propozycji z studio_api/flow.py;
- director.auto — istniejące wzorce i deterministyczny planner z apps/studio/src/directorTypes.ts (docelowo wydzielić algorytm do współdzielonego backendu; nie odtwarzać różnych reguł w TS i Pythonie);
- director.ai — istniejący generator kierunku przez studio_api/flow.py;
- project.review — kontrola spójności flow/reżyserii i istniejące check_project;
- storyboard/scenes — wykorzystanie istniejących scen i stabilnych referencji flow_outline_id oraz flow_director_shot_id;
- generator obrazów, audio, animation, render — adaptery delegujące do obecnych API/workerów, bez tworzenia osobnych pipeline’ów.

W rejestrze każdy adapter deklaruje: accepted_input_schema, output_schema, deterministic flag, side_effects, cost_estimate, capability_check, idempotency, retry.

**Tryby:** documentary, animation_2d i broll mają różne wymagania. Documentary wymaga weryfikacji faktów, fikcyjny horror nie. Paper Theatre 2.5D pozostaje jedną z opcji produkcyjnych, nie zasadą każdego filmu.

## 9. Zapisywanie flow i migracje P0

Zamiast dopuścić dowolną modyfikację całego legacy w ProjectService.patch:
- wprowadzić typowany ProductionFlow model (Pydantic) i dedykowane PATCH /api/projects/{pid}/flow, z expected_revision i walidacją;
- na start zachować produkcyjne dane w legacy.production_flow i zgodność z istniejącymi projektami;
- naprawić wszystkie miejsca zapisu FilmFlow/Director oraz dodać test rzeczywistego round trip przez API;
- zdefiniować wersję flow v2 i kontrolowaną migrację bez kasowania starych pól;
- później, gdy wszystkie moduły przejdą na nowy kontrakt, ewentualnie wynieść flow do dedykowanego pola Project.

Wymagany test regresyjny: kliknięcie zatwierdzenia Master Story i planu reżyserii -> 200 -> nowa rewizja -> reload z backendu -> wartości i status zachowane.

## 10. Trwałe joby i bezpieczny retry

Obecna SQLite Jobs zostaje. Dodać trwały **TaskDescriptor**: project_id, stage_id, scope_id, input_signature, adapter_id, adapter_version, params, estimated_cost, retry_count, idempotency_key, status.

- Zapis transakcyjny przed uruchomieniem, kontrola tylko jednego joba dla tego samego scope/input.
- Odtwarzanie przez rejestr adapterów po restarcie zamiast callbacków z self.tasks.
- Jawne rozróżnienie nieukończonego joba i gotowego wyniku oczekującego na zatwierdzenie.
- Wyniki z nieaktualnych wejść odkładać jako wariant do przeglądu, nie aplikować automatycznie.
- Limit prób i backoff dla błędów transportowych, bez ponownego kosztownego generowania po błędnym kliknięciu.
- Przed generacją pokazać wymagany model i szacunek wydatku; utrzymać limity z budget.reserve.
- Dziennik: kto uruchomił, który model/adapter, czego użył, co wygenerował, co zatwierdzono.

## 11. Plan prac w paczkach (zadania)

| Priorytet | Zadanie | Obszar | Kryterium ukończenia |
|---|---|---|---|
| P0 | ORCH-001: audit save flow i reprodukcja błędu | API/testy | Test wykazuje aktualny problem zapisu |
| P0 | ORCH-002: typowany endpoint zapisu flow | studio_core, studio_api | Round trip zapis/reload i konflikt 409 |
| P0 | ORCH-003: migracja danych i integracja FilmFlow/Director | TS/Python | Stare projekty nadal się otwierają i zapisują |
| P0 | ORCH-004: mapa istniejących etapów i dubli modeli | dokumentacja | Kanoniczne ID, scope i owner danych |
| P1 | ORCH-005: Registry v1 i warianty według trybu | studio_core/orchestrator | Każdy etap ma wymagania i adapter |
| P1 | ORCH-006: Resolver statusu, blokad i NextAction | backend | Ten sam wynik przy tym samym stanie projektu |
| P1 | ORCH-007: podpisy i stale propagation | backend | Zmiana scenariusza unieważnia zależną reżyserię |
| P1 | ORCH-008: read-only status API | backend | Status sprawdzany bez wywołania AI |
| P2 | ORCH-009: przycisk, pasek postępu, blokery i skróty | React | Jedna akcja zależna od stanu |
| P2 | ORCH-010: uruchamianie NextAction + idempotency | API | Double-click nie uruchamia duplikatu |
| P2 | ORCH-011: backendowe approval/review gating | API | Bez akceptacji nie przechodzi do produkcji |
| P3 | ORCH-012: Context Builder i podgląd „co wie AI” | backend/UI | Spójny zakres i wersja promptu |
| P3 | ORCH-013: Adaptery flow, director, review | backend | Wynik jest propozycją, nie cichą modyfikacją |
| P4 | ORCH-014: storyboard, generowanie assetów i audio | adaptery | Delegacja do istniejących modułów |
| P4 | ORCH-015: JobDescriptor i retry po restarcie | Workers/API | Wznowienie po zamknięciu bez strat |
| P5 | ORCH-016: montaż, kontrola finalna i eksport | backend/UI | Brak eksportu mimo krytycznych blockerów |
| P5 | ORCH-017: testy przekrojowe, 3 tryby, migracje | CI | Pełny film testowy i testy restartu |
| P5 | ORCH-018: dokumentacja oraz wycofanie starych ścieżek | docs/UI | Jeden stan orkiestratora bez dubli reguł |

**Kolejność dostarczania:** P0 -> P1 -> P2 -> P3 -> P4 -> P5. Najpierw naprawić zapis i stworzyć niezmienny, sprawdzalny stan, potem dopiero przycisk. Nie udawać, że cały automat jest gotowy po dodaniu UI.

## 12. Kryteria akceptacji końcowej

1. Uruchomienie aplikacji offline i otwarcie filmu nie wysyła żadnego promptu do modelu AI.
2. UI pokazuje jedną akcję „Następny krok” wynikającą z backendowego statusu, nie z lokalnej tablicy if/else.
3. Nowy horror 2D: można przejść od pomysłu do scen i planu ujęć bez ręcznego wymyślania kolejności modułów.
4. Documentary: generowanie faktograficznej narracji zostaje zablokowane bez wymaganych zweryfikowanych dowodów.
5. Zmiana Master Story, tekstu aktu, Story Bible i scene outline dezaktualizuje odpowiednie downstream rezultaty; ręczne assety są zachowane.
6. Wykres napięcia, paski montażowe, biblioteka wzorców i notatki reżyserii działają po restarcie i reloadzie.
7. Dwa kliknięcia NextAction ani równoległe okna nie powodują podwójnego uruchomienia albo nadpisania nowszych danych.
8. Przerwane zadanie da się poprawnie wznowić lub bezpiecznie ponowić z trwałego deskryptora.
9. Review i krytyczne blokery nie są automatycznie omijane; eksport finalny przechodzi przez check_project i rozszerzone dependency gates.
10. Wszystkie trzy tryby produkcji oraz istniejące narzędzia ręczne pozostają dostępne i zachowują dotychczasowe dane.
11. Node/frontend tests, Python unit/integration, workflow API, end-to-end smoke i restart/retry przechodzą w CI.

## 13. Matryca testów szczególnie krytycznych

- flow_persist_and_reload, stale_approval_after_master_edit, stale_after_script_edit;
- documentary_facts_required_vs_fiction_skip, optional_broll_production;
- stage_dag_no_cycles, missing_executor_returns_manual_action;
- context_scope_no_cross_project_leakage, untrusted_source_does_not_override_rules, budget_scope;
- double_click_idempotent, parallel_tabs_conflict_409, stale_ai_response_never_overwrites;
- worker_crash_mid_generation, resume_after_restart, retry_budget_not_double_billed;
- no_duplicate_shots_after_transfer, manual_lock_blocks_overwrite;
- final_export_hard_blocker, accepted_warning_not_equivalent_to_hard_error;
- backward_compatibility_project_from_before_director_and_before_orchestrator.

## 14. Wdrożenie i zgodność

- Flaga funkcji per projekt: orchestrator_enabled (domyślnie początkowo wyłączona dla starych projektów).
- Migracja bez usuwania oryginalnej struktury; backup/snapshot przed przeniesieniem stanu.
- Najpierw tryb read-only: status i rekomendowana akcja, bez sterowania.
- Potem włączyć NextAction dla etapów pisarskich i reżyserii.
- Następnie podłączyć generację mediów i joby.
- Dopiero po testach produkcyjnych usunąć stare rozproszone reguły kolejności; na czas przejścia zachować zgodność API.
- Rollback: wyłączyć feature flag, nie nadpisywać starych danych.

## 15. Definition of Done dla pierwszej paczki

Paczkę P0 uznajemy za ukończoną dopiero gdy:
- endpoint flow przyjmuje/odrzuca zmiany zgodnie ze schematem;
- zapis Master Story, aktów, scen i reżyserii przechodzi przez API i reload bez utraty danych;
- brak możliwości modyfikowania innych, niezamówionych kluczy legacy przez tę ścieżkę;
- stare projekty otwierają się bez wymuszania ponownej generacji;
- istnieje test backendowy odtwarzający dokładny poprzedni problem i pokazujący jego naprawę.

**Decyzja końcowa:** Orkiestrator jest deterministyczną usługą sterującą. Context Builder buduje kontekst na żądanie, Module Registry wskazuje właściwy wykonawca, a przycisk „Następny krok” wykonuje tylko akcję zatwierdzoną przez backend. To zapewnia zgodną kolejność działania bez „pamięci” AI o całym repozytorium.
