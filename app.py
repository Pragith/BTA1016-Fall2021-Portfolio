# Ctrl + tilde key (~) to open terminal
# Ctrl + C to exit/kill/close the server
'''
Route:
* Decorate the function with @app.route('/')
* Define the function
* Return the response
'''

from flask import Flask, request
import pandas as pd
import json
import requests

app = Flask(__name__)



# Homepage / landing page route
@app.route("/")
def homepage():
    return "Welcome to Pragith's Portfolio Website!"


@app.route("/projects")
def my_projects():
    return "Pragith's Projects"

### Random number ###
@app.route("/projects/random")
def random_number():
    response = {}
    
    # Generate random number
    import random
    response['num'] = random.randint(1000, 9999)

    # Return the response
    return response, 200

### Hotel questions ###
@app.route("/projects/hotel/food/<food_type>")
def food_questions(food_type):
    food_type = food_type.lower()

    food_types = {
        'breakfast': 'yes',
        'lunch': 'no',
        'dinner': 'yes'
    }

    if food_type in food_types:
        return food_types[food_type]
    else:
        return {
            'error': f'I do not understand {food_type}. You can choose from one of the food types that we offer',
            'food_types': list(food_types.keys())
        }



#### TODO APP ####

# Read all todo items
@app.route("/projects/todo/read")
def read_todo():
    result = {}
    
    # Read all todo items and add them to the result dictionary
    df = pd.read_excel('db/todo_items.xlsx')
    dfJson = df.to_json(orient='records')
    result['items'] = json.loads(dfJson)

    # Success / Failure message
    result['message'] = 'success'

    # Return the result object with the HTTP response code
    return result, 200


# Read specific todo item
@app.route("/projects/todo/read/<id>")
def read_todo_item(id):
    result = {}
    id = int(id)
    
    # Read all todo items and fetch only that row with the matching id
    df = pd.read_excel('db/todo_items.xlsx')
    todoItem = df[df['id'] == id]

    if len(todoItem) == 0:
        result['message'] = 'failure'
        result['info'] = f'The item id {id} was not found in our database.'
        return result, 404
    else:
        dfJson = todoItem.to_json(orient='records')
        result['item'] = json.loads(dfJson)    
        
        # Success / Failure message
        result['message'] = 'success'

        # Return the result object with the HTTP response code
        return result, 200


# Delete all todo items
@app.route("/projects/todo/remove")
def remove_todo():
    result = {}
    
    # Read all todo items and add them to the result dictionary
    df = pd.read_excel('db/todo_items.xlsx')
    df = df[0:0]
    df.to_excel('db/todo_items.xlsx', index=False)

    # Success / Failure message
    result['message'] = 'success'
    result['info'] = 'All todo items were removed.'

    # Return the result object with the HTTP response code
    return result, 200


# Delete specific todo item
@app.route("/projects/todo/remove/<id>")
def remove_todo_item(id):
    result = {}
    id = int(id)
    
    # Read all todo items and delete only that row with the matching id
    df = pd.read_excel('db/todo_items.xlsx')
    todoItem = df[df['id'] == id].index    

    if len(todoItem) == 0:
        result['message'] = 'failure'
        result['info'] = f'The item id {id} was not found in our database.'
        return result, 404
    else:
        df = df.drop(todoItem)   
        df.to_excel('db/todo_items.xlsx', index=False)       
        
        # Success / Failure message
        result['message'] = 'success'
        result['info'] = f'The item id {id} was removed from our database.'

        # Return the result object with the HTTP response code
        return result, 200


# Create todo item - This route should ONLY listen to POST method
@app.route('/projects/todo/create', methods=['POST'])
def create_item():
    # Check if the HTTP method is POST
    if request.method == 'POST':  
        # Create an empty item object
        itemObj = {}          
        
        # Capture the 'item' from the request object into itemObj
        itemObj['item'] = request.form['item']
        
        # Generate a random number as id         
        import random
        itemObj['id'] = random.randint(1000, 9999)        

        # Open the database (excel file)      
        df = pd.read_excel('db/todo_items.xlsx')

        # Append the new object to the database
        df = df.append(itemObj, ignore_index=True)
        print(df)

        # Save the database
        df.to_excel('db/todo_items.xlsx', index=False)

        # Classwork - Create success or failure message

        # Return the response
        return itemObj
    else:
        return 'Come back with a valid POST request, please!'


# Update item
@app.route('/projects/todo/edit/<id>', methods=['GET', 'POST'])
def update_item(id):
    newObj = {}

    # Capture the request from the client
    id = int(id)
    newItem = request.form['item']

    # Open the database
    df = pd.read_excel('db/todo_items.xlsx')

    # Check if the user provided id exists already in the database
    todoItem = df[df['id'] == id].index    

    if len(todoItem) == 0:
        newObj['message'] = 'failure'
        newObj['info'] = f'The item id {id} was not found in our database.'
        return newObj, 404
    else:
        # Update the item for the given id with the new item text
        df.loc[df['id'] == id, 'item'] = newItem    
        print(df)

        # Save the database
        df.to_excel('db/todo_items.xlsx', index=False)

        # Build the response object
        newObj = {
            'id': id,
            'item': newItem
        }
        
        # Return the response
        return newObj

##################


#### FINANCE API ####
# Alphavantage API key - TWWPBFUC9XGBUNTO, B4P3O1SABUZLB7RP
@app.route('/projects/finance/stock/<function>', methods=['GET'])
def company_info(function='OVERVIEW'):
    # http://127.0.0.1:8000/projects/finance/company_info?symbol=FB
    # http://127.0.0.1:8000/projects/finance/company_info?symbol=FB,AAPL,IBM
    # http://127.0.0.1:8000/projects/finance/company_info?symbol=FB,AAPL,IBM&api_key=12123123

    # Get the API key from the URL parameter 'api_key'
    api_key = request.args.get('api_key')

    # Fetch one or more comma separated stock symbols from the URL parameter 'symbol'
    symbols = request.args.get('symbol')

    # Split the symbols by comma and create a list of symbols from it
    symbols = symbols.split(',')

    # For each symbol, query the Alphavantage API and store the response in a response list
    result = []
    for symbol in symbols:
        response = requests.get(f'https://www.alphavantage.co/query?function={function}&symbol={symbol}&apikey={api_key}&interval=60min')
        jsonResponse = json.loads(response.text)
        result.append(jsonResponse)

    # Store the final result as a Pandas dataframe and then export it to Excel under the 'db' folder with the filename 'stock.xlsx'
    df = pd.DataFrame(result)
    df.to_excel('db/stock.xlsx', index=False)

    # Return the response list
    return { 'final_result': result }

##################

#### HTTPBIN PRACTICE ####
@app.route('/projects/httpbin/get')
def httpbin_get_view():
    response = requests.get(f'http://httpbin.org/get?course=BTA1016')
    jsonResponse = json.loads(response.text)

    return jsonResponse

##########################

app.run(host='0.0.0.0', debug=True, port=8000)