import uuid
from pathlib import Path

from django.core.exceptions import ValidationError
from django.core.validators import (
    FileExtensionValidator,
    MaxValueValidator,
    MinValueValidator,
)
from django.db import models
from django.utils.text import slugify
from django_countries.fields import CountryField
from paradedb.indexes import ParadeDBIndex
from paradedb.queryset import ParadeDBManager
from paradedb.search import Tokenizer

from catalog.types import (
    AccelerationMetric,
    ApprovalDomain,
    ApprovalStatus,
    BatteryChemistry,
    BrakeType,
    BodyStyle,
    ChargingConnector,
    ChargingCurrentType,
    ChargingPortLocation,
    ChargingSupplyContext,
    ComplianceCategory,
    CompressorType,
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
    SuspensionType,
    TestCycle,
    TorqueMetric,
    TorqueUnit,
    TractionPosition,
    TransmissionType,
)


class ModelGeneration(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    model = models.CharField(max_length=255)
    make = models.ForeignKey(
        "Make", on_delete=models.CASCADE, related_name="model_generations"
    )
    platform = models.ForeignKey(
        "Platform",
        on_delete=models.CASCADE,
        related_name="model_generations",
        null=True,
        blank=True,
    )
    generation_prefix = models.CharField(
        max_length=32, null=True, blank=True, default="Gen"
    )
    generation_number = models.PositiveSmallIntegerField(null=True, blank=True)
    objects = ParadeDBManager()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            ParadeDBIndex(
                fields={
                    "generation_prefix": {"tokenizer": Tokenizer.unicode_words()},
                    "id": {},
                    "model": {"tokenizer": Tokenizer.unicode_words()},
                },
                key_field="id",
                name="model_generation_search_idx",
            ),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=("make", "model", "generation_prefix", "generation_number"),
                name="unique_model_generation_identifier",
            )
        ]

    def __str__(self):
        generation = f" {self.generation}" if self.generation else ""
        return f"{self.make.name} {self.model}{generation}".strip()

    def save(self, *args, **kwargs):
        self.generation_prefix = self.generation_prefix or "Gen"
        super().save(*args, **kwargs)

    @property
    def generation(self):
        parts = [self.generation_prefix or "Gen", self.generation_number]
        return "".join(str(part) for part in parts if part is not None) or None


class BaseModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    model_generation = models.ForeignKey(
        ModelGeneration,
        on_delete=models.CASCADE,
        related_name="model_years",
    )
    body_style = models.CharField(
        max_length=255,
        choices=BodyStyle.choices,
        null=True,
        blank=True,
    )
    year = models.IntegerField()
    objects = ParadeDBManager()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(
                fields=("body_style", "model_generation", "year"),
                name="basemodel_body_gen_year_idx",
            ),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=("model_generation", "year", "body_style"),
                name="unique_model_year_body_style",
                condition=models.Q(body_style__isnull=False),
            )
        ]

    def __str__(self):
        body_style = f" {self.get_body_style_display()}" if self.body_style else ""
        return f"{self.model_generation} {self.year}{body_style}".strip()


class BaseModelWarranty(models.Model):
    base_model = models.OneToOneField(
        BaseModel, on_delete=models.CASCADE, related_name="warranty"
    )
    basic_years = models.PositiveSmallIntegerField(null=True, blank=True)
    basic_kilometers = models.PositiveIntegerField(null=True, blank=True)
    basic_kilometers_unlimited = models.BooleanField(default=False)
    drivetrain_years = models.PositiveSmallIntegerField(null=True, blank=True)
    drivetrain_kilometers = models.PositiveIntegerField(null=True, blank=True)
    drivetrain_kilometers_unlimited = models.BooleanField(default=False)
    corrosion_years = models.PositiveSmallIntegerField(null=True, blank=True)
    corrosion_kilometers = models.PositiveIntegerField(null=True, blank=True)
    corrosion_kilometers_unlimited = models.BooleanField(default=False)

    def clean(self):
        errors = {}
        for name in ("basic", "drivetrain", "corrosion"):
            kilometers = getattr(self, f"{name}_kilometers")
            unlimited = getattr(self, f"{name}_kilometers_unlimited")
            if kilometers is not None and unlimited:
                errors[f"{name}_kilometers_unlimited"] = (
                    "Enter a kilometre limit or mark it unlimited, not both."
                )
        if errors:
            raise ValidationError(errors)

    def __str__(self):
        return f"Warranty for {self.base_model}"


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


