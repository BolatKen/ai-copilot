from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
import json
import openai

# Новый клиент OpenAI (v1+)
client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)

@csrf_exempt
def ask(request):
    if request.method != "POST":
        return JsonResponse({"error": "POST only"}, status=405)

    try:
        data = json.loads(request.body)
        context = data.get("context")
        question = data.get("question")

        if not context or not question:
            return JsonResponse({"error": "Missing context or question"}, status=400)

        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "Ты ИИ-помощник, анализирующий текст и отвечающий на вопросы."},
                {"role": "user", "content": f"Текст: {context}\n\nВопрос: {question}"}
            ],
            temperature=0.5,
        )
        answer = response.choices[0].message.content.strip()
        return JsonResponse({"answer": answer})

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
