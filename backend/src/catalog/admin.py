from pathlib import Path

from django import forms
from django.contrib import admin
from django.core.exceptions import ValidationError
from django.db.models import Q
from django.forms.models import BaseInlineFormSet
from django.urls import reverse
from django.utils.html import format_html, format_html_join
from unfold.admin import ModelAdmin

from .models import (
    AccelerationResult,
    ApprovalSourceDocument,
    BaseModel,
    BaseModelWarranty,
    BatteryPack,
    ChargeTimeResult,
    ChargingPackage,
    ChargingPort,
    ClimatePackage,
    ComplianceRecord,
    EfficiencyResult,
    EmissionsResult,
    EMotor,
    Engine,
    FuelTank,
    Group,
    ImageAsset,
    Make,
    ModelImagePlacement,
    ModelGeneration,
    ModelSafetyRating,
    Platform,
    PowerTrain,
    PowerTrainBatteryPack,
    PowerTrainEMotor,
    PowerTrainEngine,
    PowerTrainFuelTank,
    RangeResult,
    Recall,
    RegulatoryApproval,
    SafetyPackage,
    TopSpeedResult,
    Transmission,
    Vehicle,
    VehicleChargingPackage,
    VehicleClimatePackage,
    VehicleMonthlySales,
    VehicleSafetyPackage,
)
from .types import PowerTrainArchitecture

SAFETY_FEATURE_DESCRIPTIONS = {
    "name": "Name used to identify this reusable safety package.",
    "group": "Corporate group that owns or supplies this safety package.",
    "collisionWarnings_fcw": "Forward collision warning alerts the driver to a possible frontal collision.",
    "collisionWarnings_ldw": "Lane departure warning alerts when the vehicle leaves its lane unintentionally.",
    "collisionWarnings_bsw": "Blind spot warning detects vehicles in adjacent lanes that may be hard to see.",
    "collisionWarnings_rctw": "Rear cross-traffic warning alerts of approaching traffic while reversing.",
    "collisionIntervention_aebCity": "Automatic emergency braking tuned for lower-speed urban driving.",
    "collisionIntervention_aebPedestrian": "Automatic emergency braking with pedestrian detection.",
    "collisionIntervention_aebHighway": "Automatic emergency braking designed for higher-speed driving.",
    "collisionIntervention_aebRear": "Rear automatic emergency braking helps avoid obstacles while backing up.",
    "drivingControlAssistance_lka": "Lane keeping assist applies steering support to keep the vehicle in lane.",
    "drivingControlAssistance_lca": "Lane centering assist helps keep the vehicle centered within the lane.",
    "drivingControlAssistance_acc": "Adaptive cruise control adjusts speed to maintain distance from traffic ahead.",
    "drivingControlAssistance_activeDrivingAssistanceDirectDriverMonitoring": "Driver monitoring checks driver attention during assisted driving.",
    "rearSeatSafety_childSafety": "Rear-seat child safety features such as child locks or child-seat support.",
    "rearSeatSafety_rearOccupantAlertEndOfTripReminder": "Rear occupant alert reminds the driver to check the back seats after a trip.",
    "visibilityAndControl_drl": "Daytime running lights improve vehicle visibility during the day.",
    "visibilityAndControl_rearViewCamera": "Rear-view camera shows the area behind the vehicle while reversing.",
    "visibilityAndControl_esc": "Electronic stability control helps maintain control during skids or evasive maneuvers.",
    "visibilityAndControl_tractionControl": "Traction control reduces wheel slip under acceleration.",
    "visibilityAndControl_abs": "Anti-lock braking system helps prevent wheel lock during hard braking.",
    "restraints_airbagSideFront": "Front side airbags protect the torso of front occupants in side impacts.",
    "restraints_airbagSideRear": "Rear side airbags protect rear occupants in side impacts.",
    "restraints_headProtectionAirbag": "Head protection airbags, often curtain airbags, help protect occupants' heads in side impacts or rollovers.",
}

CHARGING_PACKAGE_FIELD_DESCRIPTIONS = {
    "name": "Name used to identify this reusable charging package.",
    "group": "Corporate group that owns or supplies this charging package.",
    "ac_max_power_kw": "Maximum alternating-current (AC) charging power, in kilowatts.",
    "ac_max_voltage_v": "Maximum alternating-current (AC) charging voltage, in volts.",
    "ac_max_current_a": "Maximum alternating-current (AC) charging current, in amperes.",
    "ac_phases": "Number of electrical phases supported for alternating-current (AC) charging.",
    "dc_max_power_kw": "Maximum direct-current (DC) charging power, in kilowatts.",
    "dc_max_voltage_v": "Maximum direct-current (DC) charging voltage, in volts.",
    "dc_max_current_a": "Maximum direct-current (DC) charging current, in amperes.",
    "v2l": "Allows the vehicle battery to power external devices (Vehicle-to-Load).",
    "v2h": "Allows the vehicle battery to power a home (Vehicle-to-Home).",
    "v2g": "Allows the vehicle battery to send power back to the electrical grid (Vehicle-to-Grid).",
}

