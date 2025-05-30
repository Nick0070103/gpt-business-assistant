import openai

def chat_with_gpt(user_text, api_key, db=None):
    openai.api_key = api_key

    prompt = f"Ты умный и дружелюбный ассистент. Пользователь пишет: {user_text}"

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
        )
        return response.choices[0].message['content']
    except Exception as e:
        return "🤖 Не смог придумать ответ. Попробуй ещё раз."
