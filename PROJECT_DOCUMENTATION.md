# STRIX Project Documentation

## 1. Project overview

STRIX is a real-time webcam surveillance pipeline that:

1. Captures frames from a camera.
2. Detects people and possible weapons with YOLO.
3. Associates each weapon with the nearest person.
4. Computes a local threat score from confidence, proximity, overlap, and tracking consistency.
5. Confirms a threat over multiple frames.
6. Sends a confirmed frame to a vision-language model for final visual verification.
7. Stores event information in SQLite.
8. Sends an email alert for an accepted `LOW`, `MEDIUM`, or `HIGH` result.
9. Writes an annotated live feed image for the frontend or other consumers.

The computer-vision pipeline is the primary detector. The external AI model is a final visual sanity check and should not be treated as the only source of detection.

---

## 2. Current architecture

```text
Webcam
  |
  v
main.py
  |
  v
LangGraph state machine
  |
  +--> detection_node
  |      |
  |      +--> YOLO person model
  |      +--> YOLO weapon model
  |      +--> SimpleTracker
  |
  +--> proximity_node
  |      |
  |      +--> nearest person/weapon pairing
  |      +--> distance and IoU
  |      +--> weighted threat score
  |
  +--> confirmation_node
  |      |
  |      +--> MultiFrameConfirmer
  |
  +--> confirmation_router
         |
         +--> mistral_verification_node
         |      |
         |      +--> Gemini vision request
         |      +--> strict response parsing
         |      +--> snapshot/detection persistence
         |
         +--> alert_node
                |
                +--> Gmail SMTP email

SQLite database <---- event_manager.py / database.py
Snapshot files <----- app/data/snapshots/
Live feed image <---- app/data/snapshots/live_feed.jpg
```

The class is still named `MistralVerifier`, but the current provider implementation uses `ChatGoogleGenerativeAI` and `GOOGLE_API_KEY`.

---

## 3. Repository structure

Important application files:

| File | Responsibility |
|---|---|
| `app/main.py` | Camera loop, graph invocation, live-feed output, OpenCV display |
| `app/graph.py` | LangGraph workflow and orchestration |
| `app/detection.py` | YOLO model loading, detection parsing, annotation drawing |
| `app/proximity.py` | Person/weapon pairing and threat-score calculation |
| `app/tracker.py` | IoU tracker and multi-frame confirmation |
| `app/mistral_verification.py` | Gemini vision request, image encoding, response parsing |
| `app/event_manager.py` | Event lifecycle, verification gating, event cooldown state |
| `app/database.py` | SQLAlchemy models and SQLite persistence functions |
| `app/alert.py` | Email alert construction and SMTP delivery |
| `app/data/strix.db` | SQLite database created at runtime |
| `app/data/snapshots/` | Event snapshots and live-feed JPEG |
| `app/yolov8n.pt` | Default person detector path used by two-model mode |
| `models/gun_best.pt` | Trained weapon detector path used by two-model mode |
| `requirements.txt` | Python dependencies |

The repository also contains YOLO training datasets and training runs. Those are development assets; they are not executed by the live inference loop.

---

## 4. Detection subsystem

### 4.1 Model selection

`WeaponPersonDetector` supports two configurations:

#### Current two-model configuration

When `WEAPON_MODEL_PATH` exists:

- `PERSON_MODEL_PATH` loads the person detector.
- `WEAPON_MODEL_PATH` loads the trained weapon detector.
- person detections are filtered to class ID `0`.
- weapon detections accept all classes emitted by the weapon model.

Current paths in `app/detection.py`:

```text
Person model: app/yolov8n.pt
Weapon model: models/gun_best.pt
```

#### Optional combined-model configuration

If the weapon model path does not exist, the detector loads:

```text
app/models/person_gun_best.pt
```

In that mode:

- class ID `0` is treated as person.
- class ID `1` is treated as weapon.

### 4.2 Detection output

Each detection is normalized into a dictionary containing:

```text
box: (x1, y1, x2, y2)
confidence: float
class_id: int
center: (x, y)
```

Detection thresholds currently default to `0.3` for both person and weapon detections.

### 4.3 Development simulation switch

`SIMULATE_SECOND_PERSON_AS_WEAPON` can simulate a second person as a weapon-like detection for development. It is currently disabled and should remain disabled for real operation.

---

## 5. Tracking

`SimpleTracker` is an IoU-based tracker:

- Existing detections are matched greedily by highest IoU.
- A detection is matched when IoU is at least `0.3`.
- Unmatched detections receive a new track ID.
- Tracks expire after more than `5` missed frames.
- Each detection receives `tracking_consistency`.

