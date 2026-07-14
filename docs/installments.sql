-- Импорт тарифов рассрочки из файла "квартиры (1).pdf"
-- Запуск на сервере:
--   psql -U dreamuser -d dreamhouse_db -f installments.sql
--
-- Карточки ищутся по названию (ILIKE), id знать не нужно.
-- ОБЯЗАТЕЛЬНО сначала выполните ШАГ 1 и ШАГ 2 — они ничего не меняют.

-- ============================================================
-- ШАГ 1. Проверка схемы: нужные колонки должны существовать.
-- Ожидаем 20 строк, среди них floor_from и floor_to.
-- ============================================================
\echo '--- ШАГ 1: колонки таблицы cards_installmentplan ---'
SELECT column_name, is_nullable
FROM information_schema.columns
WHERE table_name = 'cards_installmentplan'
ORDER BY ordinal_position;


-- ============================================================
-- Набор тарифов. selector — маска названия карточки,
-- exclude — маска-исключение (чтобы «Ватан» не цеплял «Ватан (Киргу)»).
-- ============================================================
CREATE TEMP VIEW _plans (
    selector, exclude, floor_from, floor_to, is_cash, term_months,
    dp_type, dp_percent, dp_min, dp_max, price
) AS
VALUES
-- ---------- ЖК Новый Горизонт, 22 блок (50 мес, взнос от 500 т) ----------
('%Новый Горизонт%22%', NULL, 9, 16, true,   0, '',      NULL::numeric, NULL::numeric,  NULL::numeric,  75000::numeric),
('%Новый Горизонт%22%', NULL, 9, 16, false, 50, 'fixed', NULL,          1000000,        NULL,            80000),
('%Новый Горизонт%22%', NULL, 9, 16, false, 50, 'fixed', NULL,           500000,        999999,          85000),
('%Новый Горизонт%22%', NULL, 2,  8, true,   0, '',      NULL,          NULL,           NULL,            80000),
('%Новый Горизонт%22%', NULL, 2,  8, false, 50, 'fixed', NULL,          1000000,        NULL,            85000),
('%Новый Горизонт%22%', NULL, 2,  8, false, 50, 'fixed', NULL,           500000,        999999,          90000),

-- ---------- ЖК Новый Горизонт, 10 блок (55 мес, взнос от 300 т) ----------
('%Новый Горизонт%10%', NULL, 9, 16, true,   0, '',      NULL,          NULL,           NULL,            70000),
('%Новый Горизонт%10%', NULL, 9, 16, false, 55, 'fixed', NULL,          1000000,        NULL,            75000),
('%Новый Горизонт%10%', NULL, 9, 16, false, 55, 'fixed', NULL,           500000,        999999,          80000),
('%Новый Горизонт%10%', NULL, 9, 16, false, 55, 'fixed', NULL,           300000,        499999,          85000),
('%Новый Горизонт%10%', NULL, 2,  8, true,   0, '',      NULL,          NULL,           NULL,            75000),
('%Новый Горизонт%10%', NULL, 2,  8, false, 55, 'fixed', NULL,          1000000,        NULL,            80000),
('%Новый Горизонт%10%', NULL, 2,  8, false, 55, 'fixed', NULL,           500000,        999999,          85000),
('%Новый Горизонт%10%', NULL, 2,  8, false, 55, 'fixed', NULL,           300000,        499999,          90000),

-- ---------- ЖК Парк у дома (?? соответствие цен срокам не указано) ----------
('%Парк у дома%',       NULL, NULL, NULL, true,   0, '',      NULL, NULL,    NULL,   75000),
('%Парк у дома%',       NULL, NULL, NULL, false, 48, 'fixed', NULL, 1000000, NULL,   80000),
('%Парк у дома%',       NULL, NULL, NULL, false, 48, 'fixed', NULL,  500000, 999999, 85000),
('%Парк у дома%',       NULL, NULL, NULL, false, 48, 'fixed', NULL,  300000, 499999, 90000),

-- ---------- ЖК Московский (?? соответствие цен срокам не указано) ----------
('%Московский%',        NULL, NULL, NULL, true,   0, '',      NULL, NULL,    NULL,   75000),
('%Московский%',        NULL, NULL, NULL, false, 72, 'fixed', NULL, 1000000, NULL,   80000),
('%Московский%',        NULL, NULL, NULL, false, 72, 'fixed', NULL,  500000, 999999, 85000),