CLIMATE_PACKAGE_FIELD_DESCRIPTIONS = {
    "name": "Name used to identify this reusable climate package.",
    "group": "Corporate group that owns or supplies this climate package.",
    "zone_count": "Number of independently controlled climate zones.",
    "automatic_climate_control": "Automatically regulates cabin temperature and airflow.",
    "rear_climate_control": "Provides a dedicated climate control zone for rear passengers.",
    "cabin_air_filter": "Filters dust, pollen, and other particles from incoming cabin air.",
    "air_purification_system": "Actively improves cabin air quality beyond a standard filter.",
    "remote_preconditioning": "Preconditions the cabin before occupants enter the vehicle.",
    "heat_pump": "Uses a heat pump to warm or cool the cabin efficiently.",
    "heated_front_seats": "Provides heating for the front seats.",
    "heated_rear_seats": "Provides heating for the rear seats.",
    "heated_steering_wheel": "Provides heating for the steering wheel.",
    "refrigerant_type": "Refrigerant used by the air-conditioning system.",
    "refrigerant_gwp": "100-year global warming potential, in kilograms of CO2e per kilogram of refrigerant.",
    "compressor_type": "Air-conditioning compressor technology, such as fixed or variable displacement.",
    "cooling_capacity_kw": "Nominal cabin cooling capacity, in kilowatts of thermal output.",
    "cooling_power_draw_kw": "Nominal electrical power required while cooling, in kilowatts.",
    "cooling_cop": "Coefficient of performance, in kilowatts thermal per kilowatt electric.",
    "refrigerant_charge_g": "Refrigerant charge, in grams.",
}

ENGINE_FIELD_DESCRIPTIONS = {
    "name": "Manufacturer or model name used to identify this engine.",
    "maker": "Vehicle manufacturer that produces or supplies this engine.",
    "energy_source": "Fuel or energy source used by the engine.",
    "displacement_cc": "Total cylinder displacement, in cubic centimetres (cc).",
    "power_kW": "Maximum engine power output, in kilowatts (kW).",
    "cylinder_count": "Number of cylinders in the engine.",
    "aspiration": "Method used to supply air to the engine, such as naturally aspirated or turbocharged.",
    "layout": "Physical arrangement of the engine cylinders, such as inline, V, or boxer.",
}

E_MOTOR_FIELD_DESCRIPTIONS = {
    "name": "Manufacturer or model name used to identify this electric motor.",
    "maker": "Vehicle manufacturer that produces or supplies this electric motor.",
    "motor_type": "Electric motor technology, such as permanent-magnet synchronous or induction.",
    "power_kW": "Maximum electric motor power output, in kilowatts (kW).",
    "torque_Nm": "Maximum electric motor torque, in newton-metres (Nm).",
    "cooling_type": "Method used to cool the electric motor.",
}

BATTERY_PACK_FIELD_DESCRIPTIONS = {
    "name": "Manufacturer or model name used to identify this battery pack.",
    "group": "Corporate group that owns or supplies this battery pack.",
    "provider": "Company that manufactures or supplies the battery cells or pack.",
    "chemistry": "Electrochemical cell chemistry used by the battery pack.",
    "capacity_kWh": "Nominal total energy capacity, in kilowatt-hours (kWh).",
    "gross_capacity_kWh": "Total energy capacity before the manufacturer reserve buffer, in kilowatt-hours (kWh).",
    "usable_capacity_kWh": "Energy capacity available to power the vehicle, in kilowatt-hours (kWh).",
    "voltage_V": "Nominal battery pack voltage, in volts (V).",
    "weight_kg": "Battery pack weight, in kilograms (kg).",
}

POWERTRAIN_FIELD_DESCRIPTIONS = {
    "name": "Manufacturer or model name used to identify this powertrain.",
    "make": "Vehicle manufacturer associated with this powertrain.",
    "architecture": "Powertrain configuration, such as internal combustion, hybrid, plug-in hybrid, or battery electric.",
}

CHARGING_PORT_FIELD_DESCRIPTIONS = {
    "vehicle": "Vehicle configuration that uses this charging port.",
    "current_type": "Type of electrical current supported by the port: AC, DC, or both.",
    "connector": "Physical charging connector standard fitted to the port.",
    "location": "Physical location of the charging port on the vehicle body.",
}


class SafetyPackageAdminForm(forms.ModelForm):
    class Meta:
        model = SafetyPackage
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, description in SAFETY_FEATURE_DESCRIPTIONS.items():
            if field_name in self.fields:
                self.fields[field_name].help_text = description


class ChargingPackageAdminForm(forms.ModelForm):
    class Meta:
        model = ChargingPackage
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, description in CHARGING_PACKAGE_FIELD_DESCRIPTIONS.items():
            if field_name in self.fields:
                self.fields[field_name].help_text = description


class ClimatePackageAdminForm(forms.ModelForm):
    class Meta:
        model = ClimatePackage
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, description in CLIMATE_PACKAGE_FIELD_DESCRIPTIONS.items():
            if field_name in self.fields:
                self.fields[field_name].help_text = description


class EngineAdminForm(forms.ModelForm):
    class Meta:
        model = Engine
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, description in ENGINE_FIELD_DESCRIPTIONS.items():
            if field_name in self.fields:
                self.fields[field_name].help_text = description


