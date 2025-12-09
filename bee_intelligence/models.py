from huggingface_hub import hf_hub_download

model_path = "meta-llama/Llama-2-7b-chat-hf"
download_path = "C:/path/to/your/directory"  # Change this to your desired directory
hf_hub_download(repo_id=model_path, filename="pytorch_model.bin", cache_dir=download_path)

print("Model downloaded successfully!")
