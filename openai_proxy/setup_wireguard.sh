#!/bin/bash
# Быстрая установка WireGuard VPN на голландском сервере
# Использование: sudo bash setup_wireguard.sh

set -e

echo "=== Установка WireGuard VPN ==="

# Установка WireGuard
apt update
apt install -y wireguard qrencode

# Генерация ключей сервера
cd /etc/wireguard
umask 077

wg genkey | tee server_private.key | wg pubkey > server_public.key
SERVER_PRIVATE=$(cat server_private.key)
SERVER_PUBLIC=$(cat server_public.key)

# Генерация ключей клиента
wg genkey | tee client_private.key | wg pubkey > client_public.key
CLIENT_PRIVATE=$(cat client_private.key)
CLIENT_PUBLIC=$(cat client_public.key)

# Определяем внешний интерфейс
INTERFACE=$(ip route | grep default | awk '{print $5}')
SERVER_IP=$(curl -s ifconfig.me)

# Конфиг сервера
cat > /etc/wireguard/wg0.conf << EOF
[Interface]
Address = 10.0.0.1/24
ListenPort = 51820
PrivateKey = $SERVER_PRIVATE
PostUp = iptables -A FORWARD -i wg0 -j ACCEPT; iptables -t nat -A POSTROUTING -o $INTERFACE -j MASQUERADE
PostDown = iptables -D FORWARD -i wg0 -j ACCEPT; iptables -t nat -D POSTROUTING -o $INTERFACE -j MASQUERADE

[Peer]
PublicKey = $CLIENT_PUBLIC
AllowedIPs = 10.0.0.2/32
EOF

# Конфиг клиента
cat > /etc/wireguard/client.conf << EOF
[Interface]
PrivateKey = $CLIENT_PRIVATE
Address = 10.0.0.2/24
DNS = 1.1.1.1, 8.8.8.8

[Peer]
PublicKey = $SERVER_PUBLIC
Endpoint = $SERVER_IP:51820
AllowedIPs = 0.0.0.0/0
PersistentKeepalive = 25
EOF

# Включаем IP forwarding
echo "net.ipv4.ip_forward=1" >> /etc/sysctl.conf
sysctl -p

# Запуск WireGuard
systemctl enable wg-quick@wg0
systemctl start wg-quick@wg0

# Открываем порт
ufw allow 51820/udp 2>/dev/null || true

echo ""
echo "=== WireGuard установлен! ==="
echo ""
echo "Конфиг клиента сохранён в: /etc/wireguard/client.conf"
echo ""
echo "QR-код для мобильного приложения:"
qrencode -t ansiutf8 < /etc/wireguard/client.conf
echo ""
echo "Скопируйте client.conf на свой компьютер/телефон"
