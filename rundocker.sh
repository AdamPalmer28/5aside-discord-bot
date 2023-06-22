
# docker run -it \
#     -e P=data \
#     -v smb://TRUENAS/Misc_storage:app/ \
#     5asidebot:latest
docker run -it\
    -e channel='test' \
    -e path='data/' \
    --mount type=bind,source=//TRUENAS/Misc_storage/5aside_discord_bot/,target=/app/data/ \
    5asidebot:latest