from flask import Flask, request
from flask_cors import CORS
from transformers import BertTokenizer, BertModel, XLMTokenizer, XLMModel, GPT2Tokenizer, GPT2Model
import torch

app = Flask(__name__)
CORS(app)


def format_attention(attention):
    return torch.stack([layer_attention.squeeze(0) for layer_attention in attention])


@app.route('/')
def get_attentions():
    model_name = request.args.get('model')
    source = request.args.get('source')
    target = request.args.get('target')

    if model_name == 'XLM':
        model_version = 'xlm-mlm-ende-1024'
        model = XLMModel.from_pretrained(model_version, output_attentions=True)
        tokenizer = XLMTokenizer.from_pretrained(model_version)
    elif model_name == 'GPT-2':
        model_version = 'gpt2'
        model = GPT2Model.from_pretrained(model_version, output_attentions=True)
        tokenizer = GPT2Tokenizer.from_pretrained(model_version)
    else:
        # BERT
        model_version = 'bert-base-uncased'
        model = BertModel.from_pretrained(model_version, output_attentions=True)
        tokenizer = BertTokenizer.from_pretrained(model_version, do_lower_case=True)

    inputs = tokenizer.encode_plus(source, target, return_tensors='pt', add_special_tokens=True)
    token_type_ids = inputs['token_type_ids']
    input_ids = inputs['input_ids']
    attention = model(input_ids, token_type_ids=token_type_ids)[-1]
    input_id_list = input_ids[0].tolist()
    tokens = tokenizer.convert_ids_to_tokens(input_id_list)
    return {'attention': format_attention(attention)[0].tolist(), 'source': tokens, 'target': tokens}


if __name__ == '__main__':
    app.run(host='0.0.0.0')
