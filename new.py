from fastapi import FastAPI
from fastapi.responses import StreamingResponse
import vertexai
from vertexai.generative_models import (
    GenerationConfig,
    GenerativeModel as Vmodel,
    Tool,
    Content,
    Part,
    grounding,
)
import anthropic
project_id = "milk2-32695"
anthropic_key= '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'
vertexai.init(project=project_id, location="us-central1")
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

app = FastAPI()







def mongo(username: str, messa, model, chat_id):
    uri = "mongodb+srv://thimat:wdVqp4FXj39alSFX@history.3ahrhra.mongodb.net/?retryWrites=true&w=majority&appName=history"
    client = MongoClient(uri, server_api=ServerApi('1'))
    # returns vhistory for genai and claude, adds history for vertex
    try:

        database = client.get_database('history')
        collection = database[username + model + chat_id]
        # if there no message is inputed return the content of the  n.  
        if len(messa) == 0:
            mess = []
            all_restaurants = collection.find({}, {"_id": 0})
            # the id: 0 means dont return the id adding anything else to that feild does the same for that specific feild
            for restaurant in all_restaurants:
                mess.append(restaurant)

            return mess

        

        
        # if there is a message inputed return the content of the collection and add the new contents 
        if len(messa) != 0:  
            mess = []
            collection.insert_many(messa)
            all_restaurants = collection.find({}, {"_id": 0})
            for restaurant in all_restaurants:
                mess.append(restaurant) 
            return mess
        
        client.close()
    except Exception as e:
        return e


def mongo_add_data(username: str, messa, model):
    uri = "mongodb+srv://thimat:wdVqp4FXj39alSFX@history.3ahrhra.mongodb.net/?retryWrites=true&w=majority&appName=history"
    #adds web scraping data genai
    client = MongoClient(uri)
    try:
    
        database = client.get_database('history')
        collection = database[username + model + 'data']
        collection.insert_one({"data": messa})
        client.close()
    except Exception as e:
        raise Exception("Unable to find the document due to the following error: ", e)


def mongo_find_data(username: str, model):
    uri = "mongodb+srv://thimat:wdVqp4FXj39alSFX@history.3ahrhra.mongodb.net/?retryWrites=true&w=majority&appName=history"
    #find web scarping data genai
    client = MongoClient(uri)
    try:
        
        database = client.get_database('history')
        mess = []

        collection = database[username + model + 'data']
        all_restaurants = collection.find({}, {"_id": 0})
        for restaurant in all_restaurants:
            mess.append(restaurant['data'])
        info = ''.join(mess)


        return info




    
        client.close()
    except Exception as e:
        raise Exception("Unable to find the document due to the following error: ", e)
    


def rolefind(username: str, model: str):
    uri = "mongodb+srv://thimat:wdVqp4FXj39alSFX@history.3ahrhra.mongodb.net/?retryWrites=true&w=majority&appName=history"
    #same as part finder but for roles
    client = MongoClient(uri)
    try:
        
        database = client.get_database('history')

        mess2 =[]
        

        collection = database[username + model]
        roles = collection.find({}, {"role": 1, "_id": 0})
        for role in roles:
            mess2.append(role['role'])
        
        return mess2
        #return 
        client.close()
    except Exception as e:
        raise Exception("Unable to find the document due to the following error: ", e)

def count(username: str, model: str, chat_id):
    uri = "mongodb+srv://thimat:wdVqp4FXj39alSFX@history.3ahrhra.mongodb.net/?retryWrites=true&w=majority&appName=history"
    #counts documents so the content function knows how much to contenize
    client = MongoClient(uri)
    try:
        
        database = client.get_database('history')
        collection = database[username + model + chat_id]
        count = collection.count_documents({})
        return count
        client.close()
    except Exception as e:
        raise Exception("Unable to find the document due to the following error: ", e)

def partsfind(username: str, model):
    #find the part object for any role in mongodb
    uri = "mongodb+srv://thimat:wdVqp4FXj39alSFX@history.3ahrhra.mongodb.net/?retryWrites=true&w=majority&appName=history"
    client = MongoClient(uri)
    try:
        
        database = client.get_database('history')
        mess = []

        

        collection = database[username + model]
        parts = collection.find({}, {"parts": 1, "_id": 0})
        #returns only what is stored in part object excluding the parts label
        for part in parts:
            mess.append(part['parts'])

        
        mess = sum(mess, [])
        return mess
    
        client.close()
    except Exception as e:
        raise Exception("Unable to find the document due to the following error: ", e)






def content(role, text, count):
    #inputs the history data into vertex ai content schem
    scaler = 0
    content_list = []
    for i in range(count):
        balls = Content(role=role[scaler], parts=[Part.from_text(text[scaler])])
        content_list.append(balls)
        scaler += 1
    return content_list
def cont2(model, username, count, chat_id):
    from google import genai
    from google.genai.types import HttpOptions, ModelContent, Part, UserContent
    # Initialize an empty list to store parts
    if count == 0:
        bisstory = []
        return bisstory
    else:
        all_user_parts = []
        all_model_parts = []
        uri = "mongodb+srv://thimat:wdVqp4FXj39alSFX@history.3ahrhra.mongodb.net/?retryWrites=true&w=majority&appName=history"
        client = MongoClient(uri) 
        database = client.get_database('history')
        collection = database[username + model + chat_id
                              ]
        query1 = {'role': 'user'}
        cursor = collection.find(query1, {'parts': 1, '_id': 0})
        for document in cursor:
            all_user_parts.extend(document.get('parts', []))
        query = {'role': 'model'}
        cursor = collection.find(query, {'parts': 1, '_id': 0})
        for document in cursor:
            all_model_parts.extend(document.get('parts', []))
        scaler = 0
        content_list = []
        query = {'role': 'user'}
        count = collection.count_documents(query)
        count = int(count)
    
        for i in range(count):
            user_cont = UserContent(parts=[Part(text=all_user_parts[scaler])])
            model_cont = ModelContent(parts=[Part(text=all_model_parts[scaler])])
            content_list.append(user_cont)
            content_list.append(model_cont)
            scaler += 1
        return content_list
            
        
        






