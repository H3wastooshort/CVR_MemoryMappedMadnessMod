#define STOP_PIN A5
void setup() {
  // put your setup code here, to run once:
  for (uint8_t p = A0; p <= STOP_PIN; p++) pinMode(p, INPUT);
  Serial.begin(115200);
}

#define ANALOG_AVG 64
uint16_t analogReadAVG(uint8_t pin) {
  uint32_t val = 0;
  for (uint8_t i = 0; i < ANALOG_AVG; i++) val += analogRead(pin);
  val /= ANALOG_AVG;
  return val;
}

void loop() {
  for (uint8_t p = A0; p <= STOP_PIN; p++) {
    uint16_t n;
    n = analogReadAVG(p);
    Serial.write((char*)(void*)&n,2);
  }
  Serial.write(42);
  Serial.print("EndOfPkg\n");
  //delay(10);
}
