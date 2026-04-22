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
