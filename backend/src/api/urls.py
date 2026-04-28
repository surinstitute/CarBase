from django.urls import include, path
from rest_framework import routers

from api.views import (
    BaseModelViewSet,
    BatteryPackViewSet,
    EMotorViewSet,
    EngineViewSet,
    FuelTankViewSet,
    GroupViewSet,
    MakeViewSet,
    PlatformViewSet,
    PowerTrainViewSet,
    TransmissionViewSet,
    VehicleViewSet,
)

router = routers.DefaultRouter()
router.register("groups", GroupViewSet, basename="group")
router.register("makes", MakeViewSet, basename="make")
router.register("models", BaseModelViewSet, basename="basemodel")
router.register("platforms", PlatformViewSet, basename="platform")
router.register("engines", EngineViewSet, basename="engine")
router.register("battery-packs", BatteryPackViewSet, basename="batterypack")
router.register("fuel-tanks", FuelTankViewSet, basename="fueltank")
router.register("e-motors", EMotorViewSet, basename="emotor")
router.register("powertrains", PowerTrainViewSet, basename="powertrain")
router.register("transmissions", TransmissionViewSet, basename="transmission")
router.register("vehicles", VehicleViewSet, basename="vehicle")

urlpatterns = [
    path("", include(router.urls)),
]