def model_image_upload_to(instance, filename):
    base_model = getattr(instance, "_base_model", None)
    if base_model is None:
        raise ValueError("Model images must be uploaded from a model placement.")

    model_generation = base_model.model_generation
    make_slug = slugify(model_generation.make.name) or "unknown-make"
    model_slug = slugify(model_generation.model) or "unknown-model"
    extension = Path(filename).suffix.lower()
    return (
        f"catalog/images/{make_slug}/{model_slug}/"
        f"{uuid.uuid4().hex}{extension}"
    )


class ImageAsset(models.Model):
    file = models.ImageField(upload_to=model_image_upload_to)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    credit = models.CharField(max_length=255, blank=True)
    license = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return self.title


class ModelImagePlacement(models.Model):
    class View(models.TextChoices):
        FRONT = "front", "Front"
        REAR = "rear", "Rear"
        LEFT_SIDE = "left_side", "Left side"
        RIGHT_SIDE = "right_side", "Right side"
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
        ordering = (
            models.Case(
                models.When(view="front", then=models.Value(0)),
                models.When(view="rear", then=models.Value(1)),
                models.When(view="left_side", then=models.Value(2)),
                models.When(view="right_side", then=models.Value(3)),
                default=models.Value(4),
                output_field=models.IntegerField(),
            ),
            "id",
        )
        constraints = [
            models.UniqueConstraint(
                fields=("base_model", "view"),
                name="unique_base_model_image_view",
            )
        ]


