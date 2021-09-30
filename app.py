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


app.run(debug=True, port=8000)