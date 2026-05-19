# ESP32 Detection Code Snippets

> These are standalone Arduino code snippets for reference.
> The production detection logic lives in `Security_hub.ino`.

---

## Brute Force Detection (Arduino)

Detects rapid successive login attempts by tracking frequency within a 2-second window.

```cpp
int loginAttempts = 0;
unsigned long lastAttemptTime = 0;

void detectBruteForce() {
    unsigned long currentTime = millis();

    if (currentTime - lastAttemptTime < 2000) {
        loginAttempts++;
    } else {
        loginAttempts = 1;
    }

    lastAttemptTime = currentTime;

    if (loginAttempts > 5) {
        Serial.println("BRUTE FORCE DETECTED");
        attackLabel = "ATTACK";
    }
}
```

**Integration note:** Call `detectBruteForce()` inside the MQTT `callback()` function
whenever a command with `action == "AUTH"` or a PIN attempt is received.
