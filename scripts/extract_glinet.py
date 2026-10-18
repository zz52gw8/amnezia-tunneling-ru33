#!/usr/bin/env python3
"""Конвертирует amnezia-ip.json в текстовый список для роутеров GL.iNet.

Формат — онлайн-файл правил VPN-политики по целевым адресам (прошивка
4.7+): по одной записи на строку, CIDR-подсеть или одиночный IPv4-адрес.
Комментарии документацией не предусмотрены, поэтому в файле только записи.
https://docs.gl-inet.com/router/en/4/tutorials/how_to_configure_domain_and_ip_filtering_rules_for_glinet_routers_via_an_online_text_file/

Использование: extract_glinet.py <amnezia-ip.json> <out.txt>
"""
import ipaddress, json, os, sys

SRC, OUT = sys.argv[1], sys.argv[2]

# Строгий разбор: IPv6, биты хоста или мусор роняют сборку, а не уходят на роутер
nets = [ipaddress.IPv4Network(e['hostname'])
        for e in json.load(open(SRC, encoding='utf-8'))]

# Роутер сам перекачивает файл раз в сутки и применяет как есть. Обрезанный
# список (сбой загрузки ru.txt в основной сборке) молча снял бы правила
# с части российских сетей, поэтому резкое сокращение считаем ошибкой.
old = 0
if os.path.exists(OUT):
    old = sum(1 for line in open(OUT, encoding='utf-8') if line.strip())
if not nets or len(nets) < old * 0.75:
    sys.exit(f"ошибка: {len(nets)} подсетей против {old} в текущем {OUT} — "
             f"похоже на сбой источника, список публиковать нельзя")

with open(OUT, 'w', encoding='utf-8', newline='\n') as f:
    for n in nets:
        # /32 пишем голым адресом: этот формат в документации указан явно
        f.write(f"{n.network_address if n.prefixlen == 32 else n}\n")
print(f"{len(nets)} подсетей -> {OUT} (было {old})")
