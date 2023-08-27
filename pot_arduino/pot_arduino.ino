#define STOP_PIN A5
void setup() {
  // put your setup code here, to run once:
  for (uint8_t p = A0; p <= STOP_PIN; p++) pinMode(p, INPUT);
  Serial.begin(115200);
}

#define ANALOG_AVG 20
uint16_t analogReadAVG(uint8_t pin) {
  uint32_t val = 0;
  for (uint8_t i = 0; i < ANALOG_AVG; i++) val += analogRead(pin);
  val /= ANALOG_AVG;
  return val;
}

void loop() {
  for (uint8_t p = A0; p <= STOP_PIN; p++) {
    Serial.write(uint8_t(analogReadAVG(p)/4));
  }
  Serial.write(42);
  Serial.print("END\n");
  delay(10);
}