def palm(q: str, username: str, modeltype: str, chat_id):
    messages = []
    full_response = []


    from google import genai
    from google.genai.types import (
    GenerateContentConfig,
    GoogleSearch,
    HttpOptions,
    Tool,
    )


    client = genai.Client(http_options=HttpOptions(api_version="v1"))
    full_response = []
    history = cont2(modeltype, username, count=count(username=username, model=modeltype, chat_id=chat_id), chat_id=chat_id)
    chat = client.chats.create(
    model=modeltype,
    history=history,  
    config=GenerateContentConfig(
        tools=[Tool(google_search=GoogleSearch())]
    )
)
    chat
    for chunk in chat.send_message_stream(q):
        full_response.append(chunk.text) 
        yield chunk.text

    full_response = ' '.join(full_response)
    messages.append({'role':'user', 'parts': [q]})
    messages.append({'role':'model', 'parts': [full_response]})
    mongo(username=username, messa=messages, model=modeltype, chat_id=chat_id)










def vertex(q, username: str, modeltype: str, chat_id):
    partsfinder = partsfind(username=username, model=modeltype)
    rolefinder = rolefind(username=username, model=modeltype)
    history = content(rolefinder, partsfinder, count=count(username=username, model=modeltype))
    messages = []
    tool = Tool.from_google_search_retrieval(grounding.GoogleSearchRetrieval())
    model = modeltype
    chat = model.start_chat(history=history, response_validation=False)
    chat
    repo = []
    full_response = []
    response = chat.send_message(q, tools=[tool], generation_config=GenerationConfig(temperature=0.0), stream=True)
    try: 
        
        for chunk in response:
            repo.append(chunk.text)
            repos = ' '.join(repo)
            full_response.append(chunk.text)
            yield repos
            repo.clear()

    except ValueError as e:
        x = 0
    full_response = ' '.join(full_response)
    messages.append({'role':'user', 'parts': [q]})
    messages.append({'role':'model', 'parts': [full_response]})
    mongo(username=username, messa=messages, model=modeltype, chat_id=chat_id)


def anthropi(q: str, username: str, modeltype: str, chat_id):
    client = anthropic.Anthropic(
    api_key=anthropic_key
    )
    history = mongo(username=username, messa=[], model=modeltype, chat_id=chat_id)
    history.append({"role": "user", "content": q})
    messages = []
    repo = []

    full_response = []
    try: 
        with client.messages.stream(
            max_tokens=1024,
            messages=history,
            model=modeltype,
            ) as stream:
            for text in stream.text_stream:
                repo.append(text)
                repos = ' '.join(repo)
                full_response.append(text)
                yield repos
                repo.clear()


    except ValueError as e:
        x = 0
    full_response = ' '.join(full_response)
    messages.append({"role": "user", "content": q})
    messages.append({'role':'assistant', 'content': full_response})
    mongo(username=username, messa=messages, model=modeltype, chat_id=chat_id)


def Openai(q: str, username: str, modeltype: str, chat_id):
    from openai import OpenAI
    client = OpenAI()
    history = mongo(username=username, messa=[], model=modeltype, chat_id=chat_id)
    history.append({"role": "user", "content": q})
    messages = []
    full_response = []
    try: 
        completion = client.chat.completions.create(
            model=modeltype,
            messages=history,
            stream=True
                )
        for chunk in completion:
            if chunk.choices[0].delta.content is not None:
                yield chunk.choices[0].delta.content
    except ValueError as e:
        x = 0
    full_response = ' '.join(full_response)
    messages.append({"role": "user", "content": q})
    messages.append({'role':'assistant', 'content': full_response})
    mongo(username=username, messa=messages, model=modeltype, chat_id=chat_id)



@app.get("/openai/")
async def read_item(q: str, username: str, model: str, chat_id: str):
    return StreamingResponse(Openai(q, username, model, chat_id), media_type="text/plain")



@app.get("/anthropic/")
async def read_item(q: str, username: str, model: str, chat_id: str):
    return StreamingResponse(anthropi(q, username, model, chat_id), media_type="text/plain")


@app.get("/vertex/")
async def read_item(q: str, username: str, model: str, chat_id: str):
    return StreamingResponse(vertex(q, username, model, chat_id), media_type="text/plain")


@app.get("/genai/")
async def read_item(q: str, username: str, model: str, chat_id: str):
    return StreamingResponse(palm(q, username, model, chat_id), media_type="text/plain")



@app.get("/clear/")
def clear(username: str, model, chat_id: str):
    uri = "mongodb+srv://thimat:wdVqp4FXj39alSFX@history.3ahrhra.mongodb.net/?retryWrites=true&w=majority&appName=history"
    client = MongoClient(uri)
    database = client.get_database('history') 
    database[username + model + chat_id].drop()


@app.get("/retrieve/")
def read_item(username: str, model: str):
    history = mongo(username=username, messa=[], model=model)
    return history

