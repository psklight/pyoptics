from ctypes import (
    Structure,
    cdll,
    c_bool,
    c_short,
    c_int,
    c_uint,
    c_int16,
    c_int32,
    c_char,
    c_byte,
    c_long,
    c_float,
    c_double,
    POINTER,
    CFUNCTYPE,
    c_ushort,
    c_ulong,
    c_char_p
)

c_word = c_ushort
c_dword = c_ulong

from .._tool import bind, null_function
from .._enumeration import MOT_MotorTypes, MOT_JogModes, MOT_StopModes, MOT_TravelDirection, MOT_HomeLimitSwitchDirection, MOT_LimitSwitchModes, MOT_LimitSwitchSWModes, MOT_DirectionSense, MOT_TravelModes
from .. import DeviceManager as dm

from comtypes import _safearray
import ctypes
from ctypes import byref, pointer
from time import sleep

lib = cdll.LoadLibrary("Thorlabs.MotionControl.KCube.DCServo.dll")

#encoder_counters = {
#    'MTS25-Z8':     34304,
#    'MTS50-Z8':     34304,
#    'Z8':           34304,
#    'Z6':           24600,
#    'PRM1-Z8':      1919.64,
#    'CR1-Z7':       12288}

class StructureEx(Structure):

    def getdict(self):
        return dict((f, getattr(self, f)) for f, _ in self._fields_)

    def loaddict(self, d):
        """
        d -- a dictionary of parameters. The keys of the dictionary much match the attributes of the class.
        """
        for f in d.keys():
            if not hasattr(self, f):
                raise AttributeError('Given dictionary has unmatched attributes.')
            for field, ctype in self._fields_:
                if field == f:
                    break
            if ctype in [c_short, c_long, c_int, c_int16, c_int32, c_uint, c_ushort, c_ulong]:
                setattr(self, f, ctype(int(d[f])))
            if ctype in [c_float, c_double]:
                setattr(self, f, ctype(float(d[f])))

# Define data structures
class TLI_DeviceInfo(StructureEx):
    _fields_ = [("typeID", c_dword),
                ("description", (65 * c_char)),
                ("serialNo", (9 * c_char)),
                ("PID", c_dword),
                ("isKnownType", c_bool),
                ("motorType", MOT_MotorTypes),
                ("isPiezoDevice", c_bool),
                ("isLaser", c_bool),
                ("isCustomType", c_bool),
                ("isRack", c_bool),
                ("maxChannels", c_short)]

    def __str__(self):
        d = dict()
        d['typeID'] = self.typeID
        d['description'] = self.description
        d['serialNo'] = self.serialNo
        d['PID'] = self.PID
        d['isKnownType'] = self.isKnownType
        d['motorType'] = self.motorType
        d['isPiezoDevice'] = self.isPiezoDevice
        d['isCustomType'] = self.isCustomType
        d['isRack'] = self.isRack
        d['maxChannels'] = self.maxChannels
        return str(d)


class TLI_HardwareInformation(StructureEx):
    _fields_ = [("serialNumber", c_dword),
                ("modelNumber", (8 * c_char)),
                ("type", c_word),
                ("firmwareVersion", c_dword),
                ("notes", (48 * c_char)),
                ("deviceDependantData", (12 * c_byte)),
                ("hardwareVersion", c_word),
                ("modificationState", c_word),
                ("numChannels", c_short)]


class MOT_VelocityParameters(StructureEx):
    _fields_ = [("minVelocity", c_int),
                ("acceleration", c_int),
                ("maxVelocity", c_int)]


class MOT_JogParameters(StructureEx):
    _fields_ = [("mode", MOT_JogModes),
                ("stepSize", c_uint),
                ("velParams", MOT_VelocityParameters),
                ("stopMode", MOT_StopModes)]


class MOT_HomingParameters(StructureEx):
    _fields_ = [("direction", MOT_TravelDirection),
                ("limitSwitch", MOT_HomeLimitSwitchDirection),
                ("velocity", c_uint),
                ("offsetDistance", c_uint)]


