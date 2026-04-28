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
    EMotor,
    EfficiencyResult,
    EmissionsResult,
    Engine,
    FuelTank,
    Group,
    Make,
    Platform,
    PowerResult,
    PowerTrain,
    PowerTrainBatteryPack,
    PowerTrainEMotor,
    PowerTrainEngine,
    PowerTrainFuelTank,
    RangeResult,
    RegulatoryApproval,
    SafetyPackage,
    TopSpeedResult,
    TorqueResult,
    Transmission,
    Vehicle,
)


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


class TorqueResultInline(admin.TabularInline):
    model = TorqueResult
    extra = 0


class PowerResultInline(admin.TabularInline):
    model = PowerResult
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
        "is_primary",
    )
    search_fields = (
        "vehicle__modelId__model",
        "vehicle__modelId__make__name",
        "region",
        "standard",
        "classification",
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


@admin.register(TorqueResult)
class TorqueResultAdmin(VehicleResultAdmin):
    list_display = ("vehicle", "metric", "value", "unit", "is_primary")


@admin.register(PowerResult)
class PowerResultAdmin(VehicleResultAdmin):
    list_display = ("vehicle", "metric", "value", "unit", "is_primary")


@admin.register(BaseModel)
class BaseModelAdmin(GroupScopedAdminMixin, ModelAdmin):
    list_display = ("id", "make", "model", "year", "generation")
    search_fields = ("model", "make__name", "generation")
    list_filter = ("year",)
    group_paths = ("make__group",)
    foreignkey_group_paths = {"make": "group"}


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
    list_display = ("name", "maker", "energy_source")
    search_fields = ("name", "maker__name")
    group_paths = ("maker__group",)
    foreignkey_group_paths = {"maker": "group"}


@admin.register(BatteryPack)
class BatteryPackAdmin(GroupScopedAdminMixin, ModelAdmin):
    list_display = (
        "batteryPackId",
        "name",
        "group",
        "provider",
        "capacity_kWh",
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
    list_display = ("eMotorId", "name", "maker", "power_kW", "torque_Nm")
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
    list_display = ("powerTrainId", "name", "group", "architecture")
    search_fields = ("name",)
    group_paths = ("group",)
    foreignkey_group_paths = {"group": "self"}
    owner_group_field = "group"
    inlines = (
        PowerTrainEngineInline,
        PowerTrainEMotorInline,
        PowerTrainBatteryPackInline,
        PowerTrainFuelTankInline,
    )


@admin.register(Vehicle)
class VehicleAdmin(GroupScopedAdminMixin, ModelAdmin):
    list_display = ("id", "modelId", "platformId", "powerTrainId", "transmissionId")
    search_fields = (
        "id",
        "modelId__model",
        "modelId__make__name",
        "platformId__name",
        "powerTrainId__name",
        "transmissionId__name",
    )
    autocomplete_fields = ("modelId", "platformId", "powerTrainId", "transmissionId")
    inlines = (
        SafetyPackageInline,
        ChargingPackageInline,
        ChargingPortInline,
        ChargeTimeResultInline,
        ComplianceRecordInline,
        RegulatoryApprovalInline,
        EfficiencyResultInline,
        RangeResultInline,
        EmissionsResultInline,
        AccelerationResultInline,
        TopSpeedResultInline,
        TorqueResultInline,
        PowerResultInline,
    )
    readonly_fields = (
        "transmission_inline",
        "powertrain_engines_inline",
        "powertrain_motors_inline",
        "powertrain_battery_packs_inline",
        "powertrain_fuel_tanks_inline",
    )
    fieldsets = (
        (
            None,
            {
                "fields": (
                    "modelId",
                    "platformId",
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
            "Powertrain Components",
            {
                "fields": (
                    "powertrain_engines_inline",
                    "powertrain_motors_inline",
                    "powertrain_battery_packs_inline",
                    "powertrain_fuel_tanks_inline",
                )
            },
        ),
    )
    group_paths = ("modelId__make__group",)
    foreignkey_group_paths = {
        "modelId": "make__group",
        "platformId": "groups",
        "powerTrainId": "group",
        "transmissionId": "maker__group",
    }

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
                "{} | storage: {}{}",
                self._admin_change_link(
                    "catalog",
                    "batterypack",
                    fitment.battery_pack_id,
                    fitment.battery_pack.name,
                ),
                fitment.storage_type,
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
                "{} | storage: {}{}",
                self._admin_change_link(
                    "catalog",
                    "fueltank",
                    fitment.fuel_tank_id,
                    fitment.fuel_tank.name,
                ),
                fitment.storage_type,
                " | primary" if fitment.is_primary else "",
            ),
            "No fuel tanks",
        )

    powertrain_fuel_tanks_inline.short_description = "Fuel Tanks"
