## The Case

Computer labs and server rooms overheat quietly. The project set out to read temperature and
humidity continuously, push the readings to the cloud so they can be seen from anywhere, and
show them on a dashboard that makes a problem visible at a glance. The deck lists four reasons:
energy efficiency (cooling decisions based on real data), device safety (no overheating), cloud
accessibility (no geographic limit), and real-time analysis (fast response to sudden changes).

## Key Findings

- **Use the managed broker.** AWS IoT Core replaces a self-run MQTT server and brings device
  identity with it: each ESP32 carries its own X.509 certificate and private key, connects over
  TLS, and is limited by an IoT policy to the topics it needs.
- **Keep the device simple.** The ESP32 does three things: read the DHT22, connect to Wi-Fi,
  and publish a small JSON payload. Everything else, from logic to visualisation, lives in
  Node-RED where it can be changed without reflashing.
- **Reliability is a protocol setting.** MQTT quality-of-service levels cover delivery
  guarantees; the deck names QoS as the mechanism that makes messages arrive reliably.

## Infrastructure

Hardware: an ESP32 development board (dual-core 240 MHz, Wi-Fi and Bluetooth, low power, TLS
capable) and a DHT22 digital sensor (temperature -40 to 80 °C with ±0.5 °C accuracy, humidity
0 to 100% RH with ±2% RH accuracy) on a breadboard with jumper wires. Cloud: an AWS IoT Core
thing with a certificate and policy. Processing: a Node-RED instance with the dashboard nodes.

## Application

Firmware written in the Arduino IDE reads the sensor on a fixed interval and publishes a JSON
object with the temperature and humidity to an MQTT topic on the IoT Core endpoint. Node-RED
subscribes to that topic, parses the payload, and feeds gauge widgets, a 24-hour line chart,
and alert logic that changes colour when the temperature exceeds a threshold such as 30 °C.

## Security

Device authentication uses an X.509 certificate and TLS end-to-end between the ESP32 and AWS.
An AWS IoT policy restricts the device's rights to specific topics. No shared password travels
over the network.

## Result

The deck reports stable monitoring with a transmission delay under one second on AWS. That
figure comes from the presentation; no measurement log was kept, and the dashboard image in the
deck is the Node-RED reference dashboard rather than a screenshot of this system. The firmware,
cloud configuration, and flow were implemented but not documented beyond the presentation.

Planned extensions, none of them built: Telegram bot notifications, InfluxDB storage for yearly
audits, and automatic air-conditioning control through a relay.
