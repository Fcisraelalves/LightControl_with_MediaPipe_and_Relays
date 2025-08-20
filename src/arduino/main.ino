#define LED1 2
#define LED2 3
#define LED3 4
#define LED4 5
#define LED5 6

int leds[] = {LED1, LED2, LED3, LED4, LED5};

void apagarTodos() {
  for (int i = 0; i < 5; i++) {
    digitalWrite(leds[i], LOW);
  }
}

void setup() {
  Serial.begin(9600); 

  for (int i = 0; i < 5; i++) {
    pinMode(leds[i], OUTPUT);
  }

  apagarTodos(); 
}

void loop() {
  if (Serial.available() > 0) {
    String dedos = Serial.readStringUntil('\n'); 

    if (dedos.length() == 5) { 
      for (int i = 0; i < 5; i++) {
        if (dedos[i] == '1') {
          digitalWrite(leds[i], HIGH);
        } else {
          digitalWrite(leds[i], LOW);
        }
      }
    }
  } 
  else {
    apagarTodos();
  }
}
