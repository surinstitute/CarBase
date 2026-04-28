import uuid
from django.db import models


class FuelType(models.TextChoices):
    GASOLINE = "gasoline", "Gasoline"
    DIESEL = "diesel", "Diesel"
    E85 = "e85", "E85"
    CNG = "cng", "Compressed Natural Gas"
    LPG = "lpg", "Liquefied Petroleum Gas"
    HYDROGEN = "hydrogen", "Hydrogen"


class PowerTrainArchitecture(models.TextChoices):
    ICE = "ice", "Internal Combustion Engine"
    MILD_HYBRID = "mild_hybrid", "Mild Hybrid"
    SERIES_HYBRID = "series_hybrid", "Series Hybrid"
    PARALLEL_HYBRID = "parallel_hybrid", "Parallel Hybrid"
    POWER_SPLIT_HYBRID = "power_split_hybrid", "Power Split Hybrid"
    PHEV = "phev", "Plug-in Hybrid Electric Vehicle"
    BEV = "bev", "Battery Electric Vehicle"
    FCEV = "fcev", "Fuel Cell Electric Vehicle"


class ConverterRole(models.TextChoices):
    TRACTION = "traction", "Traction"
    GENERATOR = "generator", "Generator"
    MIXED = "mixed", "Mixed"
    AUXILIARY = "auxiliary", "Auxiliary"


class TractionPosition(models.TextChoices):
    FRONT_AXLE = "front_axle", "Front Axle"
    REAR_AXLE = "rear_axle", "Rear Axle"
    FRONT_LEFT = "front_left", "Front Left"
    FRONT_RIGHT = "front_right", "Front Right"
    REAR_LEFT = "rear_left", "Rear Left"
    REAR_RIGHT = "rear_right", "Rear Right"
    CENTER = "center", "Center"
    OTHER = "other", "Other"


class StorageType(models.TextChoices):
    BATTERY_PACK = "battery_pack", "Battery Pack"
    FUEL_TANK = "fuel_tank", "Fuel Tank"
    OTHER = "other", "Other"


class BodyStyle(models.TextChoices):
    SEDAN = "sedan", "Sedan"
    HATCHBACK = "hatchback", "Hatchback"
    FASTBACK = "fastback", "Fastback"
    COUPE = "coupe", "Coupe"
    CONVERTIBLE = "convertible", "Convertible"
    WAGON = "wagon", "Wagon"
    SUV = "suv", "SUV"
    CROSSOVER = "crossover", "Crossover"
    PICKUP = "pickup", "Pickup"
    VAN = "van", "Van"
    MINIVAN = "minivan", "Minivan"
    LIFTBACK = "liftback", "Liftback"
    ROADSTER = "roadster", "Roadster"
    TARGA = "targa", "Targa"
    OTHER = "other", "Other"


class TransmissionType(models.TextChoices):
    MANUAL = "manual", "Manual"
    AUTOMATIC = "automatic", "Automatic"
    DCT = "dct", "Dual-clutch"
    CVT = "cvt", "CVT"
    SINGLE_SPEED = "single_speed", "Single speed"
    OTHER = "other", "Other"


class TestCycle(models.TextChoices):
    EPA = "epa", "EPA"
    FTP = "ftp", "FTP"
    HFET = "hfet", "HFET"
    WLTP = "wltp", "WLTP"
    NEDC = "nedc", "NEDC"
    CLTC = "cltc", "CLTC"
    JC08 = "jc08", "JC08"
    OTHER = "other", "Other"


class ResultScope(models.TextChoices):
    CITY = "city", "City"
    HIGHWAY = "highway", "Highway"
    COMBINED = "combined", "Combined"
    MIXED = "mixed", "Mixed"
    OTHER = "other", "Other"


class EfficiencyMetric(models.TextChoices):
    FUEL_CONSUMPTION = "fuel_consumption", "Fuel consumption"
    ENERGY_CONSUMPTION = "energy_consumption", "Energy consumption"
    FUEL_ECONOMY = "fuel_economy", "Fuel economy"