class EMotorAdminForm(forms.ModelForm):
    class Meta:
        model = EMotor
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, description in E_MOTOR_FIELD_DESCRIPTIONS.items():
            if field_name in self.fields:
                self.fields[field_name].help_text = description


class BatteryPackAdminForm(forms.ModelForm):
    class Meta:
        model = BatteryPack
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, description in BATTERY_PACK_FIELD_DESCRIPTIONS.items():
            if field_name in self.fields:
                self.fields[field_name].help_text = description


class PowerTrainAdminForm(forms.ModelForm):
    class Meta:
        model = PowerTrain
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, description in POWERTRAIN_FIELD_DESCRIPTIONS.items():
            if field_name in self.fields:
                self.fields[field_name].help_text = description


class ChargingPortAdminForm(forms.ModelForm):
    class Meta:
        model = ChargingPort
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, description in CHARGING_PORT_FIELD_DESCRIPTIONS.items():
            if field_name in self.fields:
                self.fields[field_name].help_text = description


class GroupScopedAdminMixin:
    group_paths = ()
    foreignkey_group_paths = {}
    manytomany_group_paths = {}
    owner_group_field = None

    def get_allowed_groups(self, request):
        if request.user.is_superuser:
            return Group.objects.all()
        return request.user.catalog_groups.all()

    def _get_single_allowed_group(self, request):
        allowed_groups = self.get_allowed_groups(request)
        if allowed_groups.count() != 1:
            return None
        return allowed_groups.first()

    def _filter_by_group_paths(self, queryset, allowed_groups, group_paths):
        if not group_paths:
            return queryset.none()

        query = Q()
        for group_path in group_paths:
            if group_path == "self":
                query |= Q(pk__in=allowed_groups.values("pk"))
            else:
                query |= Q(**{f"{group_path}__in": allowed_groups})
        return queryset.filter(query).distinct()

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        if request.user.is_superuser:
            return queryset
        return self._filter_by_group_paths(
            queryset, self.get_allowed_groups(request), self.group_paths
        )

    def _has_object_permission(self, request, obj):
        if request.user.is_superuser:
            return True
        return self.get_queryset(request).filter(pk=obj.pk).exists()

    def has_view_permission(self, request, obj=None):
        allowed = super().has_view_permission(request, obj)
        if not allowed or obj is None:
            return allowed
        return self._has_object_permission(request, obj)

    def has_change_permission(self, request, obj=None):
        allowed = super().has_change_permission(request, obj)
        if not allowed or obj is None:
            return allowed
        return self._has_object_permission(request, obj)

    def has_delete_permission(self, request, obj=None):
        allowed = super().has_delete_permission(request, obj)
        if not allowed or obj is None:
            return allowed
        return self._has_object_permission(request, obj)

    def has_module_permission(self, request):
        allowed = super().has_module_permission(request)
        if not allowed or request.user.is_superuser:
            return allowed
        return self.get_queryset(request).exists()

    def has_add_permission(self, request):
        allowed = super().has_add_permission(request)
        if not allowed or request.user.is_superuser:
            return allowed
        return self.get_allowed_groups(request).exists()

    def _filter_related_queryset(self, request, queryset, group_path):
        if request.user.is_superuser:
            return queryset
        return self._filter_by_group_paths(
            queryset, self.get_allowed_groups(request), (group_path,)
        )

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        group_path = self.foreignkey_group_paths.get(db_field.name)
        if group_path and not request.user.is_superuser:
            kwargs["queryset"] = self._filter_related_queryset(
                request, db_field.remote_field.model.objects.all(), group_path
            )
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        group_path = self.manytomany_group_paths.get(db_field.name)
        if group_path and not request.user.is_superuser:
            kwargs["queryset"] = self._filter_related_queryset(
                request, db_field.remote_field.model.objects.all(), group_path
            )
        return super().formfield_for_manytomany(db_field, request, **kwargs)

    def get_exclude(self, request, obj=None):
        exclude = list(super().get_exclude(request, obj) or [])
        if (
            self.owner_group_field
            and not request.user.is_superuser
            and self._get_single_allowed_group(request) is not None
        ):
            exclude.append(self.owner_group_field)
        return tuple(dict.fromkeys(exclude))

    def save_model(self, request, obj, form, change):
        if self.owner_group_field and not request.user.is_superuser:
            owner_group = self._get_single_allowed_group(request)
            if (
                owner_group is not None
                and getattr(obj, f"{self.owner_group_field}_id") is None
            ):
                setattr(obj, self.owner_group_field, owner_group)
        super().save_model(request, obj, form, change)


class GroupScopedInlineMixin:
    foreignkey_group_paths = {}

    def get_allowed_groups(self, request):
        if request.user.is_superuser:
            return Group.objects.all()
        return request.user.catalog_groups.all()

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        group_path = self.foreignkey_group_paths.get(db_field.name)
        if group_path and not request.user.is_superuser:
            queryset = db_field.remote_field.model.objects.all()
            if group_path == "self":
                queryset = queryset.filter(pk__in=self.get_allowed_groups(request))
            else:
                queryset = queryset.filter(
                    **{f"{group_path}__in": self.get_allowed_groups(request)}
                ).distinct()
            kwargs["queryset"] = queryset
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