class MOT_LimitSwitchParameters(StructureEx):
    _fields_ = [("clockwiseHardwareLimit", MOT_LimitSwitchModes),
                ("anticlockwiseHardwareLimit", MOT_LimitSwitchModes),
                ("clockwisePosition", c_dword),
                ("anticlockwisePosition", c_dword),
                ("softLimitMode", MOT_LimitSwitchSWModes)]

class MOT_DC_PIDParameters(StructureEx):
    _fields_ = [("proportionalGain", c_int),
                ("integralGain", c_int),
                ("differentialGain", c_int),
                ("integralLimit", c_int),
                ("parameterFilter", c_word)]

class KMOT_MMIParams(StructureEx):
    _fields_ = [("JoystickMODE", c_int),
                ("JoystickMaxVelocity", c_int32),
                ("JoystickAcceleration", c_int32),
                ("JoystickDirectionSense", MOT_DirectionSense),
                ("PresetPos1", c_int32),
                ("PresetPos2", c_int32),
                ("DisplayIntensity", c_int16),
                ("reserved",6*c_int16)]

class KMOT_TriggerConfig(StructureEx):
    _fields_ = [("Trigger1Mode", c_int),
                ("Trigger1Polarity", c_int),
                ("Trigger2Mode", c_int),
                ("Trigger2Polarity", c_int)]

class KMOT_TriggerParams(StructureEx):
    _fields_ = [("TriggerStartPositionFwd", c_int32),
                ("TriggerIntervalFwd", c_int32),
                ("TriggerPulseCountFwd", c_int32),
                ("TriggerStartPositionRev", c_int32),
                ("TriggerIntervalRev", c_int32),
                ("TriggerPulseCountRev", c_int32),
                ("TriggerPulseWidth", c_int32),
                ("CycleCount", c_int32),
                ("reserved", 6*c_int32)]

TLI_BuildDeviceList = bind(lib, "TLI_BuildDeviceList", None, c_short)
TLI_GetDeviceListSize = bind(lib, "TLI_GetDeviceListSize", None, c_short)
# TLI_GetDeviceList = bind(lib, "TLI_GetDeviceList", [_safearray.tagSAFEARRAY], c_short)
# TLI_GetDeviceList  <- TODO: Implement SAFEARRAY first. BENCHTOPSTEPPERMOTOR_API short __cdecl TLI_GetDeviceList(SAFEARRAY** stringsReceiver);
# TLI_GetDeviceListByType  <- TODO: Implement SAFEARRAY first. BENCHTOPSTEPPERMOTOR_API short __cdecl TLI_GetDeviceListByType(SAFEARRAY** stringsReceiver, int typeID);
# TLI_GetDeviceListByTypes  <- TODO: Implement SAFEARRAY first. BENCHTOPSTEPPERMOTOR_API short __cdecl TLI_GetDeviceListByTypes(SAFEARRAY** stringsReceiver, int * typeIDs, int length);
TLI_GetDeviceListExt = bind(lib, "TLI_GetDeviceListExt", [POINTER(c_char), c_dword], c_short)
TLI_GetDeviceListByTypeExt = bind(lib, "TLI_GetDeviceListByTypeExt", [POINTER(c_char), c_dword, c_int], c_short)
TLI_GetDeviceListByTypesExt = bind(lib, "TLI_GetDeviceListByTypesExt", [POINTER(c_char), c_dword, POINTER(c_int), c_int], c_short)
TLI_GetDeviceInfo = bind(lib, "TLI_GetDeviceInfo", [POINTER(c_char), POINTER(TLI_DeviceInfo)], c_short)

# KDC specific functions
CC_Open = bind(lib, "CC_Open", [POINTER(c_char)], c_short)
CC_Close = bind(lib, "CC_Close", [POINTER(c_char)], c_short)
CC_Identify = bind(lib, "CC_Identify", [POINTER(c_char)], None)

