# Temperature, Humidity, and Pressure(BME280 Sensor) using a RPi that Broadcasts Data Over MQTT

### Description:
This program was written with the intent to measure temperature, humidity, and pressure using a
Raspberry Pi, and a BME280 Temperature, Humidity, and Pressure sensor. The program sends data to
the serial monitor (console output) and publishes [MQTT](https://mqtt.org/) messages using 
specific topics. A Node Red program is subscribed to all the topics that are published and it
also sends the messages to Home Assistant.

### Parts List and Cost:
- [Raspberry Pi 3 Kit - $59.99](https://vilros.com/products/raspberry-pi-3-complete-starter-kit-clear-case)
- [BME280 Temp, Hum, and PSI Sensor - $8.99](https://www.amazon.com/HiLetgo-Atmospheric-Pressure-Temperature-Humidity/dp/B01N47LZ4P/ref=sr_1_4?crid=1E5WDNIF8YHQE&dib=eyJ2IjoiMSJ9.Alw1tIQnhX14R2JLX8aHhSBi0amC4H9hjB5vSoW7KUgPFC8hqxw3vfTED9-XxGFMRZIOwo5ixUDrIobOd-4Z8NNdsCqj23nuWrlxkfBDoIqvCEIeF_OIgFj9_ydL1TARUQFZQDdXxjR0p9wIbiX9auXzN_eWWScBfDOQs5rDCS-R6FvrHYT5jDBXWES_ZuuNlpp6HM2fN2t9LF_SF6-DYt0Atxm2Zx1B0S4bIQ900vX9tl1DXl_2TZ-L_QVgGBYHGSbDo01KXedpTs1o8Zi_dAJNfIctBY7Zz9zH3zOxEkg.xQK4ZLBuFycCxoK32Yee1UsMiciTACtBbPBETJ3FFHQ&dib_tag=se&keywords=bme280&qid=1723442903&s=hi&sprefix=bme280%2Ctools%2C153&sr=1-4)
- [LED and Resistor Kit - $12.99](https://www.amazon.com/WayinTop-Resistor-Assortment-Respberry-Resistors/dp/B07YWNHZHS/ref=asc_df_B07YWNHZHS/?tag=hyprod-20&linkCode=df0&hvadid=692875362841&hvpos=&hvnetw=g&hvrand=16208490164150483244&hvpone=&hvptwo=&hvqmt=&hvdev=c&hvdvcmdl=&hvlocint=&hvlocphy=9032188&hvtargid=pla-2281435178098&psc=1&mcid=6b20f53b2690311fb884331ab0bbb2b7&hvocijid=16208490164150483244-B07YWNHZHS-&hvexpln=73&gad_source=1)
- [Solderless breadboard and Wire Kit - $16.99](https://www.amazon.com/Breadboard-Jumper-Solderless-Breadboards-Tweezer/dp/B0BNH7LYH3/ref=sr_1_6?crid=3OGVIA5SKNTRJ&dib=eyJ2IjoiMSJ9.NxnfqScIfD6CLdSD3tNGHm0gFDyRkgXWVupXNNPNt7lYG2EIFeMcHNbu6rEaiUiJEHglUUFLqzj2hv2pE2KKczhIp49MDkopJHO1APLRzVN5O0qL6c5qWQQkByYMCQNlF7kd_ENgGVge4JlGZJ1K7379eo9KjGzd4pwPckJjxtaj4-650T1gYObJOiufM-jphH1ICN24KcjsO4agQUVskQLv9beqra2_eDEZA2RgxrwIgSnKummxV3OrnLEXomtweBettE7Xpul_OUaWyFkIzmmwoOVV1xq79Vjo8r6nxD0.8g8ZM_AtSW0n-5x9gn6I6NCEurJ7ue88MdNoOTcLssc&dib_tag=se&keywords=breadboard+kit&qid=1723852435&s=industrial&sprefix=breadboar+kit%2Cindustrial%2C139&sr=1-6)
Nice to Have:
- [GPIO Extension Module - $7.86](https://www.amazon.com/Vbestlife-T-Type-Extension-Adapter-Raspberry/dp/B07MX5T3LM/ref=asc_df_B07MX5T3LM/?tag=hyprod-20&linkCode=df0&hvadid=692875362841&hvpos=&hvnetw=g&hvrand=13347301927716202238&hvpone=&hvptwo=&hvqmt=&hvdev=c&hvdvcmdl=&hvlocint=&hvlocphy=9032188&hvtargid=pla-2281435177418&psc=1&mcid=3fcb503d05db325a8edc2295e6df77ce&hvocijid=13347301927716202238-B07MX5T3LM-&hvexpln=73&gad_source=1)

### Setup:
- #### Wiring:
  * Note: The bread board rows are shorted together on the right(columns a-e) and left(columns f-j) sides.
  * Raspberry Pi with GPIO Extension module installed and plugged into the breasboard. 
  * BME280 pressed into the breadboard with all of the pins in the same column.
     * Jumper wire from the pin labeled D21(SDA) on the ESP to SDA on the BME sensor.
     * Jumper wire from the pin labeled D22(SCL) on the ESP to SCL on the BME sensor.
  * Jumper wire from the pin labeled 3V3 on the ESP to "+" on the BME sensor.
  * Jumper wire from the pin lebeled GND on the ESP to "-" on the BME sensor.
  * [Optional] If using an LED to show when MQTT is connected:
     * The long side of the LED goes to GPIO 5 of the ESP32.
     * Connect the short side of the LED to one leg of the 1K Ohm resistor (both connected to the same row in the breadboard (Columns a-e or f-j)).
     * Connect the other leg of the resistor to ground(or "-" of the power supply).
