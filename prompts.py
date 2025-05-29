import openai

def chat_with_gpt(user_text, api_key, db=None):
    openai.api_key = api_key

    prompt = f"Ты умный и дружелюбный ассистент. Пользователь пишет: {user_text}"

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",  # Можно заменить на gpt-3.5-turbo
            messages=[
                {"role": "system", "content": "Ты ассистент, который помогает, спорит и направляет."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7
        )
        return response.choices[0].message['content']
    except Exception as e:
        return "🤖 Не смог придумать ответ. Попробуй ещё раз."
