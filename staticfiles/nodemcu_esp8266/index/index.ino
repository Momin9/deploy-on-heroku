#include <ESP8266WiFi.h>
#include <WiFiUdp.h>

#include <Arduino_JSON.h>
#include <WiFiClientSecure.h>
#include <ESP8266HTTPClient.h>

// Root certificate for howsmyssl.com
const char IRG_Root_X1 [] PROGMEM = R"CERT(
-----BEGIN CERTIFICATE-----
MIIFazCCA1OgAwIBAgIRAIIQz7DSQONZRGPgu2OCiwAwDQYJKoZIhvcNAQELBQAw
TzELMAkGA1UEBhMCVVMxKTAnBgNVBAoTIEludGVybmV0IFNlY3VyaXR5IFJlc2Vh
cmNoIEdyb3VwMRUwEwYDVQQDEwxJU1JHIFJvb3QgWDEwHhcNMTUwNjA0MTEwNDM4
WhcNMzUwNjA0MTEwNDM4WjBPMQswCQYDVQQGEwJVUzEpMCcGA1UEChMgSW50ZXJu
ZXQgU2VjdXJpdHkgUmVzZWFyY2ggR3JvdXAxFTATBgNVBAMTDElTUkcgUm9vdCBY
MTCCAiIwDQYJKoZIhvcNAQEBBQADggIPADCCAgoCggIBAK3oJHP0FDfzm54rVygc
h77ct984kIxuPOZXoHj3dcKi/vVqbvYATyjb3miGbESTtrFj/RQSa78f0uoxmyF+
0TM8ukj13Xnfs7j/EvEhmkvBioZxaUpmZmyPfjxwv60pIgbz5MDmgK7iS4+3mX6U
A5/TR5d8mUgjU+g4rk8Kb4Mu0UlXjIB0ttov0DiNewNwIRt18jA8+o+u3dpjq+sW
T8KOEUt+zwvo/7V3LvSye0rgTBIlDHCNAymg4VMk7BPZ7hm/ELNKjD+Jo2FR3qyH
B5T0Y3HsLuJvW5iB4YlcNHlsdu87kGJ55tukmi8mxdAQ4Q7e2RCOFvu396j3x+UC
B5iPNgiV5+I3lg02dZ77DnKxHZu8A/lJBdiB3QW0KtZB6awBdpUKD9jf1b0SHzUv
KBds0pjBqAlkd25HN7rOrFleaJ1/ctaJxQZBKT5ZPt0m9STJEadao0xAH0ahmbWn
OlFuhjuefXKnEgV4We0+UXgVCwOPjdAvBbI+e0ocS3MFEvzG6uBQE3xDk3SzynTn
jh8BCNAw1FtxNrQHusEwMFxIt4I7mKZ9YIqioymCzLq9gwQbooMDQaHWBfEbwrbw
qHyGO0aoSCqI3Haadr8faqU9GY/rOPNk3sgrDQoo//fb4hVC1CLQJ13hef4Y53CI
rU7m2Ys6xt0nUW7/vGT1M0NPAgMBAAGjQjBAMA4GA1UdDwEB/wQEAwIBBjAPBgNV
HRMBAf8EBTADAQH/MB0GA1UdDgQWBBR5tFnme7bl5AFzgAiIyBpY9umbbjANBgkq
hkiG9w0BAQsFAAOCAgEAVR9YqbyyqFDQDLHYGmkgJykIrGF1XIpu+ILlaS/V9lZL
ubhzEFnTIZd+50xx+7LSYK05qAvqFyFWhfFQDlnrzuBZ6brJFe+GnY+EgPbk6ZGQ
3BebYhtF8GaV0nxvwuo77x/Py9auJ/GpsMiu/X1+mvoiBOv/2X/qkSsisRcOj/KK
NFtY2PwByVS5uCbMiogziUwthDyC3+6WVwW6LLv3xLfHTjuCvjHIInNzktHCgKQ5
ORAzI4JMPJ+GslWYHb4phowim57iaztXOoJwTdwJx4nLCgdNbOhdjsnvzqvHu7Ur
TkXWStAmzOVyyghqpZXjFaH3pO3JLF+l+/+sKAIuvtd7u+Nxe5AW0wdeRlN8NwdC
jNPElpzVmbUq4JUagEiuTDkHzsxHpFKVK7q4+63SM1N95R1NbdWhscdCb+ZAJzVc
oyi3B43njTOQ5yOf+1CceWxG1bQVs5ZufpsMljq4Ui0/1lvh+wjChP4kqKOJ2qxq
4RgqsahDYVvTH9w7jXbyLeiNdd8XM2w9U/t7y0Ff/9yi0GE44Za4rF2LN9d11TPA
mRGunUHBcnWEvgJBQl9nJEiU0Zsnvgc/ubhPgXRR4Xq37Z0j4r7g1SgEEzwxA57d
emyPxgcYxn/eR44/KJ4EBs+lVDR3veyJm+kXQ99b21/+jh5Xos1AnX5iItreGCc=
-----END CERTIFICATE-----
)CERT";