class EfficiencyUnit(models.TextChoices):
    L_PER_100KM = "l_per_100km", "L/100km"
    KG_PER_100KM = "kg_per_100km", "kg/100km"
    KWH_PER_100KM = "kwh_per_100km", "kWh/100km"
    WH_PER_KM = "wh_per_km", "Wh/km"
    MPG_US = "mpg_us", "mpg US"
    MPG_IMP = "mpg_imp", "mpg imp"
    KM_PER_L = "km_per_l", "km/L"
    KM_PER_KG = "km_per_kg", "km/kg"


class RangeMetric(models.TextChoices):
    TOTAL_RANGE = "total_range", "Total range"
    ELECTRIC_RANGE = "electric_range", "Electric range"


class DistanceUnit(models.TextChoices):
    KM = "km", "km"
    MI = "mi", "mi"


class EmissionsMetric(models.TextChoices):
    CO2_TAILPIPE = "co2_tailpipe", "CO2 tailpipe"
    CO2_WEIGHTED = "co2_weighted", "CO2 weighted"
    CO = "co", "CO"
    HC = "hc", "HC"
    NMHC = "nmhc", "NMHC"
    CH4 = "ch4", "CH4"
    N2O = "n2o", "N2O"
    NOX = "nox", "NOx"
    PM = "pm", "PM"
    PN = "pn", "PN"
    EVAPORATIVE_HC = "evaporative_hc", "Evaporative HC"


class EmissionsUnit(models.TextChoices):
    G_PER_KM = "g_per_km", "g/km"
    MG_PER_KM = "mg_per_km", "mg/km"
    NUMBER_PER_KM = "number_per_km", "number/km"
    G_PER_PBA = "g_per_pba", "g/PBA"


class AccelerationMetric(models.TextChoices):
    ZERO_TO_100_KMH = "0_100_kmh", "0-100 km/h"
    ZERO_TO_60_MPH = "0_60_mph", "0-60 mph"
    ZERO_TO_200_KMH = "0_200_kmh", "0-200 km/h"
    QUARTER_MILE = "quarter_mile", "Quarter mile"


class SpeedUnit(models.TextChoices):
    KM_H = "km_h", "km/h"
    MPH = "mph", "mph"


class TorqueMetric(models.TextChoices):
    SYSTEM_TORQUE = "system_torque", "System torque"
    PEAK_TORQUE = "peak_torque", "Peak torque"


class TorqueUnit(models.TextChoices):
    NM = "nm", "Nm"
    LB_FT = "lb_ft", "lb-ft"


class PowerMetric(models.TextChoices):
    COMBUSTION_ENGINE_POWER = "combustion_engine_power", "Combustion engine power"
    ELECTRIC_MOTOR_POWER = "electric_motor_power", "Electric motor power"
    SYSTEM_POWER = "system_power", "System power"


class PowerUnit(models.TextChoices):
    KW = "kw", "kW"
    HP = "hp", "hp"
    PS = "ps", "PS"


class ChargingCurrentType(models.TextChoices):
    AC = "ac", "AC"
    DC = "dc", "DC"
    AC_DC = "ac_dc", "AC/DC"


class ChargingConnector(models.TextChoices):
    TYPE1 = "type1", "Type 1"
    TYPE2 = "type2", "Type 2"
    CCS1 = "ccs1", "CCS1"
    CCS2 = "ccs2", "CCS2"
    CHADEMO = "chademo", "CHAdeMO"
    GB_T = "gb_t", "GB/T"
    GB_DC = "gb_dc", "GB DC"
    NACS = "nacs", "NACS"
    TESLA = "tesla", "Tesla"
    OTHER = "other", "Other"


