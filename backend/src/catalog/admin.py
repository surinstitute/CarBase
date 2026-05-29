from django import forms
from django.contrib import admin
from django.db.models import Q
from django.urls import reverse
from django.utils.html import format_html, format_html_join
from unfold.admin import ModelAdmin

from .models import (
    AccelerationResult,
    ApprovalSourceDocument,
    BaseModel,
    BatteryPack,
    ChargeTimeResult,
    ChargingPackage,
    ChargingPort,
    ComplianceRecord,
    EfficiencyResult,
    EmissionsResult,
    EMotor,
    Engine,
    FuelTank,
    Group,
    Make,
    Platform,
    PowerTrain,
    PowerTrainBatteryPack,
    PowerTrainEMotor,
    PowerTrainEngine,
    PowerTrainFuelTank,
    RangeResult,
    RegulatoryApproval,
    SafetyPackage,
    TopSpeedResult,
    Transmission,
    Vehicle,
)
from .types import PowerTrainArchitecture


SAFETY_FEATURE_DESCRIPTIONS = {
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


class SafetyPackageAdminForm(forms.ModelForm):
    class Meta:
        model = SafetyPackage
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, description in SAFETY_FEATURE_DESCRIPTIONS.items():
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


class SafetyPackageInline(admin.StackedInline):
    model = SafetyPackage
    form = SafetyPackageAdminForm
    extra = 0
    max_num = 1


class ChargingPackageInline(admin.StackedInline):
    model = ChargingPackage
    extra = 0
    max_num = 1


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


@admin.register(RegulatoryApproval)
class RegulatoryApprovalAdmin(GroupScopedAdminMixin, ModelAdmin):
    list_display = ("authority", "jurisdiction", "scheme", "domain", "status")
    search_fields = (
        "authority",
        "jurisdiction",
        "scheme",
        "standard",
        "vehicle__modelId__model",
    )
    group_paths = ("vehicle__modelId__make__group",)
    inlines = (ApprovalSourceDocumentInline,)


@admin.register(ApprovalSourceDocument)
class ApprovalSourceDocumentAdmin(GroupScopedAdminMixin, ModelAdmin):
    list_display = ("url", "publisher", "document_type", "is_primary")
    search_fields = ("url", "title", "publisher")
    group_paths = ("approval__vehicle__modelId__make__group",)
    foreignkey_group_paths = {"approval": "vehicle__modelId__make__group"}


class VehicleLinkedAdmin(GroupScopedAdminMixin, ModelAdmin):
    group_paths = ("vehicle__modelId__make__group",)
    foreignkey_group_paths = {"vehicle": "modelId__make__group"}


@admin.register(SafetyPackage)
class SafetyPackageAdmin(VehicleLinkedAdmin):
    form = SafetyPackageAdminForm
    list_display = ("vehicle",)
    search_fields = ("vehicle__modelId__model", "vehicle__modelId__make__name")


@admin.register(ChargingPackage)
class ChargingPackageAdmin(VehicleLinkedAdmin):
    list_display = (
        "vehicle",
        "ac_max_power_kw",
        "dc_max_power_kw",
        "v2l",
        "v2h",
        "v2g",
    )
    search_fields = ("vehicle__modelId__model", "vehicle__modelId__make__name")


@admin.register(ChargingPort)
class ChargingPortAdmin(VehicleLinkedAdmin):
    list_display = ("vehicle", "current_type", "connector", "location")
    search_fields = ("vehicle__modelId__model", "vehicle__modelId__make__name")


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
    search_fields = ("vehicle__modelId__model", "vehicle__modelId__make__name", "note")


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
        "vehicle__modelId__model",
        "vehicle__modelId__make__name",
        "region",
        "standard",
        "classification",
        "source_url",
    )


class VehicleResultAdmin(VehicleLinkedAdmin):
    search_fields = ("vehicle__modelId__model", "vehicle__modelId__make__name")


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
        "metric",
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


@admin.register(BaseModel)
class BaseModelAdmin(GroupScopedAdminMixin, ModelAdmin):
    list_display = ("id", "make", "model", "platformId", "year", "generation")
    search_fields = ("model", "make__name", "platformId__name", "generation")
    list_filter = ("year",)
    autocomplete_fields = ("make", "platformId")
    group_paths = ("make__group",)
    foreignkey_group_paths = {"make": "group", "platformId": "groups"}


