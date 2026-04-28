from rest_framework.viewsets import ReadOnlyModelViewSet

from api.serializers import (
    BaseModelSerializer,
    BatteryPackSerializer,
    EMotorSerializer,
    EngineSerializer,
    FuelTankSerializer,
    GroupSerializer,
    MakeSerializer,
    PlatformSerializer,
    PowerTrainSerializer,
    TransmissionSerializer,
    VehicleSerializer,
)
from catalog.models import (
    BaseModel,
    BatteryPack,
    EMotor,
    Engine,
    FuelTank,
    Group,
    Make,
    Platform,
    PowerTrain,
    Transmission,
    Vehicle,
)


class GroupViewSet(ReadOnlyModelViewSet):
    queryset = Group.objects.all().order_by("name")
    serializer_class = GroupSerializer


class MakeViewSet(ReadOnlyModelViewSet):
    queryset = Make.objects.select_related("group").all().order_by("name")
    serializer_class = MakeSerializer


class BaseModelViewSet(ReadOnlyModelViewSet):
    queryset = (
        BaseModel.objects.select_related("make").all().order_by("make__name", "model")
    )
    serializer_class = BaseModelSerializer


class PlatformViewSet(ReadOnlyModelViewSet):
    queryset = Platform.objects.all().order_by("name")
    serializer_class = PlatformSerializer


class EngineViewSet(ReadOnlyModelViewSet):
    queryset = Engine.objects.select_related("maker").all().order_by("name")
    serializer_class = EngineSerializer


class BatteryPackViewSet(ReadOnlyModelViewSet):
    queryset = BatteryPack.objects.select_related("group").all().order_by("name")
    serializer_class = BatteryPackSerializer


class FuelTankViewSet(ReadOnlyModelViewSet):
    queryset = FuelTank.objects.select_related("maker").all().order_by("name")
    serializer_class = FuelTankSerializer


class EMotorViewSet(ReadOnlyModelViewSet):
    queryset = EMotor.objects.select_related("maker").all().order_by("name")
    serializer_class = EMotorSerializer


class PowerTrainViewSet(ReadOnlyModelViewSet):
    queryset = PowerTrain.objects.select_related("group").all().order_by("name")
    serializer_class = PowerTrainSerializer


class TransmissionViewSet(ReadOnlyModelViewSet):
    queryset = Transmission.objects.select_related("maker").all().order_by("name")
    serializer_class = TransmissionSerializer


class VehicleViewSet(ReadOnlyModelViewSet):
    queryset = (
        Vehicle.objects.select_related(
            "modelId",
            "platformId",
            "powerTrainId",
            "transmissionId",
            "modelId__make",
            "safety_package",
            "charging_package",
        )
        .prefetch_related(
            "powerTrainId__engine_fitments__engine",
            "powerTrainId__motor_fitments__e_motor",
            "powerTrainId__battery_fitments__battery_pack",
            "powerTrainId__fuel_fitments__fuel_tank",
            "charging_ports",
            "charge_time_results",
            "regulatory_approvals__source_docs",
            "compliance_records",
            "efficiency_results",
            "range_results",
            "emissions_results",
            "acceleration_results",
            "top_speed_results",
            "torque_results",
            "power_results",
        )
        .all()
    )
    serializer_class = VehicleSerializer
