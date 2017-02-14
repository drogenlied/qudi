#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from enum import Enum
import ctypes

ok = ctypes.CDLL("libokFrontPanel.so")

OK_REGISTER_SET_ENTRIES = 64

OK_MAX_DEVICEID_LENGTH = 10  # without null
OK_MAX_SERIALNUMBER_LENGTH = 32 # without null
OK_MAX_BOARD_MODEL_STRING_LENGTH = 64 # with null


class BoardModel(Enum):
    Unknown         = 0
    XEM3001v1       = 1
    XEM3001v2       = 2
    XEM3010         = 3
    XEM3005         = 4
    XEM3001CL       = 5
    XEM3020         = 6
    XEM3050         = 7
    XEM9002         = 8
    XEM3001RB       = 9
    XEM5010         = 10
    XEM6110LX45     = 11
    XEM6110LX150    = 15
    XEM6001         = 12
    XEM6010LX45     = 13
    XEM6010LX150    = 14
    XEM6006LX9      = 16
    XEM6006LX16     = 17
    XEM6006LX25     = 18
    XEM5010LX110    = 19
    ZEM4310         = 20
    XEM6310LX45     = 21
    XEM6310LX150    = 22
    XEM6110v2LX45   = 23
    XEM6110v2LX150  = 24
    XEM6002LX9      = 25
    XEM6310MTLX45T  = 26
    XEM6320LX130T   = 27


class ClockSource_22150(Enum):
    Ref = 0
    Div1ByN = 1
    Div1By2 = 2
    Div1By3 = 3
    Div2ByN = 4
    Div2By2 = 5
    Div2By4 = 6


class ClockSource_22393(Enum):
    Ref         = 0
    PLL0_0      = 2
    PLL0_180    = 3
    PLL1_0      = 4
    PLL1_180    = 5
    PLL2_0      = 6
    PLL2_180    = 7


class DividerSource(Enum):
    Ref = 0
    VCO = 1

class ErrorCode(Enum):
    NoError                 = 0
    Failed                  = -1
    Timeout                 = -2
    DoneNotHigh             = -3
    TransferError           = -4
    CommunicationError      = -5
    InvalidBitstream        = -6
    FileError               = -7
    DeviceNotOpen           = -8
    InvalidEndpoint         = -9
    InvalidBlockSize        = -10
    I2CRestrictedAddress    = -11
    I2CBitError             = -12
    I2CNack                 = -13
    I2CUnknownStatus        = -14
    UnsupportedFeature      = -15
    FIFOUnderflow           = -16
    FIFOOverflow            = -17
    DataAlignmentError      = -18
    InvalidResetProfile     = -19
    InvalidParameter        = -20



#typedef struct okRegisterEntry {
#	UINT32   address;
#	UINT32   data;
#} okTRegisterEntry;

class RegisterEntry(ctypes.Structure):
    _fields_ = [
        ('address', ctypes.c_uint32),
        ('data', ctypes.c_uint32)
    ]


# #define okREGISTER_SET_ENTRIES       (64)
#typedef struct okFPGARegisterSet {
#	UINT32            count;
#	okTRegisterEntry  entries[okREGISTER_SET_ENTRIES];
#} okTRegisterSet;


class RegisterSet(ctypes.Structure):
    _fields_ = [
        ('count', ctypes.c_uint32),
        ('entries', RegisterEntry * OK_REGISTER_SET_ENTRIES)
    ]

#typedef struct okTriggerEntry {
#	UINT32   address;
#	UINT32   mask;
#} okTTriggerEntry;

class TriggerEntry(ctypes.Structure):
    _fields_ = [
        ('address', ctypes.c_uint32),
        ('mask', ctypes.c_uint32)
    ]