-- ---------- ЖК Сириус (?? студия 105 т — отдельный тариф, не задан) ----------
('%Сириус%',            NULL, NULL, NULL, true,   0, '',        NULL, NULL, NULL, 95000),
('%Сириус%',            NULL, NULL, NULL, false, 36, 'percent', 30,   NULL, NULL, 100000),

-- ---------- ЖК Гранд Эра ----------
('%Гранд Эра%',         NULL, NULL, NULL, true,   0, '',        NULL, NULL, NULL, 80000),
('%Гранд Эра%',         NULL, NULL, NULL, false, 48, 'percent', 50,   NULL, NULL, 85000),
('%Гранд Эра%',         NULL, NULL, NULL, false, 48, 'percent', 30,   NULL, NULL, 90000),

-- ---------- ЖК Товерс ----------
('%Товерс%',            NULL, NULL, NULL, true,   0, '',        NULL, NULL, NULL, 90000),
('%Товерс%',            NULL, NULL, NULL, false, 30, 'percent', 30,   NULL, NULL, 115000),

-- ---------- ЖК Ватан (Киргу) (?? "95т – 2млн" против "взнос 30%") ----------
('%Киргу%',             NULL, NULL, NULL, true,   0, '',      NULL, NULL,    NULL, 85000),
('%Киргу%',             NULL, NULL, NULL, false, 12, 'fixed', NULL, 2000000, NULL, 95000),

-- ---------- ЖК Ватан (без Киргу) (?? соответствие цен не указано) ----------
('%Ватан%',        '%Киргу%', NULL, NULL, true,   0, '',        NULL, NULL, NULL, 95000),
('%Ватан%',        '%Киргу%', NULL, NULL, false, 36, 'percent', 50,   NULL, NULL, 100000),

-- ---------- АК Алые Паруса (?? "70-75 нал" — взял 75) ----------
('%Алые Паруса%',       NULL, NULL, NULL, true,   0, '',      NULL, NULL,    NULL,   75000),
('%Алые Паруса%',       NULL, NULL, NULL, false, 36, 'fixed', NULL, 1000000, NULL,   80000),
('%Алые Паруса%',       NULL, NULL, NULL, false, 36, 'fixed', NULL,  500000, 999999, 85000),
('%Алые Паруса%',       NULL, NULL, NULL, false, 36, 'fixed', NULL,  300000, 499999, 90000),

-- ---------- ЖК Брода 2 (?? соответствие цен 60/65/70 не указано) ----------
('%Брода%',             NULL, NULL, NULL, true,   0, '',        NULL, NULL, NULL, 60000),
('%Брода%',             NULL, NULL, NULL, false, 36, 'percent', 30,   NULL, NULL, 70000),

-- ---------- АК Морская Деревня ----------
('%Морская Деревня%',   NULL, NULL, NULL, true,   0, '',        NULL, NULL, NULL, 75000),
('%Морская Деревня%',   NULL, NULL, NULL, false, 12, 'percent', 30,   NULL, NULL, 80000),

-- ---------- ЖК СИТЕ (?? только 5 блок; для 1-2 блока цена диапазоном) ----------
('%СИТЕ%',              NULL, NULL, NULL, false, 39, 'percent', 30,   NULL, NULL, 130000),

-- ---------- ЖК Арена Парк ----------
('%Арена Парк%',        NULL, NULL, NULL, true,   0, '',      NULL, NULL,   NULL, 98000),
('%Арена Парк%',        NULL, NULL, NULL, false, 30, 'fixed', NULL, 500000, NULL, 120000),
('%Арена Парк%',        NULL, NULL, NULL, false, 60, 'fixed', NULL, 500000, NULL, 140000),

-- ---------- АК Azure Prime ----------
('%Azure Prime%',       NULL, NULL, NULL, true,   0, '',        NULL, NULL, NULL, 165000),
('%Azure Prime%',       NULL, NULL, NULL, false, 36, 'percent', 30,   NULL, NULL, 185000),

-- ---------- АК Azure Residence ----------
('%Azure Residence%',   NULL, NULL, NULL, true,   0, '',        NULL, NULL, NULL, 150000),
('%Azure Residence%',   NULL, NULL, NULL, false, 30, 'percent', 30,   NULL, NULL, 220000),

-- ---------- ЖК Белый дом (?? срок рассрочки не указан — только наличные) ----------
('%Белый дом%',         NULL, NULL, NULL, true,   0, '',        NULL, NULL, NULL, 135000),

