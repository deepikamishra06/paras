from gpiozero import LED
import serial
import time

# Configure the GPIO pin for the LED
LED_PIN_24 = 24
led_24 = LED(LED_PIN_24)

# Configure the serial connection to the SIM800L
ser = serial.Serial(
    port='/dev/ttyUSB0',  # Replace with your port if different
    baudrate=9600,
    timeout=1
)

# Read saved numbers from shortcodes.txt
with open('shortcodes.txt', 'r') as f:
    saved_numbers = [line.strip() for line in f]

def blink_led(led, blink_count=1, blink_duration=5.0):
    """Blink the specified LED a number of times."""
    for _ in range(blink_count):
        led.on()
        time.sleep(blink_duration)
        led.off()
        time.sleep(blink_duration)

def process_incoming_call():
    print("Incoming call detected")
    ser.write(b'ATA\r')  # Answer the call
    time.sleep(2)  # Give some time to ensure the command is processed
    response = ser.read(ser.in_waiting).decode('utf-8').strip()
    print(f"Response to ATA: {response}")
    if "OK" in response or "CONNECT" in response:
        print("Call answered successfully")
        blink_led(led_24)  # Blink LED when call is picked up
    else:
        print("Failed to answer call")

def main():
    try:
        ser.write(b'AT+CLIP=1\r')  # Enable caller ID notification
        while True:
            if ser.in_waiting > 0:
                response = ser.readline().decode('utf-8').strip()
                print(f"Response: {response}")
                if response.startswith('+CLIP:'):
                    caller_id = response.split('"')[1]
                    print(f"Caller ID: {caller_id}")
                    if caller_id in saved_numbers:
                        process_incoming_call()
                elif response.startswith('RING'):
                    print("RING detected")
                elif response.startswith('NO CARRIER'):
                    print("Call ended")
    except KeyboardInterrupt:
        pass
    finally:
        ser.close()

if __name__ == '__main__':
    main()

