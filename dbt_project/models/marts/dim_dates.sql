{{ config(
    materialized='table',
    schema='marts'
) }}

WITH date_spine AS (
    SELECT generate_series(
        (SELECT MIN(message_date)::DATE FROM {{ ref('stg_telegram_messages') }}),
        (SELECT MAX(message_date)::DATE FROM {{ ref('stg_telegram_messages') }}),
        INTERVAL '1 day'
    ) AS date_day
)
SELECT
    date_day::DATE AS date_id,
    date_day::DATE AS date,
    EXTRACT(YEAR FROM date_day) AS year,
    EXTRACT(MONTH FROM date_day) AS month,
    EXTRACT(DAY FROM date_day) AS day,
    EXTRACT(DOW FROM date_day) AS day_of_week,
    EXTRACT(WEEK FROM date_day) AS week_of_year
FROM date_spine