The consistency value is approximately:

```text
hits / age
```

It is capped to the range `[0.0, 1.0]`.

This tracker is intentionally lightweight. It is not a full multi-object tracking system such as ByteTrack, BoT-SORT, or DeepSORT.

---

## 6. Proximity and threat score

`find_person_weapon_pairs()` finds the nearest person for each weapon. It then calculates:

- Euclidean center-to-center distance.
- Bounding-box IoU between the person and weapon.
- Tracking consistency.
- A weighted threat score.

### 6.1 Threat-score formula

The current score is:

```text
proximity_score = max(0, 1 - distance / 350)
holding_score   = min(1, IoU * 2.5)

threat_score =
    0.35 * weapon_confidence
  + 0.30 * proximity_score
  + 0.20 * holding_score
  + 0.15 * tracking_consistency
```

The result is capped to `[0.0, 1.0]` and rounded to three decimal places.

### 6.2 Meaning of the weights

| Signal | Weight | Meaning |
|---|---:|---|
| Weapon confidence | 0.35 | How confidently the weapon model detects the object |
| Proximity | 0.30 | How close the weapon is to the nearest person |
| IoU/holding score | 0.20 | How much the weapon overlaps the person box |
| Tracking consistency | 0.15 | Whether the weapon persists across frames |

The maximum pairing distance is `400` pixels. The score's proximity normalization uses `350` pixels.

The score is a local CV score. The Gemini result is not included in this numeric formula.

---

## 7. Multi-frame confirmation

`MultiFrameConfirmer` prevents a single noisy detection from immediately causing verification.

Current configuration in `app/graph.py`:

```text
window_size = 6
confirm_threshold = 0.46
min_hits = 3
min_avg_score = 0.40
instant_confirm_threshold = 0.80
```

### 7.1 Normal confirmation

The confirmer:

1. Appends the current threat score to a six-score rolling window.
2. Counts scores at or above `0.46`.
3. Calculates the rolling average.
4. Confirms when at least three scores meet the threshold and the average is at least `0.40`.

### 7.2 Strong-score confirmation

If the current score is at least `0.80` and the average is at least `0.40`, verification can be triggered immediately without waiting for three stable high-scoring frames.

This was added because requiring a target to remain still caused moving targets to miss verification. Motion itself does not reduce the score; only the detection geometry and tracking values affect it.

---

## 8. LangGraph workflow

The graph in `app/graph.py` contains these nodes:

### `detect`

- Runs the YOLO detector.
- Updates the weapon tracker.
- Returns `persons` and `weapons`.

### `proximity`

- Builds person/weapon pairs.
- Chooses the highest-scoring pair.
- Returns `pairs` and `current_score`.

### `confirm`

- Updates the rolling confirmation window.
- Returns `confirmed`, `avg_score`, and a display status.

### Confirmation router

Routing is:

```text
confirmed and verification allowed -> mistral
confirmed but verification already processed/cooling down -> END
not confirmed -> END
```

### `mistral`

Despite the node name, this currently calls Gemini through `MistralVerifier`.

- Selects the highest-scoring pair.
- Sends the current frame and CV metrics to Gemini.
- Parses the response.
- Saves a snapshot only for `HIGH`, `MEDIUM`, or `LOW`.
- Creates a detection audit row for accepted threat levels.
- Stores the AI decision and reasoning.

### `alert`

- Checks whether an email should be sent.
- Sends an SMTP email with the current frame attached.
- Stores the email result.

---

## 9. External AI verification

### 9.1 Provider

The current implementation uses:

```text
langchain_google_genai.ChatGoogleGenerativeAI
```

The API key is loaded from:

```text
GOOGLE_API_KEY
```

The configured model is currently:

```text
gemini-3.6-flash
```

The verifier is multimodal: it sends text plus a JPEG data URL.

### 9.2 Image preparation

Before sending:

- the frame is resized so its largest dimension is at most `640` pixels.
- JPEG quality is set to `40`.
- the JPEG is base64 encoded.
- the result is sent as a `data:image/jpeg;base64,...` URL.

### 9.3 Prompt evidence

The prompt includes:

- weapon confidence
- person/weapon distance
- IoU
- threat score
- tracking consistency
- average confirmation score

The model is instructed to return exactly:

```text
LEVEL: <HIGH | MEDIUM | LOW | FALSE ALARM>
REASONING: <short explanation>
```

### 9.4 Response handling

The parser:

- extracts `LEVEL:`.
- extracts `REASONING:`.
- accepts only `HIGH`, `MEDIUM`, `LOW`, and `FALSE ALARM`.
- defaults invalid or malformed output to `FALSE ALARM`.