X509List cert(IRG_Root_X1);

void setup()
{
  int retry = 0, config_done = 0;

  // configure WiFi in Station Mode
  WiFi.mode(WIFI_STA);
  WiFi.setAutoReconnect(true);
  WiFi.reconnect();
  WiFi.persistent(true);

  // Set time via NTP, as required for x.509 validation
  configTime(3 * 3600, 0, "pool.ntp.org", "time.nist.gov");

  // configure serial port baud rate
  Serial.begin(9600);

  // configure on-board LED as output pin
  pinMode(16, OUTPUT);

  // turn LED on
  digitalWrite(16, LOW);

  delay(1000);
  // check whether WiFi connection can be established
  Serial.println("Attempt to connect to WiFi network…");
  while (WiFi.status() != WL_CONNECTED){
    Serial.print(".");
    delay(500);
    if (retry++ >= 20) // timeout for connection is 10 seconds
    {
      Serial.println("Connection timeout expired! Start SmartConfig…");
      WiFi.beginSmartConfig();
      // forever loop: exit only when SmartConfig packets have been received
      while (true)
      {
        delay(500);
        Serial.print(".");
        if (WiFi.smartConfigDone())
        {
          Serial.println("nSmartConfig successfully configured");
          config_done = 1;
          break; // exit from loop
        }
        toggleLED();
      }
      if (config_done == 1)
        break;
    }
  }
  // turn LED off
  digitalWrite(16, HIGH);

  // wait for IP address assignment
  while (WiFi.status() != WL_CONNECTED)
  {
    delay(50);
  }
  // show WiFi connection data
  Serial.println(".");
  WiFi.printDiag(Serial);

  // show the IP address assigned to our device
  Serial.println(WiFi.localIP());
}

// GET REQUEST METHOD
String httpGETRequest(const char* serverName) {

  WiFiClientSecure client;

  client.setTrustAnchors(&cert);

  HTTPClient http;

  http.begin(client, serverName);

  int httpResponseCode = http.GET();
  
  String payload = "{}"; 
  
  if (httpResponseCode>0) {
    Serial.print("HTTP Response code: ");
    Serial.println(httpResponseCode);
    payload = http.getString();
  }
  else {
    Serial.print("Error code: ");
    Serial.println(httpResponseCode);
  }
  http.end();

  JSONVar myObject = JSON.parse(payload);

  if (JSON.typeof(myObject) == "undefined") {
    Serial.println("Parsing input failed!");
    // return;
  }
  Serial.print("JSON object = ");
  Serial.println(myObject);
  return myObject;
}

// POST REQUEST METHOD
String httpPostRequest(const char* serverName, const char* body){

  WiFiClientSecure client;

  client.setTrustAnchors(&cert);

  HTTPClient http;

  http.begin(client, serverName);
  http.addHeader("Content-Type", "application/json");

  int httpResponseCode = http.POST(body);
  
  String payload = "{}"; 
  
  if (httpResponseCode == HTTP_CODE_CREATED) {
    Serial.print("HTTP Response code: ");
    Serial.println(httpResponseCode);
    payload = http.getString();
  }
  else {
    Serial.print("Error code: ");
    Serial.println(httpResponseCode);
  }
  http.end();

  Serial.println(payload);
  return payload;
}

// PUT REQUEST METHOD
String httpPutRequest(const char* serverName, const char* body){

  WiFiClientSecure client;

  client.setTrustAnchors(&cert);

  HTTPClient http;

  http.begin(client, serverName);
  http.addHeader("Content-Type", "application/json");

  int httpResponseCode = http.PUT(body);
  
  String payload = "{}"; 
  
  if (httpResponseCode > 0) {
    Serial.print("HTTP Response code: ");
    Serial.println(httpResponseCode);
    payload = http.getString();
  }
  else {
    Serial.print("Error code: ");
    Serial.println(httpResponseCode);
  }
  http.end();

  Serial.println(payload);
  return payload;
}

void loop()
{
  if (WiFi.status() == WL_CONNECTED) {
    // GET REQUEST
    httpGETRequest("https://jsonplaceholder.typicode.com/users/1");


    // POST REQUEST
    // String myObject = "{\"userId\": 1, \"title\": \"Aamir\", \"body\": \"est rerum tempore vitae\"}";
    // // httpPostRequest("https://jsonplaceholder.typicode.com/posts", myObject.c_str());
    // httpPutRequest("https://jsonplaceholder.typicode.com/posts/1", myObject.c_str());

  }
  delay(5000);
}

void toggleLED()
{
  static int pinStatus = LOW;

  if (pinStatus == HIGH)
    pinStatus = LOW;
  else
    pinStatus = HIGH;

  digitalWrite(16, pinStatus);
}