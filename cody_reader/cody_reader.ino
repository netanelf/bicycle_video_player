
#define CODER_0_PIN_0  2
#define CODER_0_PIN_1  3
#define FAN_PIN        4
#define LOAD_PIN       5
#define BUTTON_0_PIN   6
#define BUTTON_1_PIN   7
#define BUTTON_2_PIN   8
#define SPARE_PIN_0    9
#define SPARE_PIN_1    10
#define SPARE_PIN_2    11
#define SPARE_PIN_3    12
#define SPARE_PIN_4    14
#define SPARE_PIN_5    15
#define JUMPER_PIN_0   16 //DEVICE_ID LSB
#define JUMPER_PIN_1   17 //...
#define JUMPER_PIN_2   18 //...
#define JUMPER_PIN_3   19 //DEVICE ID MSB

#define ILLEGAL   0
#define UP        1
#define DOWN      2
#define NO_CHANGE 3

#define DESIRED_DIRECTION_0 DOWN

#define STOP  LOW
#define START HIGH

#define CODER_0        0
#define BUTTON_0       1
#define BUTTON_1       2
#define BUTTON_2       3
#define PING           4
#define IDENTIFICATION 5
#define BUTTON_OP      6 

int DEVICE_ID; //this is a "semi-define" variable, set once in the setup phase
int DEVICE_ID_MAP[16] = {10, 11, 12, 20, 21, 22, 23, 30, 40, 41, 42, 43, 00, 00, 00, 00}; //"tens" digit = which exhibit, "ones" digit = which arduino inside the exhibit. currently mapping is arbitrary. need to revise.

int poll_result_button_0 = 0x2;
int poll_result_button_1 = 0x2;
int poll_result_button_2 = 0x2;
int poll_result_coder_0  = 0;

int coder_0_movement = ILLEGAL;

volatile unsigned int coder_0_counter = 0;
volatile unsigned int send_data = 0;

char in_char;
String in_command;
int command_complete;

void setup() {
  in_command.reserve(10);
  
  Serial.begin(9600);
  
  pinMode(CODER_0_PIN_0,INPUT_PULLUP);
  pinMode(CODER_0_PIN_1,INPUT_PULLUP);
  
  pinMode(BUTTON_0_PIN,INPUT_PULLUP);
  pinMode(BUTTON_1_PIN,INPUT_PULLUP);
  pinMode(BUTTON_2_PIN,INPUT_PULLUP);  

  pinMode(FAN_PIN,OUTPUT);
  pinMode(LOAD_PIN,OUTPUT);

  pinMode(JUMPER_PIN_0,INPUT_PULLUP);
  pinMode(JUMPER_PIN_1,INPUT_PULLUP);
  pinMode(JUMPER_PIN_2,INPUT_PULLUP);
  pinMode(JUMPER_PIN_3,INPUT_PULLUP);
  
  int bit0 = 1 * digitalRead(JUMPER_PIN_0);
  int bit1 = 2 * digitalRead(JUMPER_PIN_1);
  int bit2 = 4 * digitalRead(JUMPER_PIN_2);
  int bit3 = 8 * digitalRead(JUMPER_PIN_3);

  DEVICE_ID = DEVICE_ID_MAP[bit0 + bit1 + bit2 + bit3];

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
    counter_write(CODER_0);
    send_data = 0;
    check_id_request();
  }
}
       
void counter_write(byte op_id) {
  unsigned int temp_data;
  switch (op_id) {
  case CODER_0 : 
    temp_data = coder_0_counter;
    coder_0_counter = 0;
    break;
  case BUTTON_0 : case BUTTON_1 : case BUTTON_2 :
    temp_data = op_id; //op_id at this stage is differet for each button, we set the data to this temp op_id, and the op id to a one that is common for all buttons
    op_id = BUTTON_OP;
    break;  
  case IDENTIFICATION :
    temp_data = DEVICE_ID;
    break;
  case PING :
    Serial.print("P\n");
    return; //this one is differnt as we need to send only P, hence we return instead of doing the regular break and Serial prints below.
  }
  
  Serial.print(op_id);
  //Serial.print('\n');
  Serial.print(temp_data);
  Serial.print('\n');
  
}

