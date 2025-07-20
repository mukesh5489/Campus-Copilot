from openai import OpenAI

client = OpenAI(
    api_key="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"
)

def ask_ai(prompt):
    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        store=True,
        messages=[
            {"role": "user", "content": prompt}
        ]
    )