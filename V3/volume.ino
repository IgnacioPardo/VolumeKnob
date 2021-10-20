int v1, v2, v3, v4;
String json;
void setup() {
  // put your setup code here, to run once:
  Serial.begin(9600);

}

void loop() {
  // put your main code here, to run repeatedly:
  v1 = 100-map(analogRead(A0), 0, 1023, 0, 100);
  v2 = 100-map(analogRead(A1), 0, 1023, 0, 100);
  v3 = 100-map(analogRead(A2), 0, 1023, 0, 100);
  v4 = 100-map(analogRead(A3), 0, 1023, 0, 100);

  json = "{\"0\":"+String(v1)+", \"1\":"+String(v2)+", \"2\":"+String(v3)+", \"3\":"+String(v4)+"}";
  Serial.println(json);
}
