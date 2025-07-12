{{ config(materialized='table', schema='marts') }}

SELECT DISTINCT
    channel_name AS channel_id,
    channel_name
FROM {{ ref('stg_telegram_messages') }}
WHERE channel_name IS NOT NULL