class PowerTrainEngineInline(GroupScopedInlineMixin, admin.TabularInline):
    model = PowerTrainEngine
    extra = 0
    foreignkey_group_paths = {"engine": "maker__group"}


class PowerTrainEMotorInline(GroupScopedInlineMixin, admin.TabularInline):
    model = PowerTrainEMotor
    extra = 0
    foreignkey_group_paths = {"e_motor": "maker__group"}


class PowerTrainBatteryPackInline(GroupScopedInlineMixin, admin.TabularInline):
    model = PowerTrainBatteryPack
    extra = 0
    foreignkey_group_paths = {"battery_pack": "group"}


class PowerTrainFuelTankInline(GroupScopedInlineMixin, admin.TabularInline):
    model = PowerTrainFuelTank
    extra = 0
    foreignkey_group_paths = {"fuel_tank": "maker__group"}


class VehicleSafetyPackageInline(GroupScopedInlineMixin, admin.StackedInline):
    model = VehicleSafetyPackage
    extra = 0
    max_num = 1
    autocomplete_fields = ("safety_package",)
    foreignkey_group_paths = {"safety_package": "group"}


class ModelSafetyRatingInline(admin.StackedInline):
    model = ModelSafetyRating
    extra = 0


class VehicleClimatePackageInline(GroupScopedInlineMixin, admin.StackedInline):
    model = VehicleClimatePackage
    extra = 0
    max_num = 1
    autocomplete_fields = ("climate_package",)
    foreignkey_group_paths = {"climate_package": "group"}


class VehicleChargingPackageInline(GroupScopedInlineMixin, admin.StackedInline):
    model = VehicleChargingPackage
    extra = 0
    max_num = 1
    autocomplete_fields = ("charging_package",)
    foreignkey_group_paths = {"charging_package": "group"}


class ChargingPortInline(admin.TabularInline):
    model = ChargingPort
    extra = 0


class ChargeTimeResultInline(admin.TabularInline):
    model = ChargeTimeResult
    extra = 0


class ComplianceRecordInline(admin.TabularInline):
    model = ComplianceRecord
    extra = 0


class RegulatoryApprovalInline(admin.TabularInline):
    model = RegulatoryApproval
    extra = 0


class ApprovalSourceDocumentInline(admin.TabularInline):
    model = ApprovalSourceDocument
    extra = 0


class EfficiencyResultInline(admin.TabularInline):
    model = EfficiencyResult
    extra = 0


class RangeResultInline(admin.TabularInline):
    model = RangeResult
    extra = 0


class EmissionsResultInline(admin.TabularInline):
    model = EmissionsResult
    extra = 0


class AccelerationResultInline(admin.TabularInline):
    model = AccelerationResult
    extra = 0


class TopSpeedResultInline(admin.TabularInline):
    model = TopSpeedResult
    extra = 0


class ImagePlacementFileInput(forms.FileInput):
    def render(self, name, value, attrs=None, renderer=None):
        file_input = super().render(name, value, attrs, renderer)
        return format_html(
            '{}<input type="text" hidden aria-hidden="true" tabindex="-1">',
            file_input,
        )


class ModelImagePlacementInlineForm(forms.ModelForm):
    image_file = forms.ImageField(
        label="Upload image", required=False, widget=ImagePlacementFileInput
    )

    class Meta:
        model = ModelImagePlacement
        fields = ("image_file", "view", "alt_text", "is_visible")

    class Media:
        js = ("catalog/js/image_placement_preview.js",)

    def clean(self):
        cleaned_data = super().clean()
        if not self.instance.pk and not cleaned_data.get("image_file"):
            self.add_error("image_file", "Upload an image for this model placement.")
        return cleaned_data


class ModelImagePlacementInlineFormSet(BaseInlineFormSet):
    def save_new(self, form, commit=True):
        instance = form.save(commit=False)
        setattr(instance, self.fk.name, self.instance)
        self._save_uploaded_image(form, instance)
        if commit:
            instance.save()
        return instance

    def save_existing(self, form, instance, commit=True):
        instance = form.save(commit=False)
        self._save_uploaded_image(form, instance)
        if commit:
            instance.save()
        return instance

    def _save_uploaded_image(self, form, placement):
        uploaded_file = form.cleaned_data.get("image_file")
        if uploaded_file is None:
            return

        image = ImageAsset(title=Path(uploaded_file.name).stem[:255])
        image._base_model = placement.base_model
        image.file = uploaded_file
        image.save()
        placement.image = image


class ModelImagePlacementInline(admin.TabularInline):
    model = ModelImagePlacement
    form = ModelImagePlacementInlineForm
    formset = ModelImagePlacementInlineFormSet
    extra = 1
    fields = ("image_file", "image_preview", "view", "alt_text", "is_visible")
    readonly_fields = ("image_preview",)

    @admin.display(description="Image preview")
    def image_preview(self, obj):
        style = (
            "display:block;max-width:180px;max-height:120px;object-fit:contain;"
            "margin:.75rem 0;background:#fff;border:1px solid #d1d5db;"
        )
        if not obj.pk or not obj.image_id:
            return format_html(
                '<img class="image-placement-preview" hidden style="{}">', style
            )

        image_url = obj.image.file.url
        return format_html(
            '<img class="image-placement-preview" data-original-src="{}" '
            'src="{}" alt="{}" style="{}">',
            image_url,
            image_url,
            obj.image.title,
            style,
        )


