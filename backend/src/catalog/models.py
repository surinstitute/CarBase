import uuid

from django.core.validators import FileExtensionValidator
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django_countries.fields import CountryField
from paradedb.indexes import BM25Index
from paradedb.queryset import ParadeDBManager
from paradedb.search import Tokenizer

from catalog.types import (
    AccelerationMetric,
    ApprovalDomain,
    ApprovalStatus,
    BatteryChemistry,
    BodyStyle,
    ChargingConnector,
    ChargingCurrentType,
    ChargingPortLocation,
    ChargingSupplyContext,
    ComplianceCategory,
    ConverterRole,
    DistanceUnit,
    EfficiencyMetric,
    EfficiencyUnit,
    ElectricMotorType,
    EmissionsMetric,
    EmissionsUnit,
    EngineAspiration,
    EngineLayout,
    FuelType,
    MotorCoolingType,
    PowerTrainArchitecture,
    RangeMetric,
    ResultScope,
    SafetyRatingProgram,
    SourceDocumentType,
    SpeedUnit,
    TestCycle,
    TorqueMetric,
    TorqueUnit,
    TractionPosition,
    TransmissionType,
)


class BaseModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    model = models.CharField(max_length=255)
    make = models.ForeignKey("Make", on_delete=models.CASCADE, related_name="models")
    platform = models.ForeignKey(
        "Platform",
        on_delete=models.CASCADE,
        related_name="base_models",
        null=True,
        blank=True,
    )
    body_style = models.CharField(
        max_length=255,
        choices=BodyStyle.choices,
        null=True,
        blank=True,
    )
    generation = models.CharField(max_length=255, null=True, blank=True)
    year = models.IntegerField()
    objects = ParadeDBManager()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            BM25Index(
                fields={
                    "generation": {"tokenizer": Tokenizer.unicode_words()},
                    "id": {},
                    "model": {"tokenizer": Tokenizer.unicode_words()},
                },
                key_field="id",
                name="base_model_search_idx",
            ),
        ]

    def __str__(self):
        return f"{self.make.name} {self.model} {self.year}"


class SafetyRatingMetrics(models.Model):
    overall_stars = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(5)]
    )
    adult_occupant_protection = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    child_occupant_protection = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    vulnerable_road_user_protection = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    safety_assist = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )

    class Meta:
        abstract = True


class ModelSafetyRating(SafetyRatingMetrics):
    model = models.ForeignKey(
        BaseModel,
        on_delete=models.CASCADE,
        related_name="safety_ratings",
    )
    program = models.CharField(
        max_length=32,
        choices=SafetyRatingProgram.choices,
        default=SafetyRatingProgram.LATIN_NCAP,
    )
    assessment_year = models.PositiveSmallIntegerField()
    source_url = models.URLField(blank=True)

    class Meta:
        ordering = ("-assessment_year", "program")
        constraints = [
            models.UniqueConstraint(
                fields=("model", "program", "assessment_year"),
                name="unique_model_safety_rating_program_year",
            )
        ]


class ImageAsset(models.Model):
    file = models.ImageField(upload_to="catalog/images/%Y/%m/")
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    credit = models.CharField(max_length=255, blank=True)
    license = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return self.title


class ModelImagePlacement(models.Model):
    class View(models.TextChoices):
        LEFT_SIDE = "left_side", "Left side"
        RIGHT_SIDE = "right_side", "Right side"
        FRONT = "front", "Front"
        REAR = "rear", "Rear"
        SILHOUETTE = "silhouette", "Silhouette"

    base_model = models.ForeignKey(
        BaseModel,
        on_delete=models.CASCADE,
        related_name="image_placements",
    )
    image = models.ForeignKey(
        ImageAsset,
        on_delete=models.PROTECT,
        related_name="model_placements",
    )
    view = models.CharField(max_length=20, choices=View.choices)
    alt_text = models.CharField(max_length=255, blank=True)
    sort_order = models.PositiveIntegerField(default=0)
    is_visible = models.BooleanField(default=True)

    class Meta:
        ordering = ("sort_order", "id")
        constraints = [
            models.UniqueConstraint(
                fields=("base_model", "view"),
                name="unique_base_model_image_view",
            )
        ]


