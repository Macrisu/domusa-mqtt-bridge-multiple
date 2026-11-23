import json


class Discovery:
    """Publish Home Assistant MQTT Discovery entities with friendly names."""

    def __init__(self, mqtt, device, lang="en"):
        self.mqtt = mqtt
        self.device = device
        self.lang = lang

    async def _publish(self, component, object_id, payload):
        topic = f"homeassistant/{component}/{object_id}/config"
        payload = {k: v for k, v in payload.items() if v is not None}
        await self.mqtt.client.publish(topic, json.dumps(payload), retain=True)

    @staticmethod
    def _value_template(key, invalid_values=None, scale=None):
        # scale: optional multiplier, e.g. 10 to convert MPa (as reported by the unit) to bar
        out = "v" if scale is None else f"(v | float * {scale}) | round(2)"
        if invalid_values:
            values = ", ".join(str(v) for v in invalid_values)
            return (
                f"{{% set v = value_json.{key} %}}"
                f"{{% if v not in [{values}] %}}{{{{ {out} }}}}{{% endif %}}"
            )
        if scale is None:
            return f"{{{{ value_json.{key} }}}}"
        return f"{{% set v = value_json.{key} %}}{{{{ {out} }}}}"

    async def publish(self):
        cid = self.device["id"]
        name = self.device.get("name") or f"Domusa {cid}"
        status_topic = f"domusa/{cid}/status"

        dev_info = {
            "identifiers": [f"domusa_htec_{cid}"],
            "name": name,
            "manufacturer": "Domusa",
            "model": "Dual Clima HT / HTEC Pro",
        }

        # Friendly, useful operating sensors. Raw Domusa field names stay hidden.
        sensors = [
            # Water circuit
            ("flow_temperature", "Flow Temperature", "s_ida_hp_c08", "°C", "temperature", "mdi:thermometer-chevron-up", "measurement", None),
            ("return_temperature", "Return Temperature", "s_ret_hp_c07", "°C", "temperature", "mdi:thermometer-chevron-down", "measurement", None),
            # C11 = suction temperature - evaporation temperature (superheat), NOT flow/return water delta.
            # unique_id kept as "delta_t" so existing installs keep their entity and history.
            ("delta_t", "Suction Superheat (C11)", "dt_hp_c11", "°C", "temperature", "mdi:delta", "measurement", None),
            ("active_heating_setpoint", "Active Heating Setpoint", "st_activa_c_f", "°C", "temperature", "mdi:radiator", "measurement", None),
            ("otc_requested_temperature", "OTC Requested Temperature", "st_activa_c_f", "°C", "temperature", "mdi:chart-bell-curve", "measurement", None),
            ("heating_setpoint", "Heating Setpoint", "st_c_p02", "°C", "temperature", "mdi:radiator", "measurement", None),
            ("cooling_setpoint", "Cooling Setpoint", "st_f_p03", "°C", "temperature", "mdi:snowflake", "measurement", None),

            # Buffer / DHW
            ("buffer_temperature", "Buffer Temperature", "s_buffer_c57", "°C", "temperature", "mdi:thermometer-water", "measurement", [-255, -3276.8]),
            ("dhw_temperature", "DHW Temperature", "s_acs_c09", "°C", "temperature", "mdi:water-thermometer", "measurement", [-255, -3276.8]),
            ("dhw_setpoint", "DHW Setpoint", "st_activa_acs", "°C", "temperature", "mdi:water-boiler", "measurement", None),

            # Outdoor / refrigeration circuit
            ("outdoor_temperature", "Outdoor Temperature", "s_ext_c02", "°C", "temperature", "mdi:thermometer", "measurement", [-255, -3276.8]),
            ("evaporator_temperature", "Evaporator Temperature", "s_evap_c00", "°C", "temperature", "mdi:thermometer-low", "measurement", [-255, -3276.8]),
            ("evaporating_temperature", "Calculated Evaporating Temperature", "s_evap_calc_c27", "°C", "temperature", "mdi:thermometer-low", "measurement", [-255, -3276.8]),
            ("suction_temperature", "Suction Temperature", "s_suction_c03", "°C", "temperature", "mdi:thermometer", "measurement", [-255, -3276.8]),
            ("discharge_temperature", "Discharge Temperature", "s_discharge_c01", "°C", "temperature", "mdi:thermometer-high", "measurement", [-255, -3276.8]),
            ("condenser_temperature", "Condenser Temperature", "s_condens_c06", "°C", "temperature", "mdi:thermometer-high", "measurement", [-255, -3276.8]),
            ("condensing_temperature", "Calculated Condensing Temperature", "s_cond_calc_c28", "°C", "temperature", "mdi:thermometer-high", "measurement", [-255, -3276.8]),
            ("ipm_temperature", "IPM Temperature", "s_ipm_c22", "°C", "temperature", "mdi:thermometer", "measurement", [-255, -3276.8]),
            ("t6_temperature", "T6 Temperature", "s_t6_c25", "°C", "temperature", "mdi:thermometer", "measurement", [-255, -3276.8]),

            # Compressor / fans
            ("compressor_frequency", "Compressor Frequency", "freq_c15", "Hz", "frequency", "mdi:sine-wave", "measurement", None),
            ("compressor_frequency_setpoint", "Compressor Frequency Setpoint", "st_freq_c20", "Hz", "frequency", "mdi:sine-wave", "measurement", None),
            ("compressor_current", "Compressor Current", "curr_comp_c21", "A", "current", "mdi:current-ac", "measurement", None),
            ("compressor_phase_current", "Compressor Phase Current", "curr_ph_comp", "A", "current", "mdi:current-ac", "measurement", None),
            ("fan_1_speed", "Fan 1 Speed", "rpm_vent1_c16", "rpm", None, "mdi:fan", "measurement", None),
            ("fan_2_speed", "Fan 2 Speed", "rpm_vent2_c17", "rpm", None, "mdi:fan", "measurement", None),
            ("eev_position", "Electronic Expansion Valve Position", "eev_c18", "steps", None, "mdi:valve", "measurement", None),

            # Electrical
            ("ac_voltage", "AC Voltage", "volt_ac_c23", "V", "voltage", "mdi:flash", "measurement", None),
            ("dc_bus_voltage", "DC Bus Voltage", "volt_dc_c24", "V", "voltage", "mdi:flash", "measurement", None),
            ("grid_frequency", "Grid Frequency", "e_freq", "Hz", "frequency", "mdi:sine-wave", "measurement", None),

            # Pressures
            # The unit reports C13/C14 in MPa; converted to bar (x10) so the "bar" unit is correct.
            ("high_pressure", "High Refrigerant Pressure", "s_pralta_c13", "bar", "pressure", "mdi:gauge-high", "measurement", None, 10),
            ("low_pressure", "Low Refrigerant Pressure", "s_prbaja_c14", "bar", "pressure", "mdi:gauge-low", "measurement", None, 10),

            # Other useful values
            ("water_flow", "Water Flow", "s_q_c10", "L/min", None, "mdi:water", "measurement", None),
            # C51 = speed of circulation pump C1, NOT compressor demand.
            # unique_id kept as "compressor_demand" so existing installs keep their entity and history.
            ("compressor_demand", "C1 Pump Speed (C51)", "pwm_c1_c51", "%", None, "mdi:pump", "measurement", None),
            ("p06_hysteresis", "P06 Heating/Cooling Hysteresis", "hyst_c_f_p06", "°C", "temperature", "mdi:delta", "measurement", None),
            ("otc_curve", "OTC Curve", "ck_zona1_p154", None, None, "mdi:chart-bell-curve", "measurement", None),
            ("operation_state", "Operation State", "estado_func_c52", None, None, "mdi:state-machine", None, None),
            ("heat_demand", "Heat Demand", "demanda_hp", None, None, "mdi:fire", None, None),
            ("hp_mode", "Heat Pump Mode", "m_hp_p01", None, None, "mdi:hvac", None, None),
            ("alarm_code", "Alarm Code", "alarma", None, None, "mdi:alert", None, None),
            ("sub_alarm_code", "Sub Alarm Code", "sub_alarma", None, None, "mdi:alert-outline", None, None),
        ]

        for entry in sensors:
            uid, friendly_name, key, unit, device_class, icon, state_class, invalid = entry[:8]
            scale = entry[8] if len(entry) > 8 else None
            payload = {
                "name": friendly_name,
                "object_id": f"domusa_{cid}_{uid}",
                "unique_id": f"domusa_{cid}_{uid}",
                "device": dev_info,
                "state_topic": status_topic,
                "value_template": self._value_template(key, invalid, scale),
                "unit_of_measurement": unit,
                "device_class": device_class,
                "state_class": state_class,
                "icon": icon,
            }
            await self._publish("sensor", f"domusa_{cid}_{uid}", payload)

        # Remove the previously published writable OTC Select entity from Home Assistant.
        # Empty retained discovery payload tells Home Assistant to delete that entity.
        otc_select_config_topic = (
            f"homeassistant/select/domusa_{cid}_otc_curve_control/config"
        )
        await self.mqtt.client.publish(otc_select_config_topic, "", retain=True)

        binary_sensors = [
            ("power", "Heat Pump Power", "on_off_p00", "mdi:power", None),
            ("otc_enabled", "OTC Enabled", "m_otc_p19", "mdi:chart-bell-curve", None),
            ("zone_1_demand", "Zone 1 Demand", "demanda_zona1", "mdi:home-thermometer", None),
            ("zone_2_demand", "Zone 2 Demand", "demanda_zona2", "mdi:home-thermometer", None),
            ("zone_3_demand", "Zone 3 Demand", "demanda_zona3", "mdi:home-thermometer", None),
            # P40 = compressor automatic/manual mode flag, NOT "compressor running".
            # For running state use freq_c15 > 0 (see configuration.yaml "Compressor Running").
            ("compressor_enabled", "Compressor Auto Mode (P40)", "m_comp_p40", "mdi:engine", None),
            ("dhw_active", "DHW Active", "m_estadoacs", "mdi:water-boiler", None),
            ("sg_ready", "SG Ready Active", "m_sgready_p201", "mdi:transmission-tower", None),
            ("alarm", "Alarm Active", "alarma", "mdi:alert", "problem"),
        ]

        for uid, friendly_name, key, icon, device_class in binary_sensors:
            if key == "alarma":
                template = "{{ value_json.alarma | int > 0 }}"
            else:
                template = f"{{{{ value_json.{key} }}}}"

            payload = {
                "name": friendly_name,
                "object_id": f"domusa_{cid}_{uid}",
                "unique_id": f"domusa_{cid}_{uid}",
                "device": dev_info,
                "state_topic": status_topic,
                "value_template": template,
                "payload_on": True,
                "payload_off": False,
                "icon": icon,
                "device_class": device_class,
            }
            await self._publish("binary_sensor", f"domusa_{cid}_{uid}", payload)

        # DHW climate entity
        climate = {
            "name": "DHW Thermostat",
            "object_id": f"domusa_{cid}_dhw_thermostat",
            "unique_id": f"domusa_{cid}_dhw_thermostat",
            "device": dev_info,
            "temperature_command_topic": f"domusa/{cid}/set/setACS",
            "current_temperature_topic": status_topic,
            "current_temperature_template": "{{ value_json.s_acs_c09 }}",
            "temperature_state_topic": status_topic,
            "temperature_state_template": "{{ value_json.st_acs_p04 }}",
            "min_temp": 30,
            "max_temp": 70,
            "temp_step": 1,
            "icon": "mdi:water-boiler",
        }
        await self._publish("climate", f"domusa_{cid}_dhw_thermostat", climate)
