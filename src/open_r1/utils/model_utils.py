import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, PreTrainedTokenizer

from trl.trainer.utils import get_kbit_device_map, get_quantization_config

from ..configs import GRPOConfig, SFTConfig, ModelConfig
from ..choreo import ChoreographedCausalLM

def get_tokenizer(model_args: ModelConfig, training_args: SFTConfig | GRPOConfig) -> PreTrainedTokenizer:
    """Get the tokenizer for the model."""
    tokenizer = AutoTokenizer.from_pretrained(
        model_args.model_name_or_path,
        revision=model_args.model_revision,
        trust_remote_code=model_args.trust_remote_code,
    )

    if training_args.chat_template is not None:
        tokenizer.chat_template = training_args.chat_template

    return tokenizer

def get_model(
    model_args: ModelConfig,
    training_args: SFTConfig | GRPOConfig,
) -> AutoModelForCausalLM:
    model_cls = ChoreographedCausalLM if model_args.to_choreo else AutoModelForCausalLM
    torch_dtype = (
        model_args.torch_dtype
        if model_args.torch_dtype in ["auto", None]
        else getattr(torch, model_args.torch_dtype)
    )
    quantization_config = get_quantization_config(model_args)
    model_kwargs = dict(
        revision=model_args.model_revision,
        trust_remote_code=model_args.trust_remote_code,
        attn_implementation=model_args.attn_implementation,
        torch_dtype=torch_dtype,
        use_cache=False if training_args.gradient_checkpointing else True,
        device_map=get_kbit_device_map() if quantization_config is not None else None,
        quantization_config=quantization_config,
        choreography_k=model_args.choreography_k,
    )
    model = model_cls.from_pretrained(
        model_args.model_name_or_path,
        **model_kwargs,
    )
    return model
