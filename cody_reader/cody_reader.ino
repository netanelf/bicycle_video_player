
#define CODER_0_PIN_0 2
#define CODER_0_PIN_1 3

#define NUM_OF_CODERS 1

#define ILLEGAL   0
#define UP        1
#define DOWN      2
#define NO_CHANGE 3

#define DESIRED_DIRECTION_0 DOWN

int poll_result_0       = 0;
int coder_0_movement    = ILLEGAL;
int illegal_0_counter   = 0;

volatile unsigned int coder_0_counter = 0;
volatile unsigned int coder_1_counter = 0;
volatile unsigned int send_data = 0;

void setup() {
  Serial.begin(9600);
  
  pinMode(CODER_0_PIN_0,INPUT);
  pinMode(CODER_0_PIN_1,INPUT);

  // initialize timer1 
  noInterrupts();           // disable all interrupts
  TCCR1A = 0;
  TCCR1B = 0;

  TCNT1 = 49911;            // preload timer 65536-16MHz/1024 -> ~1sec until overflow, need to set this value on every call to interrupt routine
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
  unsigned int temp_data;
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
  Serial.print(temp_data);
  Serial.print('\n');
  
}

ISR(TIMER1_OVF_vect) {      // interrupt service routine that wraps a user defined function supplied by attachInterrupt
  TCNT1 = 49911;            // reset the timer to the 1sec value
  send_data = 1;
}

void poll_inputs() {
  if (NUM_OF_CODERS > 0) {
    poll_result_0 = poll_result_0 << 2; //we are reading 2 bits every time so we should get |P1|P0|C1|C0|
    poll_result_0 = digitalRead(CODER_0_PIN_0) ? (poll_result_0 | (0x1 << 0)) : (poll_result_0 & ~(0x1 << 0));  
    poll_result_0 = digitalRead(CODER_0_PIN_1) ? (poll_result_0 | (0x1 << 1)) : (poll_result_0 & ~(0x1 << 1)); 
  }

  switch (poll_result_0 & 0xF) {
/*  case 0x0:  //00_00
      break;          */
    case 0x1:  //00_01
      coder_0_movement = UP;
      break;
    case 0x2:  //00_10
      coder_0_movement = DOWN;
      break;
    case 0x3:  //00_11
      coder_0_movement = ILLEGAL;
      poll_result_0 >> 2;
      break;
    case 0x4:  //01_00
      coder_0_movement = DOWN;
      break;
/*  case 0x5:  //01_01
      break;          */
    case 0x6:  //01_10
      coder_0_movement = ILLEGAL;
      poll_result_0 >> 2;
      break;
    case 0x7:  //01_11
      coder_0_movement = UP;
      break;
    case 0x8:  //10_00
      coder_0_movement = UP;
      break;
    case 0x9:  //10_01
      coder_0_movement = ILLEGAL;
      poll_result_0 >> 2;
      break;
/*  case 0xA:  //10_10
      break;          */
    case 0xB:  //10_11
      coder_0_movement = DOWN;
      break;
    case 0xC:  //11_00
      coder_0_movement = ILLEGAL;
      poll_result_0 >> 2;
      break;
    case 0xD:  //11_01
      coder_0_movement = DOWN;
      break;
    case 0xE:  //11_10
      coder_0_movement = UP;
      break;
/*    case 0xF:  //11_11
      break;          */      
    default:
      coder_0_movement = NO_CHANGE;
      break;
  }

  if (coder_0_movement == DESIRED_DIRECTION_0) coder_0_counter++;
}


