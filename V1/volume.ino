int val = 0;
void setup() {
  // put your setup code here, to run once:
  Serial.begin(9600);

}

void loop() {
  // put your main code here, to run repeatedly:
  val = analogRead(A0);                      //read potentiometer value
  val = map(val, 0, 1023, 0, 100);
  Serial.println(val);
}