class ChargingPortLocation(models.TextChoices):
    FRONT_LEFT = "front_left", "Front left"
    FRONT_RIGHT = "front_right", "Front right"
    REAR_LEFT = "rear_left", "Rear left"
    REAR_RIGHT = "rear_right", "Rear right"
    FRONT_CENTER = "front_center", "Front center"
    REAR_CENTER = "rear_center", "Rear center"
    LEFT = "left", "Left"
    RIGHT = "right", "Right"
    OTHER = "other", "Other"


class ChargingSupplyContext(models.TextChoices):
    HOME_STANDARD_OUTLET = "home_standard_outlet", "Home standard outlet"
    HOME_DEDICATED_AC = "home_dedicated_ac", "Home dedicated AC"
    PUBLIC_AC = "public_ac", "Public AC"
    PUBLIC_DC_FAST = "public_dc_fast", "Public DC fast"
    PUBLIC_DC_ULTRAFAST = "public_dc_ultrafast", "Public DC ultrafast"
    OTHER = "other", "Other"


class ComplianceCategory(models.TextChoices):
    EMISSIONS = "emissions", "Emissions"
    SAFETY = "safety", "Safety"


class ApprovalDomain(models.TextChoices):
    EMISSIONS = "emissions", "Emissions"
    SAFETY = "safety", "Safety"
    NOISE = "noise", "Noise"
    ENERGY_EFFICIENCY = "energy_efficiency", "Energy efficiency"
    OTHER = "other", "Other"


class ApprovalStatus(models.TextChoices):
    APPROVED = "approved", "Approved"
    CERTIFIED = "certified", "Certified"
    ACCEPTED = "accepted", "Accepted"
    PENDING = "pending", "Pending"
    WITHDRAWN = "withdrawn", "Withdrawn"
    EXPIRED = "expired", "Expired"
    REJECTED = "rejected", "Rejected"
    OTHER = "other", "Other"


class SourceDocumentType(models.TextChoices):
    CERTIFICATE = "certificate", "Certificate"
    APPROVAL_RECORD = "approval_record", "Approval record"
    DATABASE_ENTRY = "database_entry", "Database entry"
    REGULATION = "regulation", "Regulation"
    TEST_REPORT = "test_report", "Test report"
    OTHER = "other", "Other"


class BaseModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=True)
    model = models.CharField(max_length=255)
    make = models.ForeignKey("Make", on_delete=models.CASCADE, related_name="models")
    generation = models.CharField(max_length=255, null=True, blank=True)
    year = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.make.name} {self.model} {self.year}"


class Make(models.Model):
    makeId = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=True)
    name = models.CharField(max_length=255)
    group = models.ForeignKey(
        "Group",
        on_delete=models.CASCADE,
        related_name="makes",
        null=True,
        blank=True,
    )

    def __str__(self):
        return self.name


class Group(models.Model):
    groupId = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=True)
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class Platform(models.Model):
    platformId = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=True)
    name = models.CharField(max_length=255)
    groups = models.ManyToManyField(Group, related_name="platforms")

    def __str__(self):
        return self.name


class Engine(models.Model):
    engineId = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=True)
    name = models.CharField(max_length=255)
    maker = models.ForeignKey(Make, on_delete=models.CASCADE, related_name="engines")
    energy_source = models.CharField(
        max_length=255,
        choices=FuelType.choices,
    )

    def __str__(self):
        return self.name


class BatteryPack(models.Model):
    batteryPackId = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=True
    )
    name = models.CharField(max_length=255)
    group = models.ForeignKey(
        "Group",
        on_delete=models.CASCADE,
        related_name="battery_packs",
        null=True,
        blank=True,
    )
    provider = models.CharField(max_length=255)
    capacity_kWh = models.FloatField()
    voltage_V = models.FloatField()
    weight_kg = models.FloatField()

    def __str__(self):
        return self.name