class Make(models.Model):
    makeId = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    website = models.URLField(blank=True)
    phone = models.CharField(max_length=50, blank=True)
    legal_representative = models.CharField(max_length=255, blank=True)
    icon_svg = models.FileField(
        upload_to="catalog/make-icons/",
        blank=True,
        validators=[FileExtensionValidator(["svg"])],
    )
    country = CountryField(null=True, blank=True)
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
    groupId = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    country = CountryField(null=True, blank=True)

    def __str__(self):
        return self.name


class Platform(models.Model):
    platformId = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    groups = models.ManyToManyField(Group, related_name="platforms")

    def __str__(self):
        return self.name


class Engine(models.Model):
    engineId = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    maker = models.ForeignKey(Make, on_delete=models.CASCADE, related_name="engines")
    energy_source = models.CharField(
        max_length=255,
        choices=FuelType.choices,
    )
    displacement_cc = models.PositiveIntegerField(null=True, blank=True)
    power_kW = models.FloatField(null=True, blank=True)
    cylinder_count = models.PositiveIntegerField(null=True, blank=True)
    aspiration = models.CharField(
        max_length=255,
        choices=EngineAspiration.choices,
        null=True,
        blank=True,
    )
    layout = models.CharField(
        max_length=255,
        choices=EngineLayout.choices,
        null=True,
        blank=True,
    )

    def __str__(self):
        return self.name


class BatteryPack(models.Model):
    batteryPackId = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False
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
    chemistry = models.CharField(
        max_length=255,
        choices=BatteryChemistry.choices,
        null=True,
        blank=True,
    )
    capacity_kWh = models.FloatField()
    gross_capacity_kWh = models.FloatField(null=True, blank=True)
    usable_capacity_kWh = models.FloatField(null=True, blank=True)
    voltage_V = models.FloatField()
    weight_kg = models.FloatField()

    def __str__(self):
        return self.name


class FuelTank(models.Model):
    fuelTankId = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    maker = models.ForeignKey(Make, on_delete=models.CASCADE, related_name="fuel_tanks")
    fuel_type = models.CharField(max_length=255, choices=FuelType.choices)
    capacity_L = models.FloatField()

    def __str__(self):
        return self.name


class EMotor(models.Model):
    eMotorId = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    maker = models.ForeignKey(Make, on_delete=models.CASCADE, related_name="e_motors")
    motor_type = models.CharField(
        max_length=255,
        choices=ElectricMotorType.choices,
        null=True,
        blank=True,
    )
    power_kW = models.FloatField()
    torque_Nm = models.FloatField()
    cooling_type = models.CharField(
        max_length=255,
        choices=MotorCoolingType.choices,
        null=True,
        blank=True,
    )

    def __str__(self):
        return self.name


class Transmission(models.Model):
    transmissionId = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False
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
    powerTrainId = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    make = models.ForeignKey(Make, on_delete=models.CASCADE, related_name="powertrains")
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
    is_primary = models.BooleanField(default=False)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["powertrain", "fuel_tank"],
                name="unique_powertrain_fuel_tank",
            )
        ]


