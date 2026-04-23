import boto3
import os
from decimal import Decimal
from botocore.exceptions import ClientError
from dotenv import load_dotenv

load_dotenv()

def connect_to_dynamodb():
    endpoint = os.getenv('DYNAMODB_ENDPOINT', 'http://dynamodb-local:8000')
    try:
        dynamodb = boto3.resource('dynamodb',
            region_name=os.getenv('AWS_DEFAULT_REGION'),
            aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
            endpoint_url=endpoint
        )
        print(f"Connecté à DynamoDB via {endpoint}")
        return dynamodb
    except Exception as e:
        print(f"Erreur de connexion: {e}")
        return None

def create_users_table(db):
    try:
        table = db.create_table(
            TableName='Users',
            KeySchema=[{'AttributeName': 'email', 'KeyType': 'HASH'}],
            AttributeDefinitions=[{'AttributeName': 'email', 'AttributeType': 'S'}],
            ProvisionedThroughput={'ReadCapacityUnits': 5, 'WriteCapacityUnits': 5}
        )
        table.wait_until_exists()
        print("Table Users créée.")
    except db.meta.client.exceptions.ResourceInUseException:
        print("Table Users existe déjà.")

def save_user(db, user_data):
    table = db.Table('Users')
    # Conversion cruciale des floats en Decimal pour DynamoDB
    if 'face_encoding' in user_data:
        user_data['face_encoding'] = [Decimal(str(v)) for v in user_data['face_encoding']]
    try:
        table.put_item(Item=user_data)
        return True
    except Exception as e:
        print(f"Erreur save: {e}")
        return False

def get_user_by_email(db, email):
    table = db.Table('Users')
    try:
        response = table.get_item(Key={'email': email})
        return response.get('Item')
    except Exception as e:
        print(f"Erreur get: {e}")
        return None