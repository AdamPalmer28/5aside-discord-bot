

docker run -it \
    --env-file //truenas/Misc_storage/env_vars/env_values.txt \
    -e channel='test' \
    -e path='data/' \
#    --mount type=bind,source= //TRUENAS/Misc_storage/5aside_discord_bot/,target=/app/data/ \
    5asidebot:latest