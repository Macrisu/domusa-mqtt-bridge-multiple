# Domusa Dual Clima 16HTT PRO — key reference & oversizing (detuning) guide

Community notes for an **oversized Dual Clima 16HTT PRO (EC / Easy Connect)** heating a well-insulated house with underfloor heating. The notes are compiled from the Domusa Service Manual (rev. 2, Oct 2026), the Easy Connect installation/operating manual and real operating data logged in Home Assistant with this add-on. The manuals themselves aren't included; get them from Domusa or your installer.

Not affiliated with Domusa. Changing service parameters (passwords 99 / 8563) is at your own risk and can affect warranty. Several parameters below carry manufacturer warnings.

Labels used in this doc:
- **[Manual]** means the information is stated in the manuals.
- **[Estimate]** or **[Suggestion]** means it's my own reasoning. Check it against what the unit actually does.

---

## 0. Settings currently applied on this unit (example installation, Nov 2026)

Changes were made with password 8563.

| Param | Default | **Now** | Meaning |
|---|---|---|---|
| P06 | 5 | **6** | Heating/cooling hysteresis: restart at setpoint − 6 °C |
| P20 | 0 | 0 | C1 pump continuous |
| **P45** | 85 | **50** | Max compressor frequency (Hz). This is the main detune. |
| P46 | 35 | 35 | Min compressor frequency. User note: it's ignored if higher than P105. |
| P47 | 50 | 50 | Defrost frequency |
| **P58** | 5 | **3** | Flow–return ΔT target for C1 pump modulation (heating) |
| P59 | 8 | 8 | Min C1 pump speed (80 %) |
| **P61** | 18 | **15** | Min water flow (E15 trip), l/min. Set 24 Nov 2026 00:21 (briefly 10 before that) after two E15 trips at compressor start (flow dipped to about 15.8). Temporary: restore 18 once the flow is at least 22 l/min at 80 % pump speed (strainer, air, all loops open). Watch the flow during defrost. |
| **P66** | 0.5 | **2** | Starts modulating at setpoint − 2 °C |
| **P104** | 50 | **40** | Start-up ramp target, Hz |
| **P105** | 50 | **35** | Start-up frequency, Hz |
| **P106** | 60 | **280** | Time held at start-up frequency, s |
| **P114** | 2 | **15** | % frequency drop when the P66 point is reached |
| P121 | 0 | 0 | Buffer-sensor function off |

What the combination does **[Estimate / reasoning from manual logic]**:

- **Soft start.** Each start sits at 35 Hz for about 4 min 40 s (P105/P106), then ramps toward 40 Hz (P104). After that it can rise to at most 50 Hz (P45). Most short runs therefore never leave the 35–40 Hz band. That's gentler, but the unit is no less oversized at the bottom end, because the 35 Hz minimum is unchanged.
- **Capped output.** 50/85 Hz is about 59 % of the maximum. **[Estimate]** That's roughly 9–10 kW at A7/W35 and noticeably less at −10 to −15 °C. On the coldest days, check that the house still holds temperature. If it doesn't, the E2 backup (P22, default 0 °C, after the P36 15-min delay) or a higher P45 is the fallback.
- **Approach and stop.**
  - The modulation band now starts 2 °C below setpoint with a 15 % drop.
  - It slows at 4 Hz/min from setpoint − 0.5 °C.
  - It stops at setpoint + 0.5 °C and restarts at setpoint − 6 °C.
  - That gives a 6.5 °C flow-temperature swing per cycle, buffered by the 80 L tank and the slab.
- **Oil return** (P41 = 50 Hz) and **defrost** (P47 = 50 Hz) both still sit within the 50 Hz cap, so there's no conflict.
- **DHW** also runs at most 50 Hz, because P48 is a % of P45. That should help a 200 L coil cylinder avoid high-pressure limiting, at the cost of slower reheats.
- **P58 = 3 °C.** The pump aims for a small ΔT, so it'll tend to run fast. With P59 = 8 it only modulates between 80 and 100 % anyway. High flow suits underfloor heating and the series buffer. Watch that C07/C08 still show a sensible ΔT and that C10 stays ≥ 20 l/min.

**To check on the unit:**
1. Read C15/C20 during a run to confirm it never exceeds 50 Hz and that the start hold behaves as expected.
2. Count the starts per day (C50 against time).
3. Watch C13 during DHW.
4. Check comfort on the coldest day.

---

