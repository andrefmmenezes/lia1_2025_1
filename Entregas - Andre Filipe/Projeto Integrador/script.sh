# Builda a imagem Docker
docker build -t final_proj .

# Para e Remove container antigo se existir
docker stop final_proj_container && docker rm final_proj_container

# Roda o container com suporte a GPU
docker run --gpus all --name final_proj_container -p 8001:8000 final_proj
