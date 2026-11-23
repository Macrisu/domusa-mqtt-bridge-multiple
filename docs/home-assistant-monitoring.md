# Home Assistant monitoring for Dual Clima HT PRO — notes and lessons learned

These notes come from running this add-on on a Dual Clima 16HTT PRO EC with a Shelly energy meter on the heat pump supply. See also the [16HTT PRO guide](16HTT-PRO-guide.md) and the [OTC heating curves](OTC-heating-curves.md).

Replace `xxxxxx` with your installation ID (iConnect app or LCD → Working status).

## 1. Data sources

### The add-on (this repository)
- **Cloud, not local.** It polls the Domusa iConnect cloud (`/v2/calderas/{id}/estado` and `/configuracion`) every `poll_interval` seconds (default 60). It publishes the **whole raw JSON** to `domusa/<id>/status`, so any key can be turned into a sensor with a `value_template`. MQTT Explorer shows them all.
- **Writes:** only the DHW setpoint (`domusa/<id>/set/setACS`). P-parameters can only be changed on the control panel.
- **Field meanings checked against the service manual:**

| Entity (name since v1.2.4) | Raw key | Meaning |
|---|---|---|
| Flow / Return temperature | `s_ida_hp_c08` / `s_ret_hp_c07` | C08 / C07 |
| Suction Superheat (C11) | `dt_hp_c11` | Suction temperature − evaporation temperature. **Not** the water ΔT; use a flow − return template for that. |
| C1 Pump Speed (C51) | `pwm_c1_c51` | Circulation pump speed. **Not** compressor demand (entity ID still `..._compressor_demand`). |
| Compressor Auto Mode (P40) | `m_comp_p40` | Auto/manual mode flag. **Not** "compressor running"; use `freq_c15 > 0`. |
| High / Low refrigerant pressure | `s_pralta_c13` / `s_prbaja_c14` | Reported in MPa; converted to bar since v1.2.4. |
| Water flow | `s_q_c10` | C10, l/min. The E15 trip is P61 (18 l/min default on 16HTT). |
| Buffer temperature | `s_buffer_c57` | C57, in steps of about 0.7 °C. |
| Grid frequency | `e_freq` | Reads about 30 Hz, so **not** the mains frequency. Meaning unknown. |
| "Defrost" / "DHW preparation" (`configuration.yaml` examples) | `func_hp_4_c33` / `func_hp_2` | ⚠ Bit meanings guessed. Both switched on during a compressor *start* while the unit was in heating-only mode, so don't rely on them. For the real mode use **`estado_func_c52`** (C52: 0 standby, 1 DHW, 2 heating, 3 cooling). |
| OTC max temperature | `max_otc_p08` | P08 (listed as "reserved" in the service manual) appears to be the OTC ceiling. |

### Shelly meter on the heat pump supply
It updates every few seconds, much faster than the 60 s cloud poll. Use it for compressor on/off, start counting and electrical energy.

## 2. Package: starts, run length (`ha_heatpump_monitoring.yaml`)

Put [ha_heatpump_monitoring.yaml](ha_heatpump_monitoring.yaml) in `/config/packages/`. That's the folder next to `configuration.yaml`, **not** `/config/config/packages/`. Then add:

```yaml
homeassistant:
  packages: !include_dir_named packages
```

and do a full restart (a YAML reload isn't enough for new `history_stats`).

It provides:
- `binary_sensor.hp_compressor_running`: Shelly power > 400 W with 30 s debounce. Tune the threshold between pump-only power and the power at 35 Hz.
- Starts today / 7 days, run hours today, average run length, starts per hour.
- A ready-to-paste dashboard card (in the file's comments).

## 3. COP calculation tips

- Thermal power (W) = flow (l/min) × ΔT (°C) × 69.77. Count it only while C15 > 0, ΔT > 0 and not in defrost.
- Subtract a ΔT sensor offset measured with the compressor off and the pump running (typically 0.2–0.4 °C). With a small design ΔT (P58 = 3), a 0.3 °C error is about 10 % of COP.
- **10-minute averages:** the `statistics` platform keeps only `sampling_size` samples (default **20**). With a fast Shelly that's well under 10 minutes. Use `state_characteristic: average_step` and `sampling_size: 2000`.
- **Energy integration:** the sources change in steps (60 s polls, drops to 0 at mode changes). `method: left` is more accurate than `trapezoidal`.
- Instantaneous COP spikes at starts and stops, because the cloud data lags the Shelly by up to about 60 s. Judge by the 10-min and daily values.

## 4. Pitfalls found

- **Duplicate unique_id.** Before v1.2.4 the `configuration.yaml` example "Compressor Enabled" used the same unique_id as the auto-discovered P40 entity. Home Assistant silently keeps only one of them. Use a distinct ID, e.g. `domusa_xxxxxx_compressor_running_c15`.
- **State class on an alarm code.** Giving the alarm code `state_class: measurement` creates meaningless long-term statistics. Removing it later triggers a Repairs notice; just delete the old statistics.

## E15 insufficient flow at compressor start

Observed on a 16HTT PRO with underfloor heating and an 80 L buffer in series on the return:

- Between runs the C1 pump sits at its minimum (P59 = 8 → 80 %), giving only **19.6–19.8 l/min**, against an E15 trip at **18 l/min** (P61).
- At a compressor start the flow dipped by about 4 l/min (to 15.8) and tripped E15. Once it self-cleared. The second time it latched until a manual reset (about 4 h). With no circulation, the water in the outdoor unit cooled from 27 °C to 8 °C at +5 °C outdoor, a freeze risk in frost.
- Even at 99 % pump speed the circuit only reached about 25 l/min, against a nominal 46 l/min (2.75 m³/h). The hydraulic resistance is high.

**What helps:**
1. Clean the strainer.
2. Keep all underfloor loops open.
3. Bleed the air.
4. Check that the check valves and fittings aren't restrictive.
5. Aim for at least 22 l/min at minimum pump speed.

**Stop-gap used:** P61 = 15 (not lower). The main risk of a low P61 is the plate heat exchanger freezing during defrost at low flow. Restore 18 when the flow allows it.

**Suggested alerts:** `water_flow` < 19.5 l/min while heating, and `alarm_code` ≠ 0.
