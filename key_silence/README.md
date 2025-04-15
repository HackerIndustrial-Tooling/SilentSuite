# Key_Silence 
**KeySilence** silently unlocks macOS Keychain and extracts Chrome Safe Storage credentials using native macOS APIs with no `security` binary calls—bypassing typical EDR detection techniques.


Functionally:
 - Unlocks macOS Keychain silently
 - Extracts the Chrome Safe Storage key
 - Uses ctypes to avoid detection (no security binary call)

Detection:
- Bypasses Falcon's "security binary" matching filter.
- Requires chaining with a TCC bypass for preventing the popup (Or spam SE until they accept)




