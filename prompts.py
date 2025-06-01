from openai import OpenAI
from openai.types.chat import ChatCompletionMessageParam

def chat_with_gpt(prompt: str, openai_key: str, db=None) -> str:
    try:
        client = OpenAI(api_key=openai_key)

        messages: list[ChatCompletionMessageParam] = [
            {"role": "system", "content": "Ты умный, внимательный ассистент. Отвечай ясно, с лёгким юмором."},
            {"role": "user", "content": prompt}
        ]

        response = client.chat.completions.create(
            model="gpt-4",
            messages=messages,
            temperature=0.7,
            max_tokens=500,
        )

        return response.choices[0].message.content.strip()

    except Exception as e:
        print(f"GPT error: {e}")
        return "🤖 Не смог придумать ответ. Попробуй ещё раз."