#typedef struct okFPGAResetProfile {
#	// Magic number indicating the profile is valid.  (4 byte = 0xBE097C3D)
#	UINT32                     magic;
#
#	// Location of the configuration file (Flash boot).  (4 bytes)
#	UINT32                     configFileLocation;
#
#	// Length of the configuration file.  (4 bytes)
#	UINT32                     configFileLength;
#
#	// Number of microseconds to wait after DONE goes high before
#	// starting the reset profile.  (4 bytes)
#	UINT32                     doneWaitUS;
#
#	// Number of microseconds to wait after wires are updated
#	// before deasserting logic RESET.  (4 bytes)
#	UINT32                     resetWaitUS;
#
#	// Number of microseconds to wait after RESET is deasserted
#	// before loading registers.  (4 bytes)
#	UINT32                     registerWaitUS;
#
#	// Future expansion  (112 bytes)
#	UINT32                     padBytes1[28];
#
#	// Initial values of WireIns.  These are loaded prior to
#	// deasserting logic RESET.  (32*4 = 128 bytes)
#	UINT32                     wireInValues[32];
#
#	// Number of valid Register Entries (4 bytes)
#	UINT32                     registerEntryCount;
#
#	// Initial register loads.  (256*8 = 2048 bytes)
#	okTRegisterEntry           registerEntries[256];
#
#	// Number of valid Trigger Entries (4 bytes)
#	UINT32                     triggerEntryCount;
#
#	// Initial trigger assertions.  These are performed last.
#	// (32*8 = 256 bytes)
#	okTTriggerEntry            triggerEntries[32];
#
#	// Padding to a 4096-byte size for future expansion
#	UINT8                      padBytes2[1520];
#} okTFPGAResetProfile;

class ResetProfile(ctypes.Structure):
    _fields_ = [
        ('magic', ctypes.c_uint32),
        ('configFileLocation', ctypes.c_uint32),
        ('configFileLength', ctypes.c_uint32),
        ('doneWaitUS', ctypes.c_uint32),
        ('resetWaitUS', ctypes.c_uint32),
        ('registerWaitUS', ctypes.c_uint32),
        ('padBytes1', ctypes.c_uint32 * 28),
        ('wireInValues', ctypes.c_uint32 * 32),
        ('registerEntryCount', ctypes.c_uint32),
        ('registerEntries',  RegisterEntry * 256),
        ('triggerEntryCount', ctypes.c_uint32),
        ('triggerEntries', TriggerEntry * 32),
        ('padBytes2', ctypes.c_uint8 * 1520)
    ]

#typedef struct {
#	UINT32             sectorCount;
#	UINT32             sectorSize;
#	UINT32             pageSize;
#	UINT32             minUserSector;
#	UINT32             maxUserSector;
#} okTFlashLayout;

class FlashLayout(ctypes.Structure):
    _fields_ = [
        ('sectorCount', ctypes.c_uint32),
        ('sectorSize', ctypes.c_uint32),
        ('pageSize', ctypes.c_uint32),
        ('minUserSector', ctypes.c_uint32),
        ('maxUserSector', ctypes.c_uint32)
    ]

#typedef struct {
#	char            deviceID[OK_MAX_DEVICEID_LENGTH];
#	char            serialNumber[OK_MAX_SERIALNUMBER_LENGTH];
#	char            productName[OK_MAX_BOARD_MODEL_STRING_LENGTH];
#	int             productID;
#	int             deviceInterface;
#	int             usbSpeed;
#	int             deviceMajorVersion;
#	int             deviceMinorVersion;
#	int             hostInterfaceMajorVersion;
#	int             hostInterfaceMinorVersion;
#	bool            isPLL22150Supported;
#	bool            isPLL22393Supported;
#	bool            isFrontPanelEnabled;
#	int             wireWidth;
#	int             triggerWidth;
#	int             pipeWidth;
#	int             registerAddressWidth;
#	int             registerDataWidth;
#
#	okTFlashLayout  flashSystem;
#	okTFlashLayout  flashFPGA;
#} okTDeviceInfo;

class DeviceInfo(ctypes.Structure):
    _fields_ = [
        ('deviceID', ctypes.c_char * OK_MAX_DEVICEID_LENGTH),
        ('serialNumber', ctypes.c_char * OK_MAX_SERIALNUMBER_LENGTH),
        ('productName', ctypes.c_char * OK_MAX_BOARD_MODEL_STRING_LENGTH),
        ('productID', ctypes.c_int),
        ('deviceInterface', ctypes.c_int),
        ('usbSpeed', ctypes.c_int),
        ('deviceMajorVersion', ctypes.c_int),
        ('deviceMinorVersion', ctypes.c_int),
        ('hostInterfaceMajorVersion', ctypes.c_int),
        ('hostInterfaceMinorVersion', ctypes.c_int),
        ('isPLL22150Supported', ctypes.c_bool),
        ('isPLL22393Supported', ctypes.c_bool),
        ('isFrontPanelEnabled', ctypes.c_bool),
        ('wireWidth', ctypes.c_int),
        ('triggerWidth', ctypes.c_int),
        ('pipeWidth', ctypes.c_int),
        ('registerAddressWidth', ctypes.c_int),
        ('registerDataWidth', ctypes.c_int)
    ]

ok.
