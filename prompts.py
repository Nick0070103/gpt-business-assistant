# prompts.py
import openai

def chat_with_gpt(user_text, api_key, db):
    openai.api_key = api_key
    context = ""
    for tid, text, due, status in db.get_all_tasks():
        context += f"\n- {text} (до {due}, статус: {status})"

    messages = [
        {"role": "system", "content": (
            "Ты умный, дружелюбный, но критичный бизнес-ассистент."
            " Помогаешь ставить и отслеживать задачи, анализируешь поступки и предлагаешь улучшения."
            " Если решение сомнительное — спорь, но объясняй почему."
            " Вот список текущих задач:\n" + context)
        },
        {"role": "user", "content": user_text}
    ]

    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=messages
    )
    return response.choices[0].message.content