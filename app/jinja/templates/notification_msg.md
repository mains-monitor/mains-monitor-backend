{% if state == "ON" -%}

{{ on_emoji }} {{ "bot.electricity_has_turned_on" | t }}

    {%- if next_blackout %}


{{ "bot.according_to_schedule" | t }} \({{ "bot.group" | t }} {{ group }}\):
⏰ {{ "bot.will_turn_off_at" | t }} {{ next_blackout | time_fmt }} {{ "bot.in" | t }} {{ next_blackout | time_delta }}

    {%- else %}

🤷‍♂️ {{ "bot.next_blackout_unknown" | t }}

    {%- endif -%}

{% elif state == "OFF" -%}

    {{ off_emoji }} {{ "bot.electricity_has_turned_off" | t }}

    {%- if next_recovery %}


{{ "bot.according_to_schedule" | t }} \({{ "bot.group" | t }} {{ group }}\):
⏰ {{ "bot.will_turn_on_at" | t }} {{ next_recovery | time_fmt }} {{ "bot.in" | t }} {{ next_recovery | time_delta }}

    {%- else %}

🤷‍♂️ {{ "bot.next_recovery_unknown" | t }}

    {%- endif -%}
{%- elif state == "UNKNOWN" -%}

🤷‍♂️ {{ "bot.electricity_state_unknown" | t}}

{{ "bot.according_to_schedule" | t }} \({{ "bot.group" | t }} {{ group }}\):
⏰ {{ "bot.will_turn_on_at" | t }} {{ next_recovery | time_fmt }} {{ "bot.in" | t }} {{ next_recovery | time_delta }}
⏰ {{ "bot.will_turn_off_at" | t }} {{ next_blackout | time_fmt }} {{ "bot.in" | t }} {{ next_blackout | time_delta }}
{%- endif -%}
{%- if state_by_schedule == "ON" %}


⚡️ {{ "bot.now_in_white_zone" | t }}
{%- elif state_by_schedule == "OFF" %}


◼️ {{ "bot.now_in_black_zone" | t }}
{%- elif state_by_schedule == "UNKNOWN" %}


◻️ {{ "bot.now_in_gray_zone" | t }}
{%- endif -%}