Provider exceptions are logged and converted to:

```text
level: FALSE ALARM
```

This prevents a remote timeout from terminating the camera process.

### 9.5 Timeout and retry configuration

The current checked-in configuration is:

```text
request_timeout = 2000
max_retries = 0
```

The timeout value is passed to the Google LangChain client. If this is changed, verify the installed library's expected unit and behavior. A provider can still return a server-side `504 DEADLINE_EXCEEDED` before the client timeout is reached.

---

## 10. Event lifecycle

`ThreatEventManager` manages one global active event.

### Event start

When a frame is confirmed:

1. `should_verify()` calls `update(confirmed)`.
2. If no event is active, `new_event()` creates an event ID.
3. The event is inserted into SQLite with status `ACTIVE`.

Event IDs use this format:

```text
STRIX-YYYYMMDD-HHMMSS-XXXX
```

### Verification gating

Verification is skipped when:

- the current frame is not confirmed.
- the event already has a completed verification.
- the previous verification time is still within the configured `60` second cooldown.

### Event end

When confirmation becomes false and remains false for at least `5` seconds:

1. The event is ended in SQLite.
2. Its duration is calculated.
3. The manager resets its in-memory state.

### Important current limitation

The manager uses shared global state (`current_event_id`, `mistral_processed`, and `alert_sent`). The current graph is synchronous, so this is consistent as long as only one graph invocation is active at a time. A correct asynchronous implementation would require event-specific job IDs and protection against stale verification results.

---

## 11. Snapshot rules

Current behavior is intentionally strict:

| Result | Event DB row | Snapshot file | Detection audit row | Email |
|---|---|---|---|---|
| `HIGH` | Yes | Yes | Yes | Attempted |
| `MEDIUM` | Yes | Yes | Yes | Attempted |
| `LOW` | Yes | Yes | Yes | Attempted |
| `FALSE ALARM` | Yes | No | No | No |
| Provider timeout/error | Yes | No | No | No |

The snapshot condition is explicitly:

```python
if level in {"HIGH", "MEDIUM", "LOW"}:
```

This avoids saving a false-alarm image or treating an unavailable provider as a confirmed threat.

---

## 12. Database design

The database is SQLite:

```text
app/data/strix.db
```

It is initialized by `init_database()`.

### 12.1 `threat_events`

| Column | Purpose |
|---|---|
| `id` | Internal integer primary key |
| `event_id` | Public STRIX event identifier |
| `started_at` | Event start time |
| `ended_at` | Event end time |
| `duration_seconds` | Duration calculated when event ends |
| `snapshot_path` | Path to accepted-threat snapshot |
| `mistral_level` | Current external-AI classification |
| `mistral_reasoning` | External-AI explanation |
| `email_sent` | Whether email delivery succeeded |
| `status` | `ACTIVE` or `ENDED` |
| `created_at` | Row creation time |

False alarms are still recorded as event rows so the system has an audit trail. They normally have no snapshot path and no email.

### 12.2 `detection_records`

This optional audit table stores accepted threat detections:

| Column | Purpose |
|---|---|
| `id` | Record ID |
| `event_id` | Associated event |
| `track_id` | Tracker ID |
| `bbox` | Serialized bounding box |
| `confidence` | Weapon confidence |
| `tracking_consistency` | Tracker consistency |
| `frame_index` | Optional frame number |
| `created_at` | Record creation time |

Currently `frame_index` is passed as `None`.

---

## 13. Email alerting

`EmailAlerter` uses Gmail SMTP over SSL:

```text
smtp.gmail.com:465
```

Required environment variables:

```text
EMAIL_SENDER
EMAIL_PASSWORD
EMAIL_RECEIVER
```

The email includes:

- alert level
- timestamp
- AI reasoning
- the current frame as a JPEG attachment

There is an email cooldown of `45` seconds. Missing credentials, failed encoding, SMTP errors, and cooldown all result in a failed/skipped alert rather than a process crash.

---

## 14. Live feed and runtime behavior

`app/main.py`:

1. Initializes the database.
2. Builds the graph.
3. Opens webcam `0`.
4. Reads frames continuously.
5. Invokes the graph synchronously.
6. Draws detections, scores, and status.
7. Atomically writes `live_feed.jpg`.
8. Displays the OpenCV window.
9. Exits when `q` is pressed.

The live-feed writer first writes `live_feed_tmp.jpg` and then replaces `live_feed.jpg`. This avoids readers seeing a partially written JPEG.

The current LLM call is synchronous. Therefore, while the external provider request is running, the camera loop waits. This was intentionally restored because the synchronous flow produced correct event state and output. Moving it to a background thread without redesigning event ownership previously caused duplicate triggers, stale results, and event-reset races.

