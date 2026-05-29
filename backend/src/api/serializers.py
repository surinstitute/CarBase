from rest_framework import serializers

from catalog.models import (
    AccelerationResult,
    ApprovalSourceDocument,
    BaseModel,
    BatteryPack,
    ChargeTimeResult,
    ChargingPackage,
    ChargingPort,
    ComplianceRecord,
    EMotor,
    EfficiencyResult,
    EmissionsResult,
    Engine,
    FuelTank,
    Group,
    Make,
    Platform,
    PowerTrain,
    PowerTrainArchitecture,
    RangeResult,
    RegulatoryApproval,
    SafetyPackage,
    TopSpeedResult,
    Transmission,
    Vehicle,
)


ARCHITECTURE_MAP = {
    PowerTrainArchitecture.ICE: "ice",
    PowerTrainArchitecture.MILD_HYBRID: "mild_hybrid",
    PowerTrainArchitecture.SERIES_HYBRID: "series_hybrid",
    PowerTrainArchitecture.PARALLEL_HYBRID: "parallel_hybrid",
    PowerTrainArchitecture.POWER_SPLIT_HYBRID: "power_split_hybrid",
    PowerTrainArchitecture.PHEV: "plug_in_hybrid",
    PowerTrainArchitecture.BEV: "battery_electric",
    PowerTrainArchitecture.FCEV: "fuel_cell_electric",
}

ENGINE_FUEL_TYPE_MAP = {
    "gasoline": "gasoline",
    "diesel": "diesel",
    "e85": "flex_fuel",
    "cng": "cng",
    "lpg": "lpg",
    "hydrogen": "hydrogen",
}

FUEL_SOURCE_MAP = {
    "gasoline": "gasoline",
    "diesel": "diesel",
    "e85": "ethanol",
    "cng": "cng",
    "lpg": "lpg",
    "hydrogen": "hydrogen",
}

PROPULSION_ROLES = {"traction", "mixed"}


def mark_first_primary(items):
    if not items:
        return items
    if any(item.get("isPrimary") for item in items):
        return items
    items[0]["isPrimary"] = True
    return items


class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = "__all__"


class MakeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Make
        fields = "__all__"


class BaseModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = BaseModel
        fields = "__all__"


class PlatformSerializer(serializers.ModelSerializer):
    class Meta:
        model = Platform
        fields = "__all__"


class EngineSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(source="engineId", read_only=True)
    fuelType = serializers.SerializerMethodField()
    displacementCc = serializers.IntegerField(source="displacement_cc", read_only=True)
    powerKw = serializers.FloatField(source="power_kW", read_only=True)
    cylinderCount = serializers.IntegerField(source="cylinder_count", read_only=True)

    class Meta:
        model = Engine
        fields = (
            "id",
            "fuelType",
            "displacementCc",
            "powerKw",
            "cylinderCount",
            "aspiration",
            "layout",
        )

    def get_fuelType(self, obj):
        return ENGINE_FUEL_TYPE_MAP.get(obj.energy_source, "other")


class BatteryPackSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(source="batteryPackId", read_only=True)
    grossCapacityKWh = serializers.SerializerMethodField()
    usableCapacityKWh = serializers.FloatField(source="usable_capacity_kWh", read_only=True)
    systemVoltage = serializers.SerializerMethodField()

    class Meta:
        model = BatteryPack
        fields = (
            "id",
            "chemistry",
            "grossCapacityKWh",
            "usableCapacityKWh",
            "systemVoltage",
        )

    def get_grossCapacityKWh(self, obj):
        if obj.gross_capacity_kWh is not None:
            return obj.gross_capacity_kWh
        return obj.capacity_kWh

    def get_systemVoltage(self, obj):
        if obj.voltage_V is None:
            return None
        return int(round(obj.voltage_V))


class FuelTankSerializer(serializers.ModelSerializer):
    class Meta:
        model = FuelTank
        fields = "__all__"


class EMotorSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(source="eMotorId", read_only=True)
    motorType = serializers.CharField(source="motor_type", read_only=True)
    powerKw = serializers.FloatField(source="power_kW", read_only=True)
    coolingType = serializers.CharField(source="cooling_type", read_only=True)

    class Meta:
        model = EMotor
        fields = (
            "id",
            "motorType",
            "powerKw",
            "position",
            "coolingType",
        )