CC_Home = bind(lib, "CC_Home", [POINTER(c_char)], c_short)
CC_MoveToPosition = bind(lib, "CC_MoveToPosition", [POINTER(c_char), c_int], c_short)
CC_StopProfiled = bind(lib, "CC_StopProfiled", [POINTER(c_char)], c_short)
CC_StopImmediate = bind(lib, "CC_StopImmediate", [POINTER(c_char)], c_short)

CC_RequestPosition = bind(lib, "CC_RequestPosition", [POINTER(c_char)], c_short)
CC_GetPosition = bind(lib, "CC_GetPosition", [POINTER(c_char)], c_int)

CC_GetVelParams = bind(lib, "CC_GetVelParams", [POINTER(c_char), POINTER(c_int), POINTER(c_int)], c_short)

CC_GetRealValueFromDeviceUnit = bind(lib, "CC_GetRealValueFromDeviceUnit", [POINTER(c_char), c_int, POINTER(c_double), c_int], c_short)
CC_GetDeviceUnitFromRealValue = bind(lib, "CC_GetDeviceUnitFromRealValue", [POINTER(c_char), c_double, POINTER(c_int), c_int], c_short)

CC_GetHardwareInfoBlock = bind(lib, "CC_GetHardwareInfoBlock", [POINTER(c_char), POINTER(TLI_HardwareInformation)], c_short)

CC_ClearMessageQueue = bind(lib, "CC_ClearMessageQueue", [POINTER(c_char)], None)

CC_GetMotorParamsExt = bind(lib, "CC_GetMotorParamsExt", [POINTER(c_char), POINTER(c_double), POINTER(c_double), POINTER(c_double)], c_short)
CC_GetMotorVelocityLimits = bind(lib, "CC_GetMotorVelocityLimits", [POINTER(c_char), POINTER(c_double), POINTER(c_double)], c_short)
CC_GetMotorTravelMode = bind(lib, "CC_GetMotorTravelMode", [POINTER(c_char)], MOT_TravelModes)
CC_GetMotorTravelLimits = bind(lib, "CC_GetMotorTravelLimits", [POINTER(c_char), POINTER(c_double), POINTER(c_double)], c_short)

CC_SetMotorParamsExt = bind(lib, "CC_SetMotorParamsExt", [POINTER(c_char), c_double, c_double, c_double], c_short)
CC_SetMotorTravelLimits = bind(lib, "CC_SetMotorTravelLimits", [POINTER(c_char), c_double, c_double], c_short)
CC_SetMotorTravelMode = bind(lib, "CC_SetMotorTravelMode", [POINTER(c_char), MOT_TravelModes], c_short)
CC_SetMotorVelocityLimits = bind(lib, "CC_SetMotorVelocityLimits", [POINTER(c_char), c_double, c_double], c_short)

CC_RequestSettings = bind(lib, "CC_RequestSettings", [POINTER(c_char)], c_short)
CC_ResetStageToDefaults = bind(lib, "CC_ResetStageToDefaults", [POINTER(c_char)], c_short)
CC_LoadSettings = bind(lib, "CC_LoadSettings", [POINTER(c_char)], c_bool)
CC_PersistSettings = bind(lib, "CC_PersistSettings", [POINTER(c_char)], c_bool)

CC_CanHome = bind(lib, "CC_CanHome", [POINTER(c_char)], c_bool)

CC_GetDCPIDParams = bind(lib, "CC_GetDCPIDParams", [POINTER(c_char), POINTER(MOT_DC_PIDParameters)], c_short)
CC_SetDCPIDParams = bind(lib, "CC_SetDCPIDParams", [POINTER(c_char), POINTER(MOT_DC_PIDParameters)], c_short)

CC_GetHomingParamsBlock = bind(lib, "CC_GetHomingParamsBlock", [POINTER(c_char), POINTER(MOT_HomingParameters)], c_short)
CC_SetHomingParamsBlock = bind(lib, "CC_SetHomingParamsBlock", [POINTER(c_char), POINTER(MOT_HomingParameters)], c_short)