"""Quick test to measure LM Studio inference speed"""
import time
from openai import OpenAI

client = OpenAI(base_url="http://172.31.0.1:1234/v1", api_key="not-needed")

test_prompt = "Evaluate this market: Will BTS win a Grammy in 2025? Reply with JSON only."

print("Testing LM Studio speed...")
print("Sending request...")

start = time.time()
response = client.chat.completions.create(
    model="qwen2.5-14b-instruct",
    messages=[
        {"role": "system", "content": "You are a helpful assistant. Output JSON only."},
        {"role": "user", "content": test_prompt}
    ],
    temperature=0.3,
    max_tokens=300
)
end = time.time()

elapsed = end - start
content = response.choices[0].message.content

# Estimate tokens (rough: ~0.75 tokens per word)
tokens = len(content.split()) * 0.75
tokens_per_sec = tokens / elapsed if elapsed > 0 else 0

print(f"\n{'='*60}")
print(f"Total time: {elapsed:.2f}s")
print(f"Response length: ~{int(tokens)} tokens")
print(f"Speed: ~{tokens_per_sec:.1f} tokens/sec")
print(f"{'='*60}")
print(f"\nResponse:\n{content[:200]}...")

if tokens_per_sec < 30:
    print("\n⚠️  SLOW! Expected 40-60 t/s on RTX 4070 Super")
    print("   Check: GPU layers, context length settings")
elif tokens_per_sec > 40:
    print("\n✅ Good speed!")
else:
    print("\n⚡ Acceptable speed")
