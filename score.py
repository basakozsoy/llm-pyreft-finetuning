import torch, transformers, pyreft

# your own huggingface token here:
hf_token = ''

model_name = 'meta-llama/Llama-2-7b-chat-hf'
model = transformers.AutoModelForCausalLM.from_pretrained(
    model_name, torch_dtype=torch.bfloat16, device_map='cuda', 
    cache_dir='./workspace', token=hf_token
)

tokenizer = transformers.AutoTokenizer.from_pretrained(
    model_name, model_max_tokens=2048, use_fast=False,
    padding_side="right", token=hf_token
)

tokenizer.pad_token = tokenizer.unk_token

def prompt_template(prompt):
    return f"""
    <s>[INST]<<sys>>You are a helpful assistant<<sys>>
    {prompt}
    [/INST]"""


# test case
# add your custom prompt here:
prompt_text = ""
prompt = prompt_template(prompt_text)
tokens = tokenizer(prompt, return_tensors='pt').to('cuda')

# load the trained model
reft_model = pyreft.ReftModel.load('./trained_intervention', model)
reft_model.set_device('cuda')

# specify where the last token is
base_unit_position = tokens['input_ids'].shape[-1] - 1

# generate a prediction
_, response = reft_model.generate(tokens, 
                            unit_locations={'sources->base':(None, [[[base_unit_position]]])},
                            intervene_on_prompt=True
                            ) 
print(tokenizer.decode(response[0])) 