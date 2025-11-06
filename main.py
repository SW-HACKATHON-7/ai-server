import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
import json
from openaiClient import OpenAIClient
from dotenv import load_dotenv

load_dotenv()
app = FastAPI()
client = OpenAIClient()

talkbokki_assistant = os.getenv("TALKBOKKI_ASSISTANT")
talkbokki_suggestion_assistant = os.getenv("TALKBOKKI_SUGGESTION_ASSISTANT")
talkbokki_quiz_assistant = os.getenv("TALKBOKKI_QUIZ_ASSISTANT")

class ReviewData(BaseModel):
    group_id: int
    emotional_tone: str
    appropriateness_rating: int
    impact_score: int
    review_comment: str
    suggested_alternative: str

class AlalyzeResponse(BaseModel):
    response: List[ReviewData]

class SuggestionData(BaseModel):
    style: str
    text: str
    expected_impact: int
    explanation: str

class SuggestionResponse(BaseModel):
    response: List[SuggestionData]

class Message(BaseModel):
    message_id: str
    text: str
    speaker: str
    confidence: float
    group_id: int

class ConversationRequest(BaseModel):
    relationship: str
    relationship_info: str
    messages: List[Message]

class StartConversationRequest(BaseModel):
    relationship: str

class StartConversationResponse(BaseModel):
    message: str
    thread_id: str

class SendMessageRequest(BaseModel):
    message: str
    thread_id: str

class SendMessageData(BaseModel):
    emotional_tone: str
    appropriateness_rating: int
    impact_score: int
    review_comment: str
    suggested_alternative: str

class SendMessageResponse(BaseModel):
    message: str
    response: SendMessageData

@app.post("/analyze-messages")
async def analyze_conversation(request: ConversationRequest):
    try:
        user_message = json.dumps(request.dict(), ensure_ascii=False)
        response, thread_id = client.chat_with_assistant(user_message, talkbokki_assistant)
        parsed_data = json.loads(response)

        return AlalyzeResponse(
            response=parsed_data["response"],
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/suggestion-messages")
async def suggestion_conversation(request: ConversationRequest):
    try:
        user_message = json.dumps(request.dict(), ensure_ascii=False)
        response, thread_id = client.chat_with_assistant(user_message, talkbokki_suggestion_assistant)
        parsed_data = json.loads(response)

        return SuggestionResponse(
            response=parsed_data["response"],
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/start-conversation")
async def start_conversation(request: StartConversationRequest):
    try:
        response, thread_id = client.chat_with_assistant(request.relationship, talkbokki_quiz_assistant)
        parsed_data = json.loads(response)

        return StartConversationResponse(
            message=parsed_data["message"],
            thread_id=thread_id,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/send-message")
async def send_message(request: SendMessageRequest):
    try:
        response, thread_id = client.chat_with_assistant(request.message, talkbokki_quiz_assistant, request.thread_id)
        parsed_data = json.loads(response)

        return SendMessageResponse(
            message=parsed_data["message"],
            response=parsed_data["response"],
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))