@admin.register(Make)
class MakeAdmin(GroupScopedAdminMixin, ModelAdmin):
    list_display = ("makeId", "name", "group")
    search_fields = ("name",)
    group_paths = ("group",)
    foreignkey_group_paths = {"group": "self"}
    owner_group_field = "group"


@admin.register(Group)
class GroupAdmin(GroupScopedAdminMixin, ModelAdmin):
    list_display = ("groupId", "name")
    search_fields = ("name",)
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
    list_display = ("name", "maker", "energy_source", "power_kW", "displacement_cc")
    search_fields = ("name", "maker__name")
    group_paths = ("maker__group",)
    foreignkey_group_paths = {"maker": "group"}


@admin.register(BatteryPack)
class BatteryPackAdmin(GroupScopedAdminMixin, ModelAdmin):
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
    list_display = ("powerTrainId", "name", "make", "architecture")
    search_fields = ("name", "make__name")
    foreignkey_group_paths = {"make": "group"}
    inlines = (
        PowerTrainEngineInline,
        PowerTrainEMotorInline,
        PowerTrainBatteryPackInline,
        PowerTrainFuelTankInline,
    )


@admin.register(Vehicle)
class VehicleAdmin(GroupScopedAdminMixin, ModelAdmin):
    electric_inlines = (
        ChargingPackageInline,
        ChargingPortInline,
        ChargeTimeResultInline,
    )
    standard_inlines = (
        SafetyPackageInline,
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
    list_display = ("id", "modelId", "platform", "powerTrainId", "transmissionId")
    search_fields = (
        "id",
        "modelId__model",
        "modelId__make__name",
        "modelId__platformId__name",
        "powerTrainId__name",
        "transmissionId__name",
    )
    autocomplete_fields = ("modelId", "powerTrainId", "transmissionId")
    readonly_fields = (
        "powertrain_inline",
        "transmission_inline",
        "powertrain_engines_inline",
        "powertrain_motors_inline",
        "powertrain_battery_packs_inline",
        "powertrain_fuel_tanks_inline",
    )
    group_paths = ("modelId__make__group",)
    foreignkey_group_paths = {
        "modelId": "make__group",
        "powerTrainId": "make__group",
        "transmissionId": "maker__group",
    }

    @admin.display(ordering="modelId__platformId", description="platformId")
    def platform(self, obj):
        return obj.modelId.platformId

    def _get_selected_powertrain(self, request, obj=None):
        if obj is not None and obj.powerTrainId_id:
            return obj.powerTrainId

        powertrain_id = request.POST.get("powerTrainId")
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
        if self._supports_electric_features(request, obj):
            inlines[1:1] = self.electric_inlines
        inlines.extend(self.compliance_inlines)
        return inlines

    def get_fieldsets(self, request, obj=None):
        fieldsets = [
            (
                None,
                {
                    "fields": (
                        "modelId",
                        "powerTrainId",
                        "transmissionId",
                        "bodyStyle",
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
        if not obj.powerTrainId_id:
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
        if not obj.powerTrainId_id:
            return "No powertrain"

        details = [
            self._admin_change_link(
                "catalog",
                "powertrain",
                obj.powerTrainId_id,
                obj.powerTrainId.name,
            ),
            obj.powerTrainId.architecture,
        ]
        return format_html("{}", " | ".join(str(detail) for detail in details))

    powertrain_inline.short_description = "Powertrain"

    def powertrain_engines_inline(self, obj):
        return self._render_powertrain_fitments(
            obj,
            (
                obj.powerTrainId.engine_fitments.select_related("engine")
                if obj.powerTrainId_id
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
                obj.powerTrainId.motor_fitments.select_related("e_motor")
                if obj.powerTrainId_id
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
                obj.powerTrainId.battery_fitments.select_related("battery_pack")
                if obj.powerTrainId_id
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
                obj.powerTrainId.fuel_fitments.select_related("fuel_tank")
                if obj.powerTrainId_id
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
