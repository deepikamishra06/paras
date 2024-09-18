import RPi.GPIO as GPIO
import serial
import time
import threading
from flask import Flask, request, render_template, redirect, url_for

# Configure GPIO mode
GPIO.setmode(GPIO.BCM)

# GPIO pin numbers
LED_PIN_24 = 24
LED_PIN_14 = 14
LED_PIN_15 = 15

# Set up GPIO pins for LEDs
GPIO.setup(LED_PIN_24, GPIO.OUT)
GPIO.setup(LED_PIN_14, GPIO.OUT)
GPIO.setup(LED_PIN_15, GPIO.OUT)

# Configure the serial connection to the SIM800A
ser = serial.Serial(
    port='/dev/ttyUSB0',  # Replace with your port if different
    baudrate=9600,
    timeout=5  # Increased timeout
)

# Initialize Flask app
app = Flask(__name__)

# Read saved numbers and their corresponding strings from phnno.txt
phonebook = {}
with open('/home/raspi4/paras/tools/phnno.txt', 'r') as f:
    for line in f:
        parts = line.strip().split(',')
        if len(parts) == 2:
            key = parts[0].strip()  # Arbitrary string
            number = parts[1].strip()  # Associated phone number
            phonebook[key] = number

def blink_led(led_pin, blink_count=1, blink_duration=0.5):
    """Blink the specified LED a number of times."""
    for _ in range(blink_count):
        GPIO.output(led_pin, GPIO.HIGH)
        time.sleep(blink_duration)
        GPIO.output(led_pin, GPIO.LOW)
        time.sleep(blink_duration)

def process_incoming_call():
    print("Incoming call detected")
    time.sleep(1)  # Add a delay before sending ATA
    ser.write(b'ATA\r')  # Answer the call
    time.sleep(3)  # Increased delay to ensure the command is processed
    response = ser.read(ser.in_waiting).decode('utf-8').strip()
    print(f"Response to ATA: {response}")
    if "OK" in response or "CONNECT" in response:
        print("Call answered successfully")
        # blink_led(LED_PIN_24)
    else:
        print("Failed to answer call")

def reenable_dtmf_detection():
    ser.write(b'AT+DDET=1\r')  # Re-enable DTMF detection
    print("DTMF detection re-enabled")

def make_call(phone_number):
    """Initiate a call to the specified phone number."""
    print(f"Dialing {phone_number}...")
    ser.write(f'ATD{phone_number};\r'.encode())  # The ";" at the end makes it a voice call
    time.sleep(2)  # Short delay before checking the response
    response = ser.read(ser.in_waiting).decode('utf-8').strip()
    print(f"Response to ATD: {response}")
    if "OK" in response or "CONNECT" in response or "RINGING" in response:
        print("Call initiated successfully")
    else:
        print("Failed to initiate call")

def handle_sim800a_responses():
    """Handle incoming responses from the SIM800A module."""
    while True:
        if ser.in_waiting > 0:
            response = ser.readline().decode('utf-8').strip()
            if response:
                print(f"Response: {response}")
                if response.startswith('+CLIP:'):
                    caller_id = response.split('"')[1]
                    print(f"Caller ID: {caller_id}")
                    if caller_id in phonebook.values():
                        process_incoming_call()
                elif response.startswith('+DTMF:'):
                    dtmf_tone = response.split(':')[1].strip()
                    print(f"DTMF Tone: {dtmf_tone}")
                    if dtmf_tone == '1':
                        blink_led(LED_PIN_14)
                    elif dtmf_tone == '2':
                        blink_led(LED_PIN_15)
                elif response.startswith('RING'):
                    print("RING detected")
                elif response.startswith('NO CARRIER'):
                    print("Call ended")
                    reenable_dtmf_detection()  # Re-enable DTMF detection after call ends
                else:
                    print("Unknown response, no action taken.")
            else:
                print("No response or empty response.")

def listen_for_input():
    """Listen for user input to initiate a call."""
    while True:
        user_input = input("Enter the shortcode to make a call: ").strip()
        if user_input in phonebook:
            make_call(phonebook[user_input])
        else:
            print(f"No phone number associated with '{user_input}' in the phonebook.")

@app.route('/')
def index():
    return render_template('index.html', phonebook=phonebook)

@app.route('/make_call', methods=['POST'])
def make_call_from_web():
    shortcode = request.form.get('shortcode')
    if shortcode in phonebook:
        make_call(phonebook[shortcode])
        return redirect(url_for('index', status='Call initiated successfully'))
    else:
        return redirect(url_for('index', status='Invalid code or phone number not found.'))

@app.route('/add_number', methods=['POST'])
def add_number():
    shortcode = request.form.get('shortcode')
    phone_number = request.form.get('phone_number')
    if shortcode and phone_number:
        phonebook[shortcode] = phone_number
        with open('/home/raspi4/paras/tools/phnno.txt', 'a') as f:
            f.write(f'{shortcode},{phone_number}\n')
        return redirect(url_for('index', status='Number added successfully'))
    return redirect(url_for('index', status='Failed to add number'))

@app.route('/delete_number', methods=['POST'])
def delete_number():
    shortcode = request.form.get('shortcode')
    if shortcode in phonebook:
        del phonebook[shortcode]
        with open('/home/raspi4/paras/tools/phnno.txt', 'w') as f:
            for sc, num in phonebook.items():
                f.write(f'{sc},{num}\n')
        return redirect(url_for('index', status='Number deleted successfully'))
    return redirect(url_for('index', status='Shortcode not found'))

def main():
    time.sleep(10)  # Wait for 10 seconds for the SIM800A to fully initialize
    try:
        ser.write(b'AT+CLIP=1\r')  # Enable caller ID notification
        reenable_dtmf_detection()  # Enable DTMF detection initially

        # Start a thread to handle SIM800A responses
        response_thread = threading.Thread(target=handle_sim800a_responses, daemon=True)
        response_thread.start()

        # Start Flask app
        app.run(host='0.0.0.0', port=5000, debug=True)

    except KeyboardInterrupt:
        pass
    finally:
        ser.close()
        GPIO.cleanup()

if __name__ == '__main__':
    main()