class BaseModelWarrantyInline(admin.StackedInline):
    model = BaseModelWarranty
    extra = 1
    max_num = 1
    fieldsets = (
        (
            "Basic",
            {
                "fields": (
                    "basic_years",
                    "basic_kilometers",
                    "basic_kilometers_unlimited",
                )
            },
        ),
        (
            "Drivetrain",
            {
                "fields": (
                    "drivetrain_years",
                    "drivetrain_kilometers",
                    "drivetrain_kilometers_unlimited",
                )
            },
        ),
        (
            "Corrosion",
            {
                "fields": (
                    "corrosion_years",
                    "corrosion_kilometers",
                    "corrosion_kilometers_unlimited",
                )
            },
        ),
    )


@admin.register(RegulatoryApproval)
class RegulatoryApprovalAdmin(GroupScopedAdminMixin, ModelAdmin):
    list_display = ("authority", "jurisdiction", "scheme", "domain", "status")
    search_fields = (
        "authority",
        "jurisdiction",
        "scheme",
        "standard",
        "vehicle__model__model",
    )
    group_paths = ("vehicle__model__model_generation__make__group",)
    inlines = (ApprovalSourceDocumentInline,)


@admin.register(ApprovalSourceDocument)
class ApprovalSourceDocumentAdmin(GroupScopedAdminMixin, ModelAdmin):
    list_display = ("url", "publisher", "document_type", "is_primary")
    search_fields = ("url", "title", "publisher")
    group_paths = ("approval__vehicle__model__model_generation__make__group",)
    foreignkey_group_paths = {
        "approval": "vehicle__model__model_generation__make__group"
    }


class VehicleLinkedAdmin(GroupScopedAdminMixin, ModelAdmin):
    group_paths = ("vehicle__model__model_generation__make__group",)
    foreignkey_group_paths = {"vehicle": "model__model_generation__make__group"}


@admin.register(SafetyPackage)
class SafetyPackageAdmin(GroupScopedAdminMixin, ModelAdmin):
    form = SafetyPackageAdminForm
    list_display = ("name", "group")
    search_fields = ("name", "group__name")
    group_paths = ("group",)
    owner_group_field = "group"


@admin.register(ChargingPackage)
class ChargingPackageAdmin(GroupScopedAdminMixin, ModelAdmin):
    form = ChargingPackageAdminForm
    list_display = (
        "name",
        "group",
        "ac_max_power_kw",
        "dc_max_power_kw",
        "v2l",
        "v2h",
        "v2g",
    )
    search_fields = ("name", "group__name")
    group_paths = ("group",)
    owner_group_field = "group"


@admin.register(ClimatePackage)
class ClimatePackageAdmin(GroupScopedAdminMixin, ModelAdmin):
    form = ClimatePackageAdminForm
    list_display = (
        "name",
        "group",
        "zone_count",
        "automatic_climate_control",
        "heat_pump",
    )
    search_fields = ("name", "group__name")
    group_paths = ("group",)
    owner_group_field = "group"


@admin.register(ChargingPort)
class ChargingPortAdmin(VehicleLinkedAdmin):
    form = ChargingPortAdminForm
    list_display = ("vehicle", "current_type", "connector", "location")
    search_fields = (
        "vehicle__model__model_generation__model",
        "vehicle__model__model_generation__make__name",
    )


@admin.register(ChargeTimeResult)
class ChargeTimeResultAdmin(VehicleLinkedAdmin):
    list_display = (
        "vehicle",
        "current_type",
        "connector",
        "source_state_of_charge_percent",
        "target_state_of_charge_percent",
        "duration_minutes",
        "is_primary",
    )
    search_fields = (
        "vehicle__model__model_generation__model",
        "vehicle__model__model_generation__make__name",
        "note",
    )


@admin.register(ComplianceRecord)
class ComplianceRecordAdmin(VehicleLinkedAdmin):
    list_display = (
        "vehicle",
        "category",
        "region",
        "standard",
        "classification",
        "source_url",
        "is_primary",
    )
    search_fields = (
        "vehicle__model__model_generation__model",
        "vehicle__model__model_generation__make__name",
        "region",
        "standard",
        "classification",
        "source_url",
    )


class VehicleResultAdmin(VehicleLinkedAdmin):
    search_fields = (
        "vehicle__model__model_generation__model",
        "vehicle__model__model_generation__make__name",
    )


@admin.register(EfficiencyResult)
class EfficiencyResultAdmin(VehicleResultAdmin):
    list_display = (
        "vehicle",
        "cycle",
        "scope",
        "metric",
        "value",
        "unit",
        "is_primary",
    )


