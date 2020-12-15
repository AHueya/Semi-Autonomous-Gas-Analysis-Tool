const int calibrationLed = 13;                      
const int MQ_PIN=A1;                                
int RL_VALUE=5;                                     
float RO_CLEAN_AIR_FACTOR=9.83;                     
                                                    
int CALIBARAION_SAMPLE_TIMES=50;                    
int CALIBRATION_SAMPLE_INTERVAL=500;                
                                                    
int READ_SAMPLE_INTERVAL=50;                        
int READ_SAMPLE_TIMES=5;                            
                                                    
#define GAS_LPG     0   
#define GAS_CO      1   
#define GAS_SMOKE   2    

float LPGCurve[3]   = {2.3,0.21,-0.47};   
 
float COCurve[3]    = {2.3,0.72,-0.34};    
 
float SmokeCurve[3] = {2.3,0.53,-0.44};     // two points are taken from the curve. 
                                            // with these two points, a line is formed which is "approximately equivalent" 
                                            // to the original curve.
                                            // data format:{ x, y, slope}; point1: (lg200, 0.53), point2: (lg10000,  -0.22)                                                     
float Ro = 10;                              // Ro is initialized to 10 kilo ohms          

#define Analog_Input A0
#define CO2_Zero_Ref 55

const float Ref_Voltage = 3.3;     
const int Analog_Pin = A5;

#include <Adafruit_Sensor.h>
#include <DHT.h>

#define DHTPIN 2

#define DHTTYPE DHT22

// Initialize DHT sensor:
DHT dht = DHT(DHTPIN, DHTTYPE);

void setup() {
    Serial.begin(9600);
    pinMode(Analog_Input, INPUT);
  
    pinMode(calibrationLed,OUTPUT);
    digitalWrite(calibrationLed,HIGH);                        
  
    Ro = MQCalibration(MQ_PIN);                                  
    digitalWrite(calibrationLed,LOW);              
                                   
    delay(3000);

    dht.begin();
    delay(2000);
}

void loop() {                               
    int CO2_Conv_PPM = 0;                               
    float Vout = 0;
    long iPPM_LPG = 0;
    long iPPM_CO = 0;
    long iPPM_Smoke = 0;

    Vout = read_O2_Vout();

    //---- Serial Print --------------------------
    //Serial.println(readO2Level());
    //--------------------------------------------
    delay(10);

    CO2_Conv_PPM = read_CO2_Vout();
    
    //---- Serial Print --------------------------
    //Serial.println(CO2_Conv_PPM);
    //--------------------------------------------
    delay(10);

    iPPM_LPG = MQGetGasPercentage(MQRead(MQ_PIN)/Ro,GAS_LPG);
    iPPM_CO = MQGetGasPercentage(MQRead(MQ_PIN)/Ro,GAS_CO);
    iPPM_Smoke = MQGetGasPercentage(MQRead(MQ_PIN)/Ro,GAS_SMOKE);

    //---- Serial Print --------------------------
    //Serial.println("LPG "+iPPM_LPG); 
   
    //Serial.println(iPPM_CO);
    
    //Serial.print(iPPM_Smoke);
    //--------------------------------------------

    delay(10);
 
    float h = dht.readHumidity();
    float t = dht.readTemperature();
    float f = dht.readTemperature(true);

    if (isnan(h) || isnan(t) || isnan(f)) {
      Serial.println("Failed to read from DHT sensor!");
      return;
    }

    //---- Serial Print --------------------------
    Serial.print(f);
    Serial.print(" ");
    Serial.print(h);
    Serial.print(" ");
    Serial.print(readO2Level());
    Serial.print(" ");
    Serial.print(CO2_Conv_PPM);
    Serial.print(" ");
    Serial.print(iPPM_CO);
    Serial.print(" ");
    Serial.println(iPPM_LPG);
    //--------------------------------------------
    
}

float read_O2_Vout() {
    long sum = 0;
    for(int i=0; i<38; i++)
    {
    sum += analogRead(Analog_Pin);
    }
    sum >>= 5;
    float MeasuredVout = sum * (Ref_Voltage / 1023.0);
    return MeasuredVout;
}   // Remember that analog read only reads up to 1023

float readO2Level() {
    float MeasuredVout = read_O2_Vout(); 
    float Concentration = MeasuredVout * 0.21 / 2.0; 
    float Concentration_Percentage=Concentration*100;
    return Concentration_Percentage;
}

float read_CO2_Vout() {
    int Current_CO2_Level[10];                            
    int Raw_CO2_Level = 0;
    int CO2_PPM = 0;
    int zzz = 0;
    
    for (int x = 0;x<10;x++)  // sample CO2 10x over 2 seconds
    {                   
      Current_CO2_Level[x]=analogRead(A0);
      delay(10);
    }

    for (int x = 0;x<10;x++) 
    {                     
      zzz=zzz + Current_CO2_Level[x];  
    } 

    Raw_CO2_Level = zzz/10;                            
    CO2_PPM = Raw_CO2_Level - CO2_Zero_Ref;
    return CO2_PPM;   
}
 
float MQResistanceCalculation(int raw_adc) {
  return ( ((float)RL_VALUE*(1023-raw_adc)/raw_adc));
}
 
float MQCalibration(int mq_pin) {
    int i;
    float val=0;

    for (i=0;i<CALIBARAION_SAMPLE_TIMES;i++) {            //take multiple samples
        val += MQResistanceCalculation(analogRead(mq_pin));
        delay(CALIBRATION_SAMPLE_INTERVAL);
    }
    val = val/CALIBARAION_SAMPLE_TIMES;                   //calculate the average value
    val = val/RO_CLEAN_AIR_FACTOR;                        //divided by RO_CLEAN_AIR_FACTOR yields the Ro                                        
    return val;                                                      //according to the chart in the datasheet 

}
 
float MQRead(int mq_pin) {
    int i;
    float rs=0;
 
    for (i=0;i<READ_SAMPLE_TIMES;i++) {
        rs += MQResistanceCalculation(analogRead(mq_pin));
        delay(READ_SAMPLE_INTERVAL);
    }
 
    rs = rs/READ_SAMPLE_TIMES;
    return rs;  
}
 

long MQGetGasPercentage(float rs_ro_ratio, int gas_id) {
    if ( gas_id == GAS_LPG ) {
        return MQGetPercentage(rs_ro_ratio,LPGCurve);
    } else if ( gas_id == GAS_CO ) {
        return MQGetPercentage(rs_ro_ratio,COCurve);
    } else if ( gas_id == GAS_SMOKE ) {
        return MQGetPercentage(rs_ro_ratio,SmokeCurve);
    }    
 
    return 0;
}
 
long  MQGetPercentage(float rs_ro_ratio, float *pcurve) {
    return (pow(10,( ((log(rs_ro_ratio)-pcurve[1])/pcurve[2]) + pcurve[0])));
}

