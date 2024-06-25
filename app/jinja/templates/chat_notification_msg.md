{% if state == "ON" -%}
{{ on_emoji }} *{{ "bot.electricity_has_turned_on" | t | tg_escape }}*
{% elif state == "OFF" -%}
{{ off_emoji }} *{{ "bot.electricity_has_turned_off" | t | tg_escape}}*
{% elif state == "UNKNOWN" -%}
🤷‍♂️ *{{ "bot.electricity_state_unknown" | t | tg_escape}}*
{% endif %}
{% if message.schedule_enabled -%}
{% for group in groups %}

*{{ "bot.group" | t | tg_escape }} {{ group | tg_escape }}:*
{{ groups_state[group].current_state | now_in_zone_text | tg_escape }} до {{ groups_state[group].till | time_fmt }}
{% for zone in groups_state[group].forecast -%}
{{ "bot.next" | t | tg_escape }} \- {{ zone.name | zone_name | tg_escape }} {{ "bot.at" | t }} {{ zone.start | time_fmt }} \- {{ zone.end | time_fmt }}
{% endfor -%}
{% endfor -%}
{%- else %}

*Наразі графіки відключень не застосовуються\.*
{% if state == "OFF" %}

Можливо сталася аварія\. Що можна зробити:

\- перевірте причини відключення за допомогою [бота](https://t\.me/DTEKOdeskiElektromerezhiBot)
\- повідомте про відключення на [сайті ДТЕК](https://www\.dtek\-oem\.com\.ua/ua/shutdowns) 
\- подзвоніть за телефонами:
    [\+380487059090](tel:\+380487059090)
    [\+380687509090](tel:\+380687509090)
    [\+380957509090](tel:\+380957509090)
    [\+380737509090](tel:\+380737509090)
{% endif -%}
{%- endif -%}
{% if state == "ON" %}

⏱ Сиділи без світла {{ last_switches_timedelta | time_delta }}
{%- elif state == "OFF" %}

⏱ Світло не вимикали {{ last_switches_timedelta | time_delta }}
{%- endif -%}