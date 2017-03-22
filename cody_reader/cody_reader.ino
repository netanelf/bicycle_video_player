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

#define NUM_OF_CODERS 1

#define CODER_LIMIT   100

//these defines set the desired direction of the coders, 0 for one direction 1 for the other
#define C0_DIRECTION 1 
#define C1_DIRECTION 1 

byte poll_result;
byte coder_0_changed = 0;
byte coder_1_changed = 0;

byte coder_0_changed_prev = 0;
byte coder_1_changed_prev = 0;

volatile int coder_0_counter = 0;
volatile int coder_1_counter = 0;
volatile byte send_data = 0;

void setup() {
  Serial.begin(9600);
  
  pinMode(CODER_0_PIN_0,INPUT);
  pinMode(CODER_0_PIN_1,INPUT);
  pinMode(CODER_1_PIN_0,INPUT);
  pinMode(CODER_1_PIN_1,INPUT);

  // initialize timer1 
  noInterrupts();           // disable all interrupts
  TCCR1A = 0;
  TCCR1B = 0;

  TCNT1 = 34286;            // preload timer 65536-16MHz/1024 -> ~1sec until overflow, need to set this value on every call to interrupt routine
  TCCR1B |= (1 << CS12) | (1 << CS10);    // 1024 prescaler 
  TIMSK1 |= (1 << TOIE1);   // enable timer overflow interrupt
  interrupts();             // enable all interrupts
}

void loop() {
  poll_inputs();
  if (send_data) {
    if (NUM_OF_CODERS > 0) counter_write(0);
    if (NUM_OF_CODERS > 1) counter_write(1);
    send_data = 0;
  }
}

void counter_write(byte op_id) {
  byte temp_data;
  switch (op_id) {
  case 0 : //coder_0
    temp_data = coder_0_counter;
    coder_0_counter = 0;
    break;
  case 1 : //coder_1
    temp_data = coder_1_counter;
    coder_1_counter = 0;
    break;
  case 2 : //button_0
    //TODO
    break;  
  case 3 : //button_1
    //TODO
    break;  
  case 4 : //button_2
    //TODO
    break;  
  }
  Serial.print(op_id);
  Serial.print('\n');
  Serial.print(temp_data);
  Serial.print('\n');
}

ISR(TIMER1_OVF_vect) {      // interrupt service routine that wraps a user defined function supplied by attachInterrupt
  TCNT1 = 49911;            // reset the timer to the 1sec value
  send_data = 1;
}

void poll_inputs() {
    
  //shift one bit left is equivalent to setting the current vals bits into the prev vals bits
  poll_result = poll_result << 1;

  //set the read vals to the current vals bits and check if there is a change
  if (NUM_OF_CODERS > 0) {
    poll_result = digitalRead(CODER_0_PIN_0) ? (poll_result | (0x1 << POS_C0P0_CUR)) : (poll_result & ~(0x1 << POS_C0P0_CUR));  
    poll_result = digitalRead(CODER_0_PIN_1) ? (poll_result | (0x1 << POS_C0P1_CUR)) : (poll_result & ~(0x1 << POS_C0P1_CUR));    
    if ( ( (((poll_result & (0x1 << POS_C0P0_CUR)) >> POS_C0P0_CUR) ^ ((poll_result & (0x1 << POS_C0P0_PREV)) >> POS_C0P0_PREV)) ^ 
           (((poll_result & (0x1 << POS_C0P1_CUR)) >> POS_C0P1_CUR) ^ ((poll_result & (0x1 << POS_C0P1_PREV)) >> POS_C0P1_PREV) )) ) {
      coder_0_changed =  C0_DIRECTION &  ((poll_result &  (0x1 << POS_C0P0_CUR)) ^ (poll_result & (0x1 << POS_C0P1_PREV))) |
                        ~C0_DIRECTION & ~((poll_result &  (0x1 << POS_C0P0_CUR)) ^ (poll_result & (0x1 << POS_C0P1_PREV))) ;
    }
  }
  if (NUM_OF_CODERS > 1) {
    poll_result = digitalRead(CODER_1_PIN_0) ? (poll_result | (0x1 << POS_C1P0_CUR)) : (poll_result & ~(0x1 << POS_C1P0_CUR));  
    poll_result = digitalRead(CODER_1_PIN_1) ? (poll_result | (0x1 << POS_C1P1_CUR)) : (poll_result & ~(0x1 << POS_C1P1_CUR));  
    if ( ((poll_result & (0x1 << POS_C1P0_CUR)) ^ (poll_result & (0x1 << POS_C1P0_PREV))) ^ 
         ((poll_result & (0x1 << POS_C1P1_CUR)) ^ (poll_result & (0x1 << POS_C1P1_PREV))) ) {
      coder_1_changed =  C1_DIRECTION &  ((poll_result &  (0x1 << POS_C1P0_CUR)) ^ (poll_result & (0x1 << POS_C1P1_PREV))) |
                        ~C1_DIRECTION & ~((poll_result &  (0x1 << POS_C1P0_CUR)) ^ (poll_result & (0x1 << POS_C1P1_PREV))) ;
    }
  }

  if (coder_0_changed) {
    coder_0_counter++;
    coder_0_changed = 0;
  }
  if (coder_1_changed) {
    coder_1_counter++;
    coder_1_changed = 0;
  }
}