class PowerTrainSerializer(serializers.ModelSerializer):
    class Meta:
        model = PowerTrain
        fields = "__all__"


class TransmissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transmission
        fields = "__all__"


class VehicleSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(source="pk", read_only=True)
    lineage = serializers.SerializerMethodField()
    configuration = serializers.SerializerMethodField()

    class Meta:
        model = Vehicle
        fields = ("id", "lineage", "configuration")

    def get_lineage(self, obj):
        lineage = {
            "makeId": str(obj.modelId.make.makeId),
            "modelId": str(obj.modelId.id),
            "modelYear": obj.modelId.year,
        }
        if obj.modelId.platformId_id:
            lineage["platformId"] = str(obj.modelId.platformId.platformId)
        if obj.modelId.generation:
            lineage["generationId"] = obj.modelId.generation
        return lineage

    def get_configuration(self, obj):
        configuration = {
            "powertrain": self._serialize_powertrain(obj.powerTrainId),
        }
        if obj.bodyStyle:
            configuration["bodyStyle"] = obj.bodyStyle
        if obj.transmissionId_id:
            configuration["transmissionId"] = str(obj.transmissionId.transmissionId)
        return configuration

    def to_representation(self, instance):
        data = super().to_representation(instance)
        specs = self._serialize_specs(instance)
        if specs:
            data["specs"] = specs
        safety = self._serialize_safety(instance)
        if safety:
            data["safety"] = safety
        charging = self._serialize_charging(instance)
        if charging:
            data.setdefault("configuration", {})["charging"] = charging
        performance = self._serialize_performance(instance)
        if performance:
            data["performance"] = performance
        compliance = self._serialize_compliance(instance)
        if compliance:
            data["compliance"] = compliance
        return data

    def _serialize_powertrain(self, powertrain):
        if powertrain is None:
            return None

        serialized = {
            "architecture": ARCHITECTURE_MAP.get(
                powertrain.architecture, powertrain.architecture
            ),
        }

        energy_sources = self._build_energy_sources(powertrain)
        if energy_sources:
            serialized["energySources"] = energy_sources

        energy_storage = self._build_energy_storage(powertrain)
        if energy_storage:
            serialized["energyStorage"] = energy_storage

        energy_converters = self._build_energy_converters(powertrain)
        if energy_converters:
            serialized["energyConverters"] = energy_converters

        traction_motors = self._build_traction_motors(powertrain)
        if traction_motors:
            serialized["tractionMotors"] = traction_motors

        return serialized

    def _build_energy_sources(self, powertrain):
        items = []

        for fitment in powertrain.fuel_fitments.all():
            items.append(
                {
                    "source": FUEL_SOURCE_MAP.get(
                        fitment.fuel_tank.fuel_type, fitment.fuel_tank.fuel_type
                    ),
                    "isPrimary": fitment.is_primary,
                }
            )

        for fitment in powertrain.battery_fitments.all():
            items.append(
                {
                    "source": "grid_electricity",
                    "isPrimary": fitment.is_primary,
                }
            )

        if not items:
            for fitment in powertrain.engine_fitments.all():
                items.append(
                    {
                        "source": FUEL_SOURCE_MAP.get(
                            fitment.engine.energy_source, fitment.engine.energy_source
                        ),
                        "isPrimary": fitment.is_primary,
                    }
                )

        return mark_first_primary(items)

    def _build_energy_storage(self, powertrain):
        items = [
            {
                "type": "battery_pack",
                "batteryPackId": str(fitment.battery_pack.batteryPackId),
                "isPrimary": fitment.is_primary,
            }
            for fitment in powertrain.battery_fitments.all()
        ]

        items.extend(
            {
                "type": "fuel_tank",
                "fuelTankId": str(fitment.fuel_tank.fuelTankId),
                "fuelCapacity": fitment.fuel_tank.capacity_L,
                "isPrimary": fitment.is_primary,
            }
            for fitment in powertrain.fuel_fitments.all()
        )

        return mark_first_primary(items)

    def _build_energy_converters(self, powertrain):
        items = [
            {
                "type": "combustion_engine",
                "engineId": str(fitment.engine.engineId),
                "role": fitment.role,
                "isPrimary": fitment.is_primary,
            }
            for fitment in powertrain.engine_fitments.all()
        ]

        return mark_first_primary(items)

    def _build_traction_motors(self, powertrain):
        items = [
            {
                "electricMotorId": str(fitment.e_motor.eMotorId),
                "role": fitment.role,
                "position": fitment.position,
                "quantity": fitment.quantity,
                "isPrimary": fitment.is_primary,
            }
            for fitment in powertrain.motor_fitments.all()
        ]

        return mark_first_primary(items)

    def _serialize_specs(self, obj):
        specs = {}

        length = self._measurement(obj.length_mm, "mm")
        if length:
            specs["length"] = length

        width = self._measurement(obj.width_mm, "mm")
        if width:
            specs["width"] = width

        height = self._measurement(obj.height_mm, "mm")
        if height:
            specs["height"] = height

        wheelbase = self._measurement(obj.wheelbase_mm, "mm")
        if wheelbase:
            specs["wheelbase"] = wheelbase

        curb_weight = self._measurement(obj.curb_weight_kg, "kg")
        if curb_weight:
            specs["curbWeight"] = curb_weight

        if obj.door_count is not None:
            specs["doorCount"] = obj.door_count

        if obj.passenger_capacity is not None:
            specs["passengerCapacity"] = obj.passenger_capacity

        return specs

    def _measurement(self, value, unit):
        if value is None:
            return None
        return {"value": value, "unit": unit}

    def _serialize_safety(self, obj):
        safety_package = getattr(obj, "safety_package", None)
        if safety_package is None:
            return None

        safety = {}

        collision_warnings = self._build_safety_section(
            safety_package,
            {
                "fcw": "collisionWarnings_fcw",
                "ldw": "collisionWarnings_ldw",
                "bsw": "collisionWarnings_bsw",
                "rctw": "collisionWarnings_rctw",
            },
        )
        if collision_warnings:
            safety["collisionWarnings"] = collision_warnings

        collision_intervention = self._build_safety_section(
            safety_package,
            {
                "aebCity": "collisionIntervention_aebCity",
                "aebPedestrian": "collisionIntervention_aebPedestrian",
                "aebHighway": "collisionIntervention_aebHighway",
                "aebRear": "collisionIntervention_aebRear",
            },
        )
        if collision_intervention:
            safety["collisionIntervention"] = collision_intervention

        driving_control_assistance = self._build_safety_section(
            safety_package,
            {
                "lka": "drivingControlAssistance_lka",
                "lca": "drivingControlAssistance_lca",
                "acc": "drivingControlAssistance_acc",
                "activeDrivingAssistanceDirectDriverMonitoring": "drivingControlAssistance_activeDrivingAssistanceDirectDriverMonitoring",
            },
        )
        if driving_control_assistance:
            safety["drivingControlAssistance"] = driving_control_assistance

        rear_seat_safety = self._build_safety_section(
            safety_package,
            {
                "childSafety": "rearSeatSafety_childSafety",
                "rearOccupantAlertEndOfTripReminder": "rearSeatSafety_rearOccupantAlertEndOfTripReminder",
            },
        )
        if rear_seat_safety:
            safety["rearSeatSafety"] = rear_seat_safety

        visibility_and_control = self._build_safety_section(
            safety_package,
            {
                "drl": "visibilityAndControl_drl",
                "rearViewCamera": "visibilityAndControl_rearViewCamera",
                "esc": "visibilityAndControl_esc",
                "tractionControl": "visibilityAndControl_tractionControl",
                "abs": "visibilityAndControl_abs",
            },
        )
        if visibility_and_control:
            safety["visibilityAndControl"] = visibility_and_control

        restraints = self._build_safety_section(
            safety_package,
            {
                "airbagSideFront": "restraints_airbagSideFront",
                "airbagSideRear": "restraints_airbagSideRear",
                "headProtectionAirbag": "restraints_headProtectionAirbag",
            },
        )
        if restraints:
            safety["restraints"] = restraints

        return safety

    def _build_safety_section(self, safety_package, field_map):
        section = {}
        for output_key, model_field in field_map.items():
            value = getattr(safety_package, model_field)
            if value is not None:
                section[output_key] = value
        return section

    def _serialize_charging(self, obj):
        charging = {}
        charging_package = getattr(obj, "charging_package", None)

        if charging_package is not None:
            ac_charging = self._serialize_charging_capability(
                charging_package.ac_max_power_kw,
                charging_package.ac_max_voltage_v,
                charging_package.ac_max_current_a,
                charging_package.ac_phases,
            )
            if ac_charging:
                charging["acCharging"] = ac_charging

            dc_charging = self._serialize_charging_capability(
                charging_package.dc_max_power_kw,
                charging_package.dc_max_voltage_v,
                charging_package.dc_max_current_a,
                None,
            )
            if dc_charging:
                charging["dcCharging"] = dc_charging

            bidirectional = self._build_safety_section(
                charging_package,
                {
                    "v2l": "v2l",
                    "v2h": "v2h",
                    "v2g": "v2g",
                },
            )
            if bidirectional:
                charging["bidirectionalCharging"] = bidirectional

        ports = [
            self._serialize_charging_port(port) for port in obj.charging_ports.all()
        ]
        if ports:
            charging["ports"] = ports

        charge_times = [
            self._serialize_charge_time_result(result)
            for result in obj.charge_time_results.all()
        ]
        if charge_times:
            charging["chargeTimes"] = charge_times

        return charging

    def _serialize_charging_capability(
        self, max_power_kw, max_voltage_v, max_current_a, phases
    ):
        if max_power_kw is None:
            return None
        capability = {"maxPowerKw": max_power_kw}
        if max_voltage_v is not None:
            capability["maxVoltageV"] = max_voltage_v
        if max_current_a is not None:
            capability["maxCurrentA"] = max_current_a
        if phases is not None:
            capability["phases"] = phases
        return capability

    def _serialize_charging_port(self, port):
        data = {
            "currentType": port.current_type,
            "connector": port.connector,
        }
        if port.location:
            data["location"] = port.location
        return data

    def _serialize_charge_time_result(self, result):
        data = {
            "currentType": result.current_type,
            "sourceStateOfChargePercent": result.source_state_of_charge_percent,
            "targetStateOfChargePercent": result.target_state_of_charge_percent,
            "durationMinutes": result.duration_minutes,
        }
        if result.connector:
            data["connector"] = result.connector
        if result.supply_context:
            data["supplyContext"] = result.supply_context
        if result.power_kw is not None:
            data["powerKw"] = result.power_kw
        if result.is_primary:
            data["isPrimary"] = result.is_primary
        if result.note:
            data["note"] = result.note
        return data

    def _serialize_performance(self, obj):
        performance = {}

        efficiency = [
            self._serialize_result_with_cycle_scope(item)
            for item in obj.efficiency_results.all()
        ]
        if efficiency:
            performance["efficiency"] = efficiency

        range_results = [
            self._serialize_result_with_cycle_scope(item)
            for item in obj.range_results.all()
        ]
        if range_results:
            performance["range"] = range_results

        emissions = [
            self._serialize_result_with_cycle_scope(item)
            for item in obj.emissions_results.all()
        ]
        if emissions:
            performance["emissions"] = emissions

        acceleration = [
            self._serialize_metric_result(item)
            for item in obj.acceleration_results.all()
        ]
        if acceleration:
            performance["acceleration"] = acceleration

        top_speed = [
            self._serialize_top_speed_result(item)
            for item in obj.top_speed_results.all()
        ]
        if top_speed:
            performance["topSpeed"] = top_speed

        power = self._build_computed_power_results(obj)
        if power:
            performance["power"] = power

        torque = self._build_computed_torque_results(obj)
        if torque:
            performance["torque"] = torque

        return performance

    def _build_computed_power_results(self, obj):
        powertrain = obj.powerTrainId
        if not powertrain:
            return []

        items = []
        engine_fitments = self._propulsion_engine_fitments(powertrain)
        motor_fitments = self._propulsion_motor_fitments(powertrain)

        combustion_power_kw = sum(
            fitment.engine.power_kW
            for fitment in engine_fitments
            if fitment.engine.power_kW is not None
        )
        if combustion_power_kw > 0:
            items.append(
                {
                    "metric": "combustion_engine_power",
                    "value": combustion_power_kw,
                    "unit": "kw",
                    "isPrimary": not motor_fitments,
                }
            )

        electric_power_kw = sum(
            fitment.e_motor.power_kW * (fitment.quantity or 1)
            for fitment in motor_fitments
            if fitment.e_motor.power_kW is not None
        )
        if electric_power_kw > 0:
            items.append(
                {
                    "metric": "electric_motor_power",
                    "value": electric_power_kw,
                    "unit": "kw",
                    "isPrimary": not engine_fitments,
                }
            )

        return [item for item in items if item["value"] is not None]

    def _build_computed_torque_results(self, obj):
        powertrain = obj.powerTrainId
        if not powertrain:
            return []

        engine_fitments = self._propulsion_engine_fitments(powertrain)
        motor_fitments = self._propulsion_motor_fitments(powertrain)
        if engine_fitments or len(motor_fitments) != 1:
            return []

        fitment = motor_fitments[0]
        torque_nm = fitment.e_motor.torque_Nm
        if torque_nm is None:
            return []

        return [
            {
                "metric": "peak_torque",
                "value": torque_nm * (fitment.quantity or 1),
                "unit": "nm",
                "isPrimary": True,
            }
        ]

    def _propulsion_engine_fitments(self, powertrain):
        return [
            fitment
            for fitment in powertrain.engine_fitments.all()
            if fitment.role in PROPULSION_ROLES
        ]

    def _propulsion_motor_fitments(self, powertrain):
        return [
            fitment
            for fitment in powertrain.motor_fitments.all()
            if fitment.role in PROPULSION_ROLES
        ]

    def _serialize_result_with_cycle_scope(self, item):
        data = {
            "metric": item.metric,
            "value": item.value,
            "unit": item.unit,
        }
        if item.cycle:
            data["cycle"] = item.cycle
        if item.scope:
            data["scope"] = item.scope
        if item.is_primary:
            data["isPrimary"] = item.is_primary
        return data

    def _serialize_metric_result(self, item):
        data = {
            "metric": item.metric,
            "value": item.value,
            "unit": item.unit,
        }
        if item.is_primary:
            data["isPrimary"] = item.is_primary
        return data

    def _serialize_top_speed_result(self, item):
        data = {
            "value": item.value,
            "unit": item.unit,
        }
        if item.is_primary:
            data["isPrimary"] = item.is_primary
        return data

    def _serialize_compliance(self, obj):
        compliance = {}

        approvals = [
            self._serialize_regulatory_approval(item)
            for item in obj.regulatory_approvals.all()
        ]
        if approvals:
            compliance["approvals"] = approvals

        emissions = [
            self._serialize_compliance_record(item)
            for item in obj.compliance_records.all()
            if item.category == "emissions"
        ]
        if emissions:
            compliance["emissions"] = emissions

        safety = [
            self._serialize_compliance_record(item)
            for item in obj.compliance_records.all()
            if item.category == "safety"
        ]
        if safety:
            compliance["safety"] = safety

        return compliance

    def _serialize_compliance_record(self, item):
        data = {"standard": item.standard}
        if item.region:
            data["region"] = item.region
        if item.classification:
            data["classification"] = item.classification
        if item.is_primary:
            data["isPrimary"] = item.is_primary
        return data

    def _serialize_regulatory_approval(self, item):
        data = {
            "authority": item.authority,
            "jurisdiction": item.jurisdiction,
            "scheme": item.scheme,
            "domain": item.domain,
            "standard": item.standard,
            "status": item.status,
        }
        if item.classification:
            data["classification"] = item.classification
        if item.identifier:
            data["identifier"] = item.identifier
        if item.valid_from:
            data["validFrom"] = item.valid_from.isoformat()
        if item.valid_to:
            data["validTo"] = item.valid_to.isoformat()
        if item.is_primary:
            data["isPrimary"] = item.is_primary
        if item.references:
            data["references"] = item.references
        source_docs = [
            self._serialize_approval_source_doc(doc) for doc in item.source_docs.all()
        ]
        if source_docs:
            data["sourceDocs"] = source_docs
        if item.notes:
            data["notes"] = item.notes
        return data

    def _serialize_approval_source_doc(self, doc):
        data = {"url": doc.url}
        if doc.title:
            data["title"] = doc.title
        if doc.publisher:
            data["publisher"] = doc.publisher
        if doc.document_type:
            data["documentType"] = doc.document_type
        if doc.published_at:
            data["publishedAt"] = doc.published_at.isoformat()
        if doc.language:
            data["language"] = doc.language
        if doc.is_primary:
            data["isPrimary"] = doc.is_primary
        if doc.notes:
            data["notes"] = doc.notes
        return data