class Make(models.Model):
    makeId = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True)
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
    slug = models.SlugField(max_length=255, unique=True)
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

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
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
    trunk_capacity_liters = models.FloatField(null=True, blank=True)
    cargo_floor_width_between_wheel_houses_mm = models.FloatField(
        null=True, blank=True
    )
    front_cargo_capacity_liters = models.FloatField(null=True, blank=True)
    max_cargo_capacity_seats_folded_liters = models.FloatField(
        null=True, blank=True
    )
    door_count = models.PositiveIntegerField(null=True, blank=True)
    passenger_capacity = models.PositiveIntegerField(null=True, blank=True)
    front_brakes = models.CharField(
        max_length=32, choices=BrakeType.choices, blank=True
    )
    rear_brakes = models.CharField(
        max_length=32, choices=BrakeType.choices, blank=True
    )
    front_suspension = models.CharField(
        max_length=32, choices=SuspensionType.choices, blank=True
    )
    rear_suspension = models.CharField(
        max_length=32, choices=SuspensionType.choices, blank=True
    )
    front_tire_width_mm = models.PositiveSmallIntegerField(null=True, blank=True)
    front_tire_aspect_ratio = models.PositiveSmallIntegerField(
        null=True, blank=True, validators=[MaxValueValidator(100)]
    )
    front_rim_diameter_inches = models.PositiveSmallIntegerField(
        null=True, blank=True
    )
    rear_tire_width_mm = models.PositiveSmallIntegerField(null=True, blank=True)
    rear_tire_aspect_ratio = models.PositiveSmallIntegerField(
        null=True, blank=True, validators=[MaxValueValidator(100)]
    )
    rear_rim_diameter_inches = models.PositiveSmallIntegerField(
        null=True, blank=True
    )
    objects = ParadeDBManager()

    class Meta:
        indexes = [
            ParadeDBIndex(
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

    def clean(self):
        super().clean()
        for axle in ("front", "rear"):
            fields = (
                f"{axle}_tire_width_mm",
                f"{axle}_tire_aspect_ratio",
                f"{axle}_rim_diameter_inches",
            )
            populated = [getattr(self, field) is not None for field in fields]
            if any(populated) and not all(populated):
                raise ValidationError(
                    {
                        field: "La medida de llanta requiere ancho, perfil y diámetro."
                        for field in fields
                    }
                )


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
    name = models.CharField(max_length=255)
    group = models.ForeignKey(
        Group,
        on_delete=models.CASCADE,
        related_name="safety_packages",
        null=True,
        blank=True,
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
        return self.name


class VehicleSafetyPackage(models.Model):
    vehicle = models.OneToOneField(
        Vehicle,
        on_delete=models.CASCADE,
        related_name="safety_package_assignment",
    )
    safety_package = models.ForeignKey(
        SafetyPackage,
        on_delete=models.CASCADE,
        related_name="vehicle_assignments",
    )

    def __str__(self):
        return f"{self.vehicle}: {self.safety_package}"


class ChargingPackage(models.Model):
    name = models.CharField(max_length=255)
    group = models.ForeignKey(
        Group,
        on_delete=models.CASCADE,
        related_name="charging_packages",
        null=True,
        blank=True,
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
        return self.name


class ClimatePackage(models.Model):
    climatePackageId = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False
    )
    name = models.CharField(max_length=255)
    group = models.ForeignKey(
        Group,
        on_delete=models.CASCADE,
        related_name="climate_packages",
        null=True,
        blank=True,
    )
    zone_count = models.PositiveSmallIntegerField(
        "Climate zones", null=True, blank=True
    )
    automatic_climate_control = models.BooleanField(null=True, blank=True)
    rear_climate_control = models.BooleanField(null=True, blank=True)
    cabin_air_filter = models.BooleanField(null=True, blank=True)
    air_purification_system = models.BooleanField(null=True, blank=True)
    remote_preconditioning = models.BooleanField(null=True, blank=True)
    heat_pump = models.BooleanField(null=True, blank=True)
    heated_front_seats = models.BooleanField(null=True, blank=True)
    heated_rear_seats = models.BooleanField(null=True, blank=True)
    heated_steering_wheel = models.BooleanField(null=True, blank=True)
    refrigerant_type = models.CharField(
        "Refrigerant type", max_length=64, null=True, blank=True
    )
    refrigerant_gwp = models.FloatField(
        "Refrigerant GWP (CO2e/kg)", null=True, blank=True
    )
    compressor_type = models.CharField(
        "Compressor type",
        max_length=32,
        choices=CompressorType.choices,
        null=True,
        blank=True,
    )
    cooling_capacity_kw = models.FloatField(
        "Cooling capacity (kW thermal)", null=True, blank=True
    )
    cooling_power_draw_kw = models.FloatField(
        "Cooling power draw (kW electric)", null=True, blank=True
    )
    cooling_cop = models.FloatField(
        "Cooling COP (kW thermal/kW electric)", null=True, blank=True
    )
    refrigerant_charge_g = models.FloatField(
        "Refrigerant charge (g)", null=True, blank=True
    )

    def __str__(self):
        return self.name


class VehicleClimatePackage(models.Model):
    vehicle = models.OneToOneField(
        Vehicle,
        on_delete=models.CASCADE,
        related_name="climate_package_assignment",
    )
    climate_package = models.ForeignKey(
        ClimatePackage,
        on_delete=models.CASCADE,
        related_name="vehicle_assignments",
    )

    def __str__(self):
        return f"{self.vehicle}: {self.climate_package}"


class VehicleChargingPackage(models.Model):
    vehicle = models.OneToOneField(
        Vehicle,
        on_delete=models.CASCADE,
        related_name="charging_package_assignment",
    )
    charging_package = models.ForeignKey(
        ChargingPackage,
        on_delete=models.CASCADE,
        related_name="vehicle_assignments",
    )

    def __str__(self):
        return f"{self.vehicle}: {self.charging_package}"


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
