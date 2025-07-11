{{ config(
    materialized='table',
    schema='staging'
) }}

SELECT
    message_id::BIGINT AS message_id,
    channel_name,
    date::TIMESTAMP WITH TIME ZONE AS message_date,
    NULLIF(text, '') AS message_text,
    has_media,
    media_type,
    media_path
FROM {{ source('raw', 'telegram_messages') }}