@admin.register(RangeResult)
class RangeResultAdmin(VehicleResultAdmin):
    list_display = (
        "vehicle",
        "cycle",
        "scope",
        "metric",
        "value",
        "unit",
        "is_primary",
    )


@admin.register(EmissionsResult)
class EmissionsResultAdmin(VehicleResultAdmin):
    list_display = (
        "vehicle",
        "cycle",
        "scope",
        "criteria",
        "value",
        "unit",
        "is_primary",
    )


@admin.register(AccelerationResult)
class AccelerationResultAdmin(VehicleResultAdmin):
    list_display = ("vehicle", "metric", "value", "unit", "is_primary")


@admin.register(TopSpeedResult)
class TopSpeedResultAdmin(VehicleResultAdmin):
    list_display = ("vehicle", "value", "unit", "is_primary")


@admin.register(ImageAsset)
class ImageAssetAdmin(ModelAdmin):
    list_display = ("title", "file", "credit", "license")
    search_fields = ("title", "description", "credit", "license")
    readonly_fields = ("file",)

    def has_add_permission(self, request):
        return False


@admin.register(BaseModel)
class BaseModelAdmin(GroupScopedAdminMixin, ModelAdmin):
    list_display = ("id", "model_generation", "year", "body_style")
    ordering = ("-year", "id")
    search_fields = (
        "model_generation__model",
        "model_generation__make__name",
        "model_generation__generation_prefix",
    )
    list_filter = ("year", "body_style")
    autocomplete_fields = ("model_generation",)
    group_paths = ("model_generation__make__group",)
    foreignkey_group_paths = {"model_generation": "make__group"}
    inlines = (
        ModelImagePlacementInline,
        BaseModelWarrantyInline,
        ModelSafetyRatingInline,
    )


@admin.register(ModelGeneration)
class ModelGenerationAdmin(GroupScopedAdminMixin, ModelAdmin):
    list_display = (
        "id",
        "make",
        "model",
        "generation_prefix",
        "generation_number",
        "platform",
    )
    search_fields = ("model", "make__name", "generation_prefix", "platform__name")
    autocomplete_fields = ("make", "platform")
    group_paths = ("make__group",)
    foreignkey_group_paths = {"make": "group", "platform": "groups"}


@admin.register(Make)
class MakeAdmin(GroupScopedAdminMixin, ModelAdmin):
    list_display = ("makeId", "name", "country", "website", "phone", "group")
    search_fields = ("name", "description")
    group_paths = ("group",)
    foreignkey_group_paths = {"group": "self"}
    owner_group_field = "group"


@admin.register(Group)
class GroupAdmin(GroupScopedAdminMixin, ModelAdmin):
    list_display = ("groupId", "name", "country")
    search_fields = ("name", "description")
    group_paths = ("self",)


@admin.register(Platform)
class PlatformAdmin(GroupScopedAdminMixin, ModelAdmin):
    list_display = ("platformId", "name")
    search_fields = ("name",)
    filter_horizontal = ("groups",)
    group_paths = ("groups",)
    manytomany_group_paths = {"groups": "self"}


@admin.register(Engine)
class EngineAdmin(GroupScopedAdminMixin, ModelAdmin):
    form = EngineAdminForm
    list_display = ("name", "maker", "energy_source", "power_kW", "displacement_cc")
    search_fields = ("name", "maker__name")
    group_paths = ("maker__group",)
    foreignkey_group_paths = {"maker": "group"}


@admin.register(BatteryPack)
class BatteryPackAdmin(GroupScopedAdminMixin, ModelAdmin):
    form = BatteryPackAdminForm
    list_display = (
        "batteryPackId",
        "name",
        "group",
        "chemistry",
        "provider",
        "capacity_kWh",
        "gross_capacity_kWh",
        "usable_capacity_kWh",
        "voltage_V",
    )
    search_fields = ("name", "provider")
    group_paths = ("group",)
    foreignkey_group_paths = {"group": "self"}
    owner_group_field = "group"


@admin.register(FuelTank)
class FuelTankAdmin(GroupScopedAdminMixin, ModelAdmin):
    list_display = ("fuelTankId", "name", "maker", "fuel_type", "capacity_L")
    search_fields = ("name", "maker__name")
    group_paths = ("maker__group",)
    foreignkey_group_paths = {"maker": "group"}


@admin.register(EMotor)
class EMotorAdmin(GroupScopedAdminMixin, ModelAdmin):
    form = EMotorAdminForm
    list_display = (
        "eMotorId",
        "name",
        "maker",
        "motor_type",
        "power_kW",
        "torque_Nm",
    )
    search_fields = ("name", "maker__name")
    group_paths = ("maker__group",)
    foreignkey_group_paths = {"maker": "group"}


@admin.register(Transmission)
class TransmissionAdmin(GroupScopedAdminMixin, ModelAdmin):
    list_display = ("transmissionId", "name", "maker", "type", "gears")
    search_fields = ("name", "maker__name")
    group_paths = ("maker__group",)
    foreignkey_group_paths = {"maker": "group"}


