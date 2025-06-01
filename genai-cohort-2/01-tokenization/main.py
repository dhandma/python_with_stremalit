import tiktoken 
enc = tiktoken.encoding_for_model('gpt-4o')
text = "This is mayur dhande"
token = enc.encode(text)
print(token)

tokens=[2500, 382, 1340, 330, 8523, 4102]
decoded_token=enc.decode(tokens)
print(decoded_token)