class FuelTank(models.Model):
    fuelTankId = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=True)
    name = models.CharField(max_length=255)
    maker = models.ForeignKey(Make, on_delete=models.CASCADE, related_name="fuel_tanks")
    fuel_type = models.CharField(max_length=255, choices=FuelType.choices)
    capacity_L = models.FloatField()

    def __str__(self):
        return self.name


class EMotor(models.Model):
    eMotorId = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=True)
    name = models.CharField(max_length=255)
    maker = models.ForeignKey(Make, on_delete=models.CASCADE, related_name="e_motors")
    power_kW = models.FloatField()
    torque_Nm = models.FloatField()

    def __str__(self):
        return self.name


class Transmission(models.Model):
    transmissionId = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=True
    )
    name = models.CharField(max_length=255)
    maker = models.ForeignKey(
        Make, on_delete=models.CASCADE, related_name="transmissions"
    )
    type = models.CharField(max_length=255, choices=TransmissionType.choices)
    gears = models.PositiveIntegerField(null=True, blank=True)

    def __str__(self):
        return self.name


class PowerTrain(models.Model):
    powerTrainId = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=True)
    name = models.CharField(max_length=255)
    group = models.ForeignKey(
        "Group",
        on_delete=models.CASCADE,
        related_name="powertrains",
        null=True,
        blank=True,
    )
    architecture = models.CharField(
        max_length=255,
        choices=PowerTrainArchitecture.choices,
    )
    engines = models.ManyToManyField(
        Engine, through="PowerTrainEngine", related_name="powertrains", blank=True
    )
    e_motors = models.ManyToManyField(
        EMotor, through="PowerTrainEMotor", related_name="powertrains", blank=True
    )
    battery_packs = models.ManyToManyField(
        BatteryPack,
        through="PowerTrainBatteryPack",
        related_name="powertrains",
        blank=True,
    )
    fuel_tanks = models.ManyToManyField(
        FuelTank,
        through="PowerTrainFuelTank",
        related_name="powertrains",
        blank=True,
    )

    def __str__(self):
        return self.name


class PowerTrainEngine(models.Model):
    powertrain = models.ForeignKey(
        PowerTrain, on_delete=models.CASCADE, related_name="engine_fitments"
    )
    engine = models.ForeignKey(
        Engine, on_delete=models.CASCADE, related_name="powertrain_fitments"
    )
    role = models.CharField(max_length=255, choices=ConverterRole.choices)
    is_primary = models.BooleanField(default=False)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["powertrain", "engine"], name="unique_powertrain_engine"
            )
        ]


class PowerTrainEMotor(models.Model):
    powertrain = models.ForeignKey(
        PowerTrain, on_delete=models.CASCADE, related_name="motor_fitments"
    )
    e_motor = models.ForeignKey(
        EMotor, on_delete=models.CASCADE, related_name="powertrain_fitments"
    )
    role = models.CharField(
        max_length=255, choices=ConverterRole.choices, default=ConverterRole.TRACTION
    )
    position = models.CharField(max_length=255, choices=TractionPosition.choices)
    is_primary = models.BooleanField(default=False)
    quantity = models.PositiveIntegerField(default=1)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["powertrain", "e_motor", "position"],
                name="unique_powertrain_emotor_position",
            )
        ]


class PowerTrainBatteryPack(models.Model):
    powertrain = models.ForeignKey(
        PowerTrain, on_delete=models.CASCADE, related_name="battery_fitments"
    )
    battery_pack = models.ForeignKey(
        BatteryPack, on_delete=models.CASCADE, related_name="powertrain_fitments"
    )
    storage_type = models.CharField(
        max_length=255,
        choices=StorageType.choices,
        default=StorageType.BATTERY_PACK,
    )
    is_primary = models.BooleanField(default=False)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["powertrain", "battery_pack"],
                name="unique_powertrain_battery_pack",
            )
        ]