@admin.register(PowerTrain)
class PowerTrainAdmin(GroupScopedAdminMixin, ModelAdmin):
    form = PowerTrainAdminForm
    list_display = ("powerTrainId", "name", "make", "architecture")
    ordering = ("name", "powerTrainId")
    search_fields = ("name", "make__name")
    foreignkey_group_paths = {"make": "group"}
    inlines = (
        PowerTrainEngineInline,
        PowerTrainEMotorInline,
        PowerTrainBatteryPackInline,
        PowerTrainFuelTankInline,
    )


@admin.register(VehicleMonthlySales)
class VehicleMonthlySalesAdmin(GroupScopedAdminMixin, ModelAdmin):
    list_display = ("vehicle", "month", "year", "units_sold")
    search_fields = (
        "vehicle__model__model_generation__model",
        "vehicle__model__model_generation__make__name",
    )
    list_filter = ("year", "month")
    ordering = ("-year", "-month")
    autocomplete_fields = ("vehicle",)
    group_paths = ("vehicle__model__model_generation__make__group",)
    foreignkey_group_paths = {"vehicle": "model__model_generation__make__group"}


class RecallAdminForm(forms.ModelForm):
    class Meta:
        model = Recall
        fields = "__all__"

    def clean(self):
        cleaned_data = super().clean()
        maker = cleaned_data.get("maker")
        affected_models = cleaned_data.get("affected_models")
        if (
            maker
            and affected_models
            and affected_models.exclude(model_generation__make=maker).exists()
        ):
            raise ValidationError("Los modelos afectados deben pertenecer al maker del recall.")
        return cleaned_data


@admin.register(Recall)
class RecallAdmin(GroupScopedAdminMixin, ModelAdmin):
    form = RecallAdminForm
    list_display = ("recall_number", "maker", "status", "published_date")
    search_fields = (
        "recall_number",
        "authority",
        "maker__name",
        "affected_models__model_generation__model",
    )
    list_filter = ("status", "maker__country", "published_date")
    ordering = ("-published_date", "id")
    autocomplete_fields = ("maker",)
    filter_horizontal = ("affected_models",)
    group_paths = ("maker__group",)
    foreignkey_group_paths = {"maker": "group"}
    manytomany_group_paths = {
        "affected_models": "model_generation__make__group"
    }