## 1. Unit data — 16HTT PRO (400 V 3N~) [Manual]

| Item | Value |
|---|---|
| Rated heating capacity (A7/W35) | 16.84 kW, input 3.62 kW, COP 4.65 |
| Rated cooling capacity (A35/W18) | 15.09 kW, EER 4.21 |
| Max input / max current | 6.21 kW / 9.4 A |
| Supply | 400 V 3N~ 50 Hz |
| Refrigerant | R290, 1.4 kg |
| Max water temp | 75 °C (P115 max flow 83 °C) |
| Nominal water flow | 2.75 m³/h (≈ 46 l/min) |
| **Minimum water flow** | **18 l/min** (P61 default for 16HTT = the E15 trip, service manual). The Easy Connect user manual's installation table lists 20 l/min. |
| **Minimum system water volume** | **60 L** (fit a buffer if the system has less) |
| Water circuit max pressure | 3 bar (fill to 1–1.5 bar) |
| Operating range | heating −25…45 °C outdoor, cooling 10…45 °C |
| Noise (1 m) | 47 dB(A) |
| Dimensions H/W/D, weight | 1115 / 415 / 1320 mm, 140 kg |
| Compressor frequency | **max 85 Hz (P45), min 35 Hz (P46)**, defrost 50 Hz (P47), oil return 50 Hz (P41) |
| Fan | max 800 rpm (P60 = 80), min 400 rpm |
| Current limits (P42/P43/P44) | 7 A hold / 9 A reduce / 10 A stop |
| IPM temp limits (16HTT) | 90 °C slow increase, 95 °C limit increase, 98 °C slow decrease, 102 °C fast decrease, 105 °C stop |

**[Estimate]** At the 35 Hz minimum, the compressor runs at about 41 % of its 85 Hz maximum. That suggests the smallest steady output is roughly **6–8 kW in mild weather**. Any heat load below that will make the unit cycle on/off. This is the core of the oversizing problem. Check it by watching C15 (Hz) and C21 (A) during a mild day.

---

## 2. How the controller cycles [Manual §8.2, §8.4]

**Start/stop:**
1. The C1 pump starts first. The fan and compressor follow 60 s later.
2. When the compressor stops, the fan runs on for another 30 s.
3. There is a **3-minute minimum** before the compressor can restart (defrost excepted).
4. C1 stops 60 s after demand ends, depending on P20.
5. During defrost the water pump keeps running.

**Start-up ramp:**
1. The compressor runs at P46 (35 Hz) for 1 minute.
2. It then ramps at 1.5 Hz/s, pausing 1 minute every 10 Hz, until it reaches its target.
3. Separately, P104/P105/P106 define a start-up step: 50 Hz for 60 s.

**Approach to setpoint (heating/cooling).** The compressor always aims for maximum frequency (C20) unless something forces it to modulate:
- When the flow temperature C08 reaches setpoint − **P66** (default 0.5 °C), frequency drops by **P114 %** (default 2 %).
- At setpoint − 0.5 °C, frequency falls by 4 Hz/min.
- At **setpoint + 0.5 °C the compressor switches off.**
- It restarts when the flow drops below setpoint − **P06** (heating/cooling hysteresis, default 5 °C, range 1–15).
- Other things that also force modulation:
  - high pressure (P51 30 bar reduce / P52 29 bar release / P53 32 bar stop with E13)
  - discharge temperature (95/97/100 °C stages, 105 °C stop with E17)
  - current
  - IPM temperature

**Oil return:** if the compressor spends a cumulative **120 min below 35 Hz**, it runs at P41 (50 Hz) for 3 min (C49 = 1). So long, low-frequency running triggers short bursts at 50 Hz.

**Compressor crankcase heater:** it pre-heats for 3–10 min before the first start below 10 °C outdoor. It also runs in 60-min cycles when the compressor has been off for more than 60 min or it's below 10 °C outdoor.

---

## 3. Parameters that matter for an oversized unit

Access: Settings → System Parameters, **password 99**. Refrigerant-circuit parameters need **password 8563**. The manual repeatedly warns that changing compressor or EEV parameters can cause malfunction or damage, and the user manual says only the installer-list parameters should be touched.

