from django.db import models


class FuelType(models.TextChoices):
    GASOLINE = "gasoline", "Gasoline"
    DIESEL = "diesel", "Diesel"
    E85 = "e85", "E85"
    CNG = "cng", "Compressed Natural Gas"
    LPG = "lpg", "Liquefied Petroleum Gas"
    HYDROGEN = "hydrogen", "Hydrogen"


class EngineAspiration(models.TextChoices):
    NATURALLY_ASPIRATED = "naturally_aspirated", "Naturally Aspirated"
    TURBOCHARGED = "turbocharged", "Turbocharged"
    SUPERCHARGED = "supercharged", "Supercharged"
    TWINCHARGED = "twincharged", "Twincharged"
    OTHER = "other", "Other"


class EngineLayout(models.TextChoices):
    I = "i", "Inline"
    V = "v", "V"
    BOXER = "boxer", "Boxer"
    W = "w", "W"
    ROTARY = "rotary", "Rotary"
    OTHER = "other", "Other"


class BatteryChemistry(models.TextChoices):
    LFP = "lfp", "LFP"
    NMC = "nmc", "NMC"
    NCA = "nca", "NCA"
    NIMH = "nimh", "NiMH"
    LEAD_ACID = "lead_acid", "Lead Acid"
    SOLID_STATE = "solid_state", "Solid State"
    OTHER = "other", "Other"


class ElectricMotorType(models.TextChoices):
    AC_INDUCTION = "ac_induction", "AC Induction"
    PERMANENT_MAGNET = "permanent_magnet", "Permanent Magnet"
    EXTERNALLY_EXCITED = "externally_excited", "Externally Excited"
    SWITCHED_RELUCTANCE = "switched_reluctance", "Switched Reluctance"
    OTHER = "other", "Other"


class MotorCoolingType(models.TextChoices):
    AIR = "air", "Air"
    LIQUID = "liquid", "Liquid"
    OIL = "oil", "Oil"
    OTHER = "other", "Other"


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