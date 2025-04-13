#!/bin/bash

MODEL_NAME="qwen2:1.5b-instruct-q8_0"

echo "Attempting to pull Ollama model: $MODEL_NAME"
echo "Ensure Ollama is installed and running."

if ! command -v ollama &> /dev/null
then
    echo "Error: 'ollama' command not found. Please install Ollama first."
    echo "Visit https://ollama.com/download"
    exit 1
fi

ollama pull "$MODEL_NAME"

if [ $? -eq 0 ]; then
  echo "Successfully pulled model: $MODEL_NAME"
else
  echo "Error pulling model: $MODEL_NAME. Please check Ollama status and network connection."
  exit 1
fi

echo "Ollama model setup complete."
exit 0