| Param | What it does | Range | Default | Relevance to oversizing |
|---|---|---|---|---|
| **P06** | Heating/cooling hysteresis (negative: restart at setpoint − P06) | 1–15 °C | 5 | Main lever for cycle length. A larger value means fewer, longer cycles but a bigger flow-temperature swing. With underfloor heating, a 5–8 °C swing is usually absorbed by the slab. **[Suggestion]** |
| **P66** | Starts modulating at setpoint − P66 | 0–5 °C | 0.5 | Raising it (e.g. 2–3 °C) makes the compressor slow down earlier. That gives a softer approach and less overshoot to the +0.5 °C cut-off. **[Suggestion]** |
| **P114** | % frequency drop when P66 point is reached | 0–60 % | 2 | A bigger drop brings the unit toward minimum Hz sooner. **[Suggestion]** Try 10–30 % with P66. |
| P45 | Max compressor frequency | 50–120 Hz | 85 | Capping it lowers peak output and noise. It **does not lower the minimum**, so it doesn't cure cycling in mild weather. Password 8563, manufacturer warning. |
| P46 | Min compressor frequency | 0–90 Hz | 35 | **Do not lower.** Oil return logic is built around 35 Hz. |
| **P48** | Max frequency in DHW mode, as % of P45 | 2–10 (20–100 %) | 10 | Use it when a DHW coil can't absorb 16 kW. That situation leads to high-pressure modulation or E13 and fast cycling. **[Suggestion]** Try 6–7 (≈ 51–60 Hz) with a 200 L coil cylinder. |
| P02 | Heating setpoint | 10/25–75 °C | 45 | Ignored while OTC is active. |
| P154 | OTC K curve, Zone 1 | Off, 0.2–6.0 | Off | Weather compensation. For underfloor heating, K ≤ 0.8 (see the curve table). |
| P153 | OTC outdoor sensor source | 0/1/4/5 | 0 | A separate sensor is recommended. |
| P20 | C1 pump mode | 0/1/2 | 0 | ⚠ The manuals contradict each other (see §6). |
| P58 | Flow–return ΔT target for C1 pump modulation (heating) | 3–8 °C | 5 | Pump speed follows this ΔT. |
| **P59** | Minimum C1 pump speed | 2–8 (20–80 %) | 8 (= 80–100 %) | Lowering it widens the pump's modulation range. Keep the flow ≥ 20 l/min (watch C10), or you'll get E15. |
| P61 | Minimum flow, E15 trip | 3–80 l/min | 18 | Don't lower it to hide a flow problem. |
| P102 | Max flow–return ΔT (E22) | 8–20 °C | 15 | |
| P117 / P118 | Room-sensor hysteresis, heat/cool | 0.2–5 °C | 0.5 | With a room sensor, a larger value means longer off-periods. |
| P150 | Zone 1 room device (4 = sensor, 5 = thermostat) | | 0 | |
| P121 / P122 / P123 | Buffer-tank control: enable / hysteresis (5–40 °C) / setpoint | | 0 / 5 / 45 | EC version only. Needs a buffer sensor on T6 (15–16) and normally C4 downstream. See §5. |
| P15 / P16 / P17 | Night mode start / end / enable | | 22 / 6 / 0 | Night mode lowers the heating setpoint by 2 °C, raises the DHW setpoint by 3 °C, and cuts starts and noise. |
| P35 | Max DHW temperature with compressor | 0–70 °C | 70 | E1 finishes the job above this. |
| P36 | Delay before E1/E2 backup can engage | 0–999 min | 15 | |
| P22 / P23 / P24 | Outdoor temp for E2 / E1 backup; backup hysteresis | | 0 / 0 / 5 | |
| P81 / P82 | Backup mode (0 backup, 1 auxiliary, 2/3 combined); auxiliary-mode outdoor temp | | 0 / −15 | |
| P07 | DHW hysteresis | 1–15 °C | 5 | |
| P10–P14 | Anti-legionella: interval, hour, minutes, setpoint, mode (0 auto / 1 once / 2 off) | | 7 d / 23 h / 10 min / 70 °C / off | |
| P201–P208 | SG Ready | | off | Needs both a DHW tank and a buffer to store energy. |
| P27 / P29 / P30 / P31 / P85 / P86 / P91 | Defrost: min interval, start evaporator temp, end temp, max time, ambient limit, ΔT ≥ −7, ΔT ≤ −7 | | 50 min / 0 / 20 / 12 min / 8 / 8 / 8 | Leave at defaults unless you see defrost problems (§8.9.3 gives the allowed adjustments). |

---

## 4. Live values to watch (Working Status → C parameters) [Manual]

