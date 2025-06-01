import openai

def chat_with_gpt(prompt: str, openai_key: str, db=None) -> str:
    openai.api_key = openai_key
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "Ты умный, внимательный ассистент. Помогай по делу, отвечай понятно, с юмором, но не заигрывай."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=500
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"GPT error: {e}")
        return "🤖 Не смог придумать ответ. Попробуй ещё раз."