@admin.register(Vehicle)
class VehicleAdmin(GroupScopedAdminMixin, ModelAdmin):
    electric_inlines = (
        VehicleChargingPackageInline,
        ChargingPortInline,
        ChargeTimeResultInline,
    )
    standard_inlines = (
        VehicleSafetyPackageInline,
        VehicleClimatePackageInline,
        EfficiencyResultInline,
        RangeResultInline,
        EmissionsResultInline,
        AccelerationResultInline,
        TopSpeedResultInline,
    )
    compliance_inlines = (
        ComplianceRecordInline,
        RegulatoryApprovalInline,
    )
    list_display = (
        "id",
        "model",
        "assembly_country",
        "price_amount",
        "price_currency",
        "platform",
        "powertrain",
        "transmissionId",
    )
    search_fields = (
        "id",
        "model__model_generation__model",
        "model__model_generation__make__name",
        "model__model_generation__platform__name",
        "powertrain__name",
        "transmissionId__name",
    )
    autocomplete_fields = (
        "model",
        "powertrain",
        "transmissionId",
    )
    readonly_fields = (
        "powertrain_inline",
        "transmission_inline",
        "powertrain_engines_inline",
        "powertrain_motors_inline",
        "powertrain_battery_packs_inline",
        "powertrain_fuel_tanks_inline",
    )
    group_paths = ("model__model_generation__make__group",)
    foreignkey_group_paths = {
        "model": "model_generation__make__group",
        "powertrain": "make__group",
        "transmissionId": "maker__group",
    }

    @admin.display(
        ordering="model__model_generation__platform", description="Platform"
    )
    def platform(self, obj):
        return obj.model.model_generation.platform

    def _get_selected_powertrain(self, request, obj=None):
        if obj is not None:
            return obj.powertrain

        powertrain_id = request.POST.get("powertrain")
        if not powertrain_id:
            return None

        queryset = PowerTrain.objects.all()
        if not request.user.is_superuser:
            queryset = self._filter_by_group_paths(
                queryset,
                self.get_allowed_groups(request),
                ("make__group",),
            )
        return queryset.filter(pk=powertrain_id).first()

    def _supports_electric_features(self, request, obj=None):
        powertrain = self._get_selected_powertrain(request, obj)
        if powertrain is None:
            return False
        return powertrain.architecture != PowerTrainArchitecture.ICE

    def get_inlines(self, request, obj=None):
        inlines = [*self.standard_inlines]
        # Add forms must include electric inlines before a powertrain is selected.
        # On change forms, keep inline prefixes stable if the selection changes.
        if obj is None or self._supports_electric_features(request, obj):
            inlines[1:1] = self.electric_inlines
        inlines.extend(self.compliance_inlines)
        return inlines

    def get_fieldsets(self, request, obj=None):
        fieldsets = [
            (
                None,
                {
                    "fields": (
                        "model",
                        "variant_name",
                        "assembly_country",
                        "price_amount",
                        "price_currency",
                        "powertrain",
                        "transmissionId",
                    )
                },
            ),
            (
                "Specs",
                {
                    "fields": (
                        "length_mm",
                        "width_mm",
                        "height_mm",
                        "wheelbase_mm",
                        "curb_weight_kg",
                        "door_count",
                        "passenger_capacity",
                    )
                },
            ),
            (
                "Storage",
                {
                    "fields": (
                        "trunk_capacity_liters",
                        "cargo_floor_width_between_wheel_houses_mm",
                        "front_cargo_capacity_liters",
                        "max_cargo_capacity_seats_folded_liters",
                    )
                },
            ),
            (
                "Transmission",
                {"fields": ("transmission_inline",)},
            ),
            (
                "Powertrain",
                {"fields": ("powertrain_inline",)},
            ),
            (
                "Combustion Components",
                {
                    "fields": (
                        "powertrain_engines_inline",
                        "powertrain_fuel_tanks_inline",
                    )
                },
            ),
        ]

        if self._supports_electric_features(request, obj):
            fieldsets.append(
                (
                    "Electric Systems",
                    {
                        "fields": (
                            "powertrain_motors_inline",
                            "powertrain_battery_packs_inline",
                        )
                    },
                )
            )

        return fieldsets

    def _admin_change_link(self, app_label, model_name, object_id, label):
        url = reverse(f"admin:{app_label}_{model_name}_change", args=[object_id])
        return format_html('<a href="{}">{}</a>', url, label)

    def _render_powertrain_fitments(self, obj, fitments, renderer, empty_label):
        if not obj.powertrain_id:
            return empty_label
        items = list(fitments)
        if not items:
            return empty_label
        return format_html(
            "<ul>{}</ul>",
            format_html_join("", "<li>{}</li>", ((renderer(item),) for item in items)),
        )

    def transmission_inline(self, obj):
        if not obj.transmissionId_id:
            return "No transmission"

        details = [
            self._admin_change_link(
                "catalog",
                "transmission",
                obj.transmissionId_id,
                obj.transmissionId.name,
            ),
            obj.transmissionId.type,
        ]
        if obj.transmissionId.gears is not None:
            details.append(f"gears: {obj.transmissionId.gears}")
        return format_html("{}", " | ".join(str(detail) for detail in details))

    transmission_inline.short_description = "Transmission"

    def powertrain_inline(self, obj):
        if not obj.powertrain_id:
            return "No powertrain"

        details = [
            self._admin_change_link(
                "catalog",
                "powertrain",
                obj.powertrain_id,
                obj.powertrain.name,
            ),
            obj.powertrain.architecture,
        ]
        return format_html("{}", " | ".join(str(detail) for detail in details))

    powertrain_inline.short_description = "Powertrain"

    def powertrain_engines_inline(self, obj):
        return self._render_powertrain_fitments(
            obj,
            (
                obj.powertrain.engine_fitments.select_related("engine")
                if obj.powertrain_id
                else []
            ),
            lambda fitment: format_html(
                "{} | role: {}{}",
                self._admin_change_link(
                    "catalog",
                    "engine",
                    fitment.engine_id,
                    fitment.engine.name,
                ),
                fitment.role,
                " | primary" if fitment.is_primary else "",
            ),
            "No engines",
        )

    powertrain_engines_inline.short_description = "Engines"

    def powertrain_motors_inline(self, obj):
        return self._render_powertrain_fitments(
            obj,
            (
                obj.powertrain.motor_fitments.select_related("e_motor")
                if obj.powertrain_id
                else []
            ),
            lambda fitment: format_html(
                "{} | role: {} | position: {} | qty: {}{}",
                self._admin_change_link(
                    "catalog",
                    "emotor",
                    fitment.e_motor_id,
                    fitment.e_motor.name,
                ),
                fitment.role,
                fitment.position,
                fitment.quantity,
                " | primary" if fitment.is_primary else "",
            ),
            "No traction motors",
        )

    powertrain_motors_inline.short_description = "Traction Motors"

    def powertrain_battery_packs_inline(self, obj):
        return self._render_powertrain_fitments(
            obj,
            (
                obj.powertrain.battery_fitments.select_related("battery_pack")
                if obj.powertrain_id
                else []
            ),
            lambda fitment: format_html(
                "{}{}",
                self._admin_change_link(
                    "catalog",
                    "batterypack",
                    fitment.battery_pack_id,
                    fitment.battery_pack.name,
                ),
                " | primary" if fitment.is_primary else "",
            ),
            "No battery packs",
        )

    powertrain_battery_packs_inline.short_description = "Battery Packs"

    def powertrain_fuel_tanks_inline(self, obj):
        return self._render_powertrain_fitments(
            obj,
            (
                obj.powertrain.fuel_fitments.select_related("fuel_tank")
                if obj.powertrain_id
                else []
            ),
            lambda fitment: format_html(
                "{}{}",
                self._admin_change_link(
                    "catalog",
                    "fueltank",
                    fitment.fuel_tank_id,
                    fitment.fuel_tank.name,
                ),
                " | primary" if fitment.is_primary else "",
            ),
            "No fuel tanks",
        )

    powertrain_fuel_tanks_inline.short_description = "Fuel Tanks"