| Code | Meaning |
|---|---|
| C02 | Outdoor temperature |
| C07 / C08 | Return / flow temperature |
| C09 | DHW temperature |
| **C10** | Water flow, l/min |
| C13 / C14 | High / low pressure |
| **C15 / C20** | Actual / target compressor Hz |
| **C21** | Compressor current |
| C22 | IPM temperature |
| C33 | Defrost active |
| C49 | Oil return active |
| **C50** | Compressor run hours |
| C51 | C1 pump speed % |
| C52 / C54 | Actual / selected mode |
| C57 | Buffer tank temperature |
| C58 / C75 | OTC outdoor sensor |
| C72 | Zone 1 room temperature |

**[Suggestion]** To measure cycling, note C50 and count the starts over a day. Watching C15 tells you whether the unit spends its runs pinned at 35 Hz (oversized for the load) or ramping high (load or flow-temperature limited).

---

## 5. Example installation and its hydraulics

Layout:
- Heat pump → circulation pump → **motorized 3-way diverter valve**.
- **DHW port** → coil of a **200 L DHW cylinder**. The coil return goes straight back to the heat pump return.
- **Heating port** → underfloor heating/cooling circuit → **check valve on the underfloor return** → **80 L buffer tank in series on the return** → heat pump.
- The DHW side has a cold feed with an expansion vessel and safety valve.

What this means **[Suggestion / reasoning]**:
- **Volume.** The 80 L series buffer plus the underfloor loops exceed the 60 L minimum. Series volume only helps during space heating; DHW runs see the coil volume only.
- **Buffer sensor present (confirmed 24 Nov 2026).** A buffer temperature sensor is fitted and reads in HA as C57 (`sensor.<id>_buffer_temperature`, in steps of about 0.7 °C). P121 = 0, so it's **monitoring only**.
  - In 24 h of history it tracks the return temperature within about ±1 °C while water circulates.
  - It stayed at 26–27 °C during the E15 lockout of 23 Nov (17:26–21:15 local) while the HP's own flow/return sensors fell to 13/8 °C. So it really sits in the buffer.
  - `t6_temperature` (C25) is flat at 24.7 °C, so it's probably not this sensor.
- **Series buffer, not a separator.** There's no separate C4 secondary pump and no buffer sensor on the drawing, so the Easy Connect buffer function (P121/P122, sensor on T6) doesn't really fit this layout, even though a buffer sensor is fitted. See the P121 assessment below. The unit controls on its own flow sensor (C08) with P06 hysteresis. Enabling P121 would need a buffer sensor and normally a hydraulically separated buffer with a C4 pump.
- **P121 (buffer control) assessment [reasoning, not tested]:**
  - With P121 = 1 the unit switches on/off on the buffer temperature (setpoint P123/OTC, hysteresis P122 of at least 5 °C) instead of on flow with P06.
  - In this series layout, the buffer ≈ return temperature, so the setpoint would need to be about ΔT (4–5 °C) lower than today's flow target.
  - **Main risk:** the buffer mode is designed for a parallel buffer with its own C4/Z1 pump. Here C1 is the only pump. If C1 stops when the buffer is satisfied (depending on P20, which the two manuals describe differently), nothing flows through the floor or the buffer. The buffer temperature then wouldn't fall, so the unit might not restart while the floor cools.
  - Only worth trying with P20 = 0 (continuous) confirmed, watching C42/C51 and the buffer temperature closely.
  - Expected benefit over the current P06 = 6 flow control is modest.
