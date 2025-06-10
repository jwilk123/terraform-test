import json
import math
import boto3

a = 1.40e-3
b = 2.37e-4
c = 9.90e-8

# Funkcja do obliczania temperatury na podstawie rezystancji
def Steinhart(resistance):
    return round(1.0 / (a + b * math.log(resistance) + c * math.pow(math.log(resistance), 3)) - 273.15, 2)

# Funkcja do wysyłania powiadomienia SNS
def sns_notification(sensor_id, temperature):
    sns = boto3.client('sns')

    message = f'ALERT! Sensor {sensor_id} reported CRITICAL TEMPERATURE: {temperature:.2f}°C'
    
    response = sns.publish(
        TopicArn='arn:aws:sns:us-east-1:136590348108:TemperatureAlerts',
        Message=message,
        Subject='CRITICAL TEMPERATURE ALERT'
    )

    print(f"SNS MessageId: {response['MessageId']}")  # Debug

# Główna funkcja obsługi Lambda
def lambda_handler(event, context):
    data = event

    sensor_id = data.get("sensor_id")
    resistance = data.get("value")

    if sensor_id is None or resistance is None:
        return {
            "statusCode": 400,
            "body": json.dumps({"error": "MISSING VALUE"})
        }

    if not (1 <= resistance <= 20000):
        return {
            "statusCode": 400,
            "body": json.dumps({"error": "VALUE OUT OF RANGE"})
        }

    temperature = Steinhart(resistance)

    if -273.15 <= temperature < 20:
        status = "TEMPERATURE TOO LOW"
    elif 20 <= temperature < 100:
        status = "OK"
    elif 100 <= temperature < 250:
        status = "TEMPERATURE TOO HIGH"
    else:
        status = "TEMPERATURE CRITICAL"
        sns_notification(sensor_id, temperature)  # Wysyłamy email tylko w tym przypadku!

    response = {
        "sensor_id": sensor_id,
        "temperature_C": temperature,
        "status": status
    }

    return {
        "statusCode": 200,
        "body": json.dumps(response)
    }