class PowerTrainFuelTank(models.Model):
    powertrain = models.ForeignKey(
        PowerTrain, on_delete=models.CASCADE, related_name="fuel_fitments"
    )
    fuel_tank = models.ForeignKey(
        FuelTank, on_delete=models.CASCADE, related_name="powertrain_fitments"
    )
    storage_type = models.CharField(
        max_length=255,
        choices=StorageType.choices,
        default=StorageType.FUEL_TANK,
    )
    is_primary = models.BooleanField(default=False)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["powertrain", "fuel_tank"],
                name="unique_powertrain_fuel_tank",
            )
        ]


class Vehicle(models.Model):

    modelId = models.ForeignKey(
        BaseModel, on_delete=models.CASCADE, related_name="model_vehicles"
    )
    platformId = models.ForeignKey(
        Platform,
        on_delete=models.CASCADE,
        related_name="vehicles",
        null=True,
        blank=True,
    )
    powerTrainId = models.ForeignKey(
        PowerTrain,
        on_delete=models.CASCADE,
        related_name="vehicles",
        null=True,
        blank=True,
    )
    transmissionId = models.ForeignKey(
        Transmission,
        on_delete=models.CASCADE,
        related_name="vehicles",
        null=True,
        blank=True,
    )
    bodyStyle = models.CharField(
        max_length=255,
        choices=BodyStyle.choices,
        null=True,
        blank=True,
    )
    length_mm = models.FloatField(null=True, blank=True)
    width_mm = models.FloatField(null=True, blank=True)
    height_mm = models.FloatField(null=True, blank=True)
    wheelbase_mm = models.FloatField(null=True, blank=True)
    curb_weight_kg = models.FloatField(null=True, blank=True)
    door_count = models.PositiveIntegerField(null=True, blank=True)
    passenger_capacity = models.PositiveIntegerField(null=True, blank=True)

    def __str__(self):
        details = [str(self.modelId)]
        if self.powerTrainId:
            details.append(self.powerTrainId.name)
        return " - ".join(details)


class SafetyPackage(models.Model):
    vehicle = models.OneToOneField(
        Vehicle,
        on_delete=models.CASCADE,
        related_name="safety_package",
    )
    collisionWarnings_fcw = models.BooleanField(null=True, blank=True)
    collisionWarnings_ldw = models.BooleanField(null=True, blank=True)
    collisionWarnings_bsw = models.BooleanField(null=True, blank=True)
    collisionWarnings_rctw = models.BooleanField(null=True, blank=True)
    collisionIntervention_aebCity = models.BooleanField(null=True, blank=True)
    collisionIntervention_aebPedestrian = models.BooleanField(null=True, blank=True)
    collisionIntervention_aebHighway = models.BooleanField(null=True, blank=True)
    collisionIntervention_aebRear = models.BooleanField(null=True, blank=True)
    drivingControlAssistance_lka = models.BooleanField(null=True, blank=True)
    drivingControlAssistance_lca = models.BooleanField(null=True, blank=True)
    drivingControlAssistance_acc = models.BooleanField(null=True, blank=True)
    drivingControlAssistance_activeDrivingAssistanceDirectDriverMonitoring = (
        models.BooleanField(
            null=True,
            blank=True,
            db_column="drv_ctrl_asst_direct_monitoring",
        )
    )
    rearSeatSafety_childSafety = models.BooleanField(null=True, blank=True)
    rearSeatSafety_rearOccupantAlertEndOfTripReminder = models.BooleanField(
        null=True, blank=True
    )
    visibilityAndControl_drl = models.BooleanField(null=True, blank=True)
    visibilityAndControl_rearViewCamera = models.BooleanField(null=True, blank=True)
    visibilityAndControl_esc = models.BooleanField(null=True, blank=True)
    visibilityAndControl_tractionControl = models.BooleanField(null=True, blank=True)
    visibilityAndControl_abs = models.BooleanField(null=True, blank=True)
    restraints_airbagSideFront = models.BooleanField(null=True, blank=True)
    restraints_airbagSideRear = models.BooleanField(null=True, blank=True)
    restraints_headProtectionAirbag = models.BooleanField(null=True, blank=True)

    def __str__(self):
        return f"Safety package for {self.vehicle}"