- **Flow.** All heating flow passes through the underfloor loops. If loop actuators or zone valves can close, a bypass or an always-open loop is needed to keep flow ≥ 20 l/min (manual §6.5: multi-zone systems must keep minimum flow). Low flow means E15 and higher ΔT and short runs.
- **Check valve.** It stops reverse or thermosiphon flow through the underfloor circuit during DHW runs, so hot water doesn't get pulled through the floor.
- **⚠ E15 at compressor start (23 Nov 2026):** flow between runs is only 19.6–19.8 l/min (pump at its 80 % minimum), against an 18 l/min trip. A dip of about 4 l/min at a start trips E15. Max flow is only about 25 l/min against 46 nominal, so the circuit resistance is high. See [home-assistant-monitoring.md](home-assistant-monitoring.md#e15-insufficient-flow-at-compressor-start). (This replaces an earlier wrong 'DHW branch fault' note: the unit was in heating mode the whole time.)
- **DHW coil sizing.** A 200 L cylinder's coil is usually rated well below 16 kW. Expect fast head-pressure rise, frequency limiting or E13, and short DHW cycles. P48 (DHW max frequency %) is the manufacturer's provided tool for "accumulators with low exchange capacity".
- **Valve wiring.** For the 3-way valve G1, DHW = energised (C38 on = DHW). P98 inverts the control signal if the valve is wired NO/NC the other way.

---

## 6. Contradictions between the two manuals ⚠

| Item | Service manual | Easy Connect user manual |
|---|---|---|
| P20 = 1 | Pump stops when setpoint reached | Pump stops without demand and runs 1 min every 15 min |
| P20 = 2 | Runs 1 min every 15 min (for buffer with return probe in heat pump) | Runs while there is demand from any circuit |
| P25 default (anti-freeze) | 5 °C | 3 °C |
| Heating setpoint min | 10 °C | 25 °C |
| P123 / P124 defaults | 45 / 12 (columns shifted for 19/22 kW models, likely a table error) | Off / Off |

Check the actual P20 behaviour on the unit (watch C42) before relying on either description.

---

## 7. Error codes (index) [Manual §12]

Full diagnostic procedures are in the service manual text.

| Code | Meaning |
|---|---|
| E11 / E12 | High / low pressure sensor fault |
| E13 | High-pressure protection |
| E14 | Low-pressure protection |
| **E15** | Insufficient water flow |
| E16 | Communication error |
| E17 | Discharge temperature too high |
| E18 | Wrong configuration |
| E20-x | IPM/compressor faults (1 overcurrent, 4/5 compressor, 16/32 low/high voltage, 257 IPM comms, 260 AC current, 261 supply, 264 AC voltage, 288 IPM overtemperature, 320 compressor overcurrent, 384 PFC) |
| E21 | Voltage |
| **E22** | Flow–return ΔT too large |
| E23 / E24 | DHW / heating anti-freeze repeated |
| E27 | Ambient above limit |
| E28 | High return in cooling |
| E32 | High flow temperature |
| E36 / E44 | Fan comms / fan motor |
| E40 | Low flow temperature in cooling |
| E50 | Outdoor exchanger too hot |
| E56 | Current protection |
| E58 | Ambient below limit |
| E59 | Flow/return sensors swapped or 4-way valve fault |
| E65 / E66 | Energy meter / indoor–outdoor comms (EC) |
| E68 | Cascade setup |
| E75 / E83 / E83A / E85 | AIR hydraulic kit |
| E82 | iConnect |
| E86–E89 | Wireless devices / batteries |

---

## 8. Starting-point detuning plan [Suggestion — verify on the unit, one change at a time]

Already done (see §0): P06 = 6, P66 = 2, P114 = 15, P45 = 50, soft start (P104/P105/P106), P58 = 3. Still open: OTC (P153/P154), P48 (not really needed now that P45 = 50), night mode, measuring the starts per day, and confirming P20 behaviour.

1. **Baseline first.** Log C50 run hours, the number of starts per day, and typical C15/C08/C07/C10 for 2–3 days with outdoor temperatures noted.
2. **Lower the flow temperature with OTC.** Fit or select the OTC sensor (P153). Set P154 to about 0.4–0.6 for underfloor heating, then fine-tune by 0.1 steps until rooms hold temperature at the coldest expected outdoor temperature.
3. **Lengthen cycles.**
   - Raise P06 from 5 toward 7–8 °C.
   - Set P66 to about 2 °C and P114 to about 10–20 % so the unit glides down to 35 Hz before reaching the +0.5 °C cut-off.
4. **Pump.**
   - Keep C10 ≥ 20 l/min.
   - Set P20 so the pump keeps circulating through the slab and buffer between compressor runs (that's what lets the stored volume work). Confirm which P20 value does this (§6).
   - P59 can be lowered if the pump is noisy, but flow must stay above the minimum.
5. **DHW.** Set P48 to about 6–7. Watch C13 stay below 29–30 bar and the reheat time stay acceptable. Use night mode or a timed DHW window so DHW and heating don't interleave constantly.
6. **Room control.** If a room sensor is used, a P117 of 0.5–1.0 °C gives long off-periods. Alternatively, run on OTC alone with all underfloor loops open.
7. **Leave alone:** P46 (min Hz), EEV, fan, defrost and pressure or current limits, unless a Domusa technician advises otherwise.
