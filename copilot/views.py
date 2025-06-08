from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from drf_spectacular.utils import extend_schema
from .serializers import AskRequestSerializer, AskResponseSerializer
from django.conf import settings
import openai

client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)

class AskView(APIView):

    @extend_schema(
        request=AskRequestSerializer,
        responses={200: AskResponseSerializer},
        tags=["Copilot"]
    )
    def post(self, request):
        context = request.data.get("context")
        question = request.data.get("question")

        if not context or not question:
            return Response({"error": "Missing context or question"}, status=400)

        try:
            response = client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "Ты ИИ-помощник, анализирующий текст и отвечающий на вопросы."},
                    {"role": "user", "content": f"Текст: {context}\n\nВопрос: {question}"}
                ],
                temperature=0.5,
            )
            answer = response.choices[0].message.content.strip()
            return Response({"answer": answer})

        except Exception as e:
            return Response({"error": str(e)}, status=500)