ISR(TIMER1_OVF_vect) {      // interrupt service routine that wraps a user defined function supplied by attachInterrupt
  TCNT1 = 49911;            // reset the timer to the 1sec value
  send_data = 1;
}

void poll_inputs() {
  poll_result_coder_0 = poll_result_coder_0 << 2; //we are reading 2 bits every time so we should get |P1|P0|C1|C0|
  poll_result_coder_0 = digitalRead(CODER_0_PIN_0) ? (poll_result_coder_0 | (0x1 << 0)) : (poll_result_coder_0 & ~(0x1 << 0));  
  poll_result_coder_0 = digitalRead(CODER_0_PIN_1) ? (poll_result_coder_0 | (0x1 << 1)) : (poll_result_coder_0 & ~(0x1 << 1)); 
  coder_0_movement = coder_LUT(poll_result_coder_0);
  if (coder_0_movement == DESIRED_DIRECTION_0) coder_0_counter++;
  
  poll_result_button_0 = poll_result_button_0 << 1;
  poll_result_button_0 = digitalRead(BUTTON_0_PIN) ? (poll_result_button_0 | 0x1) : (poll_result_button_0 & ~0x1);
  poll_result_button_1 = poll_result_button_1 << 1;
  poll_result_button_1 = digitalRead(BUTTON_1_PIN) ? (poll_result_button_1 | 0x1) : (poll_result_button_1 & ~0x1);
  poll_result_button_2 = poll_result_button_2 << 1;
  poll_result_button_2 = digitalRead(BUTTON_2_PIN) ? (poll_result_button_2 | 0x1) : (poll_result_button_2 & ~0x1);
  
  if (poll_result_button_0 == 0x1) counter_write(BUTTON_0);
  if (poll_result_button_1 == 0x1) counter_write(BUTTON_1);
  if (poll_result_button_2 == 0x1) counter_write(BUTTON_2);
}

int coder_LUT(int poll_result) {
  int coder_movement;
  switch (poll_result & 0xF) {
/*  case 0x0:  //00_00
      break;          */
    case 0x1:  //00_01
      coder_movement = UP;
      break;
    case 0x2:  //00_10
      coder_movement = DOWN;
      break;
    case 0x3:  //00_11
      coder_movement = ILLEGAL;
      poll_result_coder_0 >> 2;
      break;
    case 0x4:  //01_00
      coder_movement = DOWN;
      break;
/*  case 0x5:  //01_01
      break;          */
    case 0x6:  //01_10
      coder_movement = ILLEGAL;
      poll_result_coder_0 >> 2;
      break;
    case 0x7:  //01_11
      coder_movement = UP;
      break;
    case 0x8:  //10_00
      coder_movement = UP;
      break;
    case 0x9:  //10_01
      coder_movement = ILLEGAL;
      poll_result_coder_0 >> 2;
      break;
/*  case 0xA:  //10_10
      break;          */
    case 0xB:  //10_11
      coder_movement = DOWN;
      break;
    case 0xC:  //11_00
      coder_movement = ILLEGAL;
      poll_result_coder_0 >> 2;
      break;
    case 0xD:  //11_01
      coder_movement = DOWN;
      break;
    case 0xE:  //11_10
      coder_movement = UP;
      break;
/*    case 0xF:  //11_11
      break;          */      
    default:
      coder_movement = NO_CHANGE;
      break;
  }
  return coder_movement;
}

void check_id_request() {
  command_complete = 0;
  while (Serial.available()) {
    in_char = (char)Serial.read();
    if (in_char == '\n') command_complete = 1; 
    else                 in_command += in_char;
  }
  if (command_complete) {
      if (in_command == "P")      counter_write(PING);
      if (in_command == "who_is") counter_write(IDENTIFICATION);
      if (in_command == "fan_0")  digitalWrite(FAN_PIN,STOP);
      if (in_command == "fan_1")  digitalWrite(FAN_PIN,START);
      if (in_command == "load_0") digitalWrite(LOAD_PIN,STOP);
      if (in_command == "load_1") digitalWrite(LOAD_PIN,START);
      in_command = "";
  }
}