-- ---------- ЖК Резиденция (?? срок не указан — только наличные) ----------
('%Резиденция%',        NULL, NULL, NULL, true,   0, '',        NULL, NULL, NULL, 150000),

-- ---------- ЖК Золотые пески 2 (?? "от 5 мес" — максимум неизвестен) ----------
('%Золотые пески%',     NULL, NULL, NULL, true,   0, '',        NULL, NULL, NULL, 250000),

-- ---------- ЖК Гранд Хиллс (?? цена диапазоном 130-150) ----------
('%Гранд Хиллс%',       NULL, NULL, NULL, true,   0, '',        NULL, NULL, NULL, 130000),
('%Гранд Хиллс%',       NULL, NULL, NULL, false, 50, 'percent', 30,   NULL, NULL, 150000),

-- ---------- ЖК Империал ----------
('%Империал%',          NULL, NULL, NULL, true,   0, '',      NULL, NULL,    NULL, 86000),
('%Империал%',          NULL, NULL, NULL, false, 30, 'fixed', NULL, 1000000, NULL, 115000),

-- ---------- ЖК Гранд берег (?? цена диапазоном 148-200) ----------
('%Гранд берег%',       NULL, NULL, NULL, true,   0, '',        NULL, NULL, NULL, 148000),
('%Гранд берег%',       NULL, NULL, NULL, false, 84, 'percent', 30,   NULL, NULL, 200000);

-- НЕ ВОШЛИ (цена указана диапазоном, единой цены за м² нет):
--   АК Мальта      — «от 100 до 205 т»
--   ЖК Ботаника    — «от 146 до 198 / от 138 до 196 тыс»


-- ============================================================
-- ШАГ 2. ПРЕДПРОСМОТР (ничего не меняет).
-- Смотрим, какие карточки нашлись под какие маски.
-- Если какой-то ЖК не нашёлся или нашёлся лишний — правьте selector выше.
-- ============================================================
\echo '--- ШАГ 2а: сколько карточек нашла каждая маска ---'
SELECT p.selector,
       count(DISTINCT c.id) AS cards_found,
       string_agg(DISTINCT c.title, ' | ' ORDER BY c.title) AS titles
FROM _plans p
LEFT JOIN cards_card c
       ON c.title ILIKE p.selector
      AND (p.exclude IS NULL OR c.title NOT ILIKE p.exclude)
GROUP BY p.selector
ORDER BY cards_found, p.selector;

\echo '--- ШАГ 2б: сколько всего тарифов будет создано ---'
SELECT count(*) AS plans_to_create
FROM _plans p
JOIN cards_card c
       ON c.title ILIKE p.selector
      AND (p.exclude IS NULL OR c.title NOT ILIKE p.exclude);


-- ============================================================
-- ШАГ 3. ЗАПИСЬ. Раскомментируйте блок ниже и запустите файл снова.
-- Транзакция: при ошибке откатится целиком.
-- ============================================================

-- BEGIN;
--
-- -- Удалить старые тарифы у затронутых карточек (чтобы не было дублей
-- -- при повторном запуске). Если старые тарифы нужно сохранить — уберите.
-- DELETE FROM cards_installmentplan
-- WHERE card_id IN (
--     SELECT DISTINCT c.id
--     FROM _plans p
--     JOIN cards_card c
--            ON c.title ILIKE p.selector
--           AND (p.exclude IS NULL OR c.title NOT ILIKE p.exclude)
-- );
--
-- INSERT INTO cards_installmentplan (
--     card_id, apartment_type, floor_from, floor_to,
--     is_cash, term_months,
--     down_payment_type, down_payment_percent,
--     down_payment_min_amount, down_payment_max_amount,
--     price_per_sqm,
--     accepts_mat_capital, mat_capital_note,
--     extra_conditions, note,
--     valid_from, valid_until, is_active,
--     created_at, updated_at
-- )
-- SELECT
--     c.id, '', p.floor_from, p.floor_to,
--     p.is_cash, p.term_months,
--     p.dp_type, p.dp_percent,
--     p.dp_min, p.dp_max,
--     p.price,
--     false, '',
--     '{}', '',
--     NULL, NULL, true,
--     NOW(), NOW()
-- FROM _plans p
-- JOIN cards_card c
--        ON c.title ILIKE p.selector
--       AND (p.exclude IS NULL OR c.title NOT ILIKE p.exclude);
--
-- COMMIT;