---

## 15. Environment setup

Create and activate the project virtual environment, then install:

```powershell
pip install -r requirements.txt
```

Create a `.env` file in the project root with values similar to:

```text
GOOGLE_API_KEY=your_google_key
EMAIL_SENDER=sender@example.com
EMAIL_PASSWORD=app_password
EMAIL_RECEIVER=receiver@example.com
```

Do not commit `.env`, API keys, email passwords, or generated databases.

Before running, verify:

- the camera is available.
- `app/yolov8n.pt` exists.
- `models/gun_best.pt` exists.
- the selected Gemini model is available to the API account.
- the Google API key has quota.
- Gmail credentials use an app password where required.

Run:

```powershell
python app/main.py
```

Expected startup output:

```text
[DATABASE] SQLite database ready: ...
STRIX LangGraph running...
Live feed: ...
Press 'q' to quit.
```

---

## 16. Common runtime errors

### `KeyboardInterrupt` inside PyTorch

This normally means the process was interrupted manually with Ctrl+C while YOLO was performing inference. It is not automatically a model failure.

### `429` or rate-limit errors

The provider rejected the request because of quota or rate limits. This is external to YOLO and the local threat score.

### `403 tier_not_allowed`

The selected provider model is not available to the API account or subscription tier.

### `504 DEADLINE_EXCEEDED`

The provider did not complete the request before its server-side deadline. The verifier catches this and returns a safe `FALSE ALARM` result, so the camera process should continue.

### Camera loop appears frozen during verification

This is expected with the current synchronous architecture: the loop waits for the external vision response. It is a known trade-off for preserving simple, correct event state.

### No LLM request is sent

Check the confirmation stage first. The request is sent only after the local threat score passes the rolling confirmation or instant-confirm path.

---

## 17. Work completed

The project currently includes:

- person and weapon detection.
- support for combined-model and two-model detection.
- trained weapon-model integration.
- nearest-person/weapon association.
- distance and IoU calculations.
- weighted threat scoring.
- IoU-based tracking.
- tracking consistency scoring.
- multi-frame threat confirmation.
- strong-score confirmation for moving targets.
- LangGraph orchestration.
- Gemini multimodal verification.
- strict AI response parsing.
- safe handling for provider timeouts and malformed responses.
- SQLite event persistence.
- detection audit records.
- event timeout and verification cooldown.
- false-alarm snapshot prevention.
- SMTP email alerting.
- atomic live-feed image output.
- OpenCV live display.

---

## 18. Current limitations and recommended next work

### Highest-priority improvements

1. **Make the provider configurable**
   - Rename `MistralVerifier` to a provider-neutral name.
   - Move model name, timeout, and retry count into environment variables.
   - Validate the configured model at startup.

2. **Separate event identity from verification jobs**
   - Required before returning to asynchronous verification.
   - Every request should carry an immutable event ID and frame copy.
   - A stale response must never update a newer event.

3. **Avoid swallowing broad exceptions**
   - Some existing graph paths intentionally continue after errors.
   - Replace broad catches with explicit logging and targeted exception handling.

4. **Improve tracking**
   - Consider ByteTrack or BoT-SORT if fast movement causes ID switches.
   - Tune detector image size and inference device for the target hardware.

5. **Improve persistence semantics**
   - Add explicit fields such as `verification_status`, `is_false_alarm`, and `provider_error`.
   - Store provider failures separately from model-classified false alarms.

6. **Add tests**
   - Threat-score unit tests.
   - Multi-frame confirmation tests.
   - Response-parser tests.
   - Snapshot eligibility tests.
   - Event lifecycle tests.
   - Database persistence tests.

7. **Add operational controls**
   - Configurable camera index.
   - Configurable model paths.
   - Configurable confidence and score thresholds.
   - Health/status endpoint for the frontend.
   - Structured logging.

### Design recommendation

Keep the local CV pipeline authoritative for triggering and use the external model only for visual verification. For a production asynchronous design, use a queue with:

```text
event_id
frame copy or immutable snapshot path
CV metrics
request timestamp
job status
```

The worker should write its result to that specific event ID, and the main camera loop should never let a worker mutate the currently active event blindly.

---

## 19. Security and privacy notes

- API keys and email passwords must remain in environment variables.
- Camera frames and event snapshots contain sensitive visual data.
- Restrict access to `app/data/` and the frontend serving the live feed.
- Do not expose the SQLite database or snapshot directory publicly.
- Use a provider account with the minimum required permissions.
- Consider retention and deletion policies for snapshots and event records.

