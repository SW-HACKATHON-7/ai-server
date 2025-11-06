import os
import time
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

class OpenAIClient:
    def create_thread(self):
        thread = client.beta.threads.create()
        print(f"Thread 생성됨: {thread.id}")
        return thread.id


    def add_message_to_thread(self, thread_id, user_message):
        message = client.beta.threads.messages.create(
            thread_id=thread_id,
            role="user",
            content=user_message
        )
        print(f"메시지 추가됨: {message.id}")
        return message


    def run_assistant_and_get_response(self, thread_id, assistant_id, timeout=60):
        run = client.beta.threads.runs.create(
            thread_id=thread_id,
            assistant_id=assistant_id
        )
        print(f"Run 생성됨: {run.id}")

        start_time = time.time()
        while True:
            if time.time() - start_time > timeout:
                raise TimeoutError(f"Run이 {timeout}초 내에 완료되지 않았습니다.")

            run_status = client.beta.threads.runs.retrieve(
                thread_id=thread_id,
                run_id=run.id
            )

            print(f"Run 상태: {run_status.status}")

            if run_status.status == 'completed':
                break
            elif run_status.status in ['failed', 'cancelled', 'expired']:
                raise Exception(f"Run 실패: {run_status.status}")

            time.sleep(2)

        messages = client.beta.threads.messages.list(thread_id=thread_id)

        for message in messages.data:
            if message.role == 'assistant':
                response_text = message.content[0].text.value
                print(f"\nAssistant 응답:\n{response_text}")
                return response_text

        return None


    def chat_with_assistant(self, user_message, assistant_id, thread_id=None):
        try:
            if thread_id is None:
                thread_id = self.create_thread()

            self.add_message_to_thread(thread_id, user_message)

            response = self.run_assistant_and_get_response(thread_id, assistant_id)

            return response, thread_id
        except Exception as e:
            raise Exception(f"chat_with_assistant 실행 중 오류 발생: {str(e)}")