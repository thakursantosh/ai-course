curl https://api.groq.com/openai/v1/chat/completions -s^
 -H "Content-Type: application/json"^
 -H "Authorization: Bearer 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"^
 -d '{"model": "llama-3.3-70b-versatile", "messages": [{"role": "user", "content": "Explain the importance of fast language models"}]}'