class ChargingPackage(models.Model):
    vehicle = models.OneToOneField(
        Vehicle,
        on_delete=models.CASCADE,
        related_name="charging_package",
    )
    ac_max_power_kw = models.FloatField(null=True, blank=True)
    ac_max_voltage_v = models.FloatField(null=True, blank=True)
    ac_max_current_a = models.FloatField(null=True, blank=True)
    ac_phases = models.PositiveIntegerField(null=True, blank=True)
    dc_max_power_kw = models.FloatField(null=True, blank=True)
    dc_max_voltage_v = models.FloatField(null=True, blank=True)
    dc_max_current_a = models.FloatField(null=True, blank=True)
    v2l = models.BooleanField(null=True, blank=True)
    v2h = models.BooleanField(null=True, blank=True)
    v2g = models.BooleanField(null=True, blank=True)

    def __str__(self):
        return f"Charging package for {self.vehicle}"


class ChargingPort(models.Model):
    vehicle = models.ForeignKey(
        Vehicle,
        on_delete=models.CASCADE,
        related_name="charging_ports",
    )
    current_type = models.CharField(max_length=255, choices=ChargingCurrentType.choices)
    connector = models.CharField(max_length=255, choices=ChargingConnector.choices)
    location = models.CharField(
        max_length=255,
        choices=ChargingPortLocation.choices,
        null=True,
        blank=True,
    )


class ChargeTimeResult(models.Model):
    vehicle = models.ForeignKey(
        Vehicle,
        on_delete=models.CASCADE,
        related_name="charge_time_results",
    )
    current_type = models.CharField(max_length=255, choices=ChargingCurrentType.choices)
    connector = models.CharField(
        max_length=255,
        choices=ChargingConnector.choices,
        null=True,
        blank=True,
    )
    supply_context = models.CharField(
        max_length=255,
        choices=ChargingSupplyContext.choices,
        null=True,
        blank=True,
    )
    source_state_of_charge_percent = models.PositiveIntegerField()
    target_state_of_charge_percent = models.PositiveIntegerField()
    duration_minutes = models.FloatField()
    power_kw = models.FloatField(null=True, blank=True)
    is_primary = models.BooleanField(default=False)
    note = models.TextField(null=True, blank=True)


class ComplianceRecord(models.Model):
    vehicle = models.ForeignKey(
        Vehicle,
        on_delete=models.CASCADE,
        related_name="compliance_records",
    )
    category = models.CharField(max_length=255, choices=ComplianceCategory.choices)
    region = models.CharField(max_length=255, null=True, blank=True)
    standard = models.CharField(max_length=255)
    classification = models.CharField(max_length=255, null=True, blank=True)
    is_primary = models.BooleanField(default=False)


class RegulatoryApproval(models.Model):
    vehicle = models.ForeignKey(
        Vehicle,
        on_delete=models.CASCADE,
        related_name="regulatory_approvals",
    )
    authority = models.CharField(max_length=255)
    jurisdiction = models.CharField(max_length=255)
    scheme = models.CharField(max_length=255)
    domain = models.CharField(max_length=255, choices=ApprovalDomain.choices)
    standard = models.CharField(max_length=255)
    classification = models.CharField(max_length=255, null=True, blank=True)
    identifier = models.CharField(max_length=255, null=True, blank=True)
    status = models.CharField(max_length=255, choices=ApprovalStatus.choices)
    valid_from = models.DateField(null=True, blank=True)
    valid_to = models.DateField(null=True, blank=True)
    is_primary = models.BooleanField(default=False)
    references = models.JSONField(default=dict, blank=True)
    notes = models.TextField(null=True, blank=True)


