
import os
from langchain.memory import ConversationBufferMemory
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import RunnableLambda, RunnablePassthrough
from langchain_openai import ChatOpenAI
from operator import itemgetter
import time

# OpenAI API 키 설정 (사용자가 직접 설정해야 함)
# os.environ["OPENAI_API_KEY"] = "your-api-key-here"

class MemoryBot:
    def __init__(self, model_name="gpt-3.5-turbo", temperature=0):
        """메모리 기능이 있는 챗봇 초기화"""

        # LLM 모델 설정
        self.llm = ChatOpenAI(model=model_name, temperature=temperature)

        # 프롬프트 템플릿 설정
        self.prompt = ChatPromptTemplate([
            ('system', '당신은 도움이 되는 친근한 AI 어시스턴트입니다. 사용자와의 이전 대화 내용을 기억하며 자연스럽게 대화하세요.'),
            MessagesPlaceholder(variable_name='chat_history'),  # 기존 채팅 내역 주입
            ('human', '{input}'),
        ])

        # 메모리 설정
        self.memory = ConversationBufferMemory(
            return_messages=True, 
            memory_key='chat_history'
        )

        # 실행 체인 구성
        self.runnable = RunnablePassthrough.assign(
            chat_history=RunnableLambda(self.memory.load_memory_variables) |
            itemgetter('chat_history')
        )

        self.chain = self.runnable | self.prompt | self.llm

        print("🤖 기억하는 챗봇이 준비되었습니다!")
        print("💡 ('quit', '정지', '그만', 'exit') 중 아무거나 입력하면 대화가 종료됩니다.")
        print("=" * 50)

    def chat(self, user_input):
        """사용자 입력을 받아 AI 응답 생성 및 메모리 저장"""
        try:
            # AI 응답 생성
            response = self.chain.invoke({'input': user_input})
            ai_response = response.content

            # 대화 내용을 메모리에 저장
            self.memory.save_context(
                {'human': user_input},
                {'ai': ai_response}
            )

            return ai_response

        except Exception as e:
            return f"죄송합니다. 오류가 발생했습니다: {str(e)}"

    def get_memory(self):
        """현재 저장된 메모리 내용 확인"""
        return self.memory.load_memory_variables({})

    def clear_memory(self):
        """메모리 내용 초기화"""
        self.memory.clear()
        print("🧹 메모리가 초기화되었습니다.")

    def start_conversation(self):
        """대화 시작"""
        print("👋 안녕하세요! 무엇을 도와드릴까요?\n")

        while True:
            try:
                # 사용자 입력 받기
                user_input = input("😊 You: ").strip()

                # 종료 명령 확인
                if user_input.lower() in ('quit', '정지', '그만', 'exit', 'q'):
                    print("\n👋 대화를 종료합니다. 좋은 하루 되세요!")
                    break

                # 빈 입력 처리
                if not user_input:
                    print("❓ 메시지를 입력해주세요.")
                    continue

                # 특별 명령어 처리
                if user_input.lower() == '/memory':
                    memory_content = self.get_memory()
                    print(f"\n🧠 현재 메모리 내용:")
                    for msg in memory_content.get('chat_history', []):
                        role = "사용자" if msg.type == "human" else "AI"
                        print(f"   {role}: {msg.content}")
                    print()
                    continue

                if user_input.lower() == '/clear':
                    self.clear_memory()
                    continue

                # AI 응답 생성
                print("\n🤖 Bot: ", end="")
                ai_response = self.chat(user_input)
                print(ai_response)
                print("-" * 50)

            except KeyboardInterrupt:
                print("\n\n👋 대화가 중단되었습니다.")
                break
            except Exception as e:
                print(f"\n❌ 오류 발생: {e}")

def main():
    """메인 실행 함수"""
    print("🚀 기억하는 AI 챗봇을 시작합니다!")
    print("\n📝 사용 가능한 명령어:")
    print("   /memory - 현재 대화 기록 확인")
    print("   /clear  - 메모리 초기화") 
    print("   quit, 정지, 그만, exit - 프로그램 종료")
    print()

    try:
        # 챗봇 인스턴스 생성 및 대화 시작
        bot = MemoryBot()
        bot.start_conversation()

    except Exception as e:
        print(f"❌ 챗봇 초기화 중 오류 발생: {e}")
        print("💡 OpenAI API 키가 설정되어 있는지 확인해주세요.")

if __name__ == "__main__":
    main()