class Vehicle(models.Model):
    class PriceCurrency(models.TextChoices):
        USD = "USD", "Dólares estadounidenses"
        MXN = "MXN", "Pesos mexicanos"

    model = models.ForeignKey(
        BaseModel, on_delete=models.CASCADE, related_name="model_vehicles"
    )
    variant_name = models.CharField(max_length=255, null=True, blank=True)
    assembly_country = CountryField(null=True, blank=True)
    price_amount = models.DecimalField(
        max_digits=12, decimal_places=2, null=True, blank=True
    )
    price_currency = models.CharField(
        max_length=3,
        choices=PriceCurrency.choices,
        blank=True,
    )
    powertrain = models.ForeignKey(
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
    length_mm = models.FloatField(null=True, blank=True)
    width_mm = models.FloatField(null=True, blank=True)
    height_mm = models.FloatField(null=True, blank=True)
    wheelbase_mm = models.FloatField(null=True, blank=True)
    curb_weight_kg = models.FloatField(null=True, blank=True)
    door_count = models.PositiveIntegerField(null=True, blank=True)
    passenger_capacity = models.PositiveIntegerField(null=True, blank=True)
    objects = ParadeDBManager()

    class Meta:
        indexes = [
            BM25Index(
                fields={
                    "id": {},
                    "variant_name": {"tokenizer": Tokenizer.unicode_words()},
                },
                key_field="id",
                name="vehicle_search_idx",
            ),
        ]

    def __str__(self):
        details = [str(self.model)]
        if self.powertrain:
            details.append(self.powertrain.name)
        return " - ".join(details)


class VehicleMonthlySales(models.Model):
    class Month(models.IntegerChoices):
        JANUARY = 1, "Enero"
        FEBRUARY = 2, "Febrero"
        MARCH = 3, "Marzo"
        APRIL = 4, "Abril"
        MAY = 5, "Mayo"
        JUNE = 6, "Junio"
        JULY = 7, "Julio"
        AUGUST = 8, "Agosto"
        SEPTEMBER = 9, "Septiembre"
        OCTOBER = 10, "Octubre"
        NOVEMBER = 11, "Noviembre"
        DECEMBER = 12, "Diciembre"

    vehicle = models.ForeignKey(
        Vehicle,
        on_delete=models.CASCADE,
        related_name="monthly_sales",
    )
    month = models.PositiveSmallIntegerField(choices=Month.choices)
    year = models.PositiveIntegerField()
    units_sold = models.PositiveIntegerField()

    class Meta:
        ordering = ("year", "month")
        constraints = [
            models.UniqueConstraint(
                fields=("vehicle", "year", "month"),
                name="unique_vehicle_monthly_sales_year_month",
            )
        ]


class Recall(models.Model):
    class Status(models.TextChoices):
        OPEN = "open", "Open"
        RESOLVED = "resolved", "Resolved"

    maker = models.ForeignKey(
        Make,
        on_delete=models.CASCADE,
        related_name="recalls",
    )
    affected_models = models.ManyToManyField(BaseModel, related_name="recalls")
    recall_number = models.CharField(max_length=100)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    risk = models.TextField(blank=True)
    risk_consequence = models.TextField(blank=True)
    countermeasure = models.TextField(blank=True)
    actions = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.OPEN)
    published_date = models.DateField(null=True, blank=True)
    total_units_affected = models.PositiveIntegerField(null=True, blank=True)
    source_url = models.URLField(blank=True)
    damage_report = models.TextField(blank=True)

    class Meta:
        ordering = ("-published_date", "id")
        constraints = [
            models.UniqueConstraint(
                fields=("maker", "recall_number"),
                name="unique_recall_reference",
            )
        ]


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
    restraints_airbagSideFront = models.PositiveIntegerField(null=True, blank=True)
    restraints_airbagSideRear = models.PositiveIntegerField(null=True, blank=True)
    restraints_headProtectionAirbag = models.PositiveIntegerField(
        null=True, blank=True
    )

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
    source_url = models.URLField(null=True, blank=True)
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
    criteria = models.CharField(max_length=255, choices=EmissionsMetric.choices)
    cycle = models.CharField(
        max_length=255, choices=TestCycle.choices, null=True, blank=True
    )
    scope = models.CharField(
        max_length=255, choices=ResultScope.choices, null=True, blank=True
    )
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