class ApprovalSourceDocument(models.Model):
    approval = models.ForeignKey(
        RegulatoryApproval,
        on_delete=models.CASCADE,
        related_name="source_docs",
    )
    url = models.URLField()
    title = models.CharField(max_length=255, null=True, blank=True)
    publisher = models.CharField(max_length=255, null=True, blank=True)
    document_type = models.CharField(
        max_length=255,
        choices=SourceDocumentType.choices,
        null=True,
        blank=True,
    )
    published_at = models.DateField(null=True, blank=True)
    language = models.CharField(max_length=255, null=True, blank=True)
    is_primary = models.BooleanField(default=False)
    notes = models.TextField(null=True, blank=True)


class EfficiencyResult(models.Model):
    vehicle = models.ForeignKey(
        Vehicle,
        on_delete=models.CASCADE,
        related_name="efficiency_results",
    )
    cycle = models.CharField(
        max_length=255, choices=TestCycle.choices, null=True, blank=True
    )
    scope = models.CharField(
        max_length=255, choices=ResultScope.choices, null=True, blank=True
    )
    metric = models.CharField(max_length=255, choices=EfficiencyMetric.choices)
    value = models.FloatField()
    unit = models.CharField(max_length=255, choices=EfficiencyUnit.choices)
    is_primary = models.BooleanField(default=False)


class RangeResult(models.Model):
    vehicle = models.ForeignKey(
        Vehicle,
        on_delete=models.CASCADE,
        related_name="range_results",
    )
    cycle = models.CharField(
        max_length=255, choices=TestCycle.choices, null=True, blank=True
    )
    scope = models.CharField(
        max_length=255, choices=ResultScope.choices, null=True, blank=True
    )
    metric = models.CharField(max_length=255, choices=RangeMetric.choices)
    value = models.FloatField()
    unit = models.CharField(max_length=255, choices=DistanceUnit.choices)
    is_primary = models.BooleanField(default=False)


class EmissionsResult(models.Model):
    vehicle = models.ForeignKey(
        Vehicle,
        on_delete=models.CASCADE,
        related_name="emissions_results",
    )
    cycle = models.CharField(
        max_length=255, choices=TestCycle.choices, null=True, blank=True
    )
    scope = models.CharField(
        max_length=255, choices=ResultScope.choices, null=True, blank=True
    )
    metric = models.CharField(max_length=255, choices=EmissionsMetric.choices)
    value = models.FloatField()
    unit = models.CharField(max_length=255, choices=EmissionsUnit.choices)
    is_primary = models.BooleanField(default=False)


class AccelerationResult(models.Model):
    vehicle = models.ForeignKey(
        Vehicle,
        on_delete=models.CASCADE,
        related_name="acceleration_results",
    )
    metric = models.CharField(max_length=255, choices=AccelerationMetric.choices)
    value = models.FloatField()
    unit = models.CharField(max_length=255, default="s")
    is_primary = models.BooleanField(default=False)


class TopSpeedResult(models.Model):
    vehicle = models.ForeignKey(
        Vehicle,
        on_delete=models.CASCADE,
        related_name="top_speed_results",
    )
    value = models.FloatField()
    unit = models.CharField(max_length=255, choices=SpeedUnit.choices)
    is_primary = models.BooleanField(default=False)


class TorqueResult(models.Model):
    vehicle = models.ForeignKey(
        Vehicle,
        on_delete=models.CASCADE,
        related_name="torque_results",
    )
    metric = models.CharField(max_length=255, choices=TorqueMetric.choices)
    value = models.FloatField()
    unit = models.CharField(max_length=255, choices=TorqueUnit.choices)
    is_primary = models.BooleanField(default=False)


class PowerResult(models.Model):
    vehicle = models.ForeignKey(
        Vehicle,
        on_delete=models.CASCADE,
        related_name="power_results",
    )
    metric = models.CharField(max_length=255, choices=PowerMetric.choices)
    value = models.FloatField()
    unit = models.CharField(max_length=255, choices=PowerUnit.choices)
    is_primary = models.BooleanField(default=False)
