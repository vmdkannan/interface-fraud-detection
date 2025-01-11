from flask import Flask, request, jsonify, render_template
import psycopg2
from psycopg2.extras import RealDictCursor
from flask_cors import CORS
import os
from datetime import datetime

app = Flask(__name__)
CORS(app)

# Database configuration
DATABASE_URL = os.environ.get('POSTGRES_URL')

# Database connection function
def get_db_connection():
    conn = psycopg2.connect(DATABASE_URL)
    return conn

# Route for the home page
@app.route('/')
def index():
    return render_template('index.html')
    # return "Successfully reached"

# Route to post transaction data
@app.route('/api/transaction', methods=['POST'])
def post_transaction():
    try:
        data = request.get_json()
        
        # Check if data is valid
        if not data:
            return jsonify({'error': 'Invalid JSON input'}), 400
        
        
        timestamp_with_microseconds = datetime.now()
        # Truncate microseconds by setting it to 0
        timestamp_without_microseconds = timestamp_with_microseconds.replace(microsecond=0)
        # Convert datetime object to string (YYYY-MM-DD HH:MM:SS format)
        trans_date_str = timestamp_without_microseconds.strftime('%Y-%m-%d %H:%M')
        

        # Extract fields from JSON
        trans_date = trans_date_str
        amount = data.get('amount')
        currency = data.get('currency')
        trans_num = data.get('trans_num')
        unix_time = data.get('unix_time')
        customer_id = data.get('customer_id')
        merchant_id = data.get('merchant_id')
        product_id = data.get('product_id')
        location_id = data.get('location_id')

        # Connect to the database
        conn = get_db_connection()
        cursor = conn.cursor()
        
        print("Persist transaction...")

        # Insert transaction data into the database
        cursor.execute(
            '''
            INSERT INTO transactions (
                trans_date, amount, currency, trans_num, unix_time, customer_id, merchant_id, product_id, location_id
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING transaction_id
            ''',
            (trans_date, amount, currency, trans_num, unix_time, customer_id, merchant_id, product_id, location_id)
        )

        # Commit the transaction and retrieve the ID
        conn.commit()
        transaction_id = cursor.fetchone()[0]

        # Clean up
        cursor.close()
        conn.close()

        # Return success response
        return jsonify({'message': 'Transaction added', 'id': transaction_id}), 201

    except Exception as e:
        # Handle exceptions gracefully and return JSON error
        return jsonify({'error': str(e)}), 500

# Route to get transaction data
@app.route('/api/transaction', methods=['GET'])
def get_transaction():
    id = request.args.get('id')
    
    if not id:
        return jsonify({'error': 'Transaction ID is required'}), 400
    
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    
    # Query with the `id` from the query parameter
    cursor.execute('SELECT * FROM transactions WHERE transaction_id = %s', (str(id),))
    result = cursor.fetchone()
    cursor.close()
    conn.close()
    
    if result:
        # Return only the required fields
        filtered_result = {
            'id': result.get('transaction_id'),
            'trans_num': result.get('trans_num'),
            'is_fraud': result.get('is_fraud')  # Could be null
        }
        return jsonify(filtered_result)
    else:
        return jsonify({'error': 'Transaction not found'}), 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=7860)
