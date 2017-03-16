#define CODER_0_PIN_0 2
#define CODER_0_PIN_1 3
#define CODER_1_PIN_0 4
#define CODER_1_PIN_1 5

#define POS_C0P0_CUR  0
#define POS_C0P0_PREV 1
#define POS_C0P1_CUR  2
#define POS_C0P1_PREV 3
#define POS_C1P0_CUR  4
#define POS_C1P0_PREV 5
#define POS_C1P1_CUR  6
#define POS_C1P1_PREV 7

#define NUM_OF_CODERS 2

#define CODER_LIMIT   100

byte poll_result;
byte coder_0_changed = 0;
byte coder_1_changed = 0;

int coder_0_counter = 0;
int coder_1_counter = 0;

void setup() {
  Serial.begin(9600);
  
  pinMode(CODER_0_PIN_0,INPUT);
  pinMode(CODER_0_PIN_1,INPUT);
  pinMode(CODER_1_PIN_0,INPUT);
  pinMode(CODER_1_PIN_1,INPUT);
}

void loop() {
  poll_inputs();
}

void serial_write(byte coder_num) {
  Serial.write(coder_num);
  if (coder_num == 0) coder_0_counter = 0;
  if (coder_num == 1) coder_1_counter = 0;
}

void poll_inputs() {
    
  //shift one bit left is equivalent to setting the current vals bits into the prev vals bits
  poll_result = poll_result << 1;

  //set the read vals to the current vals bits and check if there is a change
  if (NUM_OF_CODERS > 0) {
    poll_result = digitalRead(CODER_0_PIN_0) ? (poll_result | (0x1 << POS_C0P0_CUR)) : (poll_result & ~(0x1 << POS_C0P0_CUR));  
    poll_result = digitalRead(CODER_0_PIN_1) ? (poll_result | (0x1 << POS_C0P1_CUR)) : (poll_result & ~(0x1 << POS_C0P1_CUR));  
    coder_0_changed = ((poll_result & (0x1 << POS_C0P0_CUR)) ^ ((poll_result & (0x1 << POS_C0P0_PREV)))) || ((poll_result & (0x1 << POS_C0P1_CUR)) ^ ((poll_result & (0x1 << POS_C0P1_PREV))));
  }
  if (NUM_OF_CODERS > 1) {
    poll_result = digitalRead(CODER_1_PIN_0) ? (poll_result | (0x1 << POS_C1P0_CUR)) : (poll_result & ~(0x1 << POS_C1P0_CUR));  
    poll_result = digitalRead(CODER_1_PIN_1) ? (poll_result | (0x1 << POS_C1P1_CUR)) : (poll_result & ~(0x1 << POS_C1P1_CUR));  
    coder_1_changed = ((poll_result & (0x1 << POS_C1P0_CUR)) ^ ((poll_result & (0x1 << POS_C1P0_PREV)))) || ((poll_result & (0x1 << POS_C1P1_CUR)) ^ ((poll_result & (0x1 << POS_C1P1_PREV))));
  }

  if (coder_0_changed) coder_0_counter++;
  if (coder_1_changed) coder_1_counter++;

  if (coder_0_counter == CODER_LIMIT) serial_write(0);
  if (coder_1_counter == CODER_LIMIT) serial_write(1);
}

