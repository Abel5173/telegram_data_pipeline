{{ config(
    materialized='table',
    schema='marts'
) }}

-- SELECT
--     m.message_id,
--     m.channel_name AS channel_id,
--     m.message_date::DATE AS date_id,
--     m.message_text,
--     m.has_media,
--     m.media_type,
--     m.media_path,
--     LENGTH(m.message_text) AS message_length
-- FROM {{ ref('stg_telegram_messages') }} m
-- WHERE m.message_text IS NOT NULL


SELECT
    m.message_id,
    m.channel_id,
    m.date_id,
    m.message_text,
    m.has_media,
    m.media_type,
    m.media_path,
    d.product_label
FROM {{ ref('stg_telegram_messages') }} m
LEFT JOIN {{ source('raw', 'image_detections') }} d
    ON m.message_id = d.message_id
    AND m.channel_name = d